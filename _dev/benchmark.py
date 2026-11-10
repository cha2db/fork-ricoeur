"""Headless retrieval benchmark: correctness, ranking, Unicode, SQL safety and latency."""
from __future__ import annotations
import argparse
import json
import random
import sqlite3
import statistics
import tempfile
import time
from pathlib import Path
from ricoeur.db import init_db
from ricoeur.retrieval import search_messages, get_message_context

TOPICS = [
 ("ssh", "A conexão SSH permite acesso remoto seguro usando autenticação por chave."),
 ("postgresql", "PostgreSQL suporta transações ACID e índices B-tree para consultas."),
 ("devops", "O pipeline Jenkins executa integração contínua e testes de regressão."),
 ("auok", "A aprendizagem utiliza regressão guiada e unidades atômicas de conhecimento."),
 ("mcp", "O protocolo MCP conecta ferramentas a clientes por contratos explícitos."),
 ("android", "Android Studio compila aplicativos móveis e executa testes instrumentados."),
 ("seguranca", "A política de segurança aplica menor privilégio e auditoria."),
 ("web", "A API REST oferece endpoints HTTP com contratos JSON estáveis."),
]
def build(conn, n, per):
    rows=[]
    for i in range(n):
        topic, text = TOPICS[i % len(TOPICS)]
        cid=f"bench-c{i:06d}"
        conn.execute("INSERT INTO conversations(id,title,platform) VALUES(?,?,?)",
                     (cid, f"Benchmark {topic} {i}",("chatgpt","claude","gemini","copilot")[i%4]))
        for j in range(per):
            suffix = (" MARCADOR_UNICO_2026" if i==0 and j==3 else "")
            rows.append((f"bench-m{i:06d}-{j:04d}",cid,"user" if j%2==0 else "assistant",
                         f"Mensagem {j}. {text} Discussão técnica sobre {topic}.{suffix}",
                         f"2026-01-01T00:{j//60:02d}:{j%60:02d}"))
        if len(rows)>=1000:
            conn.executemany("INSERT INTO messages(id,conv_id,role,content,timestamp) VALUES(?,?,?,?,?)",rows)
            rows=[]
    if rows:
        conn.executemany("INSERT INTO messages(id,conv_id,role,content,timestamp) VALUES(?,?,?,?,?)",rows)
    conn.commit()

def literal(conn, term, limit=200):
    return conn.execute(
        """SELECT m.id FROM messages m WHERE instr(lower(m.content),lower(?))>0
           ORDER BY m.rowid LIMIT ?""",(term,limit)).fetchall()

def timed(fn, repeats=5):
    samples=[]
    result=None
    for _ in range(repeats):
        t=time.perf_counter()
        result=fn()
        samples.append(round((time.perf_counter()-t)*1000,3))
    return result,{"median_ms":round(statistics.median(samples),3),
                   "min_ms":min(samples),"max_ms":max(samples)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--conversations",type=int,default=300)
    p.add_argument("--messages",type=int,default=40)
    p.add_argument("--output",default="_dev/results/benchmark.json")
    args=p.parse_args()
    if not 1<=args.conversations<=10000 or not 4<=args.messages<=100:
        p.error("conversations 1..10000, messages 4..100")
    random.seed(2026)
    checks={}
    benchmarks={}
    errors={}
    with tempfile.TemporaryDirectory(prefix="cha2db-benchmark-") as tmp:
        conn=init_db(Path(tmp))
        try:
            build(conn,args.conversations,args.messages)
            checks["count"]=conn.execute("SELECT count(*) FROM messages").fetchone()[0]==args.conversations*args.messages
            checks["fts_integrity"]=True
            try:
                conn.execute("INSERT INTO messages_fts(messages_fts) VALUES('integrity-check')")
            except sqlite3.DatabaseError as exc:
                checks["fts_integrity"]=False
                errors["fts_integrity"]=str(exc)
            for term in ("SSH","PostgreSQL","Jenkins","MCP","Android","REST","regressão","MARCADOR_UNICO_2026"):
                # Compare sets at corpus scale, not a truncated top-N list.
                expected={r[0] for r in literal(conn,term,args.conversations*args.messages+1)}
                result,metric=timed(lambda: search_messages(conn,term,limit=200,context=0))
                actual={hit["message"]["id"] for hit in result["hits"]}
                checks["fts_precision_"+term]=actual.issubset(expected)
                checks["fts_recall_"+term]=actual==expected if len(expected)<=200 else len(actual)==200
                benchmarks["fts_"+term]=metric
                _,benchmarks["literal_"+term]=timed(lambda: literal(conn,term,200))
            for term in ("MARCADOR_UNICO_2026","sem_palavra_inexistente_987654"):
                result=search_messages(conn,term,limit=200,context=0)
                checks["exact_"+term]=result["count"]==(1 if term=="MARCADOR_UNICO_2026" else 0)
            ctx=get_message_context(conn,"bench-m000000-0003",context=2)
            checks["context_navigation"]=bool(ctx and len(ctx["before"])==2 and len(ctx["after"])==2)
            checks["provider_filter"]=all(
                hit["conversation"]["platform"]=="claude"
                for hit in search_messages(conn,"SSH",platform="claude",limit=200,context=0)["hits"])
            checks["sql_injection_literal"]=len(literal(conn,"' OR 1=1 --"))==0
            checks["fts_invalid_syntax_rejected"]=False
            try:
                search_messages(conn,'"unclosed',limit=5,context=0)
            except sqlite3.OperationalError:
                checks["fts_invalid_syntax_rejected"]=True
            checks["empty_query_rejected"]=False
            try:
                search_messages(conn," ",limit=5)
            except ValueError:
                checks["empty_query_rejected"]=True
            checks["pagination_limit"]=search_messages(conn,"SSH",limit=5,context=0)["count"]<=5
            report={"status":"PASS" if all(checks.values()) else "FAIL",
                    "dataset":{"conversations":args.conversations,"messages":args.conversations*args.messages,
                               "seed":2026,"synthetic":True},
                    "checks":checks,"latency":benchmarks,"errors":errors,
                    "notes":["FTS5 token matching and literal substring matching are not equivalent.",
                             "Semantic retrieval, real HTTP and relevance judgments are not tested.",
                             "Timings are local samples, not cross-device comparisons."]}
        finally:
            conn.close()
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if report["status"]!="PASS":
        raise SystemExit(1)
if __name__=="__main__":
    main()
