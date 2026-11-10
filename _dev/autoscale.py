"""Incremental headless SQLite/FTS5 scale gates, independent of UI/MCP.

Synthetic data only; reproducible stages and machine-readable evidence. Tests
both lexical recall parity on controlled whole-word terms and FTS index sync.
"""
from __future__ import annotations
import argparse
import json
import os
import sqlite3
import statistics
import tempfile
import time
from pathlib import Path
from ricoeur.db import init_db

TOPICS = (
    ("SSH", "SSH secure shell server connection"),
    ("PostgreSQL", "PostgreSQL relational database transaction"),
    ("Jenkins", "Jenkins CI CD pipeline automation"),
    ("AUoK", "AUoK atomic learning regression guided"),
    ("MCP", "MCP tool protocol adapter contract"),
    ("Android", "Android native mobile application testing"),
    ("seguranca", "seguranca security permission audit"),
    ("REST", "REST API JSON HTTP endpoint"),
)
QUERIES = ("SSH", "PostgreSQL", "Jenkins", "AUoK", "MCP", "Android", "seguranca", "REST", "marcadorunico2026", "termoausente999")
FTS_SQL = """SELECT m.id FROM messages_fts JOIN messages m ON m.rowid=messages_fts.rowid
              WHERE messages_fts MATCH ? ORDER BY messages_fts.rowid LIMIT 100"""
LIKE_SQL = "SELECT id FROM messages WHERE content LIKE ? ORDER BY rowid LIMIT 100"

def measure(conn, sql, arg, repeats):
    values=[]; found=[]
    for _ in range(repeats):
        start=time.perf_counter_ns()
        found=[r[0] for r in conn.execute(sql,(arg,)).fetchall()]
        values.append((time.perf_counter_ns()-start)/1000000)
    return found, {"median_ms":round(statistics.median(values),3),
                   "min_ms":round(min(values),3),"max_ms":round(max(values),3)}

def grow(conn, start, stop, per):
    rows=[]
    for i in range(start//per,stop//per):
        topic, desc=TOPICS[i%len(TOPICS)]
        cid=f"scale-c{i:08d}"
        conn.execute("INSERT INTO conversations(id,title,platform) VALUES(?,?,?)",
                     (cid,"Scale "+topic,("chatgpt","claude","gemini","copilot")[i%4]))
        for j in range(per):
            content=f"Session {i} message {j}. {desc}. " + ("marcadorunico2026" if i==0 and j==0 else "")
            rows.append((f"scale-m{i:08d}-{j:04d}",cid,"user" if j%2==0 else "assistant",content,
                         f"2026-01-01T00:{(j//60)%60:02d}:{j%60:02d}"))
            if len(rows)>=1000:
                conn.executemany("INSERT INTO messages(id,conv_id,role,content,timestamp) VALUES(?,?,?,?,?)",rows)
                rows.clear()
    if rows:conn.executemany("INSERT INTO messages(id,conv_id,role,content,timestamp) VALUES(?,?,?,?,?)",rows)
    conn.commit()

def check(conn, total, repeats):
    checked={}
    actual=conn.execute("SELECT count(*) FROM messages").fetchone()[0]
    checked["count"]=actual==total
    plan=[row[3] for row in conn.execute("EXPLAIN QUERY PLAN "+FTS_SQL,("SSH",))]
    checked["fts_no_temp_sort"]=not any("TEMP B-TREE" in detail for detail in plan)
    conn.execute("INSERT INTO messages_fts(messages_fts) VALUES('integrity-check')")
    results=[]
    for query in QUERIES:
        ids_fts, latency_fts=measure(conn,FTS_SQL,query,repeats)
        ids_like, latency_like=measure(conn,LIKE_SQL,"%"+query+"%",repeats)
        nfts=conn.execute("SELECT count(*) FROM messages_fts WHERE messages_fts MATCH ?",(query,)).fetchone()[0]
        nlike=conn.execute("SELECT count(*) FROM messages WHERE content LIKE ?",("%"+query+"%",)).fetchone()[0]
        same=nfts==nlike and ids_fts==ids_like
        checked["parity_"+query]=same
        results.append({"query":query,"fts_matches":nfts,"literal_matches":nlike,
                        "same_first_100":ids_fts==ids_like,"fts":latency_fts,"literal":latency_like})
    checked["rare_term_once"]=results[8]["fts_matches"]==1
    checked["missing_term_zero"]=results[9]["fts_matches"]==0
    checked["search_escape"]=conn.execute("SELECT count(*) FROM messages WHERE content LIKE ?",("%' OR 1=1 --%",)).fetchone()[0]==0
    marker_id="scale-m00000000-0000"
    conn.execute("SAVEPOINT mutation_test")
    try:
        conn.execute("UPDATE messages SET content='substituicaounica987' WHERE id=?",(marker_id,))
        checked["update_index"]=conn.execute("SELECT count(*) FROM messages_fts WHERE messages_fts MATCH 'substituicaounica987'").fetchone()[0]==1
        checked["old_term_removed"]=conn.execute("SELECT count(*) FROM messages_fts WHERE messages_fts MATCH 'marcadorunico2026'").fetchone()[0]==0
        conn.execute("DELETE FROM messages WHERE id=?",(marker_id,))
        checked["delete_index"]=conn.execute("SELECT count(*) FROM messages_fts WHERE messages_fts MATCH 'substituicaounica987'").fetchone()[0]==0
    finally:
        conn.execute("ROLLBACK TO mutation_test")
        conn.execute("RELEASE mutation_test")
    return checked,results

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stages",default="40000,100000,400000,1000000,2000000")
    ap.add_argument("--per-conversation",type=int,default=40)
    ap.add_argument("--repeats",type=int,default=3)
    ap.add_argument("--budget-seconds",type=float,default=540)
    ap.add_argument("--disk-limit-mb",type=int,default=1400)
    ap.add_argument("--output",default="_dev/results/autoscale.json")
    a=ap.parse_args()
    stages=[int(v.strip()) for v in a.stages.split(",")]
    if not stages or stages!=sorted(set(stages)) or any(x<=0 or x%a.per_conversation for x in stages) or not 1<=a.repeats<=20 or not 1<=a.per_conversation<=100:
        ap.error("stages must be strictly increasing positive multiples of per-conversation")
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    report={"status":"RUNNING","environment":{"sqlite":sqlite3.sqlite_version,
            "python":os.sys.version.split()[0]},"stages":[],"verdict":None}
    start=time.monotonic(); prior=0
    with tempfile.TemporaryDirectory(prefix="cha2db-autoscale-") as folder:
        conn=init_db(Path(folder));db=Path(folder)/"ricoeur.db"
        try:
            for target in stages:
                if time.monotonic()-start >= a.budget_seconds:
                    report["status"]="LIMIT";report["verdict"]="time_budget_reached";break
                try:
                    began=time.monotonic()
                    grow(conn,prior,target,a.per_conversation)
                    import_seconds=round(time.monotonic()-began,3)
                    checks,queries=check(conn,target,a.repeats)
                    elapsed=round(time.monotonic()-began,3)
                    db_bytes=db.stat().st_size
                    item={"messages":target,"conversations":target//a.per_conversation,
                          "import_seconds":import_seconds,"stage_seconds":elapsed,
                          "db_bytes":db_bytes,"checks":checks,"queries":queries}
                    report["stages"].append(item);prior=target
                    report["status"]="PASS" if all(checks.values()) else "FAIL"
                    report["verdict"]="all_checks_passed" if report["status"]=="PASS" else "correctness_failure"
                    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
                    print("GATE",target,report["status"],"db_mb",round(db_bytes/1048576,1),"seconds",elapsed,flush=True)
                    if report["status"]!="PASS":break
                    if db_bytes>a.disk_limit_mb*1048576:
                        report["status"]="LIMIT";report["verdict"]="disk_budget_reached";break
                except (sqlite3.Error,MemoryError,OSError) as error:
                    report["status"]="FAIL";report["verdict"]="runtime_failure"
                    report["error"]={"stage_messages":target,"type":type(error).__name__,"message":str(error)}
                    break
            else:
                report["status"]="PASS";report["verdict"]="max_planned_volume_passed_not_physical_limit"
        finally:conn.close()
    report["duration_seconds"]=round(time.monotonic()-start,3)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("VERDICT",report["status"],report["verdict"],"max_messages",prior,flush=True)
    if report["status"]=="FAIL":raise SystemExit(1)
if __name__=="__main__":main()
