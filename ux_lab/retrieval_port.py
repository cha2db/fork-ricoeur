"""Read-only UX adapter: reuse the existing Ricoeur message retrieval core."""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ricoeur.retrieval import get_message_context, search_messages

def dispatch(db, operation, *, query="", message_id="", platform=None, limit=20, context=1):
    uri = Path(db).resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        if operation == "search":
            data = search_messages(conn, query, limit=limit, context=context, platform=platform)
        elif operation == "context":
            data = get_message_context(conn, message_id, context=context)
            if data is None:
                raise ValueError("message_not_found")
        else:
            raise ValueError("unsupported_operation")
        return {"schema_version":"ux.retrieval.v1","status":"ok","data":data,"errors":[]}
    finally:
        conn.close()

def main():
    p=argparse.ArgumentParser(description="Existing Ricoeur retrieval through read-only UX JSON port")
    p.add_argument("--db",required=True)
    sub=p.add_subparsers(dest="operation",required=True)
    s=sub.add_parser("search");s.add_argument("query");s.add_argument("--platform");s.add_argument("--limit",type=int,default=20);s.add_argument("--context",type=int,default=1)
    c=sub.add_parser("context");c.add_argument("message_id");c.add_argument("--context",type=int,default=2)
    args=vars(p.parse_args());db=args.pop("db");op=args.pop("operation")
    try:
        out=dispatch(db,op,**args)
    except (ValueError,sqlite3.Error) as exc:
        out={"schema_version":"ux.retrieval.v1","status":"error","data":None,"errors":[str(exc)]}
        print(json.dumps(out,ensure_ascii=False))
        raise SystemExit(1)
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
