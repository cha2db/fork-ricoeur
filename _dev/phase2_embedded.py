"""Phase 2: test existing embedded products against the SAME existing SQLite corpus.

Each external engine is run in its own GitHub Actions job. This script does not
install anything or modify the Cha2db runtime. Relevance labels are synthetic.
"""
from __future__ import annotations
import argparse
import importlib.metadata
import json
import math
import sqlite3
import statistics
import time
import traceback
from pathlib import Path

QUERIES=[
 ("regressão guiada",0),("contrato declarativo",1),("busca cruzada",2),
 ("pipeline Jenkins",3),("índice B-tree",4),("conexão SSH",5),
 ("Android Studio",6),("menor privilégio",7),("avaliação formativa",8),
 ("API REST",9),
]
MISSING="marcador_inexistente_zzz_2026"
def p10(ids,topic,labels):
    return round(sum(labels.get(mid)==topic for mid in ids[:10])/10,4)
def check_output(name, hits, corpus_ids):
    if not isinstance(hits,list) or len(hits)>10:
        raise AssertionError(f"{name}: invalid result size")
    if len(set(hits))!=len(hits) or any(x not in corpus_ids for x in hits):
        raise AssertionError(f"{name}: duplicate or foreign document ID")
def probe_bm25s(docs,queries):
    import bm25s
    ids=[x["id"] for x in docs]
    start=time.perf_counter()
    tokens=bm25s.tokenize([x["content"] for x in docs], show_progress=False)
    retriever=bm25s.BM25(corpus=[{"id":i} for i in ids],backend="numpy")
    retriever.index(tokens,show_progress=False)
    build_s=round(time.perf_counter()-start,3)
    def search(term):
        q=bm25s.tokenize([term],show_progress=False)
        result,scores=retriever.retrieve(q,k=10,show_progress=False)
        return [x["id"] for x in result[0] if x is not None]
    return build_s,search,{"engine":"bm25s","package":importlib.metadata.version("bm25s")}
def probe_tantivy(docs,queries):
    import tantivy
    start=time.perf_counter()
    schema=(tantivy.SchemaBuilder().add_text_field("id",stored=True,tokenizer_name="raw")
            .add_text_field("content",stored=True).build())
    index=tantivy.Index(schema)
    writer=index.writer(heap_size=50_000_000,num_threads=1)
    for row in docs:
        document=tantivy.Document()
        document.add_text("id",row["id"])
        document.add_text("content",row["content"])
        writer.add_document(document)
    writer.commit()
    index.reload()
    build_s=round(time.perf_counter()-start,3)
    def search(term):
        searcher=index.searcher()
        parsed=index.parse_query('"'+term.replace('"','')+'"',["content"])
        return [searcher.doc(addr)["id"][0] for _,addr in searcher.search(parsed,10).hits]
    return build_s,search,{"engine":"tantivy","package":importlib.metadata.version("tantivy")}
def probe_usearch(docs,queries):
    import numpy as np
    from usearch.index import Index
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD
    from sklearn.preprocessing import normalize
    start=time.perf_counter()
    vectorizer=TfidfVectorizer(strip_accents="unicode",ngram_range=(1,2),max_features=12000)
    matrix=vectorizer.fit_transform([x["content"] for x in docs])
    model=TruncatedSVD(n_components=32,random_state=2026)
    vectors=normalize(model.fit_transform(matrix)).astype("float32")
    index=Index(ndim=32,metric="cos",dtype="f32",connectivity=16,expansion_add=64,expansion_search=100)
    index.add(np.arange(1,len(docs)+1,dtype=np.uint64),vectors)
    build_s=round(time.perf_counter()-start,3)
    def search(term):
        vec=normalize(model.transform(vectorizer.transform([term]))).astype("float32")[0]
        return [docs[int(item.key)-1]["id"] for item in index.search(vec,10)]
    return build_s,search,{"engine":"usearch","package":importlib.metadata.version("usearch"),
                           "embedding":"TFIDF-SVD32: index test, NOT neural semantics"}
PROBES={"bm25s":probe_bm25s,"tantivy":probe_tantivy,"usearch":probe_usearch}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--engine",required=True,choices=sorted(PROBES))
    ap.add_argument("--db-path",required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--candidate-limit",type=int,default=1000)
    a=ap.parse_args()
    output=Path(a.output);output.parent.mkdir(parents=True,exist_ok=True)
    result={"status":"RUNNING","candidate":a.engine,"input_snapshot":a.db_path,
            "comparison":"same 1000 representative messages from existing synthetic 40k SQLite fixture",
            "queries":[],"synthetic":True,"human_gold":False}
    try:
        if not 100<=a.candidate_limit<=1000:raise ValueError("candidate limit outside 100..1000")
        conn=sqlite3.connect(f"file:{Path(a.db_path).resolve()}?mode=ro",uri=True)
        conn.row_factory=sqlite3.Row
        rows=conn.execute(
            "SELECT id,conv_id,content FROM messages WHERE id LIKE 'fixture-cha2db-v1-m%-0000' ORDER BY rowid LIMIT ?",
            (a.candidate_limit,)).fetchall()
        docs=[dict(x) for x in rows]
        labels={x["id"]:int(x["conv_id"].split("c")[-1])%10 for x in docs}
        ids={x["id"] for x in docs}
        assert len(docs)==a.candidate_limit
        conn.close()
        build,search,details=PROBES[a.engine](docs,QUERIES)
        result["build_seconds"]=build
        result.update(details)
        times=[]
        for query,topic in QUERIES:
            began=time.perf_counter_ns()
            hits=search(query)
            elapsed=(time.perf_counter_ns()-began)/1e6
            check_output(a.engine,hits,ids)
            result["queries"].append({"query":query,"topic_id":topic,"p10":p10(hits,topic,labels),
                                      "hits":hits[:10],"latency_ms":round(elapsed,3)})
            times.append(elapsed)
        result["mean_p10"]=round(statistics.mean(x["p10"] for x in result["queries"]),4)
        result["median_latency_ms"]=round(statistics.median(times),3)
        result["status"]="PASS"
        result["verdict"]="FUNCTIONAL_ONLY_NOT_COMPARABLE_SCORE_SCALE"
    except Exception as exc:
        result["status"]="BLOCKED"
        result["error"]={"type":type(exc).__name__,"message":str(exc),
                         "traceback":traceback.format_exc(limit=5)}
        result["verdict"]="API_OR_INSTALLATION_BLOCKED"
    result["limitations"]=[
      "Synthetic repetitive fixture labels generated from document IDs, NOT human judgements.",
      "One representative message per conversation, not a full-text 40k-message ranking index.",
      "Ranking semantics and tokenization differ; compare quality, storage and portability before adoption.",
      "No candidate integrated into production core; no MCP or GUI tests performed here."]
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k not in ("queries","error")},ensure_ascii=False,indent=2))
    if result["status"]!="PASS":
        print(json.dumps(result["error"],ensure_ascii=False,indent=2))
        raise SystemExit(1)
if __name__=="__main__":main()
