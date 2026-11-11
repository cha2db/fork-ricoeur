"""R14 Portable Memory actual SDK contract: lossless message content vs branch topology.

Uses the same 2-conversation/5-message branching fixture already tested on CTK,
Reweave and Chronicle, but adds canonical inner ChatGPT message IDs so that an
OpenAI data export meets its normal shape. No network/LLM used by the test.
"""
from __future__ import annotations
import argparse
import json
import tempfile
import traceback
from pathlib import Path

from phase2_import_candidate import MARKER, export

def run():
    from portable_memory.adapters.openai import OpenAIAdapter
    from portable_memory.exporter import BundleExporter
    from portable_memory.importer import BundleImporter
    from portable_memory.inmemory import InMemoryStore
    from portable_memory.validator import BundleValidator

    source=export()
    for conversation in source:
        for node_id,node in conversation["mapping"].items():
            if isinstance(node.get("message"),dict):
                node["message"]["id"]=node_id
    episodes=OpenAIAdapter.parse_episodes(source)
    by_id={ep.id:ep for ep in episodes}
    expected={"m1","m2","m3","a1","a2"}
    original_metadata={id:ep.metadata for id,ep in by_id.items()}
    checks={
        "five_message_ids":len(episodes)==5 and set(by_id)==expected,
        "all_alternative_texts_preserved":len(by_id)==5 and
             "Alternative decision" in by_id["m3"].details and MARKER in by_id["m2"].details,
        "provider_conversation_provenance":all(
             ep.metadata.get("openai_conversation_id") in
             {"cha2db-branch-1","cha2db-branch-2"} for ep in episodes),
        "stable_source_message_ids":all(
             ep.source_id==ep.id and ep.metadata.get("openai_message_id")==ep.id
             for ep in episodes),
        "role_preserved":all(ep.speaker in {"user","assistant"} for ep in episodes),
    }
    with tempfile.TemporaryDirectory(prefix="cha2db-portable-memory-") as root:
        bundle=Path(root)/"chat.mem"
        store=InMemoryStore()
        for ep in episodes:store.import_episode(ep,None)
        manifest=BundleExporter().export(store,bundle)
        result=BundleValidator().validate(bundle)
        checks["valid_bundle_integrity"]=result.ok
        checks["has_checksums_and_manifest"]=((bundle/"CHECKSUMS").exists() and
            (bundle/"manifest.json").exists())
        original_ids={ep.id for ep in store.episodes.values()}
        recipient=InMemoryStore()
        BundleImporter().import_bundle(recipient,bundle,reembed=False)
        reloaded={ep.id:ep for ep in recipient.episodes.values()}
        checks["full_bundle_roundtrip_ids"]=set(reloaded)==original_ids
        checks["full_bundle_roundtrip_content"]=(len(reloaded)==5 and
             all(reloaded[key].details==by_id[key].details for key in expected))
        checks["full_bundle_roundtrip_provenance"]=(len(reloaded)==5 and
             all(reloaded[key].metadata.get("openai_conversation_id")==
                 original_metadata[key].get("openai_conversation_id") for key in expected))
        BundleImporter().import_bundle(recipient,bundle,reembed=False)
        checks["repeated_bundle_import_no_duplicates"]=len(recipient.episodes)==5
        doc=bundle/"items"/"episode.jsonl"
        data=doc.read_bytes()
        checks["episode_jsonl_nonempty"]=len(data)>0
        doc.write_bytes(data + b"\n{}\n")
        tampered=BundleValidator().validate(bundle)
        checks["tamper_detected"]=not tampered.ok and len(tampered.issues)>0
        parent_recoverable=all(
             "openai_parent_id" in ep.metadata or
             "parent_id" in ep.metadata for ep in episodes if ep.id in ("m2","m3"))
        topology={"explicit_parent_link_retained":parent_recoverable,
                  "sibling_source_ids_retained":all(k in by_id for k in ("m2","m3")),
                  "comment":"The OpenAI adapter preserves both sibling messages as episodes but "
                            "does not encode their parent/child edges in episode metadata; "
                            "therefore this bundle cannot reconstruct branch topology by itself."}
        report={"candidate":"Portable Memory (MacPaw)","upstream":"MacPaw/portable-memory",
          "status":"PASS" if all(checks.values()) else "FAIL",
          "contract":"portable messages, metadata, deterministic ID, JSONL manifest, integrity and tamper",
          "checks":checks,"branch_topology":topology,
          "bundle_items":len(episodes),"manifest_format":manifest.format,
          "roundtrip_ids":sorted(reloaded),
          "tamper_issue_count":len(tampered.issues),
          "verdict":"ADOPT_FORMAT_CANDIDATE_NOT_LOSSLESS_TREE_REPLACEMENT",
          "limitations":[
             "ChatGPT source tree edges/parent pointers are not in Portable Memory episode metadata.",
             "Only user/assistant text episodes tested, not tool calls, attachments, or raw JSON preservation.",
             "Deterministic JSONL content is separate from generation timestamps in manifest.",
             "No browser, tablet or external provider integration; core Cha2db remains untouched.",
             "PASS means portable bundle integrity and content only, NOT entire conversation structure."
          ]}
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    a=p.parse_args()
    try:r=run()
    except Exception as e:
        r={"candidate":"Portable Memory (MacPaw)","status":"BLOCKED",
           "error":{"type":type(e).__name__,"message":str(e),
                     "traceback":traceback.format_exc(limit=8)}}
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(r,ensure_ascii=False,indent=2),flush=True)
    if r["status"]!="PASS":raise SystemExit(1)

if __name__=="__main__":main()
