"""Independent read-only UX CLI/HTTP port over an existing Ricoeur SQLite DB."""
import argparse
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

VERSION = "ux.v1"

def connect(path):
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn

def payload(data):
    return {"schema_version": VERSION, "status": "ok", "data": data, "errors": []}

def conversations(conn, query="", platform="", limit=30):
    limit = max(1, min(int(limit), 100))
    if query:
        # Plain literal matching is safe, predictable and works without an FTS migration.
        sql = """SELECT DISTINCT c.id,c.title,c.platform,c.created_at,c.message_count
                 FROM conversations c JOIN messages m ON m.conv_id=c.id
                 WHERE (LOWER(COALESCE(m.content,'')) LIKE ? ESCAPE '\\'
                    OR LOWER(COALESCE(c.title,'')) LIKE ? ESCAPE '\\')
                   AND (?='' OR c.platform=?) ORDER BY c.created_at DESC,c.id LIMIT ?"""
        term = "%" + query.lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        rows = conn.execute(sql, (term, term, platform, platform, limit)).fetchall()
    else:
        rows = conn.execute("""SELECT id,title,platform,created_at,message_count
                 FROM conversations WHERE (?='' OR platform=?)
                 ORDER BY created_at DESC,id LIMIT ?""", (platform, platform, limit)).fetchall()
    return [dict(r) for r in rows]

def transcript(conn, cid):
    conv = conn.execute("SELECT id,title,platform,created_at FROM conversations WHERE id=?", (cid,)).fetchone()
    if conv is None:
        raise ValueError("conversation_not_found")
    msgs = conn.execute("""SELECT id,role,content,timestamp FROM messages WHERE conv_id=?
                          ORDER BY timestamp,id""", (cid,)).fetchall()
    messages = [dict(r) for r in msgs]
    for i, m in enumerate(messages):
        m["previous_id"] = messages[i-1]["id"] if i else None
        m["next_id"] = messages[i+1]["id"] if i+1 < len(messages) else None
    return {"conversation":dict(conv),"messages":messages}

def graph(conn, query="", limit=30):
    # Evidence-only co-occurrence: two conversations match the *same user query*.
    # No edge implies semantic or causal relation.
    nodes = conversations(conn, query, limit=limit)
    edges = []
    if query:
        for i in range(len(nodes)-1):
            edges.append({"source":nodes[i]["id"],"target":nodes[i+1]["id"],
                          "type":"shared_query_result","query":query,
                          "evidence":"both conversations matched literal query",
                          "semantic_claim":False})
    return {"nodes":nodes,"edges":edges,"relation_status":"query_cooccurrence_only"}

def execute(db, action, **kw):
    with connect(db) as conn:
        if action=="capabilities":
            return payload({"ports":["capabilities","conversations","transcript","graph","serve"],
                            "graph":"query_cooccurrence_only","storage":"read_only_ricoeur_sqlite"})
        if action=="conversations":
            return payload(conversations(conn,kw.get("query",""),kw.get("platform",""),kw.get("limit",30)))
        if action=="transcript":
            return payload(transcript(conn,kw["id"]))
        if action=="graph":
            return payload(graph(conn,kw.get("query",""),kw.get("limit",30)))
        raise ValueError("unsupported_action")

def serve(db, port):
    page = Path(__file__).with_name("index.html").read_bytes()
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path=="/":
                self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8")
                self.end_headers(); self.wfile.write(page); return
            if parsed.path!="/api":
                self.send_error(404); return
            args = {k:v[0] for k,v in parse_qs(parsed.query).items()}
            action=args.pop("action","capabilities")
            if "id" not in args and action=="transcript":
                self.send_error(400,"missing id"); return
            try:
                result=execute(db,action,**args)
                code=200
            except (ValueError,sqlite3.Error) as e:
                result={"schema_version":VERSION,"status":"error","data":None,"errors":[str(e)]}
                code=400
            raw=json.dumps(result,ensure_ascii=False).encode()
            self.send_response(code);self.send_header("Content-Type","application/json; charset=utf-8")
            self.send_header("Cache-Control","no-store");self.send_header("Content-Length",str(len(raw)))
            self.end_headers();self.wfile.write(raw)
    httpd=ThreadingHTTPServer(("127.0.0.1",int(port)),Handler)
    print(f"UX lab: http://127.0.0.1:{httpd.server_port}",flush=True)
    httpd.serve_forever()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",required=True)
    sub=p.add_subparsers(dest="action",required=True)
    sub.add_parser("capabilities")
    for name in ("conversations","graph"):
        s=sub.add_parser(name);s.add_argument("--query",default="")
        s.add_argument("--limit",type=int,default=30)
        if name=="conversations":s.add_argument("--platform",default="")
    sub.add_parser("transcript").add_argument("id")
    sub.add_parser("serve").add_argument("--port",type=int,default=8765)
    a=vars(p.parse_args());db=a.pop("db");action=a.pop("action")
    if action=="serve":return serve(db,a["port"])
    if action=="transcript":a["id"]=a.pop("id")
    try:print(json.dumps(execute(db,action,**a),ensure_ascii=False,indent=2))
    except (ValueError,sqlite3.Error) as e:
        print(json.dumps({"schema_version":VERSION,"status":"error","data":None,"errors":[str(e)]}))
        raise SystemExit(1)
if __name__=="__main__":main()
