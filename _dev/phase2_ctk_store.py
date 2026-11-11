"""CTK real SQLite persistence, branch and reimport contract on shared fixture.

Unlike the parser-only gate, this uses ConversationDB.save_conversation/load_conversation.
"""
from __future__ import annotations
import argparse,json,sqlite3,tempfile,traceback
from pathlib import Path
from phase2_import_candidate import export,MARKER

def run():
    from ctk.importers.openai import OpenAIImporter
    from ctk.core.database import ConversationDB
    source=export()
    parsed=OpenAIImporter().import_data(source)
    with tempfile.TemporaryDirectory(prefix="cha2db-ctk-db-") as root:
        db=ConversationDB(str(Path(root)/"ctk"))
        for tree in parsed:db.save_conversation(tree)
        loaded=[db.load_conversation(tree.id) for tree in parsed]
        ids1=[set(tree.message_map) for tree in loaded if tree]
        first_paths=len(loaded[0].get_all_paths()) if loaded[0] else 0
        for tree in parsed:db.save_conversation(tree)
        reloaded=[db.load_conversation(tree.id) for tree in parsed]
        ids2=[set(tree.message_map) for tree in reloaded if tree]
        conn=sqlite3.connect(str(Path(root)/"ctk"/"conversations.db"))
        try:
            table_names=[r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            count=conn.execute("SELECT count(*) FROM messages").fetchone()[0] if "messages" in table_names else None
            fts=[x for x in table_names if "fts" in x.lower()]
        finally:conn.close()
        branch=reloaded[0].message_map if reloaded[0] else {}
        checks={
           "two_conversations_after_reload":len(reloaded)==2 and all(reloaded),
           "five_messages_after_disk_roundtrip":len(ids2)==2 and sum(map(len,ids2))==5,
           "no_duplicate_after_second_save":ids1==ids2 and
                 sum(map(len,ids2))==5 and (count is None or count==5),
           "both_branch_siblings_survive":branch.get("m2") is not None and
                 branch.get("m3") is not None and branch["m2"].parent_id==branch["m3"].parent_id=="m1",
           "branch_paths_survive":first_paths>=2 and len(reloaded[0].get_all_paths())>=2,
           "content_source_survives":MARKER in branch["m2"].content.get_text() if "m2" in branch else False,
           "provider_preserved":all(t.metadata.format=="openai" and t.metadata.source=="ChatGPT" for t in reloaded if t)
        }
        return {"candidate":"CTK SQLite","status":"PASS" if all(checks.values()) else "FAIL",
            "checks":checks,"message_counts":[len(ids) for ids in ids2],
            "database_message_count":count,"tables":table_names,
            "fts_table_names":fts,"branch_paths":first_paths,
            "test_scope":"SQLite persistence, stable branch IDs, repeated save (not raw-byte fidelity)"}

def main():
    p=argparse.ArgumentParser();p.add_argument("--output",required=True);a=p.parse_args()
    try:r=run()
    except Exception as e:r={"candidate":"CTK SQLite","status":"BLOCKED",
        "error":{"type":type(e).__name__,"message":str(e),"traceback":traceback.format_exc(limit=6)}}
    r["fixture"]="Same 2-conversation, 5-message ChatGPT branch fixture as Reweave"
    r["limitations"]=["Repeated save overwrites existing messages; source raw-byte preservation untested.",
        "No export roundtrip or MCP in this gate.",
        "No production integration or human semantic-quality claim."]
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(r,ensure_ascii=False,indent=2))
    if r["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
