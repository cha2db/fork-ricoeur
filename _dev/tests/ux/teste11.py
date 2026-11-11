"""UX-011 integration: real Ricoeur FTS5 -> same CLI/HTTP -> GUI contract."""
import hashlib
import json
import sqlite3
import sys
import tempfile
import threading
import urllib.error
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "ux_lab"))
import ux


def build(db):
    conn = sqlite3.connect(db)
    conn.executescript("""
    CREATE TABLE conversations (
      id TEXT PRIMARY KEY,title TEXT,platform TEXT,model TEXT,created_at TEXT,
      updated_at TEXT,language TEXT,topic_id INTEGER,message_count INTEGER,project TEXT,source_path TEXT);
    CREATE TABLE messages (
      id TEXT PRIMARY KEY,conv_id TEXT,role TEXT,content TEXT,timestamp TEXT,
      content_type TEXT,token_count INTEGER);
    CREATE VIRTUAL TABLE messages_fts USING fts5(
      content,conv_id UNINDEXED,id UNINDEXED,role UNINDEXED,
      content='messages',content_rowid='rowid');
    CREATE TRIGGER messages_ai AFTER INSERT ON messages BEGIN
      INSERT INTO messages_fts(rowid,content,conv_id,id,role)
      VALUES(new.rowid,new.content,new.conv_id,new.id,new.role);
    END;
    """)
    conn.executemany("INSERT INTO conversations(id,title,platform,created_at,message_count,source_path) VALUES(?,?,?,?,?,?)",[
        ("c1","Docker tutorial","chatgpt","2026-10-01",3,"chatgpt-export.json"),
        ("c2","Container orchestration","claude","2026-10-02",1,"claude-export.json"),
        ("c3","Other topic","chatgpt","2026-10-03",1,"other.json"),
    ])
    conn.executemany("INSERT INTO messages(id,conv_id,role,content,timestamp) VALUES(?,?,?,?,?)",[
        ("m1","c1","user","needle docker build","2026-10-01T01:00"),
        ("m2","c1","assistant","needle compose deployment","2026-10-01T01:01"),
        ("m3","c1","user","what's next","2026-10-01T01:02"),
        ("m4","c2","user","needle kubernetes","2026-10-02T01:00"),
        ("m5","c3","user","unrelated","2026-10-03T01:00"),
    ])
    conn.commit()
    conn.close()


with tempfile.TemporaryDirectory() as temp:
    db = Path(temp) / "ricoeur.sqlite3"
    build(db)
    baseline = hashlib.sha256(db.read_bytes()).hexdigest()
    checks = 0

    def gate(condition, label):
        global checks
        assert condition, label
        checks += 1

    hits = ux.execute(db, "search", query="needle")["data"]
    gate(hits["count"] == 3, "FTS5 per-message results")
    gate({h["message"]["id"] for h in hits["hits"]} == {"m1","m2","m4"}, "stable IDs")
    gate(hits["engine"] == "ricoeur.retrieval/FTS5", "uses peer core")
    gate(ux.execute(db,"search",query="needle",platform="chatgpt")["data"]["count"] == 2,
         "platform filter")
    gate(ux.execute(db,"search",query="needle OR unrelated",syntax="fts5")["data"]["count"] == 4,
         "FTS5 operator mode")
    gate(ux.execute(db,"conversations",query="needle")["data"][0]["first_match_id"] in {"m1","m2","m4"},
         "conversation preview has matched message")
    t=ux.execute(db,"transcript",id="c1")["data"]
    gate([m["id"] for m in t["messages"]] == ["m1","m2","m3"], "order and transcript")
    gate(t["messages"][1]["previous_id"]=="m1" and t["messages"][1]["next_id"]=="m3",
         "bidirectional navigation")
    gate(t["conversation"]["source_path"]=="chatgpt-export.json", "source provenance")
    gate(ux.execute(db,"message",id="m2")["data"]["before"][0]["id"]=="m1", "context")
    graph=ux.execute(db,"graph",query="needle")["data"]
    gate(len(graph["edges"])==2 and len(graph["nodes"])==3, "query-to-conversation star")
    gate({m for e in graph["edges"] for m in e["evidence_message_ids"]}=={"m1","m2","m4"},
         "all graph edges have message proof")
    gate(all(e["semantic_claim"] is False for e in graph["edges"]), "no invented correlation")
    gate(not ux.execute(db,"graph")["data"]["edges"], "no fabricated query-less edges")
    for bad in ("", " "):
        try:ux.execute(db,"search",query=bad)
        except ValueError:pass
        else:raise AssertionError("empty query accepted")
    gate(True, "empty query rejected")
    gate(hashlib.sha256(db.read_bytes()).hexdigest()==baseline, "DB unchanged after CLI")

    server=ThreadingHTTPServer(("127.0.0.1",0),ux.handler_factory(db))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        origin=f"http://127.0.0.1:{server.server_port}"
        with urllib.request.urlopen(origin+"/",timeout=5) as response:
            html=response.read().decode("utf-8")
        gate("vis-network@9.1.9" in html and "loadSearch" in html, "GUI + optional graph lib")
        gate("api('search'" in html and "api('transcript'" in html, "GUI via HTTP ports")
        qs=urllib.parse.urlencode({"action":"search","query":"needle","platform":"chatgpt"})
        with urllib.request.urlopen(origin+"/api?"+qs,timeout=5) as response:
            http=json.loads(response.read().decode("utf-8"))
        gate(http["data"]["count"]==2 and http["schema_version"]==ux.VERSION, "HTTP=CLI contract")
        with urllib.request.urlopen(origin+"/api?"+urllib.parse.urlencode({"action":"graph","query":"needle"}),timeout=5) as response:
            hg=json.loads(response.read())
        gate(hg["data"]==graph, "graph HTTP=CLI")
        try:
            urllib.request.urlopen(origin+"/api?action=search",timeout=5)
        except urllib.error.HTTPError as exc:
            gate(exc.code==400 and json.loads(exc.read())["status"]=="error", "structured API errors")
        else:raise AssertionError("missing query returned success")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    gate(hashlib.sha256(db.read_bytes()).hexdigest()==baseline, "HTTP DB remains read-only")
    print(f"PASS UX-011: {checks} autonomous integration gates; CLI/HTTP/GUI, Ricoeur FTS5, evidence, no writes")
