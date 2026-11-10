"""Teste 3: idempotência persistente e relatório de lacunas de fidelidade."""
import json
import sqlite3
import time
from pathlib import Path
from rich.progress import Progress
from ricoeur.db import init_db
from ricoeur.importers.chatgpt import import_chatgpt
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from run_account_zip_android import conversation
import zipfile

root = Path(__file__).resolve().parents[1]
out = root / "_dev" / "results"
out.mkdir(parents=True, exist_ok=True)
archive = out / "conta-sintetica.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
    for name, indexes in [
        ("conversations.json", range(0, 3)),
        ("conversations-1.json", range(3, 6)),
        ("sub/conversations_2.json", range(6, 8)),
    ]:
        z.writestr(name, json.dumps([conversation(i) for i in indexes], ensure_ascii=False))
    z.writestr("assets/attachment.txt", "synthetic attachment")
home = out / "db-persistente"
home.mkdir(exist_ok=True)
# Reset only this isolated test DB so every run has reproducible baseline.
dbfile = home / "ricoeur.db"
if dbfile.exists():
    dbfile.unlink()
conn = init_db(home)
records = []
try:
    for run in range(1, 5):
        started = time.perf_counter()
        with Progress() as progress:
            stats = import_chatgpt(conn, archive, progress=progress)
        nconv = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
        nmsg = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        records.append({"run": run, "conversations": nconv, "messages": nmsg,
                        "new": stats.new, "seconds": round(time.perf_counter()-started, 3)})
    result = {"status": "PASS" if all(
        r["conversations"] == 8 and r["messages"] == 48 and
        (r["new"] == 8 if r["run"] == 1 else r["new"] == 0)
        for r in records) else "FAIL",
        "runs": records,
        "source_messages": 48,
        "known_gaps": {"empty_messages_missing": 8, "alternate_branches_not_preserved": 1,
                       "attachments_not_imported": True},
        "note": "PASS means idempotence only; NOT full-fidelity approval."}
    (out / "teste3.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
    if result["status"] != "PASS":
        raise SystemExit(1)
finally:
    conn.close()
