"""Evidence-linked cross-conversation relation candidates. No inferred supersession."""
import argparse
import json
import re
import sqlite3
import shutil
import tempfile
from pathlib import Path
import networkx as nx
from ricoeur.db import init_db
from corpus import populate

EXAMPLES=[
 ('r1','ca','chatgpt','DEC-101: Escolhemos SQLite como base para indexação textual.'),
 ('r2','cb','claude','DEC-102: Refinamos DEC-101 com índices FTS5 e busca por mensagens.'),
 ('r3','cc','gemini','DEC-103: Substitui DEC-102 para garantir rastreabilidade de mensagens.'),
 ('r4','cd','chatgpt','DEC-104: Contradiz DEC-101 porque perderíamos a proveniência.'),
 ('r5','ce','copilot','DEC-105: Continua DEC-103 e testa a indexação.'),
 ('r6','cf','claude','Conversa sobre índices FTS5 e SQLite sem referências a decisões.'),
 ('r7','cg','gemini','DEC-106: Substitui uma ideia anterior sem citar identificador.'),
]
GOLD={('DEC-102','DEC-101','refines'),('DEC-103','DEC-102','supersedes'),
      ('DEC-104','DEC-101','contradicts'),('DEC-105','DEC-103','follows_up')}
RELATIONS={'refinamos':'refines','substitui':'supersedes',
           'contradiz':'contradicts','continua':'follows_up'}
LINK=re.compile(r'\b(refinamos|substitui|contradiz|continua)\s+(DEC-\d+)\b',re.I)
ID=re.compile(r'\b(DEC-\d+)\s*:')

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="_dev/results/relations.json")
    p.add_argument("--db-path",default=None)
    args=p.parse_args()
    with tempfile.TemporaryDirectory(prefix="cha2db-relations-") as tmp:
        if args.db_path:
            clone=Path(tmp)/"ricoeur.db";shutil.copy2(args.db_path,clone)
            conn=sqlite3.connect(str(clone));conn.row_factory=sqlite3.Row
        else:
            conn=init_db(Path(tmp));populate(conn,100,12)
        for i,(mid,cid,platform,content) in enumerate(EXAMPLES):
            conn.execute("INSERT INTO conversations(id,title,platform) VALUES(?,?,?)",
                         (cid,"Relação documental "+mid,platform))
            conn.execute("INSERT INTO messages(id,conv_id,role,content,timestamp) VALUES(?,?,?,?,?)",
                         (mid,cid,"assistant",content,f"2026-02-{i+1:02d}T00:00:00"))
        conn.commit()
        rows=conn.execute("""SELECT m.id,m.content,c.platform FROM messages m
                             JOIN conversations c ON c.id=m.conv_id
                             WHERE m.id LIKE 'r_' ORDER BY m.rowid""").fetchall()
        known={m.group(1) for row in rows if (m:=ID.search(row["content"]))}
        links=set();candidates=[];graph=nx.DiGraph()
        for row in rows:
            own=ID.search(row["content"]);reference=LINK.search(row["content"])
            if not own or not reference or reference.group(2) not in known:continue
            source=own.group(1);target=reference.group(2)
            kind=RELATIONS[reference.group(1).casefold()]
            graph.add_edge(source,target,type=kind,evidence_message_id=row["id"],
                           status="candidate")
            links.add((source,target,kind))
            candidates.append({"source":source,"target":target,"type":kind,
                "evidence_message_id":row["id"],"platform":row["platform"],
                "status":"candidate"})
        checks={
            "explicit_links_match":links==GOLD,
            "cross_provider":len({x["platform"] for x in candidates})==4,
            "no_inferred_supersedes":all(x["source"]!="DEC-106" for x in candidates),
            "review_pending":all(x["status"]=="candidate" for x in candidates),
            "supersedes_acyclic":nx.is_directed_acyclic_graph(nx.DiGraph(
                [(a,b) for a,b,t in links if t=="supersedes"]))}
        report={"status":"PASS" if all(checks.values()) else "FAIL",
                "dataset":{"base":"_dev/corpus.py","base_messages":conn.execute("SELECT count(*) FROM messages").fetchone()[0]-len(EXAMPLES),
                           "explicit_relation_cases":len(EXAMPLES),"synthetic":True},
                "checks":checks,"precision":round(len(links&GOLD)/max(1,len(links)),4),
                "recall":round(len(links&GOLD)/len(GOLD),4),
                "candidates":candidates,
                "verdict":"EXPLICIT_REFERENCES_ONLY_HUMAN_CONFIRMATION_REQUIRED",
                "limitations":["Synthetic explicit references; not free-text semantic inference.",
                               "No automated contradiction/supersession verdict.",
                               "Graph edges remain candidates until human approval."]}
        conn.close()
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if report["status"]=="FAIL":raise SystemExit(1)
if __name__=="__main__":main()
