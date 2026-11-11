"""UX-015: fixed navigation + one catalog for all 46 candidates + footer credits.

Synthetic Ricoeur data only. No network, logos loaded only with explicit user opt-in.
"""
import hashlib
import json
import sqlite3
import sys
import tempfile
import threading
import urllib.parse
import urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"ux_lab"))
import ux
from dashboard_port import dashboard

def test():
    gates=0
    def gate(ok,why):
        nonlocal gates
        assert ok,why
        gates+=1

    data=dashboard()
    categories=data["categories"]; credits=data["credits"]
    gate(data["schema_version"]=="ux.dashboard.v1","stable schema")
    gate(data["navigation"]=="fixed","fixed navigation")
    gate(len(categories)==8,"8 GUI types")
    gate(data["candidate_count"]==46,"all 46 candidates")
    gate(len(credits)==46 and len({c["id"] for c in credits})==46,"one credit per candidate")
    gate(len({c["id"] for g in categories for c in g["candidates"]})==46,"no orphan or duplicate candidate")
    gate(all(g["state"] in ("implemented","partial","research") for g in categories),"category states")
    gate(all(c["status"] in ("adopted_core","implemented_subset",
                            "experimental_opt_in","researched_only")
             for g in categories for c in g["candidates"]),"no false adoption labels")
    adopted={c["id"] for g in categories for c in g["candidates"]
             if c["status"]=="adopted_core"}
    gate(adopted=={"ricoeur","textual"},"only existing core declared adopted")
    gate({c["id"] for g in categories for c in g["candidates"]
          if c["status"]=="experimental_opt_in"}==
         {"echarts","visnetwork","wordcloud2"},"experimentals not adopted")
    gate(next(g for g in categories if g["id"]=="research")["adopted"] is None,
         "do not invent implementation in research")
    gate({g["id"] for g in categories}==
         {"conversations","graph","timeline","tags","concepts","terminal","branches","research"},
         "category coverage")
    gate(sum(c["id"]=="echarts" and bool(c["logo"]) for c in credits)==1,
         "verified upstream logo source")
    gate(all(c["url"].startswith("https://") for c in credits),
         "all credit URLs are HTTPS")
    manifest=json.loads((ROOT/"ux_lab/candidates.json").read_text(encoding="utf-8"))
    gate({c["id"] for c in credits}=={c["id"] for c in manifest["candidates"]},
         "registry exactly matches credits")

    with tempfile.TemporaryDirectory() as td:
        db=Path(td)/"fixture.db"
        c=sqlite3.connect(db)
        c.executescript("""CREATE TABLE conversations (
            id TEXT PRIMARY KEY,title TEXT,platform TEXT,model TEXT,created_at TEXT,
            updated_at TEXT,language TEXT,topic_id INTEGER,message_count INTEGER,
            project TEXT,source_path TEXT);
        CREATE TABLE messages(id TEXT PRIMARY KEY,conv_id TEXT,role TEXT,content TEXT,timestamp TEXT,
            content_type TEXT,token_count INTEGER);
        CREATE VIRTUAL TABLE messages_fts USING fts5(content,conv_id UNINDEXED,id UNINDEXED,
            role UNINDEXED,content='messages',content_rowid='rowid');
        CREATE TRIGGER messages_ai AFTER INSERT ON messages BEGIN
        INSERT INTO messages_fts(rowid,content,conv_id,id,role)
        VALUES(new.rowid,new.content,new.conv_id,new.id,new.role); END;""")
        c.execute("INSERT INTO conversations(id,title,platform,created_at) VALUES('c1','Demo','chatgpt','2026-11-01')")
        c.execute("INSERT INTO messages(id,conv_id,role,content,timestamp) VALUES('m1','c1','user','docker','2026-11-01')")
        c.commit();c.close()
        hash_before=hashlib.sha256(db.read_bytes()).hexdigest()

        server=ThreadingHTTPServer(("127.0.0.1",0),ux.handler_factory(db))
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        host=f"http://127.0.0.1:{server.server_port}"
        try:
            def get(path):
                with urllib.request.urlopen(host+path,timeout=6) as resp:
                    return resp.status,resp.headers.get("Content-Type"),resp.read().decode("utf-8")
            code,mime,root=get("/")
            gate(code==200 and "text/html" in mime and "Catálogo por tipo" in root,"homepage dashboard")
            gate('src="/nav.js"' in root and 'id="credits-list"' in root,"footer and navigation enabled")
            gate('fetch(\'/api?action=dashboard\'' in root,"dashboard uses JSON port")
            gate("Carregar logos de fontes oficiais externas" in root,
                 "logo loader requires user confirmation")
            gate("createElement('img')" not in root and "img.src=safeUrl" in root,
                 "logo requests only in explicit callback")
            code,mime,nav=get("/nav.js")
            gate(code==200 and "javascript" in mime and "position:fixed" in nav,
                 "shared fixed navigation script")
            gate("Painel" in nav and "Créditos" in nav and '"/chats"' in nav,
                 "all primary nav destinations")
            code,mime,reader=get("/chats")
            gate("loadSearch" in reader and 'src="/nav.js"' in reader,
                 "chat reader preserved with navigation")
            code,mime,knowledge=get("/knowledge")
            gate("barChart" in knowledge and "/chats" in knowledge
                 and 'src="/nav.js"' in knowledge,"term dashboard provenance preserved")
            code,mime,body=get("/api?action=dashboard")
            result=json.loads(body)
            gate(result["status"]=="ok" and result["data"]==data,"HTTP catalog equals CLI")
            gate("dashboard" in ux.execute(db,"capabilities")["data"]["ports"],
                 "dashboard discovery in CLI")
            gate(ux.execute(db,"dashboard")["data"]==data,"CLI catalog equals API")
        finally:
            server.shutdown();server.server_close();thread.join(timeout=6)
        gate(hashlib.sha256(db.read_bytes()).hexdigest()==hash_before,
             "dashboard and reader never modify SQLite")
    print(f"PASS UX-015: {gates} gates, 46 credits, 8 GUI families, fixed navigation, optional logos, same read-only DB")

test()
