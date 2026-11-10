"""SQLite-Vector extension vs its exact full scan, same shared 40k fixture.
Tests extension portability and vector recall; no semantic model is implied.
"""
import argparse
import importlib.metadata
import importlib.resources
import json
import shutil
import struct
import sqlite3
import tempfile
import time
from pathlib import Path
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from corpus import PREFIX

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db-path",required=True)
    p.add_argument("--output",default="_dev/results/sqlite-vector.json")
    a=p.parse_args()
    with tempfile.TemporaryDirectory(prefix="cha2db-sqlite-vector-") as tmp:
        path=Path(tmp)/"ricoeur.db";shutil.copy2(a.db_path,path)
        db=sqlite3.connect(str(path))
        db.row_factory=sqlite3.Row
        texts=[r[0] for r in db.execute(
            "SELECT content FROM messages WHERE id LIKE ? ORDER BY rowid",
            (PREFIX+"m%-0000",)).fetchall()]
        word=TfidfVectorizer(strip_accents="unicode",ngram_range=(1,2),max_features=10000)
        encoded=word.fit_transform(texts)
        vectors=normalize(TruncatedSVD(n_components=32,random_state=2026).fit_transform(encoded))
        try:
            ext=str(importlib.resources.files("sqlite_vector.binaries")/"vector")
        except ModuleNotFoundError:
            distribution=importlib.metadata.distribution("sqlite-vector")
            binaries=[distribution.locate_file(f) for f in (distribution.files or [])
                      if str(f).endswith((".so",".dylib",".dll")) and "vector" in str(f).lower()]
            if not binaries:
                raise RuntimeError("No extension found; package files="+
                                   str([str(f) for f in distribution.files or []][:35]))
            ext=str(binaries[0])
        db.enable_load_extension(True)
        try:db.load_extension(ext)
        finally:db.enable_load_extension(False)
        ext_version=db.execute("SELECT vector_version()").fetchone()[0]
        functions=[row[0] for row in db.execute("SELECT name FROM pragma_function_list WHERE name LIKE 'vector_%'")]
        print("sqlite-vector version",ext_version,"functions",sorted(set(functions)),flush=True)
        db.execute("CREATE TABLE vector_candidates(id INTEGER PRIMARY KEY,embedding BLOB)")
        db.executemany("INSERT INTO vector_candidates(id,embedding) VALUES(?,?)",
                       [(i+1,struct.pack("<32f",*row)) for i,row in enumerate(vectors)])
        db.commit()
        db.execute("SELECT vector_init('vector_candidates','embedding','dimension=32,type=FLOAT32,distance=L2')")
        t=time.monotonic()
        db.execute("SELECT vector_quantize('vector_candidates','embedding')")
        index_s=round(time.monotonic()-t,3)
        queries=[]
        for i in (0,7,25,78,125,500):
            if i>=len(vectors):continue
            query=struct.pack("<32f",*vectors[i])
            t=time.perf_counter_ns()
            exact=[r["rowid"] for r in db.execute(
                "SELECT rowid,distance FROM vector_full_scan('vector_candidates','embedding',?,10)",
                (query,)).fetchall()]
            exact_ms=round((time.perf_counter_ns()-t)/1e6,3)
            t=time.perf_counter_ns()
            approximate=[r["rowid"] for r in db.execute(
                "SELECT rowid,distance FROM vector_quantize_scan('vector_candidates','embedding',?,10)",
                (query,)).fetchall()]
            approximate_ms=round((time.perf_counter_ns()-t)/1e6,3)
            brute=np.linalg.norm(vectors-vectors[i],axis=1)
            cut=float(np.partition(brute,9)[9])
            exact_valid=all(brute[k-1]<=cut+0.0001 for k in exact)
            recall=len(set(exact)&set(approximate))/max(1,len(exact))
            queries.append({"index":i,"exact_valid":exact_valid,
                            "approx_recall_at10":round(recall,3),
                            "exact_ms":exact_ms,"approx_ms":approximate_ms})
        checks={"all_exact_correct":all(q["exact_valid"] for q in queries),
                "index_present":len(vectors)==1000,
                "queries_executed":len(queries)==6}
        report={"status":"PASS" if all(checks.values()) else "FAIL",
                "candidate":"SQLite-Vector","version":ext_version,
                "package_version":importlib.metadata.version("sqlite-vector"),
                "data_source":a.db_path,"vectors":len(vectors),
                "embedding":"TF-IDF SVD32, not neural semantics",
                "quantize_seconds":index_s,"checks":checks,"queries":queries,
                "mean_approx_recall10":round(float(np.mean([q["approx_recall_at10"] for q in queries])),3),
                "verdict":"QUANTIZED_KNN_CANDIDATE_ONLY_COMPARE_WITH_SQLITE_VEC",
                "limits":["Not a neural semantic relevance test.",
                          "Approximate recall depends on ties and quantization.",
                          "Runtime/native extension portability to Termux untested."]}
        db.close()
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if report["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
