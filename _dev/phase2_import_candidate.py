"""Black-box import/search/reimport gate against the same ChatGPT export fixture.

Run only in an isolated CI job with read-only token and vendor checkout.
Tests Reweave from its *actual* ArchiveStore public API, not a mock adapter.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import tempfile
import time
import traceback

MARKER = "marcadordecisaocha2db2026"
def node(identity, role, content, timestamp, parent, children=()):
    return {"id":identity,
       "message":{"author":{"role":role},"content":{"parts":[content]},
                  "create_time":timestamp},
       "parent":parent,"children":list(children)}
def export():
    root={"id":"root","message":None,"parent":None,"children":["m1"]}
    base=1762200000
    return [
      {"id":"cha2db-branch-1","title":"Branch with two decisions",
        "create_time":base,"update_time":base+30,
        "mapping":{
          "root":root,
          "m1":node("m1","user","How is the decision recorded?",base,"root",["m2","m3"]),
          "m2":node("m2","assistant","Use the provenance ledger "+MARKER,base+10,"m1"),
          "m3":node("m3","assistant","Alternative decision with explicit source",base+20,"m1"),
        }},
      {"id":"cha2db-branch-2","title":"Cross conversation",
        "create_time":base+100,"update_time":base+130,
        "mapping":{
          "root":{"id":"root","message":None,"parent":None,"children":["a1"]},
          "a1":node("a1","user","What is FTS5?",base+100,"root",["a2"]),
          "a2":node("a2","assistant","FTS5 indexes messages from several chats",base+110,"a1"),
        }},
    ]

def reweave(path):
    from reweave.archive import ArchiveStore
    store=ArchiveStore(path)
    with tempfile.TemporaryDirectory(prefix="cha2db-export-") as tmp:
        source=Path(tmp)/"conversations.json"
        source.write_text(json.dumps(export(),ensure_ascii=False),encoding="utf-8")
        t=time.monotonic()
        first=store.import_path(source)
        first_seconds=round(time.monotonic()-t,4)
        initial=store.stats()
        all1=store.search("FTS5",limit=10)
        original=store.search(MARKER,limit=10)
        conv1=store.get_conversation(first.conversation_ids[0]) if first.conversation_ids else None
        messages=store.get_messages(first.conversation_ids[0]) if first.conversation_ids else []
        content_before={(m.source_id,m.content) for m in messages}
        t=time.monotonic()
        second=store.import_path(source)
        second_seconds=round(time.monotonic()-t,4)
        after=store.stats()
        returned=store.get_messages(first.conversation_ids[0]) if first.conversation_ids else []
        content_after={(m.source_id,m.content) for m in returned}
        checks={
          "two_conversations":initial.total_conversations==2 and after.total_conversations==2,
          "expected_five_messages":initial.total_messages==5 and after.total_messages==5,
          "idempotent_second_import":second.inserted_conversations==0 and second.inserted_messages==0,
          "marker_retrieved":len(original)>=1 and any(MARKER.lower() in hit.excerpt.lower() for hit in original),
          "cross_chat_fts":len(all1)>=1,
          "message_provenance":any(m.source_id for m in messages),
          "branch_siblings_preserved":sum(m.role=="assistant" for m in messages)>=2,
          "stable_ids_and_content":content_after==content_before and len(returned)==len(messages),
        }
        return {"status":"PASS" if all(checks.values()) else "FAIL",
           "candidate":"Reweave","mode":"actual public Python API","first_import_seconds":first_seconds,
           "second_import_seconds":second_seconds,
           "initial":{"conversations":initial.total_conversations,"messages":initial.total_messages},
           "second":{"conversations":after.total_conversations,"messages":after.total_messages},
           "first_summary":first.__dict__,"second_summary":second.__dict__,
           "tests":checks,"first_message_id":messages[0].id if messages else None,
           "search_hits":len(original),"conversation_source":conv1.source if conv1 else None,
           "source":"generated ChatGPT conversation export with branching and two conversations"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--candidate",choices=["reweave"],required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    result={"candidate":a.candidate,"status":"BLOCKED","fixture":"generated ChatGPT export, 2 conversations / 5 messages"}
    try:
        with tempfile.TemporaryDirectory(prefix="cha2db-reweave-db-") as d:
            result=reweave(Path(d)/"reweave.sqlite")
    except Exception as e:
        result.update({"status":"BLOCKED","error":{"type":type(e).__name__,
                                                   "message":str(e),"traceback":traceback.format_exc(limit=6)}})
    result["limits"]=["Functional proof is only for Reweave's current API and synthetic ChatGPT format.",
        "Claude/ZIP inputs, ACL, source byte preservation and semantic relevance not verified.",
        "No LLM was required or called, full Reweave UI was not executed.",
        "Vendor code ran in isolated read-only CI; candidate not integrated into Cha2db."]
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,default=str,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="first_summary" and k!="second_summary"},
                     ensure_ascii=False,default=str,indent=2),flush=True)
    if result["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
