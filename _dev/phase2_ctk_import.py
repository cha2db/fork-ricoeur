"""Test actual CTK OpenAI importer on same branching synthetic export as Reweave.

The scope here is the CTK public import_data parser, NOT SQLite persistence,
full CLI, semantic search or MCP. Avoids conflating parser with end-to-end app.
"""
from __future__ import annotations
import json
import traceback
from pathlib import Path
import argparse
from phase2_import_candidate import export,MARKER

def run():
    from ctk.importers.openai import OpenAIImporter
    data=export()
    importer=OpenAIImporter()
    valid=importer.validate(data)
    trees=importer.import_data(data)
    if len(trees)!=2:
        return {"status":"FAIL","tests":{"two_conversations":False},
                "returned_conversations":len(trees)}
    trees_by_id={t.id:t for t in trees}
    t1=trees_by_id.get("cha2db-branch-1")
    t2=trees_by_id.get("cha2db-branch-2")
    ids=list(t1.message_map.keys()) if t1 else []
    second_ids=list(t2.message_map.keys()) if t2 else []
    msg2=t1.message_map.get("m2") if t1 else None
    msg3=t1.message_map.get("m3") if t1 else None
    again=importer.import_data(data)
    exact=importer.validate(data)
    checks={
        "valid_source":valid and exact,
        "two_conversations":len(trees_by_id)==2,
        "five_messages_preserved":len(ids)==3 and len(second_ids)==2,
        "all_branch_ids":set(ids)=={"m1","m2","m3"},
        "alternative_siblings":msg2 is not None and msg3 is not None and msg2.parent_id==msg3.parent_id=="m1",
        "marker_preserved":msg2 is not None and MARKER in msg2.content.get_text(),
        "id_stability_second_parse":len(again)==2 and
           set(again[0].message_map.keys())==set(trees[0].message_map.keys()),
    }
    return {"status":"PASS" if all(checks.values()) else "FAIL",
            "candidate":"CTK","mode":"actual OpenAIImporter.import_data public API",
            "checks":checks,"conversation_count":len(trees),
            "first_tree_ids":ids,"second_tree_ids":second_ids,
            "branch_parent":msg2.parent_id if msg2 else None,
            "verdict":"PARSER_BRANCH_PRESERVATION_ONLY"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    a=p.parse_args()
    try:report=run()
    except Exception as error:
        report={"status":"BLOCKED","candidate":"CTK",
                "error":{"type":type(error).__name__,"message":str(error),
                         "traceback":traceback.format_exc(limit=6)}}
    report["fixture"]="exact same 2 ChatGPT conversations / 5 message, two reply branches as Reweave"
    report["limitations"]=["CTK importer parser test only, no SQLite persistence, duplicates or MCP.",
        "The parser executes external vendor code on an isolated read-only runner.",
        "No dependency on LLM models; no production integration.",
        "CLI and storage contracts require independent end-to-end gates."]
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
    if report["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
