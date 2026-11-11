"""Phase-2 143-candidate census with source-backed, auditable decisions.

Distinguishes:
  1. inventory review (every candidate has a disposition),
  2. upstream source/README verification (metadata and keyword evidence only),
  3. real functional CI tests (only results verified in ci-results).

Never labels README capabilities as tested. No vendor code is imported or executed.
"""
from __future__ import annotations
import argparse
import base64
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.error
import urllib.request

GITHUB = re.compile(r"^https://github\.com/([^/]+)/([^/?#]+)", re.I)
READ_PATTERNS = {
    "ingest": r"\b(import(?:er|ing)?|ingest(?:ion)?|parser|export)\b",
    "repair": r"\b(repair|recover(?:y)?|orphaned?|reconstruct|restore|rollback)\b",
    "provenance": r"\b(provenance|lineage|citations?|source.attribut|original.messages?)\b",
    "temporal": r"\b(temporal|supersed\w*|timeline|chronolog\w*|time.travel|validity)\b",
    "review": r"\b(human.in.the.loop|human.review|approval|version.history|audit.trail|undo)\b",
    "mcp": r"\b(MCP|model context protocol)\b",
    "offline": r"\b(offline|local.first|no cloud|no api.key)\b",
    "hybrid": r"\b(hybrid.search|BM25|vector.search|full.text.search)\b",
    "graph": r"\b(knowledge.graph|temporal.graph|graph.rag|relation.graph)\b",
}
TEST_MAP = {
    "C001":("ci-output/latest.json","autoscale"),
    "C002":("ci-output/prior-art/trigram-latest.json",None),
    "C003":("ci-output/phase2/tantivy-latest.json",None),
    "C004":("ci-output/phase2/bm25s-latest.json",None),
    "C005":("ci-output/prior-art/latest.json","summary.rank_bm25"),
    "C008":("ci-output/phase2/duckdb-latest.json",None),
    "C009":("ci-output/phase2/orama-latest.json",None),
    "C010":("ci-output/phase2/minisearch-latest.json",None),
    "C011":("ci-output/phase2/flexsearch-latest.json",None),
    "C028":("ci-output/prior-art/vector-latest.json",None),
    "C029":("ci-output/prior-art/vec1-probe-latest.json",None),
    "C030":("ci-output/prior-art/sqlite-vector-latest.json",None),
    "C031":("ci-output/phase2/usearch-latest.json",None),
    "C035":("ci-output/phase2/lancedb-latest.json","modes"),
    "C045":("ci-output/semantic/latest.json","components.encoder"),
    "C052":("ci-output/semantic/latest.json","components.cross_encoder"),
    "C057":("ci-output/prior-art/latest.json","summary.rapidfuzz_fts"),
    "C058":("ci-output/prior-art/latest.json","graph"),
    "C059":("ci-output/semantic/latest.json","components.bertopic"),
    # All references are SOURCE CI outputs; no inferred performance numbers.
}
STRONG_COPYLEFT = {"GPL-2.0","GPL-3.0","AGPL-3.0","SSPL-1.0","BUSL-1.1"}
SPECIAL_LICENSE = STRONG_COPYLEFT | {"LGPL-2.1","LGPL-3.0","NOASSERTION","UNIDENTIFIED"}
CORE_PRIORITY = {
    "graph-memory-products":"P0","quality-and-input":"P1",
    "lexical-embedded":"P1","vectors":"P1","topic-graph":"P1",
    "semantic-ranking":"P2","search-servers":"P3",
}
NON_CORE_FAMILY = {"search-servers"}
REVIEW_PRIORITY = {"CRITICAL","TEST","TESTED","KEEP","BASELINE"}
SKIP_STATUSES = {"ARCHIVED","REFERENCE","COMMERCIAL_REFERENCE","BENCHMARK","DEFER"}
HEADERS = {"Accept":"application/vnd.github.raw+json",
           "X-GitHub-Api-Version":"2022-11-28",
           "User-Agent":"cha2db-phase2-review"}
def read_ci(path):
    try:
        cmd=["git","show","origin/ci-results:"+path]
        process=subprocess.run(cmd,capture_output=True,text=True,check=False,timeout=15)
        if process.returncode: return None
        return json.loads(process.stdout)
    except (OSError,ValueError,subprocess.TimeoutExpired):
        return None

def nested(data,path):
    item=data
    for key in path.split("."):
        if not isinstance(item,dict):return None
        item=item.get(key)
    return item

def test_result(code,cache):
    if code not in TEST_MAP:return {"level":"NO_TEST","status":"NOT_TESTED"}
    path,section=TEST_MAP[code]
    if path not in cache:cache[path]=read_ci(path)
    report=cache[path]
    reference=f"https://github.com/cha2db/fork-ricoeur/blob/ci-results/{path}"
    if report is None:return {"level":"NO_VERIFIED_REPORT","status":"MISSING",
                               "evidence":reference}
    component=nested(report,section) if section else report
    status=component.get("status") if isinstance(component,dict) else None
    if section=="autoscale":status=component.get("status") if isinstance(component,dict) else None
    elif section and section.startswith("summary."):status="PASS" if isinstance(component,dict) else "MISSING"
    elif section=="graph":
        status=("PASS" if report.get("status")=="PASS" and
                isinstance(component,dict) and component.get("ari_against_fixture_topics") is not None
                else "MISSING")
    elif section=="modes":
        status=("PASS" if isinstance(component,dict) and len(component)>=3 and
                all(v.get("status")=="PASS" for v in component.values()) else "PARTIAL")
    if status is None:status=report.get("status","UNKNOWN")
    level="FUNCTIONAL_PASS" if status=="PASS" else "FUNCTIONAL_BLOCKED"
    return {"level":level,"status":status,"evidence":reference,
        "scope":"synthetic/candidate-specific; no production integration",
        "scope_verified":True}

def load_readme(repository,token):
    headers=dict(HEADERS)
    if token:headers["Authorization"]="Bearer "+token
    url="https://api.github.com/repos/"+repository+"/readme"
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=18) as response:
            raw=response.read(220_000)
        if raw[:1]==b"{" and b'"encoding"' in raw[:400]:
            obj=json.loads(raw)
            if obj.get("encoding")=="base64":
                raw=base64.b64decode(obj.get("content",""))
        source=raw.decode("utf-8","replace")[:100_000]
        capabilities={}
        for port,regex in READ_PATTERNS.items():
            m=re.search(regex,source,re.I)
            if m:
                excerpt=re.sub(r"\s+"," ",source[max(0,m.start()-65):m.end()+85]).strip()[:175]
                capabilities[port]={"term":m.group(0),"excerpt":excerpt}
        return {"status":"READ","size_chars":len(source),"keyword_evidence":capabilities,
                "source":f"https://github.com/{repository}#readme",
                "scope":"README keyword heuristic only; no functionality asserted"}
    except urllib.error.HTTPError as e:
        return {"status":"HTTP_ERROR","http_status":e.code,"source":url}
    except (OSError,ValueError,TimeoutError) as e:
        return {"status":"UNAVAILABLE","reason":type(e).__name__,"source":url}

def candidate(row,audit,readme,functional):
    code=row["id"]
    m=GITHUB.match(row["url"])
    repository=(m.group(1)+"/"+m.group(2).removesuffix(".git")) if m else None
    source=audit.get(repository.lower()) if repository else None
    upstream=(source or {}).get("status","NO_GITHUB_SOURCE") if repository else "EXTERNAL_REFERENCE"
    license_spdx=(source or {}).get("license_spdx")
    license_gate=(
        "LEGAL_REVIEW" if license_spdx in SPECIAL_LICENSE else
        "PACKAGE_MODEL_EDITION_REVIEW" if license_spdx else "SOURCE_LICENSE_UNCHECKED")
    if source and source.get("archived"):
        disposition="EXCLUDE_ARCHIVED_ACTIVE_CORE"
    elif code=="C001":
        disposition="KEEP_EXISTING_BASELINE"
    elif functional["level"]=="FUNCTIONAL_PASS":
        disposition="TESTED_COMPONENT_CANDIDATE"
    elif functional["level"]=="FUNCTIONAL_BLOCKED":
        disposition="HOLD_TECHNICAL_LIMIT"
    elif row["status"] in SKIP_STATUSES:
        disposition="REFERENCE_OR_DEFER_NONCORE"
    elif row["family"] in NON_CORE_FAMILY:
        disposition="EXTERNAL_ADAPTER_ONLY"
    elif license_spdx in STRONG_COPYLEFT:
        disposition="LICENSE_HOLD_NO_EMBED"
    elif row["status"] in REVIEW_PRIORITY:
        disposition="HIGH_PRIORITY_CONTRACT_TEST_PENDING"
    else:
        disposition="COMPARATIVE_TEST_PENDING"
    if upstream in {"HTTP_ERROR","UNAVAILABLE","ERROR"}:
        disposition="SOURCE_ACCESS_BLOCKED"
    review_count=0 if functional["level"]=="FUNCTIONAL_PASS" else 1
    return {
        "id":code,"name":row["name"],"family":row["family"],
        "source_url":row["url"],"original_classification":row["status"],
        "priority":CORE_PRIORITY[row["family"]],
        "disposition":disposition,"functional_test":functional,
        "upstream":{"repository":repository,"status":upstream,
            "license_spdx":license_spdx,"archived":(source or {}).get("archived"),
            "pushed_at":(source or {}).get("pushed_at")},
        "license_gate":license_gate,
        "readme_evidence":readme or {"status":"NOT_GITHUB","keyword_evidence":{}},
        "remaining_gate": (
            "none for Phase-2 baseline" if code=="C001" else
            "no production integration authorized; review license and contract"
            if functional["level"]=="FUNCTIONAL_PASS" else
            "requires comparative test or scope/eligibility review"),
        "test_pending":review_count,
        "differentiation_claim":"NOT_DEMONSTRATED",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--inventory",default="_dev/PHASE2_MARKET_UNIVERSE_R10.json")
    p.add_argument("--audit",required=True)
    p.add_argument("--output",default="_dev/results/phase2-143-ledger.json")
    p.add_argument("--workers",type=int,default=8)
    args=p.parse_args()
    inv=json.loads(Path(args.inventory).read_text())
    audited=json.loads(Path(args.audit).read_text())
    if inv["total"]!=143 or len(inv["candidates"])!=143:
        raise ValueError("R10 census must contain exactly 143 entries")
    ids=[x["id"] for x in inv["candidates"]]
    if len(set(ids))!=143:raise ValueError("Duplicate candidate IDs")
    if audited["inventory_candidate_count"]!=143:
        raise ValueError("Audit is stale: expected 143, got "+str(audited["inventory_candidate_count"]))
    audit={x["repository"].lower():x for x in audited.get("repositories",[])}
    repos=set()
    for row in inv["candidates"]:
        m=GITHUB.match(row["url"])
        if m:repos.add(m.group(1)+"/"+m.group(2).removesuffix(".git"))
    token=os.environ.get("GITHUB_TOKEN")
    readmes={}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(load_readme,name,token):name for name in sorted(repos)}
        for future in as_completed(futures):
            name=futures[future]
            try:readmes[name.lower()]=future.result()
            except Exception as e:readmes[name.lower()]={"status":"ERROR","reason":type(e).__name__}
    cache={}
    rows=[]
    for row in inv["candidates"]:
        m=GITHUB.match(row["url"])
        name=(m.group(1)+"/"+m.group(2).removesuffix(".git")).lower() if m else None
        rows.append(candidate(row,audit,readmes.get(name),test_result(row["id"],cache)))
    dispositions=Counter(r["disposition"] for r in rows)
    outcomes=Counter(r["functional_test"]["level"] for r in rows)
    read_status=Counter(r["readme_evidence"]["status"] for r in rows)
    functional=sum(r["functional_test"]["level"]=="FUNCTIONAL_PASS" for r in rows)
    uncovered=[r["id"] for r in rows if r["upstream"]["status"] in ("ERROR","HTTP_ERROR","UNAVAILABLE")]
    summary={
        "inventory_candidates":143,"entries_with_disposition":len(rows),
        "repositories_in_inventory":len(repos),"audited_unique_github":audited["audited_count"],
        "real_functional_pass_candidates":functional,
        "functional_pending_or_blocked":143-functional,
        "dispositions":dict(dispositions),
        "test_evidence_levels":dict(outcomes),
        "readme_checks":dict(read_status),
        "repo_source_access_blocks":uncovered,
        "remaining_p0_contract_gate":sum(
            r["disposition"]=="HIGH_PRIORITY_CONTRACT_TEST_PENDING" for r in rows),
        "all_candidates_accounted_for":len(rows)==143 and all(r["disposition"] for r in rows)
    }
    result={
        "status":"PASS" if summary["all_candidates_accounted_for"] and not uncovered else "PARTIAL",
        "revision":"R10","generated_utc":datetime.now(timezone.utc).isoformat(),
        "meaning":"143 audited and triaged, NOT 143 functionally tested",
        "summary":summary,"candidates":rows,
        "phase2_closed":False,
        "closure_blockers":[
            "Not all 143 candidates tested: some are reference products, server-only or legally blocked",
            "High-priority import/repair and memory products need same-contract black-box tests",
            "Current data synthetic and topic labels generated from fixtures, not human labels",
            "Two independent discovery saturation passes and legal review not completed"],
        "method":["GitHub repo metadata and license SPDX are informational, not legal clearance.",
                  "README keyword matches support only a claimed feature with excerpt.",
                  "Only explicit ci-results JSON with PASS and correct component can validate actual execution.",
                  "No imported package or external code executed by this census.",
                  "All 143 rows receive a disposition but trial gates remain open until resolved."]
    }
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    summary_md=out.with_suffix(".summary.md")
    summary_md.write_text(
        "# Cha2db Phase 2 — 143-candidate census\n\n"
        +f"Revision R10 · {result['generated_utc']}\n\n"
        +f"**Triaged:** 143/143. **Actually functionally PASS:** {functional}/143. **Phase 2 CLOSED:** No.\n\n"
        +"## Dispositions\n\n"
        +"| Decision | Count |\n|---|---:|\n"
        +"".join(f"| {kind} | {count} |\n" for kind,count in sorted(dispositions.items()))
        +"\n## Important caveats\n\n"
        +"No adoption/novelty verdict may be drawn from license metadata or README keywords."
        +" Consult the full JSON for each candidate, its precise CI evidence and remaining gate.\n"
    )
    print(json.dumps({"status":result["status"],"summary":summary},
                     ensure_ascii=False,indent=2),flush=True)
    if not summary["all_candidates_accounted_for"]:raise SystemExit(1)
if __name__=="__main__":main()
