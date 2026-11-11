"""PRODUCT-017: native SQLite integrity doctor on synthetic healthy and broken copies."""
import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"product_lab"))
from doctor import diagnose

def create(path, *, missing_fts=False, orphan=False):
    c=sqlite3.connect(path)
    c.executescript("""CREATE TABLE conversations (
      id TEXT PRIMARY KEY,title TEXT,platform TEXT,created_at TEXT);
    CREATE TABLE messages (id TEXT PRIMARY KEY,conv_id TEXT REFERENCES conversations(id),
      role TEXT,content TEXT,timestamp TEXT);
    CREATE TABLE attachments (id INTEGER PRIMARY KEY,conv_id TEXT REFERENCES conversations(id),
      msg_id TEXT REFERENCES messages(id),filename TEXT);""")
    if not missing_fts:
        c.executescript("""CREATE VIRTUAL TABLE messages_fts USING fts5(
         content,conv_id UNINDEXED,id UNINDEXED,role UNINDEXED,
         content='messages',content_rowid='rowid');
        CREATE TRIGGER messages_ai AFTER INSERT ON messages BEGIN
         INSERT INTO messages_fts(rowid,content,conv_id,id,role)
         VALUES(new.rowid,new.content,new.conv_id,new.id,new.role);END;
        CREATE TRIGGER messages_ad AFTER DELETE ON messages BEGIN
         INSERT INTO messages_fts(messages_fts,rowid,content,conv_id,id,role)
         VALUES('delete',old.rowid,old.content,old.conv_id,old.id,old.role);END;
        CREATE TRIGGER messages_au AFTER UPDATE ON messages BEGIN
         INSERT INTO messages_fts(messages_fts,rowid,content,conv_id,id,role)
         VALUES('delete',old.rowid,old.content,old.conv_id,old.id,old.role);
         INSERT INTO messages_fts(rowid,content,conv_id,id,role)
         VALUES(new.rowid,new.content,new.conv_id,new.id,new.role);END;""")
    c.execute("INSERT INTO conversations VALUES('c1','SENSITIVE_TITLE','chatgpt','2026-01-01')")
    c.execute("INSERT INTO messages VALUES('m1','c1','user','SECRET_CONTENT','2026-01-01')")
    c.execute("INSERT INTO attachments(conv_id,msg_id,filename) VALUES('c1','m1','SECRET_FILE')")
    if orphan:
        c.execute("INSERT INTO messages VALUES('m2','MISSING','user','bad','2026-01-02')")
    c.commit();c.close()

gates=0
def gate(cond,label):
    global gates
    assert cond,label
    gates+=1

with tempfile.TemporaryDirectory() as temp:
    p=Path(temp)/"healthy.db";create(p)
    fingerprint=hashlib.sha256(p.read_bytes()).hexdigest()
    result=diagnose(p)
    gate(result["status"]=="PASS","healthy status")
    gate(result["counts"]["messages"]==1,"count only")
    gate(result["counts"]["attachments"]==1,"attachment count")
    gate(all(ch["status"]=="PASS" for ch in result["checks"]),"healthy gates")
    gate(result["mode"]=="read_only","read-only contract")
    gate("SECRET_CONTENT" not in json.dumps(result) and "SENSITIVE_TITLE" not in json.dumps(result)
         and "SECRET_FILE" not in json.dumps(result),"no private content in JSON")
    gate(hashlib.sha256(p.read_bytes()).hexdigest()==fingerprint,"database unchanged")
    deep=diagnose(p,thorough=True)
    gate(deep["status"]=="PASS" and
         any(ch["code"]=="native_sqlite_integrity_check" for ch in deep["checks"]),
         "full SQLite integrity")
    cp=subprocess.run([sys.executable,str(ROOT/"product_lab/doctor.py"),"--db",str(p)],
                      capture_output=True,text=True)
    gate(cp.returncode==0 and json.loads(cp.stdout)["status"]=="PASS","CLI JSON parity")
    gate(hashlib.sha256(p.read_bytes()).hexdigest()==fingerprint,"CLI no mutation")
    bad=Path(temp)/"orphan.db";create(bad,orphan=True)
    bad_hash=hashlib.sha256(bad.read_bytes()).hexdigest()
    report=diagnose(bad)
    gate(report["status"]=="FAIL","orphan must fail")
    gate(any(ch["code"]=="message_conversation_orphans" and ch["observed"]==1
             for ch in report["checks"]),"precise orphan evidence")
    gate(any(ch["code"]=="sqlite_foreign_key_check" and ch["status"]=="FAIL"
             for ch in report["checks"]),"foreign key check")
    gate(len(report["suggestions"])==3,"repair only via safe copy")
    gate(hashlib.sha256(bad.read_bytes()).hexdigest()==bad_hash,"failed DB not modified")
    nofts=Path(temp)/"nofts.db";create(nofts,missing_fts=True)
    report=diagnose(nofts)
    gate(report["status"]=="FAIL","missing search index detected")
    gate(any(ch["code"]=="table_messages_fts" and ch["status"]=="FAIL"
             for ch in report["checks"]),"missing FTS evidence")
    missing=Path(temp)/"doesnotexist.db"
    report=diagnose(missing)
    gate(report["status"]=="FAIL" and not missing.exists(),"missing input never created")
print(f"PASS PRODUCT-017: {gates} gates, SQLite native checks, no source contents leaked, no writes")
