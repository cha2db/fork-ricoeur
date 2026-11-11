"""Phase2 branch-search gate: source tree, alternate indexed hits, reimport and v2 backfill."""
import json
from pathlib import Path
import sqlite3
import tempfile
from ricoeur.db import init_db, get_connection, get_read_connection, SCHEMA_VERSION
from ricoeur.importers.chatgpt import import_chatgpt
from ricoeur.importers.branch_index import parse_branch_ref, search_branch_messages
from ricoeur.retrieval import search_messages, get_message_context

passed=0
def gate(ok,name):
    global passed
    assert ok,name
    passed+=1

def make_export(current="a", alt="hiddenword"):
    def msg(mid, role, text):
        return {"id":mid,"author":{"role":role},
                "content":{"content_type":"text","parts":[text]},
                "create_time":1700000000}
    return {"id":"c1","title":"Synthetic branching","create_time":1700000000,
      "current_node":current,
      "mapping":{
        "root":{"parent":None,"children":["u"],"message":None},
        "u":{"parent":"root","children":["a","b"],"message":msg("m-u","user","question")},
        "a":{"parent":"u","children":[],"message":msg("m-a","assistant","chosenword")},
        "b":{"parent":"u","children":[],"message":msg("m-b","assistant",alt)},
      }}

with tempfile.TemporaryDirectory() as td:
    home=Path(td)/"current";home.mkdir()
    conn=init_db(home)
    gate(SCHEMA_VERSION==3,"migration version")
    fixture=Path(td)/"export.json"
    fixture.write_text(json.dumps([make_export()]))
    try:
        import_chatgpt(conn,fixture)
        main=search_messages(conn,'"chosenword"')
        gate(main["count"]==1 and main["branch_count"]==0,"selected searchable")
        alternate=search_messages(conn,'"hiddenword"')
        gate(alternate["count"]==0 and alternate["branch_count"]==1,
             "alternate discoverable, not mixed with selected main path")
        branch=alternate["branch_hits"][0]
        gate(branch["branch"]["node_id"]=="b","original node ID retained")
        gate(parse_branch_ref(branch["message"]["id"])==("c1","b"),"reversible branch reference")
        gate(branch["message"]["source_message_id"]=="m-b","original message ID retained")
        opened=get_message_context(conn,branch["message"]["id"],context=20)
        gate(opened["message"]["content"]=="hiddenword","branch text retrievable")
        gate(len(opened["before"])==1 and opened["before"][0]["content"]=="question",
             "ancestor context, not fabricated linear siblings")
        gate(conn.execute("SELECT count(*) FROM chatgpt_nodes").fetchone()[0]==4,
             "whole raw source tree remains")
        gate(conn.execute("SELECT count(*) FROM messages").fetchone()[0]==2,
             "main selected path contains only user and chosen answer")
        gate(conn.execute("SELECT count(*) FROM chatgpt_branch_messages").fetchone()[0]==1,
             "alternate view is separately indexed")

        fixture.write_text(json.dumps([make_export(current="b",alt="newhiddenword")]))
        updated=import_chatgpt(conn,fixture,update=True)
        main=search_messages(conn,'"newhiddenword"')
        gate(main["count"]==1 and main["branch_count"]==0,
             "reimport swaps selected branch")
        old=search_messages(conn,'"chosenword"')
        gate(old["count"]==0 and old["branch_count"]==1,
             "old selected branch moved to alternate index")
        gate(conn.execute("SELECT count(*) FROM messages").fetchone()[0]==2,
             "old selected projections not accumulated")
        gate(json.loads(conn.execute("SELECT message_json FROM chatgpt_nodes WHERE node_id='b'").fetchone()[0])
             ["content"]["parts"]==["newhiddenword"],"raw node updated on source update")
        gate(search_messages(conn,'"hiddenword"')["branch_count"]==0,
             "stale text removed from index")
        with get_read_connection(home) as ro:
            hits=search_branch_messages(ro,'"chosenword"')
            gate(hits["count"]==1,"read-only branch search")
        malformed=make_export()
        malformed["mapping"]["a"]["message"]["content"]=42
        fixture.write_text(json.dumps([malformed]))
        try:
            import_chatgpt(conn,fixture,dry_run=True)
        except ValueError:
            gate(True,"dry-run rejects invalid content")
        else:
            raise AssertionError("dry-run accepted content that real import cannot normalize")
    finally:
        conn.close()

    # Migration of previously imported v2 node tree retains source and backfills alternatives.
    old=Path(td)/"legacy";old.mkdir()
    con=init_db(old)
    # Construct v2 schema-meta marker in a current-schema test DB; simulate
    # preexisting ChatGPT raw tree and selected messages, without projection.
    source=make_export()
    con.execute("INSERT INTO conversations(id,title,platform) VALUES('c1','Legacy','chatgpt')")
    con.execute("INSERT INTO messages(id,conv_id,role,content) VALUES('m-a','c1','assistant','chosenword')")
    con.execute("""CREATE TABLE IF NOT EXISTS chatgpt_nodes(
        conv_id TEXT NOT NULL,node_id TEXT NOT NULL,parent_id TEXT,
        children_json TEXT NOT NULL,message_json TEXT,
        PRIMARY KEY(conv_id,node_id))""")
    for node_id,node in source["mapping"].items():
        con.execute("""INSERT INTO chatgpt_nodes
                     (conv_id,node_id,parent_id,children_json,message_json)
                     VALUES(?,?,?,?,?)""",
                    ("c1",node_id,node.get("parent"),
                     json.dumps(node["children"]),json.dumps(node["message"])))
    # Force v2 migration/backfill in a synthetic DB by clearing derived index.
    con.execute("DELETE FROM chatgpt_branch_messages")
    con.execute("UPDATE schema_meta SET value='2' WHERE key='version'")
    con.commit();con.close()
    ro_missing=False
    try:
        get_read_connection(old)
    except RuntimeError:
        ro_missing=True
    gate(ro_missing,"read adapter refuses v2 until explicitly migrated")
    migrated=get_connection(old)
    gate(migrated.execute("SELECT value FROM schema_meta WHERE key='version'").fetchone()[0]=="3",
         "migration to additive v3")
    hits=search_branch_messages(migrated,'"hiddenword"')
    gate(hits["count"]==1,"legacy tree backfilled into alternate search")
    gate(migrated.execute("SELECT count(*) FROM chatgpt_nodes").fetchone()[0]==4,
         "legacy raw nodes preserved")
    migrated.close()
print(f"PASS PHASE2 FIX-003: {passed} gates; branch FTS5, ancestry, reimport, dry-run, v2 migration")
