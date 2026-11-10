"""CPU-only optional semantic prior-art gate on Cha2db's existing synthetic fixture.
Embeddings/reranking/topic modeling are adapters, never required by core.
"""
from __future__ import annotations
import argparse
import importlib.metadata
import json
import sqlite3
import math
import tempfile
import time
import traceback
from pathlib import Path
from ricoeur.db import init_db
from corpus import PREFIX,TOPICS,populate

PARAPHRASES=[
 ("preciso acessar um computador remoto de forma protegida",5),
 ("quero acompanhar requisitos prévios para uma unidade de aprendizagem",0),
 ("componentes visuais com interfaces bem definidas",1),
 ("encontrar o mesmo tema em conversas diferentes",2),
 ("automatizar build e entrega de software",3),
 ("acelerar consultas com estrutura de acesso aos dados",4),
 ("produzir aplicativo para telefone",6),
 ("reduzir permissões e registrar ações sensíveis",7),
 ("avaliar continuamente o progresso de estudantes",8),
 ("oferecer comunicação por endpoints de rede",9),
]
def metric(indices,labels,topic):
    first=next((r for r,i in enumerate(indices[:10],1) if labels[i]==topic),None)
    hits=sum(labels[i]==topic for i in indices[:10])
    return {"p10":round(hits/10,4),"mrr10":round(1/first if first else 0,4)}
def package(name):
    try:return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:return "UNAVAILABLE"

def main():
    import numpy as np
    from sentence_transformers import SentenceTransformer
    ap=argparse.ArgumentParser()
    ap.add_argument("--conversations",type=int,default=1000)
    ap.add_argument("--output",default="_dev/results/semantic.json")
    ap.add_argument("--model",default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    ap.add_argument("--db-path",default=None)
    a=ap.parse_args()
    if a.conversations<100 or a.conversations%10:ap.error("multiple of 10, minimum 100")
    report={"status":"RUNNING","fixture":{"generator":"_dev/corpus.py",
            "conversations":a.conversations,"messages":a.conversations*40,
            "sample_documents":100,"synthetic":True,"human_gold":False},
            "model":a.model,"libraries":{"sentence-transformers":package("sentence-transformers"),
                  "bertopic":package("bertopic")},"components":{},"limitations":[]}
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    def save():
        out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    save()
    with tempfile.TemporaryDirectory(prefix="cha2db-semantic-") as d:
        if a.db_path:
            db=sqlite3.connect(str(Path(a.db_path).resolve()));db.row_factory=sqlite3.Row
            report["fixture"]["snapshot"]=a.db_path
        else:
            db=init_db(Path(d));populate(db,a.conversations,40)
        rows=db.execute("SELECT id,conv_id,content FROM messages WHERE id LIKE ? ORDER BY rowid LIMIT 100",
                        (PREFIX+"m%-0000",)).fetchall()
        docs=[r["content"] for r in rows]
        labels=[int(r["conv_id"].split("c")[-1])%len(TOPICS) for r in rows]
        t=time.perf_counter()
        model=SentenceTransformer(a.model,device="cpu")
        embeddings=model.encode(docs,normalize_embeddings=True,show_progress_bar=False,
                                batch_size=16,convert_to_numpy=True)
        queries=[text for text,_ in PARAPHRASES]
        query_emb=model.encode(queries,normalize_embeddings=True,
                               show_progress_bar=False,convert_to_numpy=True)
        report["components"]["encoder"]={"status":"PASS","load_encode_seconds":
              round(time.perf_counter()-t,3),"dimensions":int(embeddings.shape[1])}
        save()
        details=[]
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer=TfidfVectorizer(strip_accents="unicode",ngram_range=(1,2))
        tfidf=vectorizer.fit_transform(docs)
        qtfidf=vectorizer.transform(queries)
        for j,(query,topic) in enumerate(PARAPHRASES):
            scores=embeddings@query_emb[j]
            lexical=(tfidf@qtfidf[j].T).toarray().ravel()
            erank=np.argsort(-scores,kind="stable").tolist()
            lrank=np.argsort(-lexical,kind="stable").tolist()
            details.append({"query":query,"expected_topic":TOPICS[topic][0],
                "embeddings":metric(erank,labels,topic),
                "tfidf":metric(lrank,labels,topic),
                "best_message_id":rows[erank[0]]["id"]})
        report["components"]["semantic_retrieval"]={"status":"PASS","queries":details,
            "mean_mrr10":round(float(np.mean([x["embeddings"]["mrr10"] for x in details])),3),
            "baseline_tfidf_mean_mrr10":round(float(np.mean([x["tfidf"]["mrr10"] for x in details])),3)}
        save()
        # No independent annotated relation graph exists. Do not infer supersedes.
        try:
            from bertopic import BERTopic
            t=time.perf_counter()
            topics,_=BERTopic(min_topic_size=5,verbose=False,calculate_probabilities=False
                              ).fit_transform(docs,embeddings=embeddings)
            from sklearn.metrics import adjusted_rand_score
            report["components"]["bertopic"]={"status":"PASS",
                "seconds":round(time.perf_counter()-t,3),
                "clusters":len(set(topics)-{-1}),
                "outliers":sum(x==-1 for x in topics),
                "ari_against_fixture_topics":round(float(adjusted_rand_score(labels,topics)),4)}
        except Exception as exc:
            report["components"]["bertopic"]={"status":"BLOCKED",
                "reason":type(exc).__name__+": "+str(exc)[:500],
                "traceback":traceback.format_exc(limit=3)}
        save()
        try:
            from sentence_transformers import CrossEncoder
            t=time.perf_counter()
            reranker=CrossEncoder("cross-encoder/mmarco-mMiniLMv2-L12-H384-v1",
                                  device="cpu")
            cases=[]
            for j in range(min(4,len(PARAPHRASES))):
                scores=embeddings@query_emb[j]
                top=np.argsort(-scores,kind="stable")[:15]
                rescored=reranker.predict([(queries[j],docs[i]) for i in top],
                                         show_progress_bar=False)
                indices=[int(top[i]) for i in np.argsort(-rescored,kind="stable")]
                cases.append({"query":queries[j],"reranked":metric(indices,labels,PARAPHRASES[j][1]),
                              "original":metric(top.tolist(),labels,PARAPHRASES[j][1])})
            report["components"]["cross_encoder"]={"status":"PASS",
                "model":"cross-encoder/mmarco-mMiniLMv2-L12-H384-v1",
                "seconds":round(time.perf_counter()-t,3),"queries":cases}
        except Exception as exc:
            report["components"]["cross_encoder"]={"status":"BLOCKED",
                "reason":type(exc).__name__+": "+str(exc)[:500],
                "traceback":traceback.format_exc(limit=3)}
        save()
        db.close()
    states=[v["status"] for v in report["components"].values()]
    report["status"]="PASS" if all(s=="PASS" for s in states) else "PARTIAL"
    report["verdict"]="EXPERIMENT_ONLY_NO_HUMAN_ANNOTATIONS"
    report["limitations"]=["Queries and topical labels curated for a repetitive synthetic corpus.",
        "Embedding models are downloaded at test time; no model required in the Cha2db core.",
        "Retrieval similarity does not establish contradicts, supersedes or follows_up.",
        "CrossEncoder uses a 4-query subset of retrieved candidates only.",
        "Model licenses and memory constraints must be checked before adoption."]
    save()
    print(json.dumps({"status":report["status"],"components":{
        key:{k:v for k,v in result.items() if k not in ("queries","traceback")}
        for key,result in report["components"].items()}},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
