"""Phase2 strict read-only port and FTS5 bounded context regression."""
from pathlib import Path
import json
import sqlite3
import tempfile

from ricoeur.db import init_db, get_read_connection, SCHEMA_VERSION
from ricoeur.retrieval import search_messages, get_message_context

gates = 0
def check(ok, label):
    global gates
    assert ok, label
    gates += 1

with tempfile.TemporaryDirectory() as td:
    home = Path(td)
    missing = home/"missing"
    try:
        get_read_connection(missing)
    except FileNotFoundError:
        check(not (missing/"ricoeur.db").exists(), "nonexistent archive not initialized")
    else:
        raise AssertionError("read port initialized missing file")

    legacy = home/"legacy"
    legacy.mkdir()
    raw = legacy/"ricoeur.db"
    c = sqlite3.connect(raw)
    c.executescript("""CREATE TABLE conversations(id TEXT PRIMARY KEY,platform TEXT NOT NULL);
    CREATE TABLE schema_meta(key TEXT PRIMARY KEY,value TEXT);
    INSERT INTO schema_meta VALUES('version','1');""")
    c.close()
    try:
        get_read_connection(legacy)
    except RuntimeError as exc:
        check("schema version 1" in str(exc), "legacy requires explicit migration")
    else:
        raise AssertionError("reader migrated a legacy schema")
    cc=sqlite3.connect(raw)
    check(cc.execute("SELECT value FROM schema_meta WHERE key='version'").fetchone()[0]=="1",
          "legacy version unchanged")
    check("project" not in {r[1] for r in cc.execute("PRAGMA table_info(conversations)")},
          "legacy columns unchanged")
    cc.close()

    archive=home/"archive"
    archive.mkdir()
    conn=init_db(archive)
    check(SCHEMA_VERSION>=2,"versioned schema available")
    conn.execute("INSERT INTO conversations(id,title,platform) VALUES('one','Synthetic','chatgpt')")
    conn.executemany("INSERT INTO messages(id,conv_id,role,content,timestamp) VALUES(?,?,?,?,?)",[
        (f"m{i:03d}","one","user","searchneedle" if i<20 else "other",
         f"2026-01-01T00:{i//60:02d}:{i%60:02d}") for i in range(100)])
    conn.commit()
    conn.close()
    ro=get_read_connection(archive)
    try:
        check(ro.execute("PRAGMA query_only").fetchone()[0]==1, "query-only flag")
        try:
            ro.execute("INSERT INTO conversations(id,platform) VALUES ('evil','chatgpt')")
        except sqlite3.OperationalError:
            check(True,"write rejected by SQLite")
        else:
            raise AssertionError("read-only port accepted write")
        trace=[]
        ro.set_trace_callback(trace.append)
        result=search_messages(ro, '"searchneedle"',limit=20,context=1)
        ro.set_trace_callback(None)
        check(result["count"]==20,"all FTS hits")
        # Trace includes FTS5 virtual-table internal SQL; count only the
        # explicit window query, not SQLite's internal index statements.
        windows=sum("WITH numbered AS" in sql for sql in trace)
        old_full_reads=sum("WHERE conv_id = ?" in sql and
                           "ORDER BY timestamp, rowid" in sql for sql in trace)
        check(windows==1 and old_full_reads==0,
              f"one context-window query (got {windows}); no legacy full reads")
        check(result["hits"][0]["message"]["id"]=="m000","stable first ID")
        check(result["hits"][0]["before"]==[] and result["hits"][0]["after"][0]["id"]=="m001",
              "first boundary")
        check(result["hits"][-1]["before"][0]["id"]=="m018"
              and result["hits"][-1]["after"][0]["id"]=="m020","middle boundary")
        window=get_message_context(ro,"m050",context=2)
        check([x["id"] for x in window["before"]]==["m048","m049"],"reader before")
        check([x["id"] for x in window["after"]]==["m051","m052"],"reader after")
        check(get_message_context(ro,"missing") is None,"not found")
        check(search_messages(ro,'"neverpresent"')["count"]==0,"empty result")
    finally:
        ro.close()
print("PASS PHASE2 FIX-001:", gates, "gates; strict ro, no migrations, bounded SQL windows")
