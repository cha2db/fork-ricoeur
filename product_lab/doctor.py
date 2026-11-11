"""Cha2db PRODUCT-017: read-only SQLite health/repair prescreen.

Uses SQLite's native PRAGMA quick_check/foreign_key_check and metadata,
not a new database engine. Never automatically repairs or writes any data.
Reports counts only: no conversation content, IDs, titles, or user paths.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import json
import sqlite3
from pathlib import Path


def _check(out, code, passed, observed=None, required=True, description=""):
    out.append({
        "code": code, "status": "PASS" if passed else ("FAIL" if required else "WARN"),
        "required": required, "observed": observed, "description": description,
    })


def diagnose(db_path, *, thorough=False):
    path = Path(db_path).resolve()
    result = {
        "schema_version": "cha2db.doctor.v1",
        "mode": "read_only",
        "target": "local_sqlite",
        "status": "FAIL",
        "counts": {},
        "checks": [],
        "suggestions": [],
        "limit": "Quick check does not validate complete FTS token index or original export provenance",
    }
    if not path.is_file():
        _check(result["checks"], "db_exists", False, "not_a_file")
        result["suggestions"].append("Locate the existing DB; this tool never creates one.")
        return result
    checks = result["checks"]
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only=ON")
        pragma = "integrity_check" if thorough else "quick_check"
        integrity = conn.execute("PRAGMA " + pragma).fetchall()
        ok = len(integrity) == 1 and integrity[0][0] == "ok"
        _check(checks, "native_sqlite_" + pragma, ok,
               "ok" if ok else "database_page_errors", required=True,
               description="Native SQLite structural check; does not repair.")
        objects = {r["name"]: r["type"] for r in conn.execute(
            "SELECT name,type FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'")}
        tables = {"conversations", "messages", "messages_fts"}
        for name in sorted(tables):
            _check(checks, "table_" + name, objects.get(name) in {"table", "view"},
                   "present" if name in objects else "missing")
        if tables.issubset(objects):
            counts = {
                "conversations": conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0],
                "messages": conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0],
            }
            result["counts"].update(counts)
            orphans = conn.execute(
                "SELECT COUNT(*) FROM messages m LEFT JOIN conversations c ON c.id=m.conv_id "
                "WHERE c.id IS NULL").fetchone()[0]
            _check(checks, "message_conversation_orphans", orphans == 0, orphans,
                   description="Every message must have a conversation.")
            trigger_names = {"messages_ai", "messages_ad", "messages_au"}
            missing = sorted(trigger_names - {name for name, kind in objects.items()
                                             if kind == "trigger"})
            _check(checks, "fts5_update_triggers", not missing,
                   missing, required=False,
                   description="Expected FTS5 append/delete/update triggers in baseline schema.")
            if objects.get("attachments") == "table":
                cols = {r["name"] for r in conn.execute("PRAGMA table_info(attachments)")}
                if {"conv_id","msg_id"} <= cols:
                    invalid = conn.execute(
                        """SELECT COUNT(*) FROM attachments a
                        LEFT JOIN conversations c ON c.id=a.conv_id
                        LEFT JOIN messages m ON m.id=a.msg_id
                        WHERE c.id IS NULL OR (a.msg_id IS NOT NULL AND m.id IS NULL)"""
                    ).fetchone()[0]
                    _check(checks, "attachment_references", invalid == 0, invalid,
                           description="Attachment conversation/message references.")
                    result["counts"]["attachments"] = conn.execute(
                        "SELECT COUNT(*) FROM attachments").fetchone()[0]
        fk_violations = conn.execute("PRAGMA foreign_key_check").fetchall()
        _check(checks, "sqlite_foreign_key_check", len(fk_violations) == 0,
               len(fk_violations), required=True,
               description="Native SQLite FK check across tables.")
    critical_fail = [x for x in checks if x["required"] and x["status"] == "FAIL"]
    result["status"] = "FAIL" if critical_fail else (
        "PASS_WITH_WARNINGS" if any(x["status"] == "WARN" for x in checks) else "PASS")
    if critical_fail:
        result["suggestions"] = [
            "Preserve the original DB and WAL/SHM sidecars before attempting recovery.",
            "Restore or rebuild a COPY from verified raw exports; never overwrite the original.",
            "Retest original conversation IDs, branch counts, message order, and attachments.",
        ]
    return result


def main():
    p = argparse.ArgumentParser(description="Read-only health prescreen; no repair operations")
    p.add_argument("--db", required=True)
    p.add_argument("--full", action="store_true",
                   help="Use native PRAGMA integrity_check instead of quick_check")
    args = p.parse_args()
    try:
        report = diagnose(args.db, thorough=args.full)
    except (sqlite3.DatabaseError, OSError) as exc:
        report = {
            "schema_version": "cha2db.doctor.v1", "mode": "read_only",
            "status": "FAIL", "checks": [{"code": "database_open_or_check", "status": "FAIL",
                                        "reason_class": type(exc).__name__}],
            "suggestions": ["Use a verified snapshot; do not repair in place."],
        }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["status"].startswith("PASS") else 1)


if __name__ == "__main__":
    main()
