"""Read-only message retrieval contract shared by CLI, GUI and MCP adapters.

The indexed FTS5 query returns identified hits.  Context neighbors use a
single bounded-window query for the entire hit batch; do not reread a complete
conversation for each hit.
"""
from __future__ import annotations

import sqlite3


def _message(row):
    return {key: row[key] for key in ("id", "conv_id", "role", "content", "timestamp")}


def _windows(conn: sqlite3.Connection, ids: list[str],
             conv_ids: list[str], context: int) -> dict[str, dict]:
    """Get exact neighboring messages for several hits with one SQL query.

    ROW_NUMBER follows the original 'ORDER BY timestamp,rowid' contract.
    The query only returns up to 2*context+1 messages for each match.
    """
    if not ids:
        return {}
    if len(ids) > 200:
        raise ValueError("context batch exceeds limit of 200")
    idmarks = ",".join("?" for _ in ids)
    convmarks = ",".join("?" for _ in conv_ids)
    sql = f"""
      WITH numbered AS (
        SELECT id,conv_id,role,content,timestamp,
               ROW_NUMBER() OVER (
                   PARTITION BY conv_id ORDER BY timestamp,rowid
               ) AS pos
        FROM messages WHERE conv_id IN ({convmarks})
      ),
      targets AS (
        SELECT id,conv_id,pos FROM numbered WHERE id IN ({idmarks})
      )
      SELECT t.id AS target_id,t.pos AS target_pos,
             n.id,n.conv_id,n.role,n.content,n.timestamp,n.pos
      FROM targets t JOIN numbered n
        ON n.conv_id=t.conv_id
       AND n.pos BETWEEN t.pos-? AND t.pos+?
      ORDER BY t.id,n.pos
    """
    found = {}
    for row in conn.execute(sql, [*conv_ids, *ids, context, context]):
        bucket = found.setdefault(row["target_id"],
                                  {"before": [], "after": [], "message": None})
        item = _message(row)
        if row["pos"] < row["target_pos"]:
            bucket["before"].append(item)
        elif row["pos"] > row["target_pos"]:
            bucket["after"].append(item)
        else:
            bucket["message"] = item
    return found


def search_messages(conn: sqlite3.Connection, query: str, limit: int = 20,
                    context: int = 1, platform: str | None = None) -> dict:
    """Return message-level FTS hits with bounded adjacent messages.

    The query uses SQLite FTS5 syntax. Invalid syntax propagates as an error.
    No write or migration is performed.  The neighbor query is independent of
    the number of hits in one conversation (one query for the full batch).
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
    contexts = _windows(conn, [r["id"] for r in matches],
                        list(dict.fromkeys(r["conv_id"] for r in matches)),
                        context)
    hits = []
    for match in matches:
        neighbors = contexts[match["id"]]
        hits.append({
            "message": _message(match),
            "conversation": {"id": match["conv_id"], "title": match["title"],
                             "platform": match["platform"]},
            "before": neighbors["before"],
            "after": neighbors["after"],
            "rank": match["rank"],
        })
    return {"query": query, "count": len(hits), "hits": hits}


def get_message_context(conn: sqlite3.Connection, message_id: str,
                        context: int = 2) -> dict | None:
    if not 0 <= context <= 20:
        raise ValueError("context must be 0..20")
    conv = conn.execute(
        """SELECT c.id,c.title,c.platform FROM messages m
           JOIN conversations c ON c.id=m.conv_id WHERE m.id=?""",
        (message_id,),
    ).fetchone()
    if conv is None:
        return None
    context_data = _windows(conn, [message_id], [conv["id"]], context)[message_id]
    return {"message": context_data["message"],
            "conversation": dict(conv),
            "before": context_data["before"],
            "after": context_data["after"]}
