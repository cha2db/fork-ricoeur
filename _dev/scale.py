"""Comparable SQL-only FTS5 versus literal search at multiple dataset sizes.

The result shape, LIMIT, ordering and timing boundaries are the same for both.
This is a microbenchmark, not a relevance evaluation or semantic search.
"""
from __future__ import annotations
import argparse
import json
import sqlite3
import statistics
import tempfile
import time
from pathlib import Path
from ricoeur.db import init_db

TOPICS = (
    "SSH autenticação criptografia conexão remota",
    "PostgreSQL índice transação consulta relacional",
    "Jenkins pipeline DevOps integração contínua",
    "AUoK regressão guiada aprendizagem",
    "MCP ferramentas contrato adaptador",
    "Android aplicativo teste móvel",
    "segurança permissão auditoria acesso",
    "REST API endpoint JSON servidor",
)
QUERIES = ("SSH","PostgreSQL","Jenkins","AUoK","MCP","Android","segurança","REST","marcadorunico2026","termoausente999")
def populate(conn, n, per):
    batch=[]
    for i in range(n):
        cid=f"scale-c{i:07d}"
        conn.execute("INSERT INTO conversations(id,title,platform) VALUES(?,?,?)",
                     (cid,f"Scale {i}",("chatgpt","claude","gemini","copilot")[i%4]))
        for j in range(per):
            content=f"Conversa {i} mensagem {j}. {TOPICS[i%len(TOPICS)]}. "+("marcadorunico2026" if i==0 and j==0 else "")
            batch.append((f"scale-m{i:07d}-{j:04d}",cid,"user" if j%2==0 else "assistant",content,f"2026-01-01T00:{j//60:02d}:{j%60:02d}"))
            if len(batch)>=2000:
                conn.executemany("INSERT INTO messages(id,conv_id,role,content,timestamp) VALUES(?,?,?,?,?)",batch)
                batch.clear()
    if batch:conn.executemany("INSERT INTO messages(id,conv_id,role,content,timestamp) VALUES(?,?,?,?,?)",batch)
    conn.commit()

def measure(conn, sql, arg, repeats):
    times=[]
    for _ in range(repeats):
        start=time.perf_counter_ns()
        ids=[row[0] for row in conn.execute(sql,(arg,)).fetchall()]
        times.append((time.perf_counter_ns()-start)/1e6)
    return ids,{"median_ms":round(statistics.median(times),3),
                "min_ms":round(min(times),3),"max_ms":round(max(times),3)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--conversations",type=int,default=1000)
    p.add_argument("--messages",type=int,default=40)
    p.add_argument("--repeats",type=int,default=5)
    p.add_argument("--output",default="_dev/results/scale.json")
    a=p.parse_args()
    if not 1<=a.conversations<=20000 or not 1<=a.messages<=100 or not 1<=a.repeats<=50:
        p.error("out-of-range arguments")
    fts="""SELECT m.id FROM messages_fts f JOIN messages m ON m.rowid=f.rowid
           WHERE messages_fts MATCH ? ORDER BY messages_fts.rowid LIMIT 100"""
    # Use the virtual table's real name in the FROM clause for SQLite MATCH.
    fts=fts.replace("messages_fts f JOIN","messages_fts JOIN").replace("f.rowid","messages_fts.rowid")
    literal="""SELECT id FROM messages WHERE content LIKE ? ORDER BY rowid LIMIT 100"""
    with tempfile.TemporaryDirectory(prefix="cha2db-scale-") as tmp:
        conn=init_db(Path(tmp))
        start=time.perf_counter()
        populate(conn,a.conversations,a.messages)
        import_s=round(time.perf_counter()-start,3)
        rows=[]
        checks={}
        for term in QUERIES:
            fids,ft=measure(conn,fts,term,a.repeats)
            lids,lt=measure(conn,literal,"%"+term+"%",a.repeats)
            # Compare complete result sets, not only top 100, because the two
            # search methods can return distinct sets for partial tokens.
            fcount=conn.execute("SELECT count(*) FROM messages_fts WHERE messages_fts MATCH ?",(term,)).fetchone()[0]
            lcount=conn.execute("SELECT count(*) FROM messages WHERE content LIKE ?",("%"+term+"%",)).fetchone()[0]
            equal=fcount==lcount and set(fids)==set(lids)
            checks[term]=equal
            rows.append({"query":term,"fts_count":fcount,"literal_count":lcount,
                         "top100_equivalent":set(fids)==set(lids),
                         "equivalent":equal,"fts":ft,"literal":lt})
        plan=[row[3] for row in conn.execute("EXPLAIN QUERY PLAN "+fts,("SSH",))]
        no_temp_sort=not any("TEMP B-TREE" in detail for detail in plan)
        checks["fts_no_temp_sort"]=no_temp_sort
        integrity="PASS"
        try:conn.execute("INSERT INTO messages_fts(messages_fts) VALUES('integrity-check')")
        except sqlite3.DatabaseError as exc:integrity=str(exc)
        report={"status":"PASS" if all(checks.values()) and integrity=="PASS" else "FAIL",
                "dataset":{"conversations":a.conversations,"messages":a.conversations*a.messages,
                           "import_seconds":import_s,"db_bytes":Path(tmp,"ricoeur.db").stat().st_size},
                "integrity":integrity,"queries":rows,
                "notes":["Both timed queries return IDs only, order by rowid, and limit to 100.",
                         "FTS token search and LIKE substring search are only equivalent for selected corpus terms.",
                         "Timing is local; cross-run comparisons require controlled hardware."]}
        conn.close()
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if report["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
