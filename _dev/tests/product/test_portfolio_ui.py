"""PRODUCT-016 HTTP contract: portfolio works without creating a database.

The new GUI is a read-only research view. Test only localhost and synthetic
state; no users, conversations or network requests to third parties.
"""
import json
from pathlib import Path
import sys
import tempfile
import threading
import urllib.request
from http.server import ThreadingHTTPServer

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"ux_lab"))
sys.path.insert(0,str(ROOT))
import ux
from product_lab.rank import generate

gates=0
def gate(ok,label):
    global gates
    assert ok,label
    gates+=1

portfolio=generate()
gate(len(portfolio["front_ranking"])==12,"12 product fronts")
gate(all(len(f["comparison_groups"])>=1 for f in portfolio["front_ranking"]),
     "candidates divided by technical contract")
gate(all(sum(g["candidate_count"] for g in f["comparison_groups"])==f["candidate_count"]
         for f in portfolio["front_ranking"]),"no grouping information loss")
gate(all(g["candidates"]==sorted(g["candidates"],
         key=lambda x:(-x["priority_preliminary"],x["id"]))
         for f in portfolio["front_ranking"] for g in f["comparison_groups"]),
     "per-contract rank ordering")

with tempfile.TemporaryDirectory() as temp:
    missing_db=Path(temp)/"no-data-should-be-created.sqlite3"
    server=ThreadingHTTPServer(("127.0.0.1",0),ux.handler_factory(missing_db))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    host=f"http://127.0.0.1:{server.server_port}"
    try:
        def get(path):
            with urllib.request.urlopen(host+path,timeout=8) as response:
                return response.status,response.headers.get("Content-Type"),response.read().decode("utf-8")
        status,mime,html=get("/product")
        gate(status==200 and "text/html" in mime,"product dashboard path")
        gate("12" not in html or "front_ranking" in html,"dynamic data, not hard-coded benchmark")
        gate("fetch(\"/api?action=product\"" in html,"GUI consumes JSON ranking")
        gate("comparison_groups" in html,"GUI renders comparably-scoped rankings")
        gate("Fase 2" in html and "UX" in html,"prior study citations")
        gate('src="/nav.js"' in html,"fixed navigation shared")
        _,_,home=get("/")
        gate('href="/product"' in home,"central dashboard links product map")
        _,_,nav=get("/nav.js")
        gate('"/product"' in nav and "position:fixed" in nav,"global navigation includes map")
        status,mime,body=get("/api?action=product")
        decoded=json.loads(body)
        gate(status==200 and "application/json" in mime,"HTTP JSON contract")
        gate(decoded["schema_version"]==ux.VERSION and decoded["status"]=="ok",
             "same UX envelope")
        gate(decoded["data"]==portfolio,"HTTP and CLI same portfolio")
        gate(decoded["data"]["new_to_existing_inventories"]+
             decoded["data"]["overlapping_existing_inventories"]==71,"full provenance")
        gate(not missing_db.exists(),"dashboard needs no DB or write")
    finally:
        server.shutdown();server.server_close();thread.join(timeout=8)
gate(not missing_db.exists(),"no implicit init or migration")
print(f"PASS PRODUCT-016-UI: {gates} gates; shared HTTP/CLI ranking and fixed dashboard, no SQLite file created")
