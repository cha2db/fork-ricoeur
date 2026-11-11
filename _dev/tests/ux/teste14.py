"""UX-014: month histogram, clicked period, tag frequency and curated SKOS relation.
All checks use a synthetic local Ricoeur schema; no third-party network or real data.
"""
import hashlib
import json
import sqlite3
import sys
import tempfile
import threading
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path
from http.server import ThreadingHTTPServer

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"ux_lab"))
import ux

def fixture(db):
    c=sqlite3.connect(db)
    c.executescript("""CREATE TABLE conversations(
     id TEXT PRIMARY KEY,title TEXT,platform TEXT,model TEXT,created_at TEXT,
     updated_at TEXT,language TEXT,topic_id INTEGER,message_count INTEGER,project TEXT,source_path TEXT);
    CREATE TABLE messages (
     id TEXT PRIMARY KEY,conv_id TEXT,role TEXT,content TEXT,timestamp TEXT,
     content_type TEXT,token_count INTEGER);
    CREATE VIRTUAL TABLE messages_fts USING fts5(content,conv_id UNINDEXED,id UNINDEXED,role UNINDEXED,content='messages',content_rowid='rowid');
    CREATE TRIGGER messages_ai AFTER INSERT ON messages BEGIN
     INSERT INTO messages_fts(rowid,content,conv_id,id,role)
     VALUES(new.rowid,new.content,new.conv_id,new.id,new.role);
    END;""")
    c.executemany("INSERT INTO conversations(id,title,platform,created_at,message_count) VALUES(?,?,?,?,?)",[
        ("c1","Project CI","chatgpt","2026-01-03",3),
        ("c2","Claude CI","claude","2026-02-01",1),
        ("c3","History","chatgpt","2026-03-01",2)])
    c.executemany("INSERT INTO messages(id,conv_id,role,content,timestamp) VALUES(?,?,?,?,?)",[
        ("m1","c1","user","integração contínua integração contínua git testes","2026-01-03T10:00:00"),
        ("m2","c1","assistant","continuous integration git automation","2026-01-04T11:00:00"),
        ("m3","c1","user","CI pipeline release git","2026-02-07T11:00:00"),
        ("m4","c2","assistant","integração contínua testes git","2026-02-01T10:00:00"),
        ("m5","c3","user","unrelated topic words","2026-03-01T10:00:00"),
        ("m6","c3","assistant","integração contínua git fallback date",None)])
    c.commit();c.close()

def gates():
    count=0
    def check(condition,label):
        nonlocal count
        assert condition,label
        count+=1
    with tempfile.TemporaryDirectory() as tmp:
        db=Path(tmp)/"base.sqlite3"
        fixture(db); sha=hashlib.sha256(db.read_bytes()).hexdigest()
        lex=ROOT/"ux_lab/lexicon.example.json"
        base={"query":"integração contínua"}
        t=ux.execute(db,"timeline",**base)["data"]
        check(t["total_messages"]==3,"literal includes fallback timestamp")
        check([(p["period"],p["matching_messages"]) for p in t["points"]]==
              [("2026-01",1),("2026-02",1),("2026-03",1)],"timeline monthly")
        check(t["unit"]=="messages_containing_query","count distinct messages")
        check(t["date_policy"]=="message_timestamp_else_conversation_created_at","date fallback disclosed")
        expanded=ux.execute(db,"timeline",lexicon=str(lex),expand=True,**base)["data"]
        check(expanded["total_messages"]==5,"expansion includes 3 approved labels")
        check(expanded["concept_id"]=="demo:continuous-integration","concept id stable")
        check(len(expanded["terms"])==3,"compound phrase variants")
        check([(r["period"],r["matching_messages"]) for r in expanded["points"]]==
              [("2026-01",2),("2026-02",2),("2026-03",1)],"expanded trend")
        filtered=ux.execute(db,"timeline",lexicon=str(lex),expand=True,platform="chatgpt",**base)["data"]
        check(filtered["total_messages"]==4,"platform filter")
        yearly=ux.execute(db,"timeline",grain="year",**base)["data"]
        check(yearly["points"][0]["period"]=="2026","year grouping")
        daily=ux.execute(db,"timeline",grain="day",**base)["data"]
        check(len(daily["points"])==3,"day grouping")
        jan=ux.execute(db,"period",lexicon=str(lex),expand=True,period="2026-01",**base)["data"]
        check(jan["total_messages"]==2 and len(jan["messages"])==2,"period click")
        check({r["message_id"] for r in jan["messages"]}=={"m1","m2"},"message id provenance")
        check({r["conv_id"] for r in jan["messages"]}=={"c1"},"conversation origin")
        page=ux.execute(db,"period",lexicon=str(lex),expand=True,period="2026-01",limit=1,offset=1,**base)["data"]
        check(len(page["messages"])==1 and page["total_messages"]==2,"pagination")
        tags=ux.execute(db,"tagcloud",lexicon=str(lex),expand=True,period="2026-01",**base)["data"]
        frequency={row["term"]:row["message_count"] for row in tags["terms_frequency"]}
        check(frequency["git"]==2,"cloud message document frequency")
        check(frequency["integração"]==1,"no inflation for repeated words")
        check(not tags["is_truncated"],"exact sample")
        small=ux.execute(db,"tagcloud",max_messages=1,**base)["data"]
        check(small["is_truncated"] and small["sampled_messages"]==1,"sample transparency")
        concept=ux.execute(db,"concept",lexicon=str(lex),term="CI pipeline")["data"]
        check(concept["preferred"]=="integração contínua","altLabel identifies sense")
        check(concept["relations"][0]["type"]=="skos:related","typed edge")
        check(concept["relations"][0]["source"]=="human_curated_synthetic_demo","source provenance")
        check(concept["relations"][0]["verified_in_chat"] is False,"not invented chat relation")
        try:ux.execute(db,"concept",term="CI pipeline")
        except ValueError:pass
        else:raise AssertionError("sidecar was incorrectly loaded implicitly")
        check(True,"lexicon explicit-only")
        for grain, period in [("week","2026-01"),("month","bad")]:
            try:
                ux.execute(db,"period",query="integração contínua",grain=grain,period=period)
            except ValueError:
                pass
            else:
                raise AssertionError("invalid grain or period accepted")
        check(True,"invalid periods are rejected")
        check(hashlib.sha256(db.read_bytes()).hexdigest()==sha,"read-only core")
        server=ThreadingHTTPServer(("127.0.0.1",0),ux.handler_factory(db,str(lex)))
        th=threading.Thread(target=server.serve_forever,daemon=True);th.start()
        try:
            host=f"http://127.0.0.1:{server.server_port}"
            with urllib.request.urlopen(host+"/knowledge",timeout=8) as r:html=r.read().decode()
            check("barChart" in html and "loadEcharts" in html,"dashboard delivered")
            check("wordcloudCanvas" in html and "loadWordcloud" in html,"cloud delivered")
            query=urllib.parse.urlencode({"action":"timeline","query":"integração contínua","expand":"true"})
            with urllib.request.urlopen(host+"/api?"+query,timeout=8) as r:
                response=json.loads(r.read())
            check(response["data"]["total_messages"]==5,"HTTP and CLI same timeline")
            query=urllib.parse.urlencode({"action":"period","query":"integração contínua",
                                         "period":"2026-01","expand":"true"})
            with urllib.request.urlopen(host+"/api?"+query,timeout=8) as r:
                resp=json.loads(r.read())
            check(resp["data"]["total_messages"]==2,"HTTP click period")
        finally:
            server.shutdown();server.server_close();th.join(timeout=8)
        check(hashlib.sha256(db.read_bytes()).hexdigest()==sha,"HTTP no DB mutations")
    return count
print("PASS UX-014: %s gates, 3 conversations/6 messages; monthly drilldown, tags, curated lexicon, HTTP and read-only"%gates())
