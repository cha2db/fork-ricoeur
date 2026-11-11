"""Reproducible preliminary candidate ranking, NOT a tested adoption verdict."""
import argparse
import json
from pathlib import Path

def rank(path):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    w=data["weights"]
    assert sum(w.values())==100
    rows=[]
    for c in data["candidates"]:
        assert all(1<=c[k]<=5 for k in w)
        score=sum(c[k]*weight for k,weight in w.items())/5
        rows.append({**c,"score_preliminary":round(score,1),"tested":False})
    return {"schema_version":data["schema_version"],"baseline":data["baseline"],
            "weights":w,"method":"manual provisional fit, 1..5 each; not benchmarks or adoption gates",
            "ranking":sorted(rows,key=lambda x:(-x["score_preliminary"],x["id"]))}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",default=str(Path(__file__).with_name("candidates.json")))
    p.add_argument("--output")
    a=p.parse_args()
    result=rank(a.manifest)
    content=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if a.output:Path(a.output).write_text(content,encoding="utf-8")
    else:print(content,end="")
if __name__=="__main__":main()
