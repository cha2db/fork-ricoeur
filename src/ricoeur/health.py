"""Non-destructive FTS5 integrity verification of external-content indexes.

SQLite's 'integrity-check' FTS5 command is a write statement. NEVER run it
on a user's actual archive. Make a consistent SQLite online-backup snapshot,
run the command against only the temporary snapshot, and discard the copy.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile


def check_fts_snapshot(source):
    source=Path(source).resolve()
    if not source.is_file():
        return {"status":"FAIL","check":"FTS5_EXTERNAL_CONTENT",
                "reason":"SOURCE_NOT_FOUND","source_modified":False}
    with tempfile.TemporaryDirectory(prefix="cha2db-fts-audit-") as td:
        copy=Path(td)/"snapshot.sqlite3"
        with closing(sqlite3.connect(source.as_uri()+"?mode=ro", uri=True)) as original:
            original.execute("PRAGMA query_only=ON")
            with closing(sqlite3.connect(copy)) as snapshot:
                original.backup(snapshot)
                try:
                    snapshot.execute(
                      "INSERT INTO messages_fts(messages_fts,rank) VALUES('integrity-check',1)"
                    )
                    snapshot.rollback()
                    return {
                        "status":"PASS","check":"FTS5_EXTERNAL_CONTENT",
                        "scope":"consistency_with_messages_content_on_transactional_snapshot",
                        "source_modified":False,
                    }
                except sqlite3.DatabaseError as exc:
                    snapshot.rollback()
                    return {
                        "status":"FAIL","check":"FTS5_EXTERNAL_CONTENT",
                        "reason":type(exc).__name__,
                        "source_modified":False,
                    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--db",type=Path,required=True)
    options=parser.parse_args()
    try:
        result=check_fts_snapshot(options.db)
    except (OSError,sqlite3.DatabaseError) as exc:
        result={"status":"FAIL","check":"FTS5_EXTERNAL_CONTENT",
                "reason":type(exc).__name__,"source_modified":False}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result["status"]=="PASS" else 1)


if __name__=="__main__":
    main()
