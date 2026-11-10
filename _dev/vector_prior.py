"""Optional sqlite-vec adoption gate using the existing Cha2db corpus.

No new embedding model: deterministic TF-IDF->SVD only tests the vector index.
"""
import argparse
import importlib.metadata
import json
import sqlite3
import shutil
import tempfile
import time
from pathlib import Path
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from ricoeur.db import init_db
from corpus import PREFIX,populate

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--conversations",type=int,default=1000)
    ap.add_argument("--output",default="_dev/results/sqlite-vec.json")
    ap.add_argument("--db-path",default=None)
    a=ap.parse_args()
    with tempfile.TemporaryDirectory(prefix="cha2db-vec-") as tmp:
        if a.db_path:
            clone=Path(tmp)/"ricoeur.db"
            shutil.copy2(a.db_path,clone)
            db=sqlite3.connect(str(clone));db.row_factory=sqlite3.Row
        else:
            db=init_db(Path(tmp));populate(db,a.conversations,40)
        docs=db.execute("SELECT id,content FROM messages WHERE id LIKE ? ORDER BY rowid",
                        (PREFIX+"m%-0000",)).fetchall()
        ids=[r["id"] for r in docs]
        text=[r["content"] for r in docs]
        tfidf=TfidfVectorizer(strip_accents="unicode",ngram_range=(1,2),max_features=10000)
        vectors=tfidf.fit_transform(text)
        embedding=normalize(TruncatedSVD(n_components=32,random_state=2026).fit_transform(vectors))
        import sqlite_vec
        db.enable_load_extension(True)
        try:sqlite_vec.load(db)
        finally:db.enable_load_extension(False)
        db.execute("CREATE VIRTUAL TABLE vec_docs USING vec0(embedding float[32])")
        beginning=time.perf_counter()
        db.executemany("INSERT INTO vec_docs(rowid,embedding) VALUES(?,?)",
                       [(i+1,sqlite_vec.serialize_float32(v.astype('float32').tolist()))
                        for i,v in enumerate(embedding)])
        db.commit()
        import_seconds=round(time.perf_counter()-beginning,4)
        hits=[]
        for index in (0,7,25,78,125,500):
            if index>=len(ids):continue
            query=embedding[index].astype('float32')
            begin=time.perf_counter()
            found=db.execute(
                """SELECT rowid,distance FROM vec_docs WHERE embedding MATCH ?
                   AND k = 10 ORDER BY distance""",
                (sqlite_vec.serialize_float32(query.tolist()),)).fetchall()
            elapsed_ms=round((time.perf_counter()-begin)*1000,3)
            exact=np.linalg.norm(embedding-query,axis=1)
            cutoff=np.partition(exact,9)[9]
            within=all(exact[row["rowid"]-1]<=cutoff+0.0001 for row in found)
            monotonic=all(found[i]["distance"]<=found[i+1]["distance"]+1e-9
                          for i in range(len(found)-1))
            contains_self=any(row["rowid"]==index+1 for row in found)
            hits.append({"index":index,"query_id":ids[index],"latency_ms":elapsed_ms,
                         "within_brute_force_top10_with_ties":within,
                         "distance_monotonic":monotonic,"self_retrieved":contains_self})
        report={"status":"PASS" if all(all(v for k,v in row.items() if k in (
                 "within_brute_force_top10_with_ties","distance_monotonic","self_retrieved"))
                 for row in hits) else "FAIL",
                "candidate":"sqlite-vec","version":importlib.metadata.version("sqlite-vec"),
                "dataset":{"messages":a.conversations*40,"indexed_vectors":len(ids),
                           "origin":"_dev/corpus.py","synthetic":True},
                "embedding":"TruncatedSVD32 of TF-IDF (not semantic embeddings)",
                "index_seconds":import_seconds,"queries":hits,
                "verdict":"INDEX_FUNCTIONALITY_ONLY_NO_SEMANTIC_RELEVANCE_CLAIM"}
        db.close()
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if report["status"]=="FAIL":raise SystemExit(1)
if __name__=="__main__":main()
