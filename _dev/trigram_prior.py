"""FTS5 trigram index adoption gate on the same shared 40k SQLite snapshot.
A dedicated index is compared with plain LIKE; not a replacement for BM25.
"""
import argparse
import json
import shutil
import sqlite3
import tempfile
import time
from pathlib import Path

QUERIES=["agulha-mcp-2026","orquidea-violeta-2026","atômica","gres","FTS5","contrato","rastreabilidade","SSH","Jenkins","zzyyxxnotfound"]
def timed(conn,sql,params):
    t=time.perf_counter_ns()
    data=[r[0] for r in conn.execute(sql,params).fetchall()]
    return data,round((time.perf_counter_ns()-t)/1e6,3)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db-path",required=True)
    p.add_argument("--output",default="_dev/results/trigram.json")
    a=p.parse_args()
    with tempfile.TemporaryDirectory(prefix="cha2db-trigram-") as d:
        clone=Path(d)/"ricoeur.db";shutil.copy2(a.db_path,clone)
        conn=sqlite3.connect(str(clone))
        original=clone.stat().st_size
        started=time.monotonic()
        conn.execute("""CREATE VIRTUAL TABLE tri_messages USING fts5(
            content,content='messages',content_rowid='rowid',tokenize='trigram')""")
        conn.execute("INSERT INTO tri_messages(tri_messages) VALUES('rebuild')")
        conn.commit()
        index_seconds=round(time.monotonic()-started,3)
        checks=[]
        for term in QUERIES:
            pattern="%"+term+"%"
            indexed,tidx=timed(conn,"SELECT rowid FROM tri_messages WHERE content LIKE ? ORDER BY rowid LIMIT 100",(pattern,))
            raw,traw=timed(conn,"SELECT rowid FROM messages WHERE content LIKE ? ORDER BY rowid LIMIT 100",(pattern,))
            a_count=conn.execute("SELECT count(*) FROM tri_messages WHERE content LIKE ?",(pattern,)).fetchone()[0]
            b_count=conn.execute("SELECT count(*) FROM messages WHERE content LIKE ?",(pattern,)).fetchone()[0]
            checks.append({"query":term,"equal_first100":indexed==raw,"count":a_count,
                           "equal_count":a_count==b_count,"trigram_ms":tidx,"like_ms":traw})
        integrity=True
        try:conn.execute("INSERT INTO tri_messages(tri_messages) VALUES('integrity-check')")
        except sqlite3.Error:integrity=False
        plan=[str(row) for row in conn.execute("EXPLAIN QUERY PLAN SELECT rowid FROM tri_messages WHERE content LIKE ?",("%atômica%",))]
        report={"status":"PASS" if integrity and all(x["equal_first100"] and x["equal_count"] for x in checks) else "FAIL",
                "candidate":"SQLite built-in FTS5 trigram","data_source":a.db_path,
                "index_seconds":index_seconds,
                "database_growth_bytes":clone.stat().st_size-original,
                "queries":checks,"integrity":integrity,"query_plan":plan,
                "verdict":"LITERAL_SUBSTRING_CANDIDATE_ONLY",
                "limits":["LIKE patterns need >=3 consecutive literal Unicode characters for index benefits.",
                          "ESCAPE clause can disable FTS5 trigram LIKE index optimization.",
                          "Extra index costs disk and maintenance; test write synchronization before adoption."]}
        conn.close()
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if report["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
