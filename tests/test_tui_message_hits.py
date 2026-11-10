"""Regression coverage for message-level search presentation."""

import sqlite3

from ricoeur.db import SCHEMA_SQL
from ricoeur.search import fts_search
from ricoeur.tui import ConversationScreen


def test_search_snippet_and_conversation_match():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    conn.execute("INSERT INTO conversations (id, title, platform, message_count) VALUES (?, ?, ?, ?)", ("c1", "SQLite Android", "chatgpt", 2))
    conn.executemany("INSERT INTO messages (id, conv_id, role, content, timestamp) VALUES (?, ?, ?, ?, ?)", [
        ("m1", "c1", "user", "Como funciona SQLite?", "2025-01-01T10:00:00"),
        ("m2", "c1", "assistant", "SQLite é um banco embarcado.", "2025-01-01T10:00:01"),
    ])
    conn.commit()
    results = fts_search(conn, "embarcado")
    assert len(results) == 1
    assert "embarcado" in (results[0].snippet or "").lower()
    transcript = ConversationScreen(conn, "c1", "embarcado")._transcript()
    assert transcript.count("🔎 MATCH") == 1
    assert "SQLite é um banco embarcado." in transcript
    assert "Como funciona SQLite?" in transcript
    conn.close()
