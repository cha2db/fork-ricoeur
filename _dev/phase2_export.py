"""Read-only export for cross-language search engine comparison."""
import argparse,hashlib,json,sqlite3
from pathlib import Path
QUERIES=[
 ("regressão guiada",0),("contrato declarativo",1),("busca cruzada",2),
 ("pipeline Jenkins",3),("índice B-tree",4),("conexão SSH",5),
 ("Android Studio",6),("menor privilégio",7),("avaliação formativa",8),
 ("API REST",9)]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db-path",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    conn=sqlite3.connect(f"file:{Path(a.db_path).resolve()}?mode=ro",uri=True)
    conn.row_factory=sqlite3.Row
    rows=[dict(r) for r in conn.execute(
      "SELECT id,conv_id,content FROM messages WHERE id LIKE 'fixture-cha2db-v1-m%-0000' ORDER BY rowid LIMIT 1000")]
    assert len(rows)==1000
    digest=hashlib.sha256()
    for row in rows:
        digest.update(json.dumps(row,sort_keys=True,ensure_ascii=False).encode()+b"\n")
    data={"corpus":"existing fixture corpus.py","synthetic":True,"documents":rows,
          "queries":[{"text":q,"topic":topic} for q,topic in QUERIES],
          "sha256":digest.hexdigest()}
    path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2))
    print(json.dumps({"documents":len(rows),"queries":len(QUERIES),"sha256":data["sha256"]}))
    conn.close()
if __name__=="__main__":main()
