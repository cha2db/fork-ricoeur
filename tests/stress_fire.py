"""Deterministic, isolated stress test for the ChatGPT importer and FTS5.

Run from the repository root:
    python tests/stress_fire.py --conversations 1000 --messages 100 --size 2048
Use --conversations 10000 --messages 200 --size 4096 for a deliberately extreme run.
Creates a temporary SQLite database; does not touch ~/.ricoeur.
"""
from __future__ import annotations

import argparse
import json
import random
import sqlite3
import tempfile
import time
from pathlib import Path

from rich.progress import Progress
from ricoeur.db import init_db
from ricoeur.importers.chatgpt import import_chatgpt
from ricoeur.search import fts_search

ALPHABETS = [
    "Português: ação, informação, educação, São Paulo.",
    "English: reliability, retrieval, concurrency.",
    "Español: investigación, programación, búsqueda.",
    "日本語: 検索と会話の履歴。",
    "العربية: البحث في المحادثات.",
    "Emoji: 🔎🧪🧵📚",
    "Markdown: **bold** _italic_ [link](https://example.org).",
    "Code: `SELECT * FROM messages WHERE id = ?;`",
    "JSON: {\"nested\": [1, 2, {\"ok\": true}]}",
    "CSV: a,b,c\\n1,2,3",
    "HTML: <section><p>literal</p></section>",
    "Special: apostrophe ' quotes \" backslash \\\\ and tabs\\t.",
]


def generate(nconv: int, nmsg: int, size: int, seed: int):
    rng = random.Random(seed)
    for ci in range(nconv):
        conv_id = f"fire-{seed}-{ci:06d}"
        mapping = {"root": {"id": "root", "parent": None, "children": ["m0"], "message": None}}
        for mi in range(nmsg):
            nid = f"m{mi}"
            role = ("user", "assistant", "system", "tool")[mi % 4]
            text = f"conversation={ci} message={mi} role={role} "
            text += ALPHABETS[(ci + mi) % len(ALPHABETS)]
            if mi % 37 == 0:
                text += "\\n```python\\nprint('fire')\\n```"
            if mi == nmsg // 2:
                text += f" FIRE-NEEDLE-{ci:06d} "
            if mi % 41 == 0:
                text += " repeated-token" * 8
            # Preserve search marker and original content; only pad to requested size.
            text = text + " " + ("x" * max(0, size - len(text)))
            if mi % 97 == 96:
                text = ""  # deliberately empty message, not persisted by current importer
            mapping[nid] = {
                "id": nid, "parent": "root" if mi == 0 else f"m{mi-1}",
                "children": [f"m{mi+1}"] if mi + 1 < nmsg else [],
                "message": {
                    "id": f"{conv_id}-msg-{mi:05d}",
                    "author": {"role": role},
                    "create_time": 1700000000 + ci * 3600 + mi,
                    "content": {"content_type": "text", "parts": [text]},
                    "metadata": {"model_slug": "stress-model"},
                },
            }
        # Side branch: intentionally non-default; should not appear in main path.
        if nmsg >= 3 and ci % 5 == 0:
            mapping["side"] = {
                "id": "side", "parent": "m1", "children": [],
                "message": {
                    "id": f"{conv_id}-side", "author": {"role": "assistant"},
                    "create_time": 1700000000 + ci * 3600 + 2,
                    "content": {"parts": ["SIDE-BRANCH-NOT-DEFAULT"]},
                },
            }
            mapping["m1"]["children"].insert(0, "side")
        yield {
            "id": conv_id, "title": f"Stress {ci} — {ALPHABETS[ci % len(ALPHABETS)]}",
            "create_time": 1700000000 + ci * 3600,
            "update_time": 1700000000 + ci * 3600 + nmsg,
            "mapping": mapping,
        }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--conversations", type=int, default=1000)
    p.add_argument("--messages", type=int, default=100)
    p.add_argument("--size", type=int, default=2048, help="Approximate characters per message")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--keep", action="store_true", help="Keep temporary test directory")
    args = p.parse_args()
    if min(args.conversations, args.messages, args.size) <= 0:
        p.error("all size parameters must be positive")
    work = Path(tempfile.mkdtemp(prefix="ricoeur-fire-"))
    source = work / "conversations.json"
    home = work / "home"
    home.mkdir()
    started = time.perf_counter()
    # Stream JSON generation to avoid retaining the entire corpus in RAM.
    with source.open("w", encoding="utf-8") as out:
        out.write("[")
        for i, conv in enumerate(generate(args.conversations, args.messages, args.size, args.seed)):
            if i:
                out.write(",")
            json.dump(conv, out, ensure_ascii=False)
        out.write("]")
    generation_s = time.perf_counter() - started
    conn = init_db(home)
    try:
        t0 = time.perf_counter()
        with Progress() as progress:
            stats = import_chatgpt(conn, source, progress=progress)
        import_s = time.perf_counter() - t0
        actual = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        expected = args.conversations * (args.messages - args.messages // 97)
        t1 = time.perf_counter()
        needle = f"FIRE-NEEDLE-{args.conversations//2:06d}"
        results = fts_search(conn, '"' + needle + '"')
        search_s = time.perf_counter() - t1
        t2 = time.perf_counter()
        again = import_chatgpt(conn, source)
        reimport_s = time.perf_counter() - t2
        after = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        report = {
            "status": "PASS" if (
                stats.new == args.conversations and actual == expected
                and len(results) == 1 and results[0].conv_id == f"fire-{args.seed}-{args.conversations//2:06d}"
                and after == actual and again.new == 0
            ) else "FAIL",
            "input": vars(args),
            "source_bytes": source.stat().st_size,
            "generation_seconds": round(generation_s, 3),
            "import_seconds": round(import_s, 3),
            "search_seconds": round(search_s, 3),
            "reimport_seconds": round(reimport_s, 3),
            "conversations_imported": stats.new,
            "messages_expected": expected,
            "messages_actual": actual,
            "search_hits": len(results),
            "messages_after_reimport": after,
            "directory": str(work) if args.keep else "(removed)",
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        (work / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
        if report["status"] != "PASS":
            raise SystemExit(1)
    finally:
        conn.close()
        if not args.keep:
            import shutil
            shutil.rmtree(work)


if __name__ == "__main__":
    main()
