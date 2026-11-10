"""Optional MCP adapter for the read-only retrieval contract.

Requires Python >=3.11 and the official MCP SDK v2 (pip install mcp>=2).
The core retrieval contract has no MCP dependency and works on Termux 3.10.
"""
from __future__ import annotations

from .db import get_connection
from .retrieval import search_messages, get_message_context


def build_server():
    from mcp.server import MCPServer
    server = MCPServer("cha2db-ricoeur")

    @server.tool()
    def search_chat_messages(query: str, limit: int = 20,
                             context: int = 1, platform: str | None = None) -> dict:
        """Search individual chat messages across conversations and providers."""
        conn = get_connection()
        try:
            return search_messages(conn, query, limit, context, platform)
        finally:
            conn.close()

    @server.tool()
    def read_chat_message(message_id: str, context: int = 2) -> dict:
        """Read one identified message and its adjacent messages."""
        conn = get_connection()
        try:
            return get_message_context(conn, message_id, context) or {"error": "not_found"}
        finally:
            conn.close()
    return server


if __name__ == "__main__":
    build_server().run()
