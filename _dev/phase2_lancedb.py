"""Adoption probe for embedded LanceDB lexical, vector and hybrid RRF paths.

Shares same representative canonical IDs as the preceding Python and JS gates.
Embeddings are TF-IDF/SVD32, deliberately NOT neural or semantic.
"""
import argparse,importlib.metadata,json,statistics,tempfile,time,traceback
from pathlib import Path
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fixture",required=True);p.add_argument("--output",required=True)
    a=p.parse_args()
    fixture=json.loads(Path(a.fixture).read_text())
    report={"candidate":"LanceDB","status":"RUNNING","fixture_sha256":fixture["sha256"],
            "synthetic":True,"documents":len(fixture["documents"]),"modes":{}}
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    try:
        import numpy as np
        import lancedb
        from lancedb.index import FTS
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.decomposition import TruncatedSVD
        from sklearn.preprocessing import normalize
        report["version"]=importlib.metadata.version("lancedb")
        docs=fixture["documents"]
        model=TfidfVectorizer(strip_accents="unicode",ngram_range=(1,2),max_features=12000)
        s=TruncatedSVD(n_components=32,random_state=2026)
        vectors=normalize(s.fit_transform(model.fit_transform([x["content"] for x in docs]))).astype("float32")
        with tempfile.TemporaryDirectory(prefix="cha2db-lancedb-") as d:
            db=lancedb.connect(str(Path(d)/"store"))
            start=time.perf_counter()
            entries=[{"id":x["id"],"text":x["content"],
                      "topic":int(x["conv_id"].split("c")[-1])%10,"vector":vec.tolist()}
                      for x,vec in zip(docs,vectors)]
            table=db.create_table("chats",entries)
            table.create_index("text",config=FTS())
            report["build_seconds"]=round(time.perf_counter()-start,3)
            for mode in ("fts","vector","hybrid"):
                cases=[];errors=[]
                for q in fixture["queries"]:
                    query=q["text"]
                    vec=normalize(s.transform(model.transform([query]))).astype("float32")[0]
                    start=time.perf_counter_ns()
                    try:
                        if mode=="fts":found=table.search(query,query_type="fts").limit(10).to_list()
                        elif mode=="vector":found=table.search(vec.tolist(),query_type="vector").limit(10).to_list()
                        else:
                            found=(table.search(query_type="hybrid").vector(vec.tolist())
                                   .text(query).limit(10).to_list())
                        elapsed=(time.perf_counter_ns()-start)/1e6
                        ids=[hit["id"] for hit in found]
                        if len(ids)!=len(set(ids)) or len(ids)>10:raise AssertionError("invalid ids")
                        cases.append({"query":query,"p10":round(sum(x["topic"]==q["topic"] for x in found)/10,4),
                                      "latency_ms":round(elapsed,3),"hits":ids})
                    except Exception as e:
                        errors.append({"query":query,"type":type(e).__name__,"message":str(e)[:900]})
                report["modes"][mode]={"status":"PASS" if not errors else "BLOCKED",
                    "queries":cases,"errors":errors,
                    "mean_p10":round(statistics.mean(x["p10"] for x in cases),4) if cases else None,
                    "median_latency_ms":round(statistics.median(x["latency_ms"] for x in cases),3) if cases else None}
    except Exception as e:
        report["error"]=type(e).__name__+": "+str(e)
        report["traceback"]=traceback.format_exc(limit=6)
    statuses=[v["status"] for v in report["modes"].values()]
    report["status"]="PASS" if len(statuses)==3 and all(x=="PASS" for x in statuses) else (
        "PARTIAL" if "PASS" in statuses else "BLOCKED")
    report["verdict"]="CANDIDATE_ONLY_NOT_PRODUCTION_ADOPTION"
    report["limitations"]=["All modes use the same 1000 representative synthetic chat messages.",
       "TF-IDF-SVD32 cannot prove semantic value; no human annotation.",
       "No persistence, updates/deletes, disk budget, ACL or Android cross-platform test."]
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ("traceback","limitations") and k!="modes"}|
       {"modes":{k:{"status":v["status"],"mean_p10":v["mean_p10"],
                     "median_latency_ms":v["median_latency_ms"],"error_count":len(v["errors"])}
                 for k,v in report["modes"].items()}},ensure_ascii=False,indent=2))
    if report["status"]=="BLOCKED":raise SystemExit(1)
if __name__=="__main__":main()
