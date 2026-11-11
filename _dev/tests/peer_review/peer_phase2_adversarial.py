"""Independent Fase 2 adversarial audit — source is the unmodified main branch.

A PASS here means the gap was REPRODUCED, not that the product passed acceptance.
All tests use temporary synthetic fixtures and exact Ricoeur import/search code.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import tempfile

from ricoeur.db import init_db, get_connection
from ricoeur.importers.base import insert_conversation
from ricoeur.importers.chatgpt import import_chatgpt
from ricoeur.retrieval import search_messages

results = {}


def record(code, condition, observed):
    if not condition:
        raise AssertionError(f"Gap not reproduced: {code}: {observed}")
    results[code] = {"status": "REPRODUCED", "observed": observed}


def msg(mid, text):
    return {
        "id": mid, "author": {"role": "assistant"},
        "content": {"content_type": "text", "parts": [text]},
        "create_time": 1700000000,
    }


def conv(cid="chat-root", selected="b", include_side=True):
    kids = ["a", "b"] if selected == "b" else ["b", "a"]
    mapping = {"root": {"parent": None, "children": kids, "message": None},
               "a": {"parent": "root", "children": [], "message": msg("branch-a", "hiddenunique conceptual alternative")},
               "b": {"parent": "root", "children": [], "message": msg("branch-b", "visibleunique selected response")}}
    if not include_side:
        mapping["root"]["children"] = ["b"]
    return {
        "id": cid, "title": "SYNTHETIC", "create_time": 1700000000,
        "mapping": mapping, "current_node": selected,
    }


with tempfile.TemporaryDirectory() as d:
    temp = Path(d)

    # A: Source IDs are globally keyed, not qualified by provider.
    home = temp / "collision"; home.mkdir()
    con = init_db(home)
    try:
        assert insert_conversation(con, id="shared-id", title="A", platform="chatgpt",
                                   model=None, created_at=None)
        second = insert_conversation(con, id="shared-id", title="B", platform="claude",
                                     model=None, created_at=None)
        record("IDENTITY-001", second is False and con.execute(
            "SELECT platform FROM conversations WHERE id='shared-id'").fetchone()[0] == "chatgpt",
            "Second provider's conversation silently skipped when external IDs coincide")
    finally:
        con.close()

    # B: Branch saved as raw node but absent from searchable messages.
    home = temp / "branches"; home.mkdir()
    con = init_db(home)
    src = temp / "branches.json"
    src.write_text(json.dumps([conv()]), encoding="utf-8")
    try:
        import_chatgpt(con, src)
        rows = con.execute("SELECT id FROM messages").fetchall()
        hidden_nodes = con.execute(
            "SELECT count(*) FROM chatgpt_nodes WHERE node_id='a'").fetchone()[0]
        hidden_hits = search_messages(con, '"hiddenunique"')["count"]
        record("TREE-002", len(rows) == 1 and hidden_nodes == 1 and hidden_hits == 0,
               "One selected branch searchable, alternate preserved as opaque raw node")

        # Reimport with update toggles branch. Raw node INSERT OR IGNORE keeps old children JSON.
        src.write_text(json.dumps([conv(selected="a")]), encoding="utf-8")
        import_chatgpt(con, src, update=True)
        searchable = {r[0] for r in con.execute("SELECT id FROM messages")}
        children = json.loads(con.execute(
            "SELECT children_json FROM chatgpt_nodes WHERE node_id='root'").fetchone()[0])
        record("REIMPORT-003",
               searchable == {"branch-a", "branch-b"} and children == ["a", "b"],
               "Changing selected branch adds message but leaves historical main path and raw children unchanged")

        # Dry-run estimates 'new' without validating malformed mapping or existing IDs.
        bad = conv(cid="malformed")
        bad["mapping"]["root"] = None
        src.write_text(json.dumps([bad]), encoding="utf-8")
        dry = import_chatgpt(con, src, dry_run=True)
        record("DRYRUN-004", dry.new == 1 and dry.parsed == 1,
               "Malformed conversation counted as new in dry_run without validation")
    finally:
        con.close()

    # C: A bounded transaction can commit 25 conversations, then fail at conversation 26.
    home = temp / "partial"; home.mkdir()
    src = temp / "partial.json"
    messages = [conv(cid=f"c{i}") for i in range(25)]
    bad = conv(cid="broken26")
    bad["mapping"]["root"] = None
    messages.append(bad)
    src.write_text(json.dumps(messages), encoding="utf-8")
    conn = init_db(home)
    try:
        errored = False
        try:
            import_chatgpt(conn, src)
        except AttributeError:
            errored = True
        probe = sqlite3.connect(home / "ricoeur.db")
        committed = probe.execute("SELECT count(*) FROM conversations").fetchone()[0]
        probe.close()
        record("ATOMICITY-005", errored and committed == 25,
               "Import failed at 26th conversation, while 25 had already committed")
    finally:
        conn.close()

    # D: Read-only consumers that call get_connection() can initiate migration.
    home = temp / "migration"; home.mkdir()
    old_db = home / "ricoeur.db"
    legacy = sqlite3.connect(old_db)
    legacy.executescript("""
    CREATE TABLE conversations(id TEXT PRIMARY KEY, title TEXT, platform TEXT NOT NULL);
    CREATE TABLE schema_meta(key TEXT PRIMARY KEY, value TEXT);
    INSERT INTO schema_meta VALUES('version','1');
    """)
    legacy.close()
    old_hash = sha256(old_db.read_bytes()).hexdigest()
    opened = get_connection(home)
    try:
        migrated_version = opened.execute(
            "SELECT value FROM schema_meta WHERE key='version'").fetchone()[0]
    finally:
        opened.close()
    record("READONLY-006",
           migrated_version == "2" and sha256(old_db.read_bytes()).hexdigest() != old_hash,
           "get_connection() migrated an existing v1 database during opening; MCP uses this helper")

    # E: FTS5 search context re-reads the complete conversation for each hit.
    home = temp / "nplus1"; home.mkdir()
    con = init_db(home)
    try:
        con.execute("INSERT INTO conversations(id, title, platform) VALUES ('many','Synthetic','chatgpt')")
        con.executemany(
            "INSERT INTO messages(id,conv_id,role,content,timestamp) VALUES(?,?,?,?,?)",
            [(f"m{i}", "many", "user", "benchmarkneedle" if i < 20 else "other",
              f"2026-01-01T00:{i//60:02d}:{i%60:02d}") for i in range(100)]
        )
        con.commit()
        statements = []
        con.set_trace_callback(statements.append)
        out = search_messages(con, '"benchmarkneedle"', limit=20, context=1)
        con.set_trace_callback(None)
        full_reads = sum("FROM MESSAGES" in " ".join(q.upper().split())
                         and "WHERE CONV_ID" in " ".join(q.upper().split())
                         and "ORDER BY TIMESTAMP" in " ".join(q.upper().split())
                         for q in statements)
        record("RETRIEVAL-007", out["count"] == 20 and full_reads == 20,
               f"20 hits caused {full_reads} full-conversation SQL reads (100 rows each)")
    finally:
        con.close()

print(json.dumps({
    "audit": "Fase2 independent adversarial reproduction",
    "meaning": "REPRODUCED means action needed, not a functional PASS",
    "source": "unmodified ricoeur modules on main",
    "synthetic_only": True,
    "finding_count": len(results),
    "findings": results,
}, ensure_ascii=False, indent=2))
