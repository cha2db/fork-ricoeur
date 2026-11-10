"""Reproducible GitHub repository discovery for Cha2db Phase 2.

Discovery only: new results are unverified candidates, NOT adopted libraries.
The repo search API is incomplete, time-dependent and rate-limited. Public repos
are queried without downloading code. Store query outcomes and failures.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import time
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

QUERIES={
 "archives":"chatgpt claude conversation archive in:readme",
 "mcp":"conversation history mcp sqlite in:readme",
 "agent-history":"coding agent sessions search sqlite in:readme",
 "provenance":"conversation provenance memory audit in:readme",
 "memory":"local-first ai memory chat in:readme",
 "graph":"temporal graph rag memory in:readme",
 "lexical":"embedded full text search rust bm25 in:readme",
 "hybrid":"hybrid search vector bm25 embedded in:readme",
 "import":"chatgpt claude import sqlite in:readme",
}
RANK_WORDS={
 "chatgpt":2,"claude":2,"conversation":4,"chat":2,"history":3,
 "archive":3,"mcp":3,"sqlite":3,"import":3,"local":2,"provenance":5,
 "audit":4,"source":1,"memory":2,"graph":2,"hybrid":2,
 "search":2,"bm25":2,"embedded":3,"rust":1,
}
MIN_RANK=6
def evaluate(repo):
    t=" ".join([repo.get("name") or "",repo.get("description") or "",
                " ".join(repo.get("topics") or [])]).lower()
    terms={k for k in RANK_WORDS if k in t}
    score=sum(RANK_WORDS[k] for k in terms)
    return score,sorted(terms)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--inventory",default="_dev/PHASE2_MARKET_UNIVERSE_R09.json")
    p.add_argument("--output",default="_dev/results/phase2-discovery.json")
    p.add_argument("--max-results",type=int,default=40)
    args=p.parse_args()
    if not 1<=args.max_results<=100:p.error("max results must be 1..100")
    inventory=json.loads(Path(args.inventory).read_text())
    known={}
    pattern=re.compile(r"^https://github\.com/([^/]+)/([^/?#]+)")
    for item in inventory["candidates"]:
        match=pattern.match(item["url"])
        if match:known[(match.group(1)+"/"+match.group(2).removesuffix(".git")).lower()]=item["id"]
    token=os.environ.get("GITHUB_TOKEN")
    headers={"Accept":"application/vnd.github+json","User-Agent":"cha2db-phase2-discovery",
             "X-GitHub-Api-Version":"2022-11-28"}
    if token:headers["Authorization"]="Bearer "+token
    encountered={};errors={};query_details={}
    for category,terms in QUERIES.items():
        q=terms+" archived:false"
        url="https://api.github.com/search/repositories?"+urlencode({
            "q":q,"sort":"best-match","order":"desc","per_page":args.max_results})
        try:
            with urlopen(Request(url,headers=headers),timeout=20) as response:
                data=json.loads(response.read())
            items=data.get("items",[])
            query_details[category]={"query":q,"total_count":data.get("total_count"),
                                    "sampled":len(items),"incomplete_results":data.get("incomplete_results")}
            for row in items:
                full=row.get("full_name")
                if not full:continue
                id=full.lower()
                if id not in encountered:encountered[id]={"name":full,
                    "url":row.get("html_url"),"description":row.get("description"),
                    "license_spdx":(row.get("license") or {}).get("spdx_id"),
                    "stars":row.get("stargazers_count"),"pushed_at":row.get("pushed_at"),
                    "archived":row.get("archived"),"fork":row.get("fork"),
                    "topics":row.get("topics") or [],"query_groups":[]}
                encountered[id]["query_groups"].append(category)
        except (HTTPError,URLError,TimeoutError,ValueError) as error:
            errors[category]={"type":type(error).__name__,
                              "status":getattr(error,"code",None),"message":str(error)[:240]}
            query_details[category]={"query":q,"status":"ERROR"}
        time.sleep(.15)
    novel=[]
    for name,x in encountered.items():
        if name in known or x.get("archived") or x.get("fork"):continue
        score,matched=evaluate(x)
        if score<MIN_RANK:continue
        x["heuristic_score"]=score;x["matched_terms"]=matched
        x["status"]="NEEDS_HUMAN_REVIEW"
        novel.append(x)
    novel.sort(key=lambda a:(-a["heuristic_score"],-len(a["query_groups"]),-(a.get("stars") or 0),a["name"]))
    result={"status":"PASS" if not errors else "PARTIAL","timestamp_utc":datetime.now(timezone.utc).isoformat(),
        "inventory_version":inventory["revision"],"inventory_count":len(inventory["candidates"]),
        "github_repo_count":len(known),"queries":query_details,"query_errors":errors,
        "unique_hits":len(encountered),"new_review_candidates":len(novel),
        "potential_repositories":novel,"unreviewed":True,
        "limits":["GitHub search is not exhaustive and can be incomplete or rate limited.",
                  "Heuristic text score is NOT a correctness, quality, novelty or license verdict.",
                  "Novel repo names must be inspected and deduplicated before entering validated inventory.",
                  "Unreviewed candidates cannot close the Phase-2 exhaustion gate."]}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"status":result["status"],"inventory":result["inventory_count"],
        "unique_hits":result["unique_hits"],"new_review_candidates":len(novel),
        "errors":errors,"top_new":novel[:15]},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
