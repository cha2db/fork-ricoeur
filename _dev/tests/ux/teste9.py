"""Round 9: prove UX adapter delegates to existing Ricoeur FTS5 core, not LIKE."""
import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
with tempfile.TemporaryDirectory() as d:
    db=Path(d)/"fixture.db"
    con=sqlite3.connect(db)
    con.executescript("""CREATE TABLE conversations(id TEXT PRIMARY KEY,title TEXT,platform TEXT);
CREATE TABLE messages(id TEXT PRIMARY KEY,conv_id TEXT,role TEXT,content TEXT,timestamp TEXT);
CREATE VIRTUAL TABLE messages_fts USING fts5(content,conv_id UNINDEXED,id UNINDEXED,role UNINDEXED,content='messages',content_rowid='rowid');
CREATE TRIGGER messages_ai AFTER INSERT ON messages BEGIN
INSERT INTO messages_fts(rowid,content,conv_id,id,role) VALUES(new.rowid,new.content,new.conv_id,new.id,new.role); END;""")
    con.executemany("INSERT INTO conversations VALUES(?,?,?)",[("c1","A","chatgpt"),("c2","B","claude"),("c3","C","chatgpt")])
    con.executemany("INSERT INTO messages VALUES(?,?,?,?,?)",[
      ("m1","c1","user","docker build","2026-01-01T00:00:00"),
      ("m2","c1","assistant","docker deploy","2026-01-01T00:00:01"),
      ("m3","c2","user","docker networks","2026-01-01T00:00:02"),
      ("m4","c3","user","unrelated","2026-01-01T00:00:03")])
    con.commit();con.close()
    def run(*args,ok=True):
        cp=subprocess.run([sys.executable,str(ROOT/"ux_lab/retrieval_port.py"),"--db",str(db),*args],capture_output=True,text=True)
        assert (cp.returncode==0)==ok,(cp.returncode,cp.stderr,cp.stdout)
        return json.loads(cp.stdout)
    result=run("search","docker","--context","1")
    assert result["schema_version"]=="ux.retrieval.v1"
    assert result["data"]["count"]==3
    assert {h["message"]["id"] for h in result["data"]["hits"]}=={"m1","m2","m3"}
    assert all(h["conversation"]["id"] in ("c1","c2") for h in result["data"]["hits"])
    filtered=run("search","docker","--platform","chatgpt")
    assert filtered["data"]["count"]==2
    context=run("context","m1","--context","1")
    assert context["data"]["after"][0]["id"]=="m2"
    missing=run("context","absent",ok=False)
    assert missing["errors"]==["message_not_found"]
    bad=run("search","docker","--limit","0",ok=False)
    assert bad["status"]=="error"
    assert sqlite3.connect(db).execute("SELECT COUNT(*) FROM messages").fetchone()[0]==4
    print("PASS UX-009: 8 gates; existing FTS5 retrieval, context, filter, errors, read-only; 3 chats/4 messages")
