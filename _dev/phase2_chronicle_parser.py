"""Compare Chat Chronicle official ChatGPT parser on exact CTK/Reweave branch fixture."""
from __future__ import annotations
import argparse,json,traceback
from pathlib import Path
from phase2_import_candidate import export,MARKER

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--output",required=True);a=ap.parse_args()
    try:
        from chat_chronicle.adapters.chatgpt_export import parse_conversations_json
        parsed=parse_conversations_json(export())
        found=parsed.conversations
        first=next((x for x in found if x.provider_conv_id=="cha2db-branch-1"),None)
        contents=[m.body for x in found for m in x.messages]
        nodeids=[m.provider_message_id for x in found for m in x.messages]
        checks={
            "two_conversations":len(found)==2,
            "all_five_original_messages":sum(len(x.messages) for x in found)==5,
            "both_alternative_branches":first is not None and len(first.messages)==3,
            "marker_text_kept":any(MARKER in body for body in contents),
            "source_ids_available":all(x.provider_conv_id for x in found),
        }
        report={"candidate":"Chat Chronicle","status":"PASS" if all(checks.values()) else "FAIL",
            "test":"actual parse_conversations_json public parser; 2 conversations/5 messages",
            "tests":checks,"normalized_count":sum(len(x.messages) for x in found),
            "source_ids":nodeids,
            "nonfatal_parse_errors":[err.model_dump() for err in parsed.errors][:20]}
    except Exception as e:
        report={"candidate":"Chat Chronicle","status":"BLOCKED",
            "error":{"type":type(e).__name__,"message":str(e),"traceback":traceback.format_exc(limit=6)}}
    report["limitations"]=["Only parser test; no SQLite persistence or official archive ZIP.",
       "Expected five messages includes alternative branches not only active current branch.",
       "Vendor code runs in isolated GitHub Actions read-only job with no LLM.",
       "No Cha2db production integration or end-to-end MCP claim."]
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if report["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
