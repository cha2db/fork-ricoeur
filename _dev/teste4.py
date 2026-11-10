"""Teste 4: fidelidade de mensagens vazias e árvore completa."""
import json
import sqlite3
import sys
import tempfile
import zipfile
from pathlib import Path
from rich.progress import Progress
from ricoeur.db import init_db
from ricoeur.importers.chatgpt import import_chatgpt

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "tests"))
from run_account_zip_android import conversation

out = root / "_dev" / "results"
out.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix="teste4-") as temp:
    home = Path(temp)
    archive = home / "conta.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("conversations.json", json.dumps([conversation(i) for i in range(8)], ensure_ascii=False))
    conn = init_db(home)
    try:
        with Progress() as progress:
            first = import_chatgpt(conn, archive, progress=progress)
        nconv = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
        nmsg = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        empty = conn.execute("SELECT COUNT(*) FROM messages WHERE content = ''").fetchone()[0]
        nodes = conn.execute("SELECT COUNT(*) FROM chatgpt_nodes").fetchone()[0]
        side = conn.execute("SELECT COUNT(*) FROM chatgpt_nodes WHERE node_id = 'side'").fetchone()[0]
        with Progress() as progress:
            second = import_chatgpt(conn, archive, progress=progress)
        after = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        nodes_after = conn.execute("SELECT COUNT(*) FROM chatgpt_nodes").fetchone()[0]
        result = {
            "status": "PASS" if (nconv, nmsg, empty, nodes, side, after, nodes_after, second.new)
            == (8, 48, 8, 57, 1, 48, 57, 0) else "FAIL",
            "conversations": nconv, "messages": nmsg, "empty_messages": empty,
            "tree_nodes": nodes, "alternate_branch_nodes": side,
            "after_reimport_messages": after, "after_reimport_nodes": nodes_after,
            "attachment_fidelity": "NOT TESTED",
            "note": "Tree nodes stored separately; alternate branches are not yet searchable."
        }
        (out / "teste4.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
        if result["status"] != "PASS":
            raise SystemExit(1)
    finally:
        conn.close()
