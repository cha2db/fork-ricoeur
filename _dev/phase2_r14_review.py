"""Cross-validated new-candidate source audit and unified Phase-2 ranking.

Combines the existing 143 evidence-ranked candidates with *discovery-only*
R14 entries. Never promotes discovered tools to functional PASS.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import json,os,re,time,urllib.request,urllib.error

URL_RE=re.compile(r"^https://github\.com/([^/]+)/([^/?#]+)",re.I)
PORTS={
 "graph_hybrid":"topic_relations",
 "temporal_storage":"versioned_storage",
 "embedded_storage":"storage_engine",
 "browser_storage":"local_sync",
 "lexical_embedded":"lexical_core",
 "hybrid_engine":"lexical_core",
 "vector_index":"vector_index",
 "chat_product":"ingest_tree",
 "memory_product":"memory_temporal",
 "portable_format":"interoperability_formats",
 "vendor_reference":"external_reference",
}
EXCEPTIONS={
 "C146":"versioned_storage", # SirixDB
 "C147":"versioned_storage", # TerminusDB
}
TITLES={
 "versioned_storage":"Armazenamento histórico e imutável (bitemporal/branches)",
 "storage_engine":"Motor transacional embutido e mecanismos KV",
 "local_sync":"Persistência local, navegador e sincronização",
 "interoperability_formats":"Contratos e formatos portáteis entre fornecedores",
}
KEYWORDS={
 "branches":r"\b(branch(?:es|ing)?|forks?|alternate.responses?|sibling)\b",
 "provenance":r"\b(provenance|lineage|original.source|audit.trail|checksum)\b",
 "temporal":r"\b(bitemporal|time.travel|transaction.time|valid.time|history)\b",
 "search":r"\b(full.text|BM25|RRF|semantic.search|hybrid.search|vector.search)\b",
 "human":r"\b(human.review|human.in.the.loop|approval|conflict.review)\b",
 "portable":r"\b(JSONL|manifest|content.hash|SHA-256|portable|interopera\w*)\b",
 "offline":r"\b(offline|local.first|browser|WASM|on.device)\b",
}
BLOCKED_LICENSE={"AGPL-3.0","GPL-3.0","GPL-2.0","SSPL-1.0","BUSL-1.1"}
HEADERS={"Accept":"application/vnd.github+json","User-Agent":"cha2db-phase2-r14",
 "X-GitHub-Api-Version":"2022-11-28"}
def normalize(url):
 return url.rstrip("/").casefold().removesuffix(".git")
def api_get(url,token,readme=False):
 h=dict(HEADERS)
 if token:h["Authorization"]="Bearer "+token
 if readme:h["Accept"]="application/vnd.github.raw+json"
 for attempt in range(2):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers=h),timeout=20) as response:
    return response.read(75000 if readme else 90000).decode("utf-8","replace"),None
  except urllib.error.HTTPError as e:
   if e.code in (403,429) and attempt==0:time.sleep(1.5);continue
   return None,{"code":e.code,"kind":"HTTPError"}
  except (OSError,TimeoutError) as e:
   if attempt==0:time.sleep(.5);continue
   return None,{"kind":type(e).__name__}
 return None,{"kind":"API_UNAVAILABLE"}
def verify(row,token):
 m=URL_RE.match(row["url"])
 if not m:
  return {"status":"EXTERNAL_REFERENCE","source":row["url"],
   "license":"NOT_VERIFIED","claim_scope":"vendor documentation, not locally executable"}
 full=m.group(1)+"/"+m.group(2).removesuffix(".git")
 raw,err=api_get("https://api.github.com/repos/"+full,token)
 if err or raw is None:
  return {"status":"SOURCE_UNVERIFIED","repository":full,"error":err}
 try:
  x=json.loads(raw)
  result={"status":"SOURCE_FOUND","repository":x.get("full_name",full),
   "source":x.get("html_url",row["url"]),"archived":x.get("archived"),
   "fork":x.get("fork"),"created_at":x.get("created_at"),
   "pushed_at":x.get("pushed_at"),"size_kb":x.get("size"),
   "stars":x.get("stargazers_count"),"license":(x.get("license") or {}).get("spdx_id","UNDETERMINED"),
   "default_branch":x.get("default_branch"),"description":x.get("description"),
   "source_claim":"GitHub REST metadata: no functional testing"}
  if row["priority"] in ("P0","P1"):
   readme,error=api_get("https://api.github.com/repos/"+full+"/readme",token,True)
   if readme:
    # Some public GitHub APIs return base64-wrapped JSON instead of raw.
    try:
     obj=json.loads(readme)
     if obj.get("encoding")=="base64":
      import base64
      readme=base64.b64decode(obj.get("content","")).decode("utf-8","replace")
    except (TypeError,ValueError,AttributeError):pass
    caps=[]
    for k,pattern in KEYWORDS.items():
     if re.search(pattern,readme,re.I):caps.append(k)
    result["readme_keyword_matches"]=caps
    result["readme_status"]="READ"
    result["readme_source"]=result["source"]+"#readme"
   else:result["readme_status"]="UNAVAILABLE"
  else:result["readme_status"]="NOT_REQUESTED_LOW_PRIORITY"
  return result
 except ValueError:
  return {"status":"SOURCE_UNVERIFIED","repository":full,"error":"invalid upstream API JSON"}

def risk_and_rank(row,source):
 risks=[]
 if source.get("status")!="SOURCE_FOUND":risks.append("UNVERIFIED_SOURCE")
 if source.get("archived"):risks.append("ARCHIVED")
 if source.get("fork"):risks.append("FORK_OR_DUPLICATE_MUST_CHECK")
 if source.get("license") in BLOCKED_LICENSE:risks.append("STRONG_COPYLEFT_NO_EMBED")
 if source.get("license") in (None,"UNDETERMINED","NOASSERTION","NOT_VERIFIED"):
  risks.append("LICENSE_NOT_CLEARED")
 if row["priority"]=="P0" and not risks:phase="NEXT_CONTRACT_TEST"
 elif "STRONG_COPYLEFT_NO_EMBED" in risks:phase="REFERENCE_UNLESS_LEGAL_APPROVAL"
 elif risks:phase="SOURCE_OR_LICENSE_REVIEW"
 else:phase="COMPARISON_CANDIDATE"
 return risks,phase

def merge(existing, new, base, legacy_rank):
 existing_ids={x["id"] for x in existing}
 new_ids={x["id"] for x in new}
 if len(new_ids)!=len(new) or existing_ids.intersection(new_ids):
  raise ValueError("Duplicate candidate ID")
 old_urls={normalize(x["url"]) for x in base["candidates"]}
 new_urls=[normalize(x["url"]) for x in new]
 if len(set(new_urls))!=len(new_urls) or set(new_urls)&old_urls:
  raise ValueError("Duplicate GitHub/vendor URL, or candidate already in R10")
 if base.get("total")!=143 or len(legacy_rank["ports"])<10:raise ValueError("Legacy evidence missing")
 ports={k:{"title":v["title"],"entries":[dict(x) for x in v["entries"]]} for k,v in legacy_rank["ports"].items()}
 for key,title in TITLES.items():ports[key]={"title":title,"entries":[]}
 bynew={}
 for row in new:
  port=PORTS[row["category"]]
  if row["id"] in EXCEPTIONS:port=EXCEPTIONS[row["id"]]
  if row["name"]=="Moss":port="browser_index"
  if row["name"] in ("Kosha","Marqo","Turbopuffer","Kosha design"):port="search_service"
  if row["name"]=="Portable Memory (MacPaw)" or row["name"]=="PAM Portable AI Memory":port="interoperability_formats"
  if row["name"]=="Personal AI Memory":port="ingest_tree"
  if row["name"]=="Deep Lake":port="vector_index"
  ranks,decision=risk_and_rank(row,row["source_metadata"])
  item={"id":row["id"],"name":row["name"],"port":port,
   "source_url":row["url"],"source_status":row["source_metadata"]["status"],
   "functional_status":"NOT_TESTED","functional_level":"NO_TEST",
   "eligibility":"UNTESTED_CANDIDATE" if decision=="NEXT_CONTRACT_TEST" else decision,
   "original_priority":row["priority"],"search_form":row["search_or_connection_approach"],
   "storage_mechanism":row["storage_mechanism"],
   "risks":ranks,"license_spdx":row["source_metadata"].get("license"),
   "test_gate":row["comparative_gate"],"rank_evidence":"PRIOR_ART_ONLY",
   "not_integrated_in_core":True}
  bynew[item["id"]]=item;ports[port]["entries"].append(item)
 def key(x):
  status=x.get("functional_status")
  priority=x.get("original_priority","P2")
  if x.get("id")=="C001":tier=0
  elif status=="PASS":tier=1
  elif x.get("eligibility") in ("UNTESTED_CANDIDATE","NEXT_CONTRACT_TEST"):tier=2
  elif x.get("eligibility") in ("COMPARISON_CANDIDATE",):tier=3
  else:tier=4
  return (tier,{"P0":0,"P1":1,"P2":2,"P3":3}.get(priority,3),
          x.get("rank_in_port",9999),x["id"])
 for port in ports.values():
  port["entries"].sort(key=key)
  for i,x in enumerate(port["entries"],1):x["rank_in_port"]=i
  port["candidate_count"]=len(port["entries"])
  port["best_verified"]=next((x["id"] for x in port["entries"] if x.get("functional_status")=="PASS"),None)
  port["next_unverified"]=next((x["id"] for x in port["entries"]
    if x.get("functional_status")=="NOT_TESTED" and x.get("eligibility") in ("UNTESTED_CANDIDATE","NEXT_CONTRACT_TEST")),None)
 allids=[x["id"] for p in ports.values() for x in p["entries"]]
 if len(allids)!=base["total"]+len(new) or len(set(allids))!=len(allids):
  raise ValueError("One primary port per candidate violated")
 return ports

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--expansion",required=True)
 p.add_argument("--base",required=True)
 p.add_argument("--legacy-ranking",required=True)
 p.add_argument("--output",required=True)
 p.add_argument("--workers",type=int,default=8)
 args=p.parse_args()
 ext=json.loads(Path(args.expansion).read_text())
 base=json.loads(Path(args.base).read_text())
 legacy=json.loads(Path(args.legacy_ranking).read_text())
 if ext["previous_candidates"]!=143 or ext["additional_candidates"]!=len(ext["candidates"]):
  raise ValueError("R14 inventory invalid")
 if ext["total_candidates"]!=143+len(ext["candidates"]):raise ValueError("Incorrect total")
 tokens=os.environ.get("GITHUB_TOKEN")
 sources={}
 with ThreadPoolExecutor(max_workers=args.workers) as executor:
  futures={executor.submit(verify,item,tokens):item["id"] for item in ext["candidates"]}
  for future in as_completed(futures):
   i=futures[future]
   try:sources[i]=future.result()
   except Exception as exc:sources[i]={"status":"SOURCE_UNVERIFIED","error":type(exc).__name__}
 extended=[]
 for cand in ext["candidates"]:
  row=dict(cand)
  row["source_metadata"]=sources[row["id"]]
  row["functional_status"]="NOT_TESTED"
  row["comparative_gate_result"]="NOT_EXECUTED"
  extended.append(row)
 ports=merge(legacy["ports"],extended,base,legacy)
 source_counts=Counter(x["source_metadata"]["status"] for x in extended)
 priorities=Counter(x["priority"] for x in extended)
 incomplete=[x["id"] for x in extended if x["source_metadata"]["status"]=="SOURCE_UNVERIFIED"]
 report={
  "revision":"R14","status":"PASS" if not incomplete else "PARTIAL",
  "generated_utc":datetime.now(timezone.utc).isoformat(),
  "base_inventory":"R10","base_rank":"R13","old_count":143,
  "new_count":len(extended),"total_count":143+len(extended),
  "scope":"Phase2 market survey and architecture ranking; UX branch untouched",
  "source_counts":dict(source_counts),"priorities":dict(priorities),
  "unverified_sources":incomplete,
  "functional_pass_existing":legacy["summary"]["functional_pass"],
  "functional_pass_new":0,"functional_test_new":"NONE_RUN_IN_THIS_SURVEY",
  "new_candidates":extended,"ports":ports,
  "existing_confrontations":legacy["next_confrontations"],
  "expanded_confrontation_queue":[
   {"order":1,"incumbent":"C118 CTK","challengers":["Portable Memory (MacPaw)","PAM Portable AI Memory"],
    "contract":"Lossless branch+source hashes, 2 conversations 5 messages and schema roundtrip"},
   {"order":2,"incumbent":"C118 CTK","challengers":["ThreadShelf","Personal AI Memory"],
    "contract":"Multiple providers, branches, browser capture, exact export roundtrip"},
   {"order":3,"incumbent":"C001 SQLite FTS5","challengers":["SirixDB","TerminusDB","FlureeDB"],
    "contract":"Bitemporal revisions, immutable messages, rollback, source IDs, disk budget"},
   {"order":4,"incumbent":"C065 RDFLib","challengers":["HelixDB","LadybugDB","Oxigraph"],
    "contract":"Typed evidence links + graph traversal, embeddings, mutation safety"},
   {"order":5,"incumbent":"C001 SQLite FTS5","challengers":["Searchlite","Bleve","Moss","Infinity"],
    "contract":"Identical corpus, PT/EN queries, p95/memory/disk, update/delete, no cloud"},
   {"order":6,"incumbent":"C028 sqlite-vec","challengers":["turbovec","turbovecdb","ObjectBox Python"],
    "contract":"Exact recall, 2M scale, ARM, persistence, 2/4-bit tradeoffs"},
   {"order":7,"incumbent":"C114 OpenSelf (untested)","challengers":["Mnemos","Memoirs","Hearth","Lossless Memory"],
    "contract":"Conflict state, time-first, human approval, provenance, no mandatory model"},
   {"order":8,"incumbent":"C011 FlexSearch","challengers":["PGlite","RxDB","Dexie","Evolu","cr-sqlite"],
    "contract":"Persisted browser search + sync without silently merging chat source branches"},
   {"order":9,"incumbent":"R10 data contracts","challengers":["immudb","Dolt","KurrentDB","XTDB"],
    "contract":"Append-only evidence and tamper verification without losing source data"}],
  "cautions":[
   "Only 143 original candidates have functional reports; all newly added entries are NOT_TESTED.",
   "GitHub metadata or README keywords are not proof that the advertised product works.",
   "Ranking is priority to confront within a port, not universal superiority.",
   "Licenses and model weights must be inspected per version before embedding.",
   "The Phase3 UX branch and product runtime were not modified.",
   "Do not claim exhaustion; newly found products still need functional tests."]
 }
 out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 md=[
  "# Cha2db — Ranking ampliado da Fase 2 R14",
  "",
  f"**{report['total_count']} candidatos**: 143 já triados e {report['new_count']} novos da varredura.",
  f"**Fonte encontrada no GitHub:** {source_counts.get('SOURCE_FOUND',0)} novos; fontes sem verificação: {len(incomplete)}.",
  "**PASS funcional dos novos: 0.** Esta rodada é pesquisa e auditoria, não homologação.",
  "",
  "## Ranking e filas por porta",
  "",
 ]
 for key,pool in report["ports"].items():
  md.extend([f"### {pool['title']} ({pool['candidate_count']})","",
    "| Pos. | ID | Produto | Status funcional | Status da origem | Próximo gate |",
    "|---:|---|---|---|---|---|"])
  for item in pool["entries"]:
   gate=(item.get("test_gate") or "Confronto do contrato existente").replace("|","/")
   md.append(f"| {item['rank_in_port']} | {item['id']} | {item['name']} | "
     f"{item.get('functional_status','NOT_TESTED')} | {item.get('source_status','LEGACY')} | {gate} |")
  md.append("")
 md.extend(["## Confrontos novos, em ordem","","| Ordem | Referência | Candidatos | Critério |",
  "|---:|---|---|---|"])
 for b in report["expanded_confrontation_queue"]:
  md.append(f"| {b['order']} | {b['incumbent']} | {', '.join(b['challengers'])} | {b['contract']} |")
 md.extend(["","## Garantias",
  "A lista anterior de 143 continua preservada e auditável; toda adição tem ID independente.",
  "Nenhum resultado novo foi classificado como PASS sem execução funcional real.",
  "A equipe UX paralela deve consumir contratos e não depender da implementação de qualquer candidato.",
  ""])
 out.with_suffix(".md").write_text("\n".join(md),encoding="utf-8")
 print(json.dumps({"status":report["status"],"new":report["new_count"],
                   "total":report["total_count"],"source_counts":dict(source_counts),
                   "unverified":incomplete,
                   "ports":{k:v["candidate_count"] for k,v in ports.items()}},
                  ensure_ascii=False,indent=2),flush=True)
 if report["total_count"]!=ext["total_candidates"]:raise SystemExit(1)
if __name__=="__main__":main()
