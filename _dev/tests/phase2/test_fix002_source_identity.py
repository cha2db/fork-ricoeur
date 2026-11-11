"""Phase2 source identity collision and current_node choice, with real importers."""
import json
import sqlite3
from pathlib import Path
import tempfile

from ricoeur.db import init_db
from ricoeur.importers.chatgpt import import_chatgpt
from ricoeur.importers.claude import import_claude
from ricoeur.importers.base import (
    resolve_conversation_id, resolve_message_id, decode_source_id)
from ricoeur.retrieval import search_messages

checks=0
def gate(cond,name):
    global checks
    assert cond,name
    checks+=1

def chatgpt(cid, msgid):
    def msg(mid, content):
        return {"id":mid,"author":{"role":"assistant"},
                "content":{"content_type":"text","parts":[content]},
                "create_time":1700000000}
    return {
      "id":cid,"title":"Synthetic ChatGPT","create_time":1700000000,
      "current_node":"selected-a",
      "mapping":{
        "root":{"parent":None,"children":["selected-a","last-b"],"message":None},
        "selected-a":{"parent":"root","children":[],"message":msg(msgid,"visiblegpt unique")},
        "last-b":{"parent":"root","children":[],"message":msg("unselected-id","hiddenother branch")},
      },
    }

def claude(cid,msgid):
    return {"uuid":cid,"name":"Synthetic Claude", "chat_messages":[
      {"uuid":msgid,"sender":"human","text":"visibleclaude unique","created_at":"2026-01-01"}
    ]}

with tempfile.TemporaryDirectory() as root:
    home=Path(root)
    conn=init_db(home)
    cfile=home/"gpt.json"
    cfile.write_text(json.dumps([chatgpt("same-native-conv","same-native-msg")]))
    afile=home/"claude.json"
    afile.write_text(json.dumps([claude("same-native-conv","same-native-msg")]))
    try:
        s1=import_chatgpt(conn,cfile)
        gate(s1.new==1,"gpt imported")
        gpt_hits=search_messages(conn,'"visiblegpt"')
        gate(gpt_hits["count"]==1,"current_node chosen")
        gate(search_messages(conn,'"hiddenother"')["count"]==0,
             "unselected branch not falsely indexed in selected-only projection")
        gate(conn.execute("SELECT count(*) FROM chatgpt_nodes").fetchone()[0]==3,
             "raw tree preserved")
        s2=import_claude(conn,afile)
        gate(s2.new==1,"claude with same native conv imported")
        chats=list(conn.execute("SELECT id,platform FROM conversations ORDER BY platform"))
        gate(len(chats)==2 and {r["platform"] for r in chats}=={"chatgpt","claude"},
             "two providers with same native conversation ID")
        renamed=next(r["id"] for r in chats if r["platform"]=="claude")
        gate(decode_source_id(renamed)==("conversation","claude","same-native-conv"),
             "source ID reversible")
        found=search_messages(conn,'"visibleclaude"')
        gate(found["count"]==1 and found["hits"][0]["conversation"]["id"]==renamed,
             "correct hit belongs to Claude not ChatGPT")
        cid=found["hits"][0]["message"]["id"]
        gate(decode_source_id(cid)==
             ("message","claude",renamed,"same-native-msg"),"message source ID reversible")
        gate(conn.execute("SELECT count(*) FROM messages").fetchone()[0]==2,
             "messages not conflated")
        second=import_claude(conn,afile)
        gate(second.new==0 and second.skipped==1,"idempotent Claude import")
        check=resolve_message_id(conn,"claude",renamed,"same-native-msg")
        gate(check==cid,"stable namespace after reimport")
        gate(resolve_conversation_id(conn,"chatgpt","same-native-conv")=="same-native-conv",
             "existing legacy ChatGPT ID not rewritten")
        gate(decode_source_id("raw-external-id") is None,"legacy plain source ID")
    finally:
        conn.close()
print(f"PASS PHASE2 FIX-002: {checks} gates, provider+message collision, reversible source and selected branch")
