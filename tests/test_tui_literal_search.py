"""Regression: hyphenated user queries must not be parsed as FTS5 operators."""
import asyncio
import sqlite3

from textual.widgets import DataTable
from ricoeur.db import SCHEMA_SQL
from ricoeur.tui import RicoeurApp


def test_hyphenated_search(tmp_path):
    db = tmp_path / "ricoeur.db"
    conn = sqlite3.connect(db)
    conn.executescript(SCHEMA_SQL)
    conn.execute("INSERT INTO conversations (id, title, platform) VALUES ('c1', 'Contexto da IDE', 'chatgpt')")
    conn.execute("INSERT INTO messages (id, conv_id, role, content) VALUES ('m1', 'c1', 'assistant', 'Marcador agulha-contexto-ide.')")
    conn.commit()
    conn.close()

    async def scenario():
        app = RicoeurApp(home=tmp_path, splash=False)
        async with app.run_test() as pilot:
            app._run_search("agulha-contexto-ide")
            await pilot.pause()
            assert app.query_one("#results", DataTable).row_count == 1
            assert app._row_ids == ["c1"]
    asyncio.run(scenario())
