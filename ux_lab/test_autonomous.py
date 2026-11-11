"""Autonomous smoke tests; temporary synthetic SQLite, never the user's DB."""
import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as d:
    db=Path(d)/"synthetic.db"
    conn=sqlite3.connect(db)
    conn.executescript("""CREATE TABLE conversations(id TEXT PRIMARY KEY,title TEXT,platform TEXT,created_at TEXT,message_count INTEGER);
    CREATE TABLE messages(id TEXT PRIMARY KEY,conv_id TEXT,role TEXT,content TEXT,timestamp TEXT);""")
    for i in range(3):
        cid=f"c{i}";conn.execute("INSERT INTO conversations VALUES(?,?,?,?,?)",(cid,f"Chat {i}","chatgpt","2026-01-01",2))
        for j in range(2):
            conn.execute("INSERT INTO messages VALUES(?,?,?,?,?)",(f"m{i}{j}",cid,"user" if j==0 else "assistant",f"docker topic {i}" if j==0 else "answer",f"2026-01-01T00:0{j}:00"))
    conn.commit();conn.close()
    def run(*args):
        cp=subprocess.run([sys.executable,str(ROOT/"ux.py"),"--db",str(db),*args],capture_output=True,text=True)
        assert cp.returncode==0,(cp.stderr,cp.stdout)
        obj=json.loads(cp.stdout);assert obj["status"]=="ok",obj
        return obj["data"]
    assert run("capabilities")["storage"]=="read_only_ricoeur_sqlite"
    assert len(run("conversations"))==3
    assert len(run("conversations","--query","docker"))==3
    assert len(run("conversations","--query","absent"))==0
    t=run("transcript","c0");assert len(t["messages"])==2
    assert t["messages"][0]["next_id"]=="m01"
    assert t["messages"][1]["previous_id"]=="m00"
    g=run("graph","--query","docker");assert len(g["nodes"])==3 and len(g["edges"])==2
    assert all(not e["semantic_claim"] for e in g["edges"])
    assert not run("graph")["edges"]
    assert db.exists()
    print("PASS: 9 autonomous assertions; 3 chats / 6 messages; read-only SQLite; CLI ports")
