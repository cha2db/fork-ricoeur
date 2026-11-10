"""Materialize the existing deterministic corpus once for every prior-art adapter.
Produces a real SQLite snapshot plus logical-data fingerprint (not private chats).
"""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
from ricoeur.db import init_db
from corpus import populate,PREFIX

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--conversations",type=int,default=1000)
    p.add_argument("--messages",type=int,default=40)
    p.add_argument("--output",default="_dev/results/prior-base.sqlite")
    args=p.parse_args()
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():
        p.error("refusing to overwrite existing snapshot")
    import tempfile
    with tempfile.TemporaryDirectory(prefix="cha2db-base-") as tmp:
        conn=init_db(Path(tmp))
        populate(conn,args.conversations,args.messages)
        digest=hashlib.sha256()
        for row in conn.execute("SELECT id,conv_id,role,content,timestamp FROM messages ORDER BY id"):
            for val in row:digest.update((str(val) if val is not None else "").encode("utf-8")+b"\0")
        counts={
          "conversations":conn.execute("SELECT count(*) FROM conversations WHERE id LIKE ?",(PREFIX+"c%",)).fetchone()[0],
          "messages":conn.execute("SELECT count(*) FROM messages WHERE id LIKE ?",(PREFIX+"m%",)).fetchone()[0]}
        backup=sqlite3.connect(str(out))
        try:conn.backup(backup)
        finally:backup.close();conn.close()
    assert counts=={"conversations":args.conversations,"messages":args.conversations*args.messages}
    verify=sqlite3.connect(str(out))
    assert verify.execute("SELECT count(*) FROM messages").fetchone()[0]==counts["messages"]
    verify.execute("INSERT INTO messages_fts(messages_fts) VALUES('integrity-check')")
    verify.close()
    manifest={"status":"PASS","source":"_dev/corpus.py existing deterministic corpus",
              "synthetic":True,"actual_sqlite_file":str(out),
              "bytes":out.stat().st_size,"logical_sha256":digest.hexdigest(),"counts":counts}
    path=out.with_suffix(".manifest.json")
    path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
