"""Teste 5: capacidades decisivas de busca, navegação e contrato para agentes."""
import json
import tempfile
from pathlib import Path
from ricoeur.db import init_db
from ricoeur.search import fts_search

root = Path(__file__).resolve().parents[1]
out = root / "_dev" / "results"
out.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix="teste5-") as temp:
    conn = init_db(Path(temp))
    try:
        for cid, title in [("a", "Projeto A"), ("b", "Projeto B")]:
            conn.execute("INSERT INTO conversations(id,title,platform) VALUES(?,?,?)", (cid,title,"chatgpt"))
        items = [
            ("a1","a","user","agulha-mcp: como localizar uma informação?", "2026-01-01T10:00:00"),
            ("a2","a","assistant","Resposta da agulha-mcp com contexto e identificador.", "2026-01-01T10:01:00"),
            ("a3","a","user","Outra ocorrência da agulha-mcp nesta conversa.", "2026-01-01T10:02:00"),
            ("b1","b","assistant","A agulha-mcp também está na outra conversa.", "2026-01-02T10:00:00"),
        ]
        conn.executemany("INSERT INTO messages(id,conv_id,role,content,timestamp) VALUES(?,?,?,?,?)",items)
        conn.commit()
        # Existing search API: results grouped by conversation, not message.
        result = fts_search(conn, '"agulha-mcp"', limit=20)
        raw = conn.execute("""
            SELECT m.id, m.conv_id, m.role, m.timestamp, m.content
            FROM messages_fts f JOIN messages m ON m.rowid=f.rowid
            WHERE messages_fts MATCH ? ORDER BY m.conv_id,m.timestamp
        """, ('"agulha-mcp"',)).fetchall()
        # Check what is available in the code, not claim an MCP server exists.
        mcp_files = [str(p.relative_to(root)) for p in (root / "src" / "ricoeur").rglob("*mcp*") if p.is_file()]
        verdict = {
            "status": "DIAGNOSTIC",
            "capabilities": {
                "cross_conversation_search": len(result)==2,
                "conversation_snippets": all(r.snippet for r in result),
                "all_message_matches_via_public_search": len(result)==len(raw),
                "message_ids_in_public_search_result": hasattr(result[0], "msg_id") if result else False,
                "message_matches_accessible_via_sqlite": len(raw)==4,
                "structured_message_context_available": all(row["timestamp"] and row["role"] for row in raw),
                "mcp_server_file_found": bool(mcp_files),
            },
            "counts": {"conversations_found": len(result), "matching_messages":len(raw)},
            "mcp_files":mcp_files,
            "decision": "Reuse SQLite+FTS5; message-level API and MCP adapter require development.",
            "note": "MCP file detection is heuristic, not a runtime protocol compliance test."
        }
        path=out/"teste5.json"
        path.write_text(json.dumps(verdict,ensure_ascii=False,indent=2))
        print(json.dumps(verdict,ensure_ascii=False,indent=2))
        print("Relatorio:",path)
    finally:
        conn.close()
