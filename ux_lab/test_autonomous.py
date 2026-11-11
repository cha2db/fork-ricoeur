"""Round 8 regression: synthetic Ricoeur FTS5 SQLite; no user database writes."""
import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as temp:
    db = Path(temp) / "synthetic.db"
    conn = sqlite3.connect(db)
    conn.executescript("""
    CREATE TABLE conversations(
      id TEXT PRIMARY KEY,title TEXT,platform TEXT,model TEXT,created_at TEXT,
      message_count INTEGER,source_path TEXT);
    CREATE TABLE messages(id TEXT PRIMARY KEY,conv_id TEXT,role TEXT,content TEXT,timestamp TEXT);
    CREATE VIRTUAL TABLE messages_fts USING fts5(
      content,conv_id UNINDEXED,id UNINDEXED,role UNINDEXED,
      content='messages',content_rowid='rowid');
    CREATE TRIGGER messages_ai AFTER INSERT ON messages BEGIN
      INSERT INTO messages_fts(rowid,content,conv_id,id,role)
      VALUES(new.rowid,new.content,new.conv_id,new.id,new.role);
    END;
    """)
    for i in range(3):
        cid = f"c{i}"
        conn.execute("INSERT INTO conversations VALUES(?,?,?,?,?,?,?)",
                     (cid, f"Chat {i}", "chatgpt", None, "2026-01-01", 2, "fixture.json"))
        for j in range(2):
            conn.execute("INSERT INTO messages VALUES(?,?,?,?,?)",
                         (f"m{i}{j}",cid,"user" if j == 0 else "assistant",
                          f"docker topic {i}" if j == 0 else "answer",
                          f"2026-01-01T00:0{j}:00"))
    conn.commit()
    conn.close()
    before = hashlib.sha256(db.read_bytes()).hexdigest()

    def run(*args):
        cp = subprocess.run([sys.executable, str(ROOT / "ux.py"), "--db", str(db), *args],
                            capture_output=True, text=True)
        assert cp.returncode == 0, (cp.stderr, cp.stdout)
        obj = json.loads(cp.stdout)
        assert obj["status"] == "ok", obj
        return obj["data"]

    assert run("capabilities")["search_core"] == "ricoeur.retrieval.search_messages"
    assert len(run("conversations")) == 3
    assert len(run("conversations", "--query", "docker")) == 3
    assert len(run("conversations", "--query", "absent")) == 0
    assert run("search", "--query", "docker")["count"] == 3
    assert run("search", "--query", "docker", "--platform", "claude")["count"] == 0
    transcript = run("transcript", "c0")
    assert len(transcript["messages"]) == 2
    assert transcript["messages"][0]["next_id"] == "m01"
    assert transcript["messages"][1]["previous_id"] == "m00"
    graph = run("graph", "--query", "docker")
    assert len(graph["nodes"]) == 4 and len(graph["edges"]) == 3
    assert all(e["evidence_message_ids"] and not e["semantic_claim"] for e in graph["edges"])
    assert not run("graph")["edges"]
    assert run("message", "m01")["message"]["id"] == "m01"
    assert hashlib.sha256(db.read_bytes()).hexdigest() == before
    print("PASS UX-008: 14 assertions, 3 chats/6 messages, FTS5 ports, evidence graph, read-only")
