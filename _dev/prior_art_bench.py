"""Adoption comparison over Cha2db's EXISTING reproducible corpus generator.
Synthetic topical labels, not a human gold standard. No GUI or MCP required.
"""
from __future__ import annotations
import argparse
import importlib.metadata
import json
import math
import re
import sqlite3
import statistics
import tempfile
import time
import unicodedata
from collections import defaultdict
from pathlib import Path
from ricoeur.db import init_db
from corpus import PREFIX, TOPICS, populate

GOLD=[("regressão guiada",0),("contrato declarativo",1),
      ("busca cruzada",2),("pipeline Jenkins",3),("índice B-tree",4),
      ("conexão SSH",5),("Android Studio",6),("menor privilégio",7),
      ("avaliação formativa",8),("API REST",9)]
TYPOS=[("conexao SSH",5),("contrto declarativo",1),("avaliacao formatva",8)]
SQL="""SELECT m.id FROM messages_fts JOIN messages m ON m.rowid=messages_fts.rowid
WHERE messages_fts MATCH ? AND m.id LIKE ?
ORDER BY bm25(messages_fts),messages_fts.rowid LIMIT 10"""

def tokenize(s):
    return re.findall(r"\w+",''.join(x for x in unicodedata.normalize("NFKD",s).casefold()
                                   if not unicodedata.combining(x)))
def ranking(scores,ids):
    return [ids[i] for i in sorted(range(len(ids)),key=lambda i:(-float(scores[i]),i))[:10]
            if float(scores[i])>0]
def score(results,gold):
    hits=[int(mid in gold) for mid in results[:10]]
    dcg=sum(v/math.log2(i+2) for i,v in enumerate(hits))
    ideal=sum(1/math.log2(i+2) for i in range(min(10,len(gold))))
    first=next((i for i,v in enumerate(hits,1) if v),0)
    return {"p10":round(sum(hits)/10,4),"mrr":round(1/first if first else 0,4),
            "ndcg10":round(dcg/ideal if ideal else 0,4)}
def fuse(rankings):
    values=defaultdict(float)
    for hits in rankings:
        for rank,mid in enumerate(hits,1):values[mid]+=1/(60+rank)
    return [mid for mid,_ in sorted(values.items(),key=lambda v:(-v[1],v[0]))[:10]]
def version(name):
    try:return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--conversations",type=int,default=1000)
    ap.add_argument("--messages",type=int,default=40)
    ap.add_argument("--output",default="_dev/results/prior-art.json")
    ap.add_argument("--db-path",default=None)
    a=ap.parse_args()
    if a.conversations<100 or a.conversations%10 or a.messages<12:
        ap.error("conversations >=100 and multiple of 10, messages >=12")
    from rapidfuzz import process,fuzz
    from sklearn.feature_extraction.text import TfidfVectorizer
    from rank_bm25 import BM25Okapi
    import networkx as nx
    report={"status":"RUNNING",
            "corpus":{"source":"_dev/corpus.py", "synthetic":True,"human_gold":False,
                      "conversations":a.conversations,"messages":a.conversations*a.messages,
                      "candidate_documents":a.conversations},
            "libraries":{"rapidfuzz":version("rapidfuzz"),"scikit-learn":version("scikit-learn"),
                         "rank-bm25":version("rank-bm25"),"networkx":version("networkx")},
            "queries":[],"summary":{}}
    with tempfile.TemporaryDirectory(prefix="cha2db-prior-art-") as tmp:
        if a.db_path:
            conn=sqlite3.connect(str(Path(a.db_path).resolve()))
            conn.row_factory=sqlite3.Row
            report["corpus"]["snapshot"]=a.db_path
        else:
            conn=init_db(Path(tmp));populate(conn,a.conversations,a.messages)
        rows=conn.execute("SELECT id,conv_id,content FROM messages WHERE id LIKE ? ORDER BY rowid",
                          (PREFIX+"m%-0000",)).fetchall()
        ids=[r["id"] for r in rows]
        docs=[r["content"] for r in rows]
        assert len(ids)==a.conversations
        labels={r["id"]:int(r["conv_id"].split("c")[-1])%len(TOPICS) for r in rows}
        word=TfidfVectorizer(strip_accents="unicode",ngram_range=(1,2),max_features=12000)
        char=TfidfVectorizer(strip_accents="unicode",analyzer="char_wb",
                             ngram_range=(3,5),max_features=18000)
        mw=word.fit_transform(docs);mc=char.fit_transform(docs)
        pybm=BM25Okapi([tokenize(x) for x in docs])
        aggregate=defaultdict(list)
        for group,queries in (("exact",GOLD),("typo",TYPOS)):
            for term,topic in queries:
                times={}
                def run(name,fn):
                    start=time.perf_counter_ns();out=fn()
                    times[name]=round((time.perf_counter_ns()-start)/1e6,3)
                    return out
                def fts(q):
                    return [r["id"] for r in conn.execute(SQL,('"'+q.replace('"','""')+'"',PREFIX+"m%-0000"))]
                results={"fts5":run("fts5",lambda:fts(term)),
                         "tfidf_word":run("tfidf_word",lambda:ranking(
                             (mw@word.transform([term]).T).toarray().ravel(),ids)),
                         "tfidf_char":run("tfidf_char",lambda:ranking(
                             (mc@char.transform([term]).T).toarray().ravel(),ids)),
                         "rank_bm25":run("rank_bm25",lambda:ranking(pybm.get_scores(tokenize(term)),ids))}
                match=run("rapidfuzz",lambda:process.extractOne(term,[q for q,_ in GOLD],scorer=fuzz.WRatio))
                corrected=match[0] if match and match[1]>=65 else term
                results["rapidfuzz_fts"]=run("rapidfuzz_fts",lambda:fts(corrected))
                results["rrf"]=run("rrf",lambda:fuse([results[x] for x in ("fts5","tfidf_word","tfidf_char")]))
                truth={mid for mid in ids if labels[mid]==topic}
                qualities={algo:score(found,truth) for algo,found in results.items()}
                for algo,v in qualities.items():aggregate[(group,algo)].append(v)
                report["queries"].append({"query":term,"group":group,
                   "topic":TOPICS[topic][0],"relevant_documents":len(truth),
                   "quality":qualities,"latency_ms":times,
                   "correction":corrected,"top3":{x:y[:3] for x,y in results.items()}})
        for (group,algo),series in sorted(aggregate.items()):
            report["summary"].setdefault(algo,{})[group]={
                key:round(statistics.mean(row[key] for row in series),4)
                for key in ("p10","mrr","ndcg10")}
        # Topic community analysis: unsupervised graph from TF-IDF scores.
        n=min(100,len(ids));similarity=(mw[:n]@mw[:n].T).toarray()
        graph=nx.Graph();graph.add_nodes_from(range(n))
        for i in range(n):
            for j in range(i+1,n):
                if similarity[i,j]>=0.70:graph.add_edge(i,j,weight=float(similarity[i,j]))
        clusters=list(nx.algorithms.community.greedy_modularity_communities(graph))
        communities={j:k for k,part in enumerate(clusters) for j in part}
        from sklearn.metrics import adjusted_rand_score
        ari=adjusted_rand_score([labels[ids[i]] for i in range(n)],
                                [communities[i] for i in range(n)])
        report["graph"]={"library":"networkx","algorithm":"greedy_modularity_communities",
                         "nodes":n,"candidate_edges":graph.number_of_edges(),
                         "communities":len(clusters),"ari_against_fixture_topics":round(float(ari),4),
                         "relation_claims":"none; similarity does not prove follows_up/contradicts/supersedes"}
        conn.close()
    checks={"all_13_queries":len(report["queries"])==13,
            "fts_exact_gold":report["summary"]["fts5"]["exact"]["mrr"]>=0.99,
            "stable_message_ids":len(ids)==a.conversations,
            "no_claimed_semantic_relations":report["graph"]["relation_claims"].startswith("none"),
            "graph_ari_gold":report["graph"]["ari_against_fixture_topics"]>=0.85}
    report["checks"]=checks
    report["status"]="PASS" if all(checks.values()) else "FAIL"
    report["verdict"]="ALGORITHMS_EXECUTED_QUALITY_NOT_HUMAN_VALIDATED"
    report["limitations"]=[
        "Existing corpus is regenerated and ephemeral; no persistent 2M DB or private chats are accessed.",
        "Labels derive from the generator; they are not independent human judgments.",
        "All ranking methods search the same one-message-per-conversation candidate pool.",
        "NetworkX communities are topic candidates, not evidence of conversation succession.",
        "Rank metrics do not test semantic embeddings; semantic models need a separate gate."]
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"status":report["status"],"corpus":report["corpus"],
                      "summary":report["summary"],"graph":report["graph"],
                      "checks":checks},ensure_ascii=False,indent=2))
    if report["status"]=="FAIL":raise SystemExit(1)
if __name__=="__main__":main()
