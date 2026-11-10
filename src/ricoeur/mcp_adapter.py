"""Optional MCP adapter for the read-only retrieval contract.

Uses the official MCP Python SDK FastMCP adapter when installed.
The core retrieval contract has no MCP dependency.
"""
from typing import Optional

from .db import get_connection
from .retrieval import search_messages, get_message_context


def build_server():
    from mcp.server.fastmcp import FastMCP
    server = FastMCP("cha2db-ricoeur")

    @server.tool()
    def search_chat_messages(query: str, limit: int = 20,
                             context: int = 1, platform: Optional[str] = None) -> dict:
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
