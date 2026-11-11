"""Deterministic, evidence-bound ranking for the 143 Cha2db Phase-2 candidates.

Ranks are *order of comparison* within a replaceable capability/port, NOT
universal product-quality scores. No cross-language latency ordering and no
claim of production integration. Produces a reproducible JSON and Markdown
snapshot, reading only the signed GitHub ci-results checked out by CI.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path

from phase2_143_ledger import TEST_MAP, test_result

PORTS = {
    "ingest_tree": "Entrada, origem e árvore de conversas",
    "repair_merge": "Repair, deduplicação e reconstrução",
    "lexical_core": "Busca textual embutida no núcleo",
    "browser_index": "Busca JS local para clientes e Edge",
    "vector_index": "Índices vetoriais opcionais",
    "semantic_ranking": "Busca semântica, fuzzy e reranking",
    "topic_relations": "Tópicos, relações e grafos auditáveis",
    "memory_temporal": "Memória, decisões e validade temporal",
    "relevance_evaluation": "Métricas, datasets e controle de qualidade",
    "search_service": "Servidores e adapters remotos de busca",
    "external_reference": "Referências comerciais e tecnológicas",
}
FAMILY_PORT = {
    "lexical-embedded":"lexical_core",
    "search-servers":"search_service",
    "vectors":"vector_index",
    "semantic-ranking":"semantic_ranking",
    "topic-graph":"topic_relations",
    "graph-memory-products":"memory_temporal",
    "quality-and-input":"relevance_evaluation",
}
SPECIAL_PORT = {
    "browser_index": ("C009","C010","C011"),
    "repair_merge": ("C097","C098","C117","C127","C143"),
    "ingest_tree": ("C101","C108","C111","C112","C113","C115","C116","C118",
                    "C119","C120","C121","C122","C123","C126","C128",
                    "C129","C130","C131","C132","C133","C134","C135","C139"),
    "external_reference": ("C026","C027","C079","C124","C125"),
    "search_service": ("C104",),
}
# Explicit engineering priority based on replaceability, dependencies, and the
# human-first / local-first / zero-mandatory-LLM goals. It is NOT scientific
# measured superiority, only the deterministic tie-breaker for test order.
PREFERRED = {
    "ingest_tree":["C118","C115","C116","C135","C113","C119","C111",
                   "C128","C101","C112"],
    "repair_merge":["C143","C117","C097","C098","C127"],
    "lexical_core":["C001","C003","C004","C002","C005","C102","C103",
                    "C008","C006","C007"],
    "browser_index":["C011","C010","C009"],
    "vector_index":["C028","C035","C031","C032","C034","C029","C030",
                    "C033","C036"],
    "semantic_ranking":["C057","C045","C052","C046","C053","C047",
                        "C048","C049","C050","C051"],
    "topic_relations":["C065","C058","C138","C059","C060","C063","C064",
                       "C061","C066","C067"],
    "memory_temporal":["C114","C072","C142","C141","C073","C074",
                       "C137","C075","C076","C136","C077"],
    "relevance_evaluation":["C090","C091","C092","C093","C095","C096",
                            "C099","C100","C094"],
    "search_service":["C014","C015","C018","C016","C021","C019","C020",
                      "C017","C022","C023"],
    "external_reference":["C108","C124","C125","C026","C027"],
}
# This is a decision queue of head-to-head contracts, not merely a list of
# additional libraries to install. Each fight must be fair and controlled.
BATTLES = [
    ("ingest_tree","C118","C115","All branches, IDs, raw input hashes, repeated imports and missing nodes"),
    ("ingest_tree","C118","C116","Multi-provider import, incremental cursor, cross-platform packaging"),
    ("repair_merge","C118","C143","Truncated/duplicated sessions, dry-run repair, rollback and provenance"),
    ("ingest_tree","C118","C135","ChatGPT regenerated responses, browser capture fidelity and original history"),
    ("ingest_tree","C118","C113","Normalized interchange, stable IDs, idempotent imports and MCP read-only"),
    ("memory_temporal",None,"C114","Human approval, time validity, decision citation and scope without cloud"),
    ("memory_temporal",None,"C072","Episode/fact provenance and retractions, no mandatory remote LLM"),
    ("topic_relations","C065","C138","Typed relations with source-evidence, no inference as fact"),
    ("lexical_core","C001","C003","Whole 40k and 2M corpora, p95, index update/delete, disk and ARM"),
    ("browser_index","C011","C010","Same tokenizer and query set, serialized index, accent, RAM/browser"),
    ("browser_index","C011","C009","JS hybrid functionality versus legal packaging and offline build"),
    ("vector_index","C028","C035","Same vectors, recall@k, writes, persisted index, CPU/RAM/size"),
    ("semantic_ranking","C045","C046","Human-labeled paraphrase relevance PT/EN, local CPU and model license"),
    ("repair_merge","C143","C117","Repair provenance and rollback; AGPL distribution gate first"),
]
PRIORITY = {"P0":0,"P1":1,"P2":2,"P3":3}
INACTIVE = {
    "REJECT_FAILED_MANDATORY_CONTRACT",
    "HOLD_TECHNICAL_LIMIT",
    "EXCLUDE_ARCHIVED_ACTIVE_CORE",
    "LICENSE_HOLD_NO_EMBED",
    "REFERENCE_OR_DEFER_NONCORE",
}
COPyleft = {"AGPL-3.0","GPL-3.0","GPL-2.0","SSPL-1.0","BUSL-1.1"}

def port_for(item):
    for port, ids in SPECIAL_PORT.items():
        if item["id"] in ids:
            return port
    return FAMILY_PORT.get(item["family"],"external_reference")

def current_test(item, cache):
    previous=item["functional_test"]
    if item["id"] not in TEST_MAP:
        return previous
    refreshed=test_result(item["id"],cache)
    if refreshed["level"]=="NO_VERIFIED_REPORT":
        return previous
    return refreshed

def disposition(item, observed):
    if item["upstream"].get("archived"):
        return "EXCLUDE_ARCHIVED_ACTIVE_CORE"
    spdx=item["upstream"].get("license_spdx")
    if observed.get("status")=="FAIL":
        return "REJECT_FAILED_MANDATORY_CONTRACT"
    if observed.get("level")=="FUNCTIONAL_BLOCKED":
        return "HOLD_TECHNICAL_LIMIT"
    if spdx in COPyleft:
        return "LICENSE_HOLD_NO_EMBED"
    if item["disposition"] in ("REFERENCE_OR_DEFER_NONCORE",
                                "EXTERNAL_ADAPTER_ONLY") and observed.get("status")!="PASS":
        return item["disposition"]
    if item["id"]=="C001":return "KEEP_EXISTING_BASELINE"
    if observed.get("status")=="PASS":return "TESTED_COMPONENT_CANDIDATE"
    return item["disposition"]

def eligibility(item, observed, decision):
    if decision=="KEEP_EXISTING_BASELINE":return "BASELINE"
    if decision in INACTIVE:return "INELIGIBLE_OR_BLOCKED"
    if item["license_gate"] in ("LEGAL_REVIEW","SOURCE_LICENSE_UNCHECKED"):
        return "LICENCE_VERIFY_BEFORE_EMBED"
    if observed.get("status")=="PASS":return "PASS_CANDIDATE"
    return "UNTESTED_CANDIDATE"

def eligible_sort(item):
    state=item["eligibility"]
    # Distinct tiers: known PASS, still-unvalidated, legal uncertainty, blocked.
    tier={"BASELINE":0,"PASS_CANDIDATE":1,"UNTESTED_CANDIDATE":2,
          "LICENCE_VERIFY_BEFORE_EMBED":3,"INELIGIBLE_OR_BLOCKED":4}[state]
    # For the untested group, priority P0 takes precedence, while explicit
    # product ranking breaks ties. No latency cross-benchmark.
    pref=PREFERRED.get(item["port"],[])
    pref_rank=pref.index(item["id"]) if item["id"] in pref else 1000
    if state=="UNTESTED_CANDIDATE":
        return (tier,PRIORITY[item["original_priority"]],pref_rank,item["id"])
    return (tier,pref_rank,PRIORITY[item["original_priority"]],item["id"])

def metric_snapshot(code, cache):
    meta=TEST_MAP.get(code)
    if not meta:return None
    from phase2_143_ledger import read_ci
    path,sub=meta
    if path not in cache:cache[path]=read_ci(path)
    data=cache[path]
    if not isinstance(data,dict):return None
    info={}
    for name in ("median_latency_ms","mean_p10","mean_recall_at10",
                 "build_seconds","index_seconds"):
        if isinstance(data.get(name),(int,float)):
            info[name]=data[name]
    if code=="C035":
        info["modes"]={k:{"status":v.get("status"),
                          "median_latency_ms":v.get("median_latency_ms"),
                          "mean_p10":v.get("mean_p10")}
                       for k,v in data.get("modes",{}).items()}
    if code in ("C101","C112","C118"):
        info["checks"]=data.get("checks") or data.get("tests")
    return info or None

def build(ledger):
    original=ledger["candidates"]
    if len(original)!=143 or len(set(x["id"] for x in original))!=143:
        raise ValueError("Must have 143 unique R10 entries")
    evidence_cache={};metric_cache={};rows=[]
    for item in original:
        test=current_test(item,evidence_cache)
        choice=disposition(item,test)
        rank_item={
            "id":item["id"],"name":item["name"],"family":item["family"],
            "port":port_for(item),
            "original_priority":item["priority"],
            "source_url":item["source_url"],
            "source_disposition":item["disposition"],
            "current_disposition":choice,
            "eligibility":eligibility(item,test,choice),
            "license_spdx":item["upstream"].get("license_spdx"),
            "license_gate":item["license_gate"],
            "functional_level":test["level"],
            "functional_status":test["status"],
            "evidence_url":test.get("evidence"),
            "test_scope":test.get("scope","NOT_TESTED"),
            "metrics":metric_snapshot(item["id"],metric_cache),
            "risk":"not tested on human-labeled real chats, Termux or production pipeline",
        }
        rows.append(rank_item)
    by_port=defaultdict(list)
    for x in rows:by_port[x["port"]].append(x)
    ports={}
    for port in PORTS:
        pool=sorted(by_port[port],key=eligible_sort)
        for n,cand in enumerate(pool,1):
            cand["rank_in_port"]=n
            cand["rank_basis"]="contract readiness, CI result, local-first fit, license gate; NOT raw speed"
        best=next((x["id"] for x in pool if x["eligibility"] in ("BASELINE","PASS_CANDIDATE")),None)
        next_unverified=next((x["id"] for x in pool if x["eligibility"]=="UNTESTED_CANDIDATE"),None)
        ports[port]={"title":PORTS[port],"entries":pool,"best_verified":best,
                     "next_unverified":next_unverified,"candidate_count":len(pool),
                     "warning":"Rank is engineering comparison/adoption priority, not comparable measured product superiority"}
    all_ids=[x["id"] for v in ports.values() for x in v["entries"]]
    if len(all_ids)!=143 or len(set(all_ids))!=143:
        raise ValueError("Each of the 143 entries must appear in exactly one primary port")
    index={x["id"]:x for x in rows}
    battles=[]
    for n,(port,baseline,challenger,gate) in enumerate(BATTLES,1):
        if challenger not in index or (baseline is not None and baseline not in index):
            raise ValueError("Unknown candidate in confrontation queue")
        b=index[challenger]
        base=index.get(baseline)
        needs_legal=b["license_gate"] in ("LEGAL_REVIEW","SOURCE_LICENSE_UNCHECKED") or b["license_spdx"] in COPyleft
        if b["functional_status"]=="FAIL":phase="REJECTED_MANDATORY_CONTRACT"
        elif b["functional_status"]=="PASS" and base and base["functional_status"]=="PASS":
            phase="HEAD_TO_HEAD_PENDING"
        elif b["functional_status"]=="PASS":phase="ADDITIONAL_CONTRACT_PENDING"
        else:phase="CANDIDATE_UNTESTED"
        battles.append({"order":n,"port":port,"baseline":baseline,"baseline_name":base["name"] if base else None,
           "challenger":challenger,"challenger_name":b["name"],"challenger_test":b["functional_status"],
           "challenger_eligibility":b["eligibility"],"license_precheck_required":needs_legal,
           "state":phase,"contract_gate":gate,"no_llm_required":True,
           "owner":"PHASE2_RESEARCH","ux_dependency":"proposed read-only contracts only"})
    summary={
        "entries_ranked":143,
        "functional_pass":sum(x["functional_status"]=="PASS" for x in rows),
        "functional_fail":sum(x["functional_status"]=="FAIL" for x in rows),
        "functional_blocked":sum(x["functional_level"]=="FUNCTIONAL_BLOCKED" for x in rows),
        "ports":len(PORTS),"published_confrontations":len(battles),
        "head_to_head_pending":sum(x["state"]=="HEAD_TO_HEAD_PENDING" for x in battles),
        "only_provisional":True,
    }
    return {
        "revision":"R13","generated_utc":datetime.now(timezone.utc).isoformat(),
        "status":"PASS","phase":2,"scope":"back-end research only; do not change Phase-3 UX",
        "purpose":"who to confront first within each port, based on reproducible evidence",
        "policy":{
            "all_rankings_are_provisional":True,
            "not_global_quality_ranking":True,
            "no_cross_engine_latency_scoring":True,
            "pass_only_means_executed_specific_synthetic_gate":True,
            "not_integrated_in_cha2db":True,
            "human_first_no_mandatory_llm":True,
            "legal_gate_is_not_a_legal_opinion":True,
            "source_of_truth":"ci-results census plus direct current CI evidence",
            "relevance_gold":"NO_HUMAN_LABELLED_DATA_YET"},
        "summary":summary,"ports":ports,"next_confrontations":battles,
        "ux_handoff":{
            "phase3_owner":"parallel UX team; Phase2 may only propose interfaces",
            "safe_backend_reference":"SQLite FTS5 existing core with MCP/REST adapters",
            "mock_import_tree_reference":"CTK verified tree/IDs and sibling branches, not an adopted service",
            "warning":"Avoid implementing candidate engine details in frontend; consume stable adapters",
        },
    }

def markdown(doc):
    ids={x["id"]:x for p in doc["ports"].values() for x in p["entries"]}
    lines=[
        "# Cha2db — Ranking contínuo da Fase 2 (R13)",
        "",
        "Este ranking é de **prioridade de confronto por porta**, não uma classificação universal de qualidade.",
        "**A Fase 3 de UX pertence à sessão paralela; nenhuma alteração de UI é autorizada por esta matriz.**",
        "",
        f"Atualizado (UTC): {doc['generated_utc']}",
        "",
        f"**{doc['summary']['entries_ranked']}/143 candidatos classificados em {doc['summary']['ports']} portas; "
        f"{doc['summary']['functional_pass']} PASS, {doc['summary']['functional_fail']} FAIL e "
        f"{doc['summary']['functional_blocked']} bloqueios técnicos.**",
        "",
        "PASS significa exclusivamente um gate técnico específico em fixture sintética. "
        "Não prova desempenho real, licença apta nem integração no Cha2db.",
        "",
        "## Quem lidera cada porta entre os efetivamente testados",
        "",
        "| Porta | Melhor evidência disponível | Próximo sem teste equivalente |",
        "| --- | --- | --- |",
    ]
    for key,port in doc["ports"].items():
        leader=ids.get(port["best_verified"])
        nextup=ids.get(port["next_unverified"])
        a=(f"{leader['name']} ({leader['id']}, {leader['functional_status']})"
           if leader else "Ninguém homologado nesta porta")
        b=(f"{nextup['name']} ({nextup['id']})" if nextup else "—")
        lines.append(f"| {port['title']} | {a} | {b} |")
    lines+=["","## Ranking por porta (todos os candidatos)",""]
    for key,port in doc["ports"].items():
        lines.extend([f"### {port['title']}", "",
          "| Posição | ID | Candidato | Evidência funcional | Elegibilidade |",
          "| ---: | --- | --- | --- | --- |"])
        for e in port["entries"]:
            lines.append(f"| {e['rank_in_port']} | {e['id']} | {e['name']} | "
                         f"{e['functional_status']} | {e['eligibility']} |")
        lines.append("")
    lines.extend([
        "## Ordem fixa de próximos confrontos",
        "",
        "| Ordem | Porta | Incumbente | Desafiante | Prova exigida | Situação |",
        "| ---: | --- | --- | --- | --- | --- |",
    ])
    for battle in doc["next_confrontations"]:
        base=(battle["baseline_name"] or "Sem solução PASS na porta")
        lines.append(f"| {battle['order']} | {battle['port']} | {base} | "
                     f"{battle['challenger_name']} | {battle['contract_gate']} | "
                     f"{battle['state']} |")
    lines+=["",
      "## Regras de atualização",
      "",
      "A atualização é automática por GitHub Actions após os workflows de comparação e por agenda.",
      "A ordenação não usa a menor latência de fixtures desiguais como escore: exige mesmo corpus, mesmo contrato, p95, memória, persistência, proveniência, estabilidade e custo.",
      "Licenças, pesos de modelo e edições precisam ser verificados antes de embutir código. Sem LLM obrigatória.",
      "O arquivo JSON contém os **143 IDs**, evidências pontuais, licença, ranking por porta e agenda de confrontos.",
      "O contrato para a equipe UX é proposta de interface, não alteração funcional publicada.",
      ""]
    return "\n".join(lines)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--census",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    with Path(args.census).open(encoding="utf-8") as stream:source=json.load(stream)
    result=build(source)
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    out.with_suffix(".md").write_text(markdown(result),encoding="utf-8")
    print(json.dumps({"status":result["status"],"summary":result["summary"],
        "best_verified":{k:v["best_verified"] for k,v in result["ports"].items()},
        "first_five_battles":result["next_confrontations"][:5]},
        ensure_ascii=False,indent=2))
if __name__=="__main__":main()
