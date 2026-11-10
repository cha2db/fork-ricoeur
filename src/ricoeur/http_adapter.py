"""Read-only local HTTP adapter over the same retrieval contract as MCP."""
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from .db import get_connection
from .retrieval import search_messages, get_message_context

app = FastAPI(title="Cha2db/Ricoeur local search", version="0.1")

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/search")
def search(q: str, limit: int = Query(20, ge=1, le=200),
           context: int = Query(1, ge=0, le=10),
           platform: Optional[str] = None):
    conn = get_connection()
    try:
        return search_messages(conn, q, limit, context, platform)
    except (ValueError, Exception) as exc:
        if isinstance(exc, ValueError) or exc.__class__.__name__ == "OperationalError":
            raise HTTPException(status_code=400, detail=str(exc))
        raise
    finally:
        conn.close()

@app.get("/api/messages/{message_id}")
def message(message_id: str, context: int = Query(2, ge=0, le=20)):
    conn = get_connection()
    try:
        result = get_message_context(conn, message_id, context)
        if result is None:
            raise HTTPException(status_code=404, detail="message not found")
        return result
    finally:
        conn.close()


@app.get("/api/conversations")
def conversations(limit: int = Query(100, ge=1, le=500)):
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT id, title, platform, created_at, updated_at
               FROM conversations ORDER BY COALESCE(updated_at, created_at, '') DESC, rowid DESC
               LIMIT ?""", (limit,)).fetchall()
        return {"conversations": [dict(row) for row in rows]}
    finally:
        conn.close()


@app.get("/api/conversations/{conversation_id}")
def conversation(conversation_id: str, limit: int = Query(500, ge=1, le=2000)):
    conn = get_connection()
    try:
        conv = conn.execute(
            "SELECT id,title,platform FROM conversations WHERE id=?", (conversation_id,)
        ).fetchone()
        if conv is None:
            raise HTTPException(status_code=404, detail="conversation not found")
        rows = conn.execute(
            """SELECT id,conv_id,role,content,timestamp FROM messages
               WHERE conv_id=? ORDER BY timestamp,rowid LIMIT ?""",
            (conversation_id, limit + 1)
        ).fetchall()
        return {"conversation": dict(conv),
                "messages": [dict(row) for row in rows[:limit]],
                "truncated": len(rows) > limit}
    finally:
        conn.close()


@app.get("/", response_class=HTMLResponse)
def index():
    return (Path(__file__).with_name("chat_ui.html")).read_text(encoding="utf-8")
