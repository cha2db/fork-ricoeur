"""Product-016 autonomous test: 12 fronts, 71 ports, no invented adoption status.

Uses actual Phase-2 R10 (and R14 when present) and UX 46 baseline.
Does not test third-party programs, install packages, mutate the database or use
personal content. PR merged checkout MUST include R14 full inventory.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"product_lab"))
from rank import canonical_url, generate, markdown

result=generate()
checks=0
def gate(cond,label):
    global checks
    assert cond,label
    checks+=1

gate(result["schema_version"]=="cha2db.product.fronts.v1","schema")
gate(result["front_count"]==12,"12 new product fronts")
gate(result["candidate_count"]==71,"71 candidates")
gate(result["source_coverage"]["phase2_r10"]["candidate_count"]==143,"phase2 baseline 143")
gate(result["source_coverage"]["ux"]["candidate_count"]==46,"UX baseline 46")
if result["source_coverage"]["phase2_r14"]["present"]:
    gate(result["source_coverage"]["phase2_r14"]["candidate_count"]==64,"R14 +64")
if os.getenv("GITHUB_EVENT_NAME")=="pull_request":
    gate(result["source_coverage"]["phase2_r14"]["present"],
         "PR checkout must reconcile FULL 207 Phase2 candidates")
gate(result["new_to_existing_inventories"]+result["overlapping_existing_inventories"]==71,
     "cross-reference accounting")
gate(result["front_ranking"]==sorted(result["front_ranking"],
       key=lambda x:(-x["priority_preliminary"],x["id"])),"front ranking order")
gate(sum(x["candidate_count"] for x in result["front_ranking"])==71,"candidate count complete")
gate(all(f["candidates"]==sorted(f["candidates"],
       key=lambda x:(-x["priority_preliminary"],x["id"]))
       for f in result["front_ranking"]),"per-front ranking deterministic")
gate(all(0<=f["priority_preliminary"]<=100 and
         all(0<=c["priority_preliminary"]<=100 for c in f["candidates"])
         for f in result["front_ranking"]),"bounded scores")
gate(all(c["functional_verdict"]=="NOT_TESTED" and
         c["adoption_status"]=="RESEARCH_ONLY" and
         c["license_verdict"]=="VERIFY_COMPONENT_LICENSE"
         for f in result["front_ranking"] for c in f["candidates"]),"no false approvals")
gate(all(c["next_gate"] and c["subport"] and c["url"].startswith("https://")
         for f in result["front_ranking"] for c in f["candidates"]),"actionable gates")
gate("phase2_r10" in {s["survey"] for f in result["front_ranking"] for c in f["candidates"]
     for s in c["seen_elsewhere"]},"Phase2 cross-reference effective")
gate("ux" in {s["survey"] for f in result["front_ranking"] for c in f["candidates"]
     for s in c["seen_elsewhere"]} or
     result["overlapping_existing_inventories"]>0,
     "cross-reference repeated study marked")
gate(canonical_url("https://github.com/OpenRefine/OpenRefine/")==
     canonical_url("https://github.com/openrefine/openrefine#readme"),"canonical GitHub URLs")
gate(canonical_url("https://github.com/simonw/sqlite-utils/tree/main")==
     canonical_url("https://github.com/simonw/sqlite-utils"),"file path normalization")
gate("R14" in markdown(result) or result["source_coverage"]["phase2_r14"]["present"],
     "coverage markdown legible")
first=next(c for f in result["front_ranking"] for c in f["candidates"] if c["id"]=="OPS012")
gate(first["subport"]=="db_recovery" and first["functional_verdict"]=="NOT_TESTED",
     "repair not falsely adopted")
with tempfile.TemporaryDirectory() as temp:
    src=json.loads((ROOT/"product_lab/fronts.json").read_text())
    src["fronts"][1]["candidates"][0]["id"]=src["fronts"][0]["candidates"][0]["id"]
    p=Path(temp)/"invalid.json";p.write_text(json.dumps(src))
    try:generate(manifest=p)
    except ValueError as exc:gate("duplicate" in str(exc),"reject duplicate candidate id")
    else:raise AssertionError("duplicate allowed")
    src=json.loads((ROOT/"product_lab/fronts.json").read_text())
    src["fronts"][0]["candidates"][0]["adoption_status"]="ADOPTED"
    p.write_text(json.dumps(src))
    try:generate(manifest=p)
    except ValueError as exc:gate("adoption" in str(exc),"reject unsupported adoption claim")
    else:raise AssertionError("false adoption allowed")

gate(result==generate(),"deterministic rerun")
print(f"PASS PRODUCT-016: {checks} gates, 12 fronts, 71 hypotheses, "
      f"{result['new_to_existing_inventories']} inventory-new; "
      f"{result['overlapping_existing_inventories']} prior-survey overlaps; "
      f"Phase2 R14={'present' if result['source_coverage']['phase2_r14']['present'] else 'absent on source branch'}")
