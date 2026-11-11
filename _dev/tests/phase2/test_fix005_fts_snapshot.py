"""FTS5 external-content consistency test on a disposable backup snapshot."""
import hashlib
from pathlib import Path
import tempfile
from ricoeur.db import init_db
from ricoeur.health import check_fts_snapshot

gates=0
def gate(ok,name):
    global gates
    assert ok,name
    gates+=1

with tempfile.TemporaryDirectory() as td:
    home=Path(td)
    conn=init_db(home)
    try:
        conn.execute("INSERT INTO conversations(id,title,platform) VALUES('c1','SYNTHETIC','chatgpt')")
        conn.execute("""INSERT INTO messages(id,conv_id,role,content)
                        VALUES('m1','c1','user','SENSITIVE_SYNTHETIC_MARKER')""")
        conn.commit()
        db=home/"ricoeur.db"
        good_hash=hashlib.sha256(db.read_bytes()).hexdigest()
        result=check_fts_snapshot(db)
        gate(result["status"]=="PASS","healthy FTS index")
        gate(result["source_modified"] is False,"snapshot only")
        gate("SENSITIVE_SYNTHETIC_MARKER" not in str(result),"no source content disclosed")
        gate(hashlib.sha256(db.read_bytes()).hexdigest()==good_hash,"source DB unchanged")

        # Native FTS5 delete-all deliberately corrupts the external-content
        # index *inside the synthetic fixture only*.
        conn.execute("INSERT INTO messages_fts(messages_fts) VALUES('delete-all')")
        conn.commit()
        corrupted_hash=hashlib.sha256(db.read_bytes()).hexdigest()
        result=check_fts_snapshot(db)
        gate(result["status"]=="FAIL","detect FTS vs messages mismatch")
        gate(result["source_modified"] is False,"no repair on actual source")
        gate(hashlib.sha256(db.read_bytes()).hexdigest()==corrupted_hash,
             "corrupt source preserved for recovery")
        gate(conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]==1,
             "source message never deleted")
    finally:
        conn.close()
    gate(check_fts_snapshot(home/"missing.db")["status"]=="FAIL",
         "missing file returns fail not create")
print(f"PASS PHASE2 FIX-005: {gates} gates; actual FTS5 integrity, only disposable snapshot touched")
