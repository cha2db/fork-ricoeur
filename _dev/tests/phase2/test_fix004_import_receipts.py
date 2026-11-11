"""Phase2 import receipts and partial-resume test, synthetic source only."""
import hashlib
import json
from pathlib import Path
import tempfile

from ricoeur.db import init_db
from ricoeur.importers.chatgpt import import_chatgpt

checks=0
def gate(ok,name):
    global checks
    assert ok,name
    checks+=1

def conversation(index, malformed=False):
    msg={"id":f"m-{index}","author":{"role":"user"},
         "content":42 if malformed else {"content_type":"text","parts":[f"entry {index}"]},
         "create_time":1700000000}
    return {"id":f"c-{index}","title":"SYNTHETIC","create_time":1700000000,
        "current_node":"leaf",
        "mapping":{"root":{"parent":None,"children":["leaf"],"message":None},
                   "leaf":{"parent":"root","children":[],"message":msg}}}

with tempfile.TemporaryDirectory() as temp:
    root=Path(temp)
    home=root/"db";home.mkdir()
    conn=init_db(home)
    src=root/"source.json"
    items=[conversation(i) for i in range(25)]+[conversation(25,malformed=True)]
    src.write_text(json.dumps(items))
    first_sha=hashlib.sha256(src.read_bytes()).hexdigest()
    try:
        try:
            import_chatgpt(conn,src)
        except ValueError:
            gate(True,"malformed item rejected")
        else:
            raise AssertionError("malformed item accepted")
        receipt=conn.execute(
            "SELECT * FROM import_jobs ORDER BY id DESC LIMIT 1").fetchone()
        gate(receipt["source_sha256"]==first_sha,"source sha256 of raw input")
        gate(receipt["status"]=="PARTIAL","partial state persisted")
        gate(receipt["parsed"]==26 and receipt["imported"]==25,
             "attempted count plus successful count")
        gate(receipt["error_class"]=="ValueError","failure reason class")
        gate(receipt["source_bytes"]==src.stat().st_size,"source byte count")
        gate(conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]==25,
             "25 prior batches committed")
        gate(conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]==25,
             "failed 26th conversation atomic, no half-message")
        gate(conn.execute("SELECT COUNT(*) FROM chatgpt_nodes").fetchone()[0]==50,
             "failed 26th raw tree rolled back")

        items[-1]=conversation(25)
        src.write_text(json.dumps(items))
        sha2=hashlib.sha256(src.read_bytes()).hexdigest()
        gate(sha2!=first_sha,"changed source has distinct cryptographic identity")
        result=import_chatgpt(conn,src)
        gate(result.new==1 and result.skipped==25,"reimport resumes idempotently")
        last=conn.execute(
            "SELECT * FROM import_jobs ORDER BY id DESC LIMIT 1").fetchone()
        gate(last["status"]=="COMPLETE" and last["source_sha256"]==sha2,
             "complete recovery status persisted")
        gate(last["imported"]==1 and last["skipped"]==25,
             "receipt reflects deduplication")
        gate(conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]==26,
             "all conversations restored")
        gate(conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]==26,
             "no duplicated messages")

        before=conn.execute("SELECT COUNT(*) FROM import_jobs").fetchone()[0]
        dry=import_chatgpt(conn,src,dry_run=True)
        after=conn.execute("SELECT COUNT(*) FROM import_jobs").fetchone()[0]
        gate(after==before,"dry-run never creates receipt or writes")
        gate(dry.skipped==26 and dry.new==0,"dry-run reports already imported conversations")
    finally:
        conn.close()
print(f"PASS PHASE2 FIX-004: {checks} gates; SHA receipts, partial resume, atomic chat, dryrun")
