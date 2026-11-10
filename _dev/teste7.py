"""Teste 7: cliente MCP real via stdio (SDK oficial v1 compatível)."""
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from ricoeur.db import init_db

root = Path(__file__).resolve().parents[1]
out = root / "_dev" / "results"
out.mkdir(exist_ok=True)

async def main():
    with tempfile.TemporaryDirectory(prefix="teste7-") as folder:
        home = Path(folder)
        conn = init_db(home)
        conn.execute("INSERT INTO conversations(id,title,platform) VALUES(?,?,?)",
                     ("mcp-test", "MCP test", "chatgpt"))
        conn.executemany(
            "INSERT INTO messages(id,conv_id,role,content,timestamp) VALUES(?,?,?,?,?)",
            [("m1","mcp-test","user","Onde está agulha-mcp?","2026-01-01T10:00:00"),
             ("m2","mcp-test","assistant","Encontrei agulha-mcp.","2026-01-01T10:01:00"),
             ("m3","mcp-test","user","Obrigado.","2026-01-01T10:02:00")])
        conn.commit()
        conn.close()
        env = dict(os.environ)
        env["RICOEUR_HOME"] = str(home)
        env["PYTHONPATH"] = str(root / "src") + os.pathsep + env.get("PYTHONPATH", "")
        server = StdioServerParameters(
            command=sys.executable,
            args=["-m", "ricoeur.mcp_adapter"],
            env=env)
        async with stdio_client(server) as (read, write):
            async with ClientSession(read, write) as client:
                await client.initialize()
                tools = await client.list_tools()
                names = [t.name for t in tools.tools]
                found = await client.call_tool(
                    "search_chat_messages",
                    arguments={"query":'"agulha-mcp"', "context":1})
                detail = await client.call_tool(
                    "read_chat_message",
                    arguments={"message_id":"m2","context":1})
                def extract(response):
                    if response.isError:
                        raise RuntimeError(str(response.content))
                    if getattr(response, "structuredContent", None):
                        return response.structuredContent
                    for block in response.content:
                        if getattr(block,"type",None)=="text":
                            return json.loads(block.text)
                    raise ValueError("No JSON response from MCP tool")
                search = extract(found)
                message = extract(detail)
                checks = {
                    "tools_discovered": {"search_chat_messages","read_chat_message"}.issubset(names),
                    "search_over_mcp": search["count"] == 2,
                    "ids_over_mcp": {h["message"]["id"] for h in search["hits"]} == {"m1","m2"},
                    "context_over_mcp": message["message"]["id"] == "m2" and
                                        len(message["before"]) == 1 and len(message["after"]) == 1,
                }
                report = {"status":"PASS" if all(checks.values()) else "FAIL",
                          "transport":"stdio", "sdk":"official mcp v1",
                          "checks":checks,"tools":names}
                (out/"teste7.json").write_text(json.dumps(report,indent=2))
                print(json.dumps(report,indent=2),flush=True)
                if report["status"] != "PASS":
                    raise SystemExit(1)

if __name__ == "__main__":
    asyncio.run(main())
