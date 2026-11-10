"""Functional adoption gate: message-level search and navigation."""
import json
import tempfile
from pathlib import Path
from ricoeur.db import init_db
from ricoeur.retrieval import search_messages, get_message_context

root = Path(__file__).resolve().parents[1]
out = root / "_dev" / "results"
out.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix="teste6-") as temp:
    conn = init_db(Path(temp))
    try:
        conn.executemany(
            "INSERT INTO conversations(id,title,platform) VALUES (?,?,?)",
            [("a","Projeto A","chatgpt"),("b","Projeto B","claude")])
        conn.executemany(
            "INSERT INTO messages(id,conv_id,role,content,timestamp) VALUES (?,?,?,?,?)",
            [("a1","a","user","Primeiro: agulha-mcp","2026-01-01T00:00:01"),
             ("a2","a","assistant","Resposta intermediária","2026-01-01T00:00:02"),
             ("a3","a","user","Segundo: agulha-mcp","2026-01-01T00:00:03"),
             ("b1","b","user","Terceiro: agulha-mcp","2026-01-01T00:00:04"),
             ("b2","b","assistant","Resposta do outro provedor","2026-01-01T00:00:05")])
        conn.commit()
        found = search_messages(conn, '"agulha-mcp"', limit=10, context=1)
        selected = get_message_context(conn, "a3", context=2)
        filtered = search_messages(conn, '"agulha-mcp"', platform="claude")
        checks = {
            "three_message_hits": found["count"] == 3,
            "cross_provider": {h["conversation"]["platform"] for h in found["hits"]} == {"chatgpt","claude"},
            "stable_message_ids": {h["message"]["id"] for h in found["hits"]} == {"a1","a3","b1"},
            "context_before_after": len(selected["before"]) == 2 and selected["message"]["id"] == "a3",
            "provider_filter": filtered["count"] == 1 and filtered["hits"][0]["message"]["id"] == "b1",
            "structured_json_contract": bool(json.dumps(found)),
        }
        result = {"status":"PASS" if all(checks.values()) else "FAIL",
                  "checks":checks, "hits":found["count"],
                  "sample_context":selected,
                  "mcp_protocol_tested":False}
        (out/"teste6.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
        print(json.dumps(result,ensure_ascii=False,indent=2))
        if result["status"] != "PASS":
            raise SystemExit(1)
    finally:
        conn.close()
