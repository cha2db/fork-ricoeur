"""Generate and import an isolated synthetic full-account ZIP on Termux."""
import json
import sqlite3
import tempfile
import time
import zipfile
from pathlib import Path

from rich.progress import Progress
from ricoeur.db import init_db
from ricoeur.importers.chatgpt import import_chatgpt


def conversation(i):
    cid = f"account-fire-{i:02d}"
    mapping = {"root": {"id": "root", "parent": None, "children": ["m0"], "message": None}}
    parts = [
        "Pergunta com acentuação, 日本語, العربية e emoji 🔎.",
        "Resposta com Markdown **forte** e código `SELECT * FROM messages`.",
        "Anexo de imagem fictício: assets/synthetic-photo.png.",
        "Anexo de áudio fictício: assets/synthetic-audio.wav.",
        "",  # Empty content: known fidelity gap
        "Mensagem final com marcador ZIP-NEEDLE-ACCOUNT.",
    ]
    for j, body in enumerate(parts):
        mapping[f"m{j}"] = {
            "id": f"m{j}", "parent": "root" if j == 0 else f"m{j-1}",
            "children": [f"m{j+1}"] if j < len(parts)-1 else [],
            "message": {
                "id": f"{cid}-msg-{j}", "author": {"role": "user" if j % 2 == 0 else "assistant"},
                "create_time": 1700000000 + i * 86400 + j,
                "content": {"content_type": "text", "parts": [body]},
                "metadata": {"attachments": [{"name": "synthetic-photo.png"}]} if j == 2 else {},
            },
        }
    if i == 2:
        mapping["side"] = {
            "id": "side", "parent": "m1", "children": [],
            "message": {
                "id": f"{cid}-side", "author": {"role": "assistant"},
                "content": {"parts": ["Alternative branch must be audited separately."]},
            },
        }
        mapping["m1"]["children"].insert(0, "side")
    return {
        "id": cid, "title": f"Conta sintética — conversa {i}",
        "create_time": 1700000000 + i * 86400,
        "update_time": 1700000100 + i * 86400,
        "mapping": mapping,
    }


def main():
    out = Path("stress-results")
    out.mkdir(exist_ok=True)
    archive = out / "chatgpt-account-synthetic.zip"
    conversations = [conversation(i) for i in range(8)]
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in [
            ("conversations.json", conversations[:3]),
            ("conversations-1.json", conversations[3:6]),
            ("nested/conversations_2.json", conversations[6:]),
        ]:
            z.writestr(name, json.dumps(data, ensure_ascii=False))
        z.writestr("user.json", json.dumps({"email": "synthetic@example.invalid"}))
        z.writestr("chat.html", "<html>synthetic, do not import as messages</html>")
        z.writestr("assets/synthetic-notes.txt", "Synthetic attachment fixture")
        z.writestr("assets/synthetic-photo.png", b"NOT_A_REAL_IMAGE")
        z.writestr("assets/synthetic-audio.wav", b"NOT_A_REAL_AUDIO")
    print(f"ZIP generated: {archive} ({archive.stat().st_size} bytes)", flush=True)

    with tempfile.TemporaryDirectory(prefix="account-fire-") as tmp:
        home = Path(tmp)
        conn = init_db(home)
        try:
            started = time.perf_counter()
            with Progress() as progress:
                first = import_chatgpt(conn, archive, progress=progress)
            elapsed = time.perf_counter() - started
            conversations_found = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
            messages_found = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            # Known limitation: 8 empty messages intentionally skipped.
            expected_messages = 8 * 5
            with Progress() as progress:
                second = import_chatgpt(conn, archive, progress=progress)
            after = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            report = {
                "status": "PASS" if (
                    conversations_found == 8 and messages_found == expected_messages
                    and after == messages_found and second.new == 0
                ) else "FAIL",
                "conversations": conversations_found,
                "messages_imported": messages_found,
                "messages_in_source": 48,
                "empty_messages_not_preserved": 8,
                "alternate_branch_not_preserved": 1,
                "attachment_files_in_zip": 3,
                "attachment_links_verified": False,
                "reimport_messages": after,
                "seconds": round(elapsed, 3),
                "zip_path": str(archive),
            }
            report_path = out / "account-zip-report.json"
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
            print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
            print(f"Report: {report_path}", flush=True)
            if report["status"] != "PASS":
                raise SystemExit(1)
        finally:
            conn.close()


if __name__ == "__main__":
    main()
