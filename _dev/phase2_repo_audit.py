"""Read-only GitHub repository audit for Phase-2 prior-art universe.

This is metadata triage, NOT a license compliance certificate or a functional test.
Uses GitHub Actions token for public API rate quota; never prints credentials.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,os,re,time,urllib.error,urllib.parse,urllib.request
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

GITHUB=re.compile(r"^https://github\.com/([^/]+)/([^/?#]+)")
COPyleft={"GPL-2.0","GPL-3.0","AGPL-3.0","SSPL-1.0","BUSL-1.1","LGPL-2.1","LGPL-3.0"}
def fetch(name,token):
    url="https://api.github.com/repos/"+name
    headers={"Accept":"application/vnd.github+json","User-Agent":"cha2db-phase2-audit",
             "X-GitHub-Api-Version":"2022-11-28"}
    if token:headers["Authorization"]="Bearer "+token
    for attempt in range(2):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=15) as resp:
                data=json.loads(resp.read())
            lic=(data.get("license") or {}).get("spdx_id","UNIDENTIFIED")
            return {"repository":name,"status":"FOUND",
                 "full_name":data.get("full_name"),"archived":data.get("archived"),
                 "disabled":data.get("disabled"),"private":data.get("private"),
                 "fork":data.get("fork"),"pushed_at":data.get("pushed_at"),
                 "default_branch":data.get("default_branch"),"license_spdx":lic,
                 "license_review":lic in COPyleft or lic in ("NOASSERTION","UNIDENTIFIED"),
                 "homepage":data.get("homepage")}
        except urllib.error.HTTPError as error:
            if error.code==429 or (error.code==403 and attempt==0):
                time.sleep(2);continue
            return {"repository":name,"status":"HTTP_ERROR","http_status":error.code}
        except (TimeoutError,OSError,ValueError) as error:
            if attempt==0:time.sleep(.5);continue
            return {"repository":name,"status":"UNAVAILABLE","error":type(error).__name__}
    return {"repository":name,"status":"UNAVAILABLE"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--inventory",default="_dev/PHASE2_MARKET_UNIVERSE_R05.json")
    ap.add_argument("--output",default="_dev/results/phase2-repo-audit.json")
    a=ap.parse_args()
    src=json.loads(Path(a.inventory).read_text())
    entries=src["candidates"]
    names={}
    for c in entries:
        m=GITHUB.match(c["url"])
        if m:
            name=m.group(1)+"/"+m.group(2).removesuffix(".git")
            names.setdefault(name,[]).append(c["id"])
    token=os.environ.get("GITHUB_TOKEN")
    audited={}
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures={pool.submit(fetch,name,token):name for name in names}
        for future in as_completed(futures):
            name=futures[future]
            try:audited[name]=future.result()
            except Exception as error:audited[name]={"repository":name,"status":"ERROR","error":type(error).__name__}
    matches={}
    for name,cids in names.items():
        for cid in cids:matches[cid]=audited[name]
    summary=Counter(x["status"] for x in audited.values())
    archived=[x["repository"] for x in audited.values() if x.get("archived")]
    license_review=[{"repository":x["repository"],"spdx":x.get("license_spdx")}
        for x in audited.values() if x.get("status")=="FOUND" and x.get("license_review")]
    report={"status":"PASS" if all(x.get("status")=="FOUND" for x in audited.values()) else "PARTIAL",
        "timestamp_utc":datetime.now(timezone.utc).isoformat(),
        "inventory_candidate_count":len(entries),"github_unique_count":len(names),
        "audited_count":len(audited),"counts":dict(summary),
        "archived_repositories":sorted(archived),
        "requires_license_review":sorted(license_review,key=lambda x:x["repository"]),
        "repositories":[audited[name] for name in sorted(audited)],
        "candidate_id_to_repository":{cid:v["repository"] for cid,v in matches.items()},
        "limits":["Metadata only; a GitHub license identifier does not certify legal compatibility.",
                  "Package, model-weight, component and commercial edition licenses may differ.",
                  "Projects without a github.com owner/repo URL were not audited.",
                  "Archived status, recency and SPDX can change after this snapshot."]}
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k not in ("repositories","candidate_id_to_repository")},
                     ensure_ascii=False,indent=2))
if __name__=="__main__":main()
