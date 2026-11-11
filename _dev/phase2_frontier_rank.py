"""Evidence-aware frontier ranking for candidates C144..C226 (Phase 2, R15).

These are RESEARCH PRIORITIES, not functional winners. Does not change the
143-candidate tested baseline nor depend on LLM/model APIs.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from datetime import datetime,timezone
import json
from pathlib import Path
import re

CONFRONTS=[
 ("hybrid_parquet","C206","C035","Same 40k->2M messages, keyword+vector+SQL, chunk updates, file size, p95 and RAM"),
 ("temporal_state","C146","C001","Branch/recovery as-of, time of observation vs validity, no loss of original message"),
 ("temporal_state","C163","C001","XTDB system-time vs valid-time revisions and Java runtime footprint"),
 ("temporal_state","C147","C065","TerminusDB branches, merges, typed relations with evidence and license"),
 ("graph_sqlite","C216","C065","sqlite-graph recursive SQLite edges vs RDFLib on typed source-cited paths"),
 ("graph_sqlite","C144","C065","LadybugDB graph traversal/FTS/vector vs SQLite evidence-first prototype"),
 ("graph_sqlite","C145","C065","HelixDB graph+hybrid versus same normalized 40k messages"),
 ("graph_sqlite","C152","C065","CozoDB Datalog multi-hop joins and memory/platform maturity"),
 ("browser_capture","C217","C118","Threadline browser branches vs CTK exported ChatGPT trees"),
 ("browser_capture","C218","C118","Personal AI Memory capture+recency vs CTK lossless export"),
 ("android_hybrid","C220","C028","Kalan DB Android real ARM64 on synthetic 40k vs SQLite FTS5/sqlite-vec"),
 ("temporal_retrieval","C219","C118","Threadback browser semantic/keyword against CTK branches and provenance"),
 ("lineage","C214","C118","OpenLineage event model for source->adapter->normalization->index receipts"),
 ("substring","C213","C002","Zoekt positional trigram vs FTS5 trigram: regex and partial terms"),
 ("browser_static","C212","C010","Pagefind chunk index vs MiniSearch at 40k results and offline read-only"),
 ("event_log","C209","C001","LiveStore event-log replay vs SQLite existing importer idempotence"),
 ("versioned_sql","C147","C001","Dolt SQL branch/merge/rollback vs SQLite snapshot and repair ledger"),
]
# exact source URLs and IDs, never fabricate results or inferred readiness.
PREFERRED=("C206","C146","C163","C147","C216","C144","C145","C149","C152",
 "C217","C218","C220","C214","C209","C208","C212","C213","C219")
CODE_RE=re.compile(r"^https://github\.com/([^/]+)/([^/?#]+)",re.I)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--inventory",required=True)
    ap.add_argument("--audit",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    obj=json.loads(Path(args.inventory).read_text(encoding="utf-8"))
    audit=json.loads(Path(args.audit).read_text(encoding="utf-8"))
    allrows=obj["candidates"]
    assert obj["total"]==226 and len(allrows)==226
    assert [c["id"] for c in allrows]==[f"C{i:03d}" for i in range(1,227)]
    urls=[c["url"].rstrip("/").lower() for c in allrows]
    assert len(set(urls))==226, "duplicate source URL"
    assert audit["inventory_candidate_count"]==226, "audited wrong inventory"
    map_repo={x["repository"].lower():x for x in audit.get("repositories",[])}
    rows=[]
    for c in allrows[143:]:
        m=CODE_RE.match(c["url"])
        repo=(m.group(1)+"/"+m.group(2).removesuffix(".git")).lower() if m else None
        upstream=map_repo.get(repo)
        status=(upstream or {}).get("status","EXTERNAL_ONLY" if not repo else "UNAVAILABLE")
        license_id=(upstream or {}).get("license_spdx")
        legal="REVIEW_BEFORE_ADOPTION" if license_id in (None,"NOASSERTION","UNIDENTIFIED","GPL-2.0","GPL-3.0","AGPL-3.0","SSPL-1.0","BUSL-1.1") else "PACKAGE_AND_TRANSITIVE_REVIEW"
        if (upstream or {}).get("archived"):
            state="ARCHIVED_REFERENCE"
        elif repo and status!="FOUND":
            state="UPSTREAM_ACCESS_PENDING"
        elif c.get("priority")=="P0":
            state="PRIORITY_HEAD_TO_HEAD"
        else:state="BACKLOG_RESEARCH"
        rows.append({
            "id":c["id"],"name":c["name"],"url":c["url"],
            "source_revision":c.get("discovery_source"),
            "family":c["family"],"priority":c.get("priority","P2"),
            "approach":c.get("approach") or c.get("reason"),
            "storage_mechanism":c.get("storage_mechanism"),
            "retrieval_mechanism":c.get("retrieval_mechanism") or c.get("search_or_connection_approach"),
            "functional_status":"NOT_TESTED",
            "state":state,"license_gate":legal,"license_spdx":license_id,
            "upstream_state":status,"archived":(upstream or {}).get("archived"),
            "proposed_gate":c.get("proposed_gate"),
            "comparative_rank":None,
            "risk":"No independent functional result; source statements only",
        })
    assert len(rows)==83
    priority={"P0":0,"P1":1,"P2":2,"P3":3}
    pref={x:i for i,x in enumerate(PREFERRED)}
    rows.sort(key=lambda x:(priority.get(x["priority"],3),pref.get(x["id"],1000),x["id"]))
    for i,x in enumerate(rows,1):x["comparative_rank"]=i
    by_id={x["id"]:x for x in rows}
    old_ids={c["id"] for c in allrows[:143]}
    scheduled=[]
    for n,(port,new,baseline,contract) in enumerate(CONFRONTS,1):
        assert new in by_id
        assert baseline in old_ids or baseline in by_id
        scheduled.append({"order":n,"port":port,"new_candidate":new,
            "candidate":by_id[new]["name"],"baseline":baseline,
            "contract_gate":contract,"state":"NOT_TESTED",
            "priority":by_id[new]["priority"],"replace_core_approved":False})
    counts=Counter(x["priority"] for x in rows)
    result={
        "revision":"R15","status":"PASS","generated_utc":datetime.now(timezone.utc).isoformat(),
        "total_universe":226,"vetted_baseline_unchanged":143,
        "new_research_candidates":83,
        "new_this_survey":19,
        "ranking_semantics":"engineering test order, not market quality or proven performance",
        "policy":{"not_tested_are_not_failures":True,"no_p0_means_adoption":True,
         "requires_human_first_no_llm":True,
         "requires_same_dataset_legal_and_runtime_contract":True,
         "phase3_ux_unchanged":True},
        "summary":{"priority_counts":dict(counts),
           "relevant_approaches":len(set(x["retrieval_mechanism"] for x in rows)),
           "repo_count_audited":audit["audited_count"],
           "github_count_in_universe":audit["github_unique_count"],
           "upstream_unavailable":sum(x["upstream_state"] in ("UNAVAILABLE","HTTP_ERROR","ERROR") for x in rows),
           "archived":sum(x["state"]=="ARCHIVED_REFERENCE" for x in rows),
           "planned_head_to_heads":len(scheduled),
           "all_83_have_disposition":all(x["state"] for x in rows)},
        "frontier":rows,"planned_confrontations":scheduled,
        "baselines":{
          "search":"C001 SQLite FTS5 current product core",
          "full_tree_ingest":"C118 CTK measured import/branch fidelity, NOT integrated",
          "graph":"C065 RDFLib pass for explicit relation serialization only",
          "vector":"C028 sqlite-vec optional candidate",
          "browser":"C010 MiniSearch/C011 FlexSearch previously tested in Node only",
        },
        "limitations":[
          "This new 83-candidate frontier has not been functionally tested.",
          "The R13 ranking of previously tested 143 remains independently valid.",
          "Vendor-specific source/README descriptions do not establish feature correctness.",
          "GitHub license SPDX is not a legal compliance opinion, and weights/editions may differ.",
          "Rank comparisons across different functional ports are not empirical speed scores.",
        ],
    }
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# Cha2db — Fronteira de pesquisa R15", "",
      f"Gerado (UTC): {result['generated_utc']}", "",
      "**226 candidatos únicos** — 143 baseline previamente triados, 64 do primeiro levantamento de fronteira e 19 novos não duplicados.",
      "",
      "**Apenas prioridade de testes, não ranking de qualidade e NÃO homologação.** O ranking R13 dos 143 permanece separado.",
      "",
      "## Ranking de confronto da fronteira", "",
      "| Ordem | ID | Produto | Prioridade | Forma de armazenamento | Mecanismo de consulta |",
      "| ---: | --- | --- | --- | --- | --- |"]
    for x in rows:
        storage=str(x["storage_mechanism"] or "não verificado").replace("|","/")
        query=str(x["retrieval_mechanism"] or "não verificado").replace("|","/")
        lines.append(f"| {x['comparative_rank']} | {x['id']} | [{x['name']}]({x['url']}) | {x['priority']} | {storage} | {query} |")
    lines.extend(["","## Próximos confrontos definidos","",
                  "| Ordem | Portabilidade / capacidade | Desafiante | Baseline | Gate |",
                  "| ---: | --- | --- | --- | --- |"])
    for x in scheduled:
        lines.append(f"| {x['order']} | {x['port']} | {x['candidate']} | {x['baseline']} | {x['contract_gate']} |")
    lines+=["","## Fronteiras de responsabilidade","",
       "A Fase 2 só avalia bibliotecas, contratos e dados. Fase 3/UX continua independente.",
       "Nenhum dos 83 candidatos foi instalado ou integrado no núcleo por esta varredura.",
       "Saturação de mercado não comprovada: a pesquisa deve prosseguir até ciclos sem novas abordagens capazes de alterar uma porta.",
       ""]
    out.with_suffix(".md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({"status":"PASS","counts":result["summary"],
      "top_frontier":[{"id":x["id"],"name":x["name"],"priority":x["priority"]} for x in rows[:12]]},
      ensure_ascii=False,indent=2))
if __name__=="__main__":main()
