"""Phase-2 embedded gates: hnswlib, Annoy, RDFLib and ir-measures.

Each candidate runs in its own isolated CI job with an identical synthetic corpus.
Index APIs, graph storage and IR measurement are separately tested.
"""
from __future__ import annotations
import argparse,json,math,statistics,time,traceback
from pathlib import Path

def vector_gate(candidate,fixture):
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD
    from sklearn.preprocessing import normalize
    documents=fixture["documents"]; n=len(documents)
    t=time.perf_counter()
    tf=TfidfVectorizer(strip_accents="unicode",ngram_range=(1,2),max_features=12000)
    mat=tf.fit_transform([x["content"] for x in documents])
    vectors=TruncatedSVD(n_components=32,random_state=2026).fit_transform(mat)
    rng=np.random.default_rng(2026)
    vectors=normalize(vectors + rng.normal(scale=.001,size=vectors.shape)).astype("float32")
    build0=time.perf_counter()
    if candidate=="hnswlib":
        import hnswlib
        index=hnswlib.Index(space="cosine",dim=32)
        index.init_index(max_elements=n,ef_construction=200,M=16,random_seed=2026)
        index.add_items(vectors,ids=np.arange(n,dtype=np.int64))
        index.set_ef(200)
        def search(vec):
            ids,dist=index.knn_query(vec,k=10)
            return [int(i) for i in ids[0]]
    else:
        from annoy import AnnoyIndex
        index=AnnoyIndex(32,"angular")
        index.set_seed(2026)
        for i,vec in enumerate(vectors):index.add_item(i,vec.tolist())
        index.build(25)
        def search(vec):
            return [int(i) for i in index.get_nns_by_vector(vec.tolist(),10,search_k=10000)]
    index_seconds=round(time.perf_counter()-build0,3)
    stats=[]
    for i in (0,7,25,78,125,500):
        scores=np.linalg.norm(vectors - vectors[i],axis=1)
        exact=set(np.argsort(scores,kind="stable")[:10].tolist())
        start=time.perf_counter_ns()
        approx=search(vectors[i])
        elapsed=(time.perf_counter_ns()-start)/1e6
        if any(idx<0 or idx>=n for idx in approx) or len(set(approx))!=len(approx):
            raise AssertionError("index emitted duplicate or out-of-range document IDs")
        stats.append({"source_id":documents[i]["id"],"recall_at10":round(len(set(approx)&exact)/10,3),
                      "median_candidate_distance":round(statistics.median(float(scores[j]) for j in approx),5),
                      "latency_ms":round(elapsed,3)})
    recall=round(statistics.mean(s["recall_at10"] for s in stats),3)
    return {"status":"PASS" if recall>=0.85 else "FAIL","candidate":candidate,
            "corpus_hash":fixture["sha256"],"indexed_vectors":n,
            "embedding":"TFIDF-SVD32 + fixed 0.001 seed jitter; no neural semantics",
            "vector_preparation_s":round(build0-t,3),"index_seconds":index_seconds,
            "mean_recall_at10":recall,"queries":stats,
            "verdict":"OPTIONAL_ANN_ONLY_ASSET_TO_COMPARE"}

def graph_gate(fixture):
    from rdflib import Graph,Namespace,URIRef,Literal
    ns=Namespace("urn:cha2db:")
    g=Graph()
    original=[x["id"] for x in fixture["documents"][:4]]
    if len(set(original))!=4:raise AssertionError("fixture IDs must be distinct")
    # Two explicitly declared, evidenced candidates only; never infer a relation from similarity.
    evidence=[(original[0],"references",original[1],original[2]),
              (original[3],"refines",original[1],original[0])]
    for src,kind,target,msg in evidence:
        link=URIRef(ns[f"link-{src}"])
        g.add((link,ns["from"],URIRef(ns[src])))
        g.add((link,ns["to"],URIRef(ns[target])))
        g.add((link,ns["kind"],Literal(kind)))
        g.add((link,ns["evidence"],URIRef(ns[msg])))
        g.add((link,ns["status"],Literal("candidate")))
    serialized=g.serialize(format="turtle")
    copy=Graph();copy.parse(data=serialized,format="turtle")
    checks={"rdf_roundtrip_exact":set(g)==set(copy),
            "evidence_for_each_link":len(list(g.triples((None,ns["evidence"],None))))==2,
            "nothing_auto_approved":len(list(g.triples((None,ns["status"],Literal("approved")))))==0,
            "two_explicit_relations_only":len(g)==10}
    return {"status":"PASS" if all(checks.values()) else "FAIL",
            "candidate":"rdflib","tests":checks,"triples":len(copy),
            "verdict":"GRAPH_SERIALIZATION_ONLY_NO_RELATION_INFERENCE"}

def measure_gate(fixture):
    import ir_measures
    from ir_measures import Qrel,ScoredDoc,nDCG,P,RR
    labels={doc["id"]:int(doc["conv_id"].split("c")[-1])%10 for doc in fixture["documents"]}
    qrels=[];good=[];bad=[]
    for qi,q in enumerate(fixture["queries"]):
        qid=str(qi)
        relevant=[i for i in labels if labels[i]==q["topic"]]
        irrelevant=[i for i in labels if labels[i]!=q["topic"]]
        qrels.extend(Qrel(qid,i,1) for i in relevant)
        good.extend(ScoredDoc(qid,i,10-rank) for rank,i in enumerate(relevant[:10]))
        bad.extend(ScoredDoc(qid,i,10-rank) for rank,i in enumerate(irrelevant[:10]))
    metrics=[P@10,nDCG@10,RR@10]
    passed=ir_measures.calc_aggregate(metrics,qrels,good)
    failed=ir_measures.calc_aggregate(metrics,qrels,bad)
    checks={"perfect_ranking_high":all(value>=.999 for value in passed.values()),
            "wrong_ranking_low":all(value<=.001 for value in failed.values()),
            "same_questions_as_fixture":len(fixture["queries"])==10}
    return {"status":"PASS" if all(checks.values()) else "FAIL",
       "candidate":"ir-measures","tests":checks,
       "perfect":{str(k):round(float(v),4) for k,v in passed.items()},
       "adversarial":{str(k):round(float(v),4) for k,v in failed.items()},
       "verdict":"ADOPT_METRIC_LIBRARY_CANDIDATE_NO_NEW_IR_METRICS"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--candidate",required=True,choices=["hnswlib","annoy","rdflib","ir-measures"])
    p.add_argument("--fixture",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    fixture=json.loads(Path(a.fixture).read_text(encoding="utf-8"))
    try:
        if a.candidate in ("hnswlib","annoy"):report=vector_gate(a.candidate,fixture)
        elif a.candidate=="rdflib":report=graph_gate(fixture)
        else:report=measure_gate(fixture)
    except Exception as e:
        report={"status":"BLOCKED","candidate":a.candidate,
                "error":{"type":type(e).__name__,"message":str(e),
                         "traceback":traceback.format_exc(limit=6)}}
    report["limitations"]=["Same synthetic 1000 canonical IDs regenerated from existing 40k SQLite corpus.",
         "These are API and small-scale behavior gates, not end-to-end product integration.",
         "NN recall on TFIDF vectors does not imply semantic relevance, human gold or production throughput.",
         "GitHub Actions Linux x86_64 is not Android/Termux ARM64."]
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="queries"},ensure_ascii=False,indent=2),flush=True)
    if report["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
