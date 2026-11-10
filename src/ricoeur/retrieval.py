"""Read-only message-level retrieval contract; independent of MCP and TUI."""
from __future__ import annotations

import sqlite3


def _message(row):
    return {key: row[key] for key in ("id", "conv_id", "role", "content", "timestamp")}


def search_messages(conn: sqlite3.Connection, query: str, limit: int = 20,
                    context: int = 1, platform: str | None = None) -> dict:
    """Return all message-level FTS hits with adjacent messages.

    This is a reusable driver contract for CLI, GUI, MCP and A2A adapters.
    The search query uses SQLite FTS5 syntax. Invalid syntax returns an error.
    """
    if not query or not query.strip():
        raise ValueError("query must not be empty")
    if not 1 <= limit <= 200 or not 0 <= context <= 10:
        raise ValueError("limit must be 1..200 and context must be 0..10")
    sql = """
        SELECT m.id, m.conv_id, m.role, m.content, m.timestamp,
               c.title, c.platform, bm25(messages_fts) AS rank
        FROM messages_fts
        JOIN messages m ON m.rowid = messages_fts.rowid
        JOIN conversations c ON c.id = m.conv_id
        WHERE messages_fts MATCH ?
    """
    args = [query]
    if platform:
        sql += " AND c.platform = ?"
        args.append(platform)
    sql += " ORDER BY rank, m.rowid LIMIT ?"
    args.append(limit)
    matches = conn.execute(sql, args).fetchall()
    hits = []
    for match in matches:
        messages = conn.execute(
            """SELECT id, conv_id, role, content, timestamp FROM messages
               WHERE conv_id = ? ORDER BY timestamp, rowid""",
            (match["conv_id"],),
        ).fetchall()
        index = next(i for i, row in enumerate(messages) if row["id"] == match["id"])
        hits.append({
            "message": _message(match),
            "conversation": {"id": match["conv_id"], "title": match["title"],
                             "platform": match["platform"]},
            "before": [_message(row) for row in messages[max(0, index-context):index]],
            "after": [_message(row) for row in messages[index+1:index+1+context]],
            "rank": match["rank"],
        })
    return {"query": query, "count": len(hits), "hits": hits}


def get_message_context(conn: sqlite3.Connection, message_id: str,
                        context: int = 2) -> dict | None:
    if not 0 <= context <= 20:
        raise ValueError("context must be 0..20")
    row = conn.execute("SELECT conv_id FROM messages WHERE id = ?", (message_id,)).fetchone()
    if row is None:
        return None
    rows = conn.execute(
        """SELECT id, conv_id, role, content, timestamp FROM messages
           WHERE conv_id = ? ORDER BY timestamp, rowid""", (row["conv_id"],)
    ).fetchall()
    idx = next(i for i, item in enumerate(rows) if item["id"] == message_id)
    conv = conn.execute("SELECT id,title,platform FROM conversations WHERE id = ?",
                        (row["conv_id"],)).fetchone()
    return {"message": _message(rows[idx]),
            "conversation": dict(conv),
            "before": [_message(x) for x in rows[max(0, idx-context):idx]],
            "after": [_message(x) for x in rows[idx+1:idx+1+context]]}
