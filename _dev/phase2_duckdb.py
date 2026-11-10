"""Compare DuckDB FTS BM25 with canonical SQLite-sourced message IDs.
No permanent DB mutation and no LLM dependency.
"""
import argparse,json,statistics,time,traceback
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fixture",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    fixture=json.loads(Path(a.fixture).read_text())
    result={"candidate":"DuckDB FTS","source":a.fixture,"sha256":fixture["sha256"],
            "status":"RUNNING","documents":len(fixture["documents"]),"queries":[]}
    try:
        import duckdb
        db=duckdb.connect(":memory:")
        db.execute("INSTALL fts; LOAD fts")
        db.execute("CREATE TABLE documents (id VARCHAR PRIMARY KEY,content VARCHAR,topic INTEGER)")
        rows=[(d["id"],d["content"],int(d["conv_id"].split("c")[-1])%10)
              for d in fixture["documents"]]
        db.executemany("INSERT INTO documents VALUES (?,?,?)",rows)
        t=time.perf_counter()
        db.execute("PRAGMA create_fts_index('documents','id','content',stemmer='none',stopwords='none')")
        result["build_seconds"]=round(time.perf_counter()-t,3)
        timings=[]
        for q in fixture["queries"]:
            t=time.perf_counter_ns()
            hits=db.execute(
                """SELECT id,topic,score FROM (
                  SELECT id,topic,fts_main_documents.match_bm25(id, ?) AS score
                  FROM documents
                ) x WHERE score IS NOT NULL ORDER BY score DESC,id LIMIT 10""",
                (q["text"],)).fetchall()
            elapsed=(time.perf_counter_ns()-t)/1e6
            ids=[r[0] for r in hits]
            if len(set(ids))!=len(ids) or len(ids)>10:raise AssertionError("bad id result")
            result["queries"].append({"query":q["text"],"p10":
               round(sum(int(row[1]==q["topic"]) for row in hits)/10,4),
               "hits":ids,"latency_ms":round(elapsed,3)})
            timings.append(elapsed)
        result["mean_p10"]=round(statistics.mean(x["p10"] for x in result["queries"]),4)
        result["median_latency_ms"]=round(statistics.median(timings),3)
        result["status"]="PASS"
        result["version"]=duckdb.__version__
        result["verdict"]="FUNCTIONAL_ONLY_INCREMENTAL_UPDATES_NOT_VERIFIED"
        db.close()
    except Exception as exc:
        result["status"]="BLOCKED";result["error"]=type(exc).__name__+": "+str(exc)
        result["traceback"]=traceback.format_exc(limit=5)
    result["limitations"]=["Extension downloads in CI; offline portability not established",
          "Only 1000 representative docs, not the complete 40k ranked",
          "Synthetic topic labels; no human relevance evidence"]
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k not in ("queries","traceback")},
                     ensure_ascii=False,indent=2))
    if result["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
