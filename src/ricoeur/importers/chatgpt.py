"""ChatGPT conversation importer.

Handles the JSON export from ChatGPT (Settings > Data Controls > Export Data).
The export contains a conversations.json with a tree structure of messages.
"""

from __future__ import annotations

import json
import io
import sqlite3
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from rich.progress import Progress

from .base import (
    ImportStats,
    insert_conversation,
    insert_message,
    delete_conversation_messages,
    make_message_id,
    resolve_conversation_id,
    resolve_message_id,
    update_conversation_counts,
)
from .branch_index import validate_snapshot, selected_nodes, sync_projection


def import_chatgpt(
    conn: sqlite3.Connection,
    path: Path,
    *,
    update: bool = False,
    since: Optional[str] = None,
    dry_run: bool = False,
    progress: Optional[Progress] = None,
) -> ImportStats:
    """Import conversations from a ChatGPT export."""
    stats = ImportStats()
    # Progress is based on uncompressed JSON bytes, so no costly pre-scan.
    task = progress.add_task("Importing ChatGPT...", total=100) if progress else None

    # Stream individual conversations: never materialize the entire export.
    # Commit at bounded intervals so long imports do not accumulate one huge
    # transaction. Reimport remains idempotent through existing IDs.
    for conv_raw, fraction in _iter_conversations_with_progress(path):
        stats.parsed += 1
        # The batch strategy retains resumability while each individual
        # conversation remains atomic even if the 26th is malformed.
        if dry_run:
            _import_one(conn, conv_raw, stats, update=update, since=since,
                        dry_run=True)
        else:
            conn.execute("SAVEPOINT chatgpt_import_one")
            try:
                _import_one(conn, conv_raw, stats, update=update,
                            since=since, dry_run=False)
                conn.execute("RELEASE SAVEPOINT chatgpt_import_one")
            except BaseException:
                conn.execute("ROLLBACK TO SAVEPOINT chatgpt_import_one")
                conn.execute("RELEASE SAVEPOINT chatgpt_import_one")
                raise
        if not dry_run and stats.parsed % 25 == 0:
            conn.commit()
        if progress and task is not None:
            progress.update(task, completed=min(99.9, fraction * 100),
                            description=f"ChatGPT: {stats.parsed:,} conversations · {fraction * 100:.1f}%")

    if not dry_run:
        update_conversation_counts(conn)
        conn.commit()
    if progress and task is not None:
        progress.update(task, completed=100, description=f"ChatGPT: {stats.parsed:,} conversations · 100%")

    return stats


def _iter_conversations(path: Path):
    """Compatibility iterator returning only conversation objects."""
    for conv, _fraction in _iter_conversations_with_progress(path):
        yield conv


def _iter_conversations_with_progress(path: Path):
    """Stream every conversation JSON member of an official ChatGPT export.

    Progress is measured over the total uncompressed size of conversation
    members, not over unrelated account assets in the ZIP.
    """
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            import re
            members = [
                info for info in zf.infolist()
                if not info.is_dir()
                and re.fullmatch(r"conversations(?:[-_]\d+)?\.json",
                                 Path(info.filename).name, re.IGNORECASE)
            ]
            if not members:
                raise FileNotFoundError("No conversations.json or numbered conversation JSON found in ZIP")
            # Stable ordering and no extraction to disk.
            members.sort(key=lambda info: info.filename)
            total = sum(info.file_size for info in members)
            done = 0
            for info in members:
                with zf.open(info) as binary:
                    with io.TextIOWrapper(binary, encoding="utf-8") as stream:
                        for conv, fraction in _parse_json_array(stream, info.file_size):
                            yield conv, ((done + fraction * info.file_size) / total if total else 1.0)
                done += info.file_size
    else:
        total = path.stat().st_size
        with path.open(encoding="utf-8") as stream:
            yield from _parse_json_array(stream, total)


def _parse_json_array(stream, total_bytes: int):
    decoder = json.JSONDecoder()
    buffer = ""
    position = 0
    eof = False
    bytes_read = 0

    def read_chunk():
        nonlocal bytes_read
        chunk = stream.read(65536)
        bytes_read += len(chunk.encode("utf-8"))
        return chunk

    def skip_space():
        nonlocal buffer, position, eof
        while True:
            while position < len(buffer) and buffer[position].isspace():
                position += 1
            if position < len(buffer) or eof:
                return
            buffer = ""
            position = 0
            chunk = read_chunk()
            if chunk:
                buffer = chunk
            else:
                eof = True

    def next_char():
        skip_space()
        return buffer[position] if position < len(buffer) else None

    if next_char() != "[":
        raise ValueError("Expected a JSON array of conversations")
    position += 1
    first = True
    while True:
        char = next_char()
        if char is None:
            raise ValueError("Unexpected end of JSON array")
        if char == "]":
            position += 1
            if next_char() is not None:
                raise ValueError("Unexpected data after JSON array")
            return
        if not first:
            if char != ",":
                raise ValueError("Expected comma between conversations")
            position += 1
            if next_char() == "]":
                raise ValueError("Trailing comma in JSON array")
        first = False
        while True:
            try:
                item, consumed = decoder.raw_decode(buffer, position)
                position = consumed
                if not isinstance(item, dict):
                    raise ValueError("Expected conversation object")
                # Subtract buffered, not-yet-consumed UTF-8 bytes. This is
                # accurate for multibyte Unicode and ZIP uncompressed sizes.
                consumed_bytes = bytes_read - len(buffer[position:].encode("utf-8"))
                yield item, (consumed_bytes / total_bytes if total_bytes else 1.0)
                buffer = buffer[position:]
                position = 0
                break
            except json.JSONDecodeError as exc:
                if eof:
                    raise ValueError("Invalid conversation JSON") from exc
                chunk = read_chunk()
                if chunk:
                    buffer += chunk
                else:
                    eof = True


def _import_one(
    conn: sqlite3.Connection,
    conv: dict[str, Any],
    stats: ImportStats,
    *,
    update: bool,
    since: Optional[str],
    dry_run: bool,
) -> None:
    native_conv_id = conv.get("id", conv.get("conversation_id", ""))
    conv_id = resolve_conversation_id(conn, "chatgpt", native_conv_id)
    title = conv.get("title", "Untitled")
    create_time = conv.get("create_time")
    update_time = conv.get("update_time")

    created_at = _ts_to_iso(create_time) if create_time else None
    updated_at = _ts_to_iso(update_time) if update_time else None

    if since and created_at and created_at < since:
        stats.skipped += 1
        return

    # The exact same structural/content validation is used for dry run
    # and persist; no "would import" claim before checking the payload.
    nodes, selected = validate_snapshot(conv)
    model = _extract_model(conv)

    if dry_run:
        existing = conn.execute("SELECT 1 FROM conversations WHERE id=?",
                                (conv_id,)).fetchone()
        if existing and not update:
            stats.skipped += 1
        elif existing:
            stats.updated += 1
        else:
            stats.new += 1
        stats.messages += len(_walk_messages(conv))
        return

    inserted = insert_conversation(
        conn,
        id=conv_id,
        title=title,
        platform="chatgpt",
        model=model,
        created_at=created_at,
        updated_at=updated_at,
        update=update,
    )

    if inserted:
        stats.new += 1
    else:
        stats.skipped += 1
        return

    if update:
        # An updated selected path must replace the prior selected projection
        # instead of accumulating mutually exclusive responses in messages.
        delete_conversation_messages(conn, conv_id)

    # Preserve the original tree, including non-selected branches and null roots.
    conn.execute("""CREATE TABLE IF NOT EXISTS chatgpt_nodes (
        conv_id TEXT NOT NULL, node_id TEXT NOT NULL, parent_id TEXT,
        children_json TEXT NOT NULL, message_json TEXT,
        PRIMARY KEY (conv_id, node_id)
    )""")
    for node_id, node in (conv.get("mapping") or {}).items():
        if update:
            conn.execute("""INSERT INTO chatgpt_nodes
                (conv_id, node_id, parent_id, children_json, message_json)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(conv_id,node_id) DO UPDATE SET
                  parent_id=excluded.parent_id,
                  children_json=excluded.children_json,
                  message_json=excluded.message_json""",
                (conv_id,node_id,node.get("parent"),
                 json.dumps(node.get("children",[]),ensure_ascii=False),
                 json.dumps(node.get("message"),ensure_ascii=False)))
        else:
            conn.execute("""INSERT OR IGNORE INTO chatgpt_nodes
                (conv_id, node_id, parent_id, children_json, message_json)
                VALUES (?, ?, ?, ?, ?)""",
                (conv_id,node_id,node.get("parent"),
                 json.dumps(node.get("children",[]),ensure_ascii=False),
                 json.dumps(node.get("message"),ensure_ascii=False)))

    # FTS5 sidecar contains *only* nonselected branches, never the default
    # message path; raw chatgpt_nodes remains the original source structure.
    sync_projection(conn, conv_id, conv, selected=selected)

    # Keep the selected path searchable, including empty messages.
    messages = _walk_messages(conv)
    for i, msg in enumerate(messages):
        native_msg_id = msg.get("id") or make_message_id(conv_id, i)
        msg_id = resolve_message_id(conn, "chatgpt", conv_id, native_msg_id)
        role = msg.get("role", "unknown")
        content = _extract_content(msg)
        timestamp = _ts_to_iso(msg.get("create_time")) if msg.get("create_time") else created_at

        inserted, _ = insert_message(
            conn, id=msg_id, conv_id=conv_id, role=role,
            content=content, timestamp=timestamp,
        )
        if inserted:
            stats.messages += 1


def _walk_messages(conv: dict[str, Any]) -> list[dict[str, Any]]:
    """Walk the ChatGPT message tree to extract messages in order."""
    mapping = conv.get("mapping", {})
    if not mapping:
        return []

    # Build parent->children map and find root
    children_map: dict[str, list[str]] = {}
    root = None
    for node_id, node in mapping.items():
        parent = node.get("parent")
        if parent is None:
            root = node_id
        else:
            children_map.setdefault(parent, []).append(node_id)

    if root is None:
        return []

    # ChatGPT identifies the selected leaf explicitly. Following the
    # parent chain is more reliable than assuming the last sibling is active.
    selected = conv.get("current_node")
    if selected in mapping:
        path = []
        seen = set()
        cursor = selected
        while cursor in mapping and cursor not in seen:
            seen.add(cursor)
            path.append(cursor)
            node = mapping[cursor]
            if not isinstance(node, dict):
                break
            cursor = node.get("parent")
            if cursor is None:
                # Valid chain terminating at a declared root.
                path.reverse()
                selected_messages = []
                for item_id in path:
                    item = mapping[item_id]
                    msg = item.get("message")
                    if msg and isinstance(msg, dict) and msg.get("content"):
                        author = msg.get("author", {})
                        role = author.get("role", "unknown")
                        if role in ("user", "assistant", "system", "tool"):
                            selected_messages.append({**msg, "role": role})
                return selected_messages

    # Compatibility fallback for malformed/older exports without current_node.
    messages = []
    stack = [root]
    while stack:
        node_id = stack.pop()
        node = mapping.get(node_id, {})
        msg = node.get("message")
        if msg and msg.get("content"):
            author = msg.get("author", {})
            role = author.get("role", "unknown")
            if role in ("user", "assistant", "system", "tool"):
                messages.append({**msg, "role": role})

        # Add children to stack (reversed so first child is processed first)
        # Prefer the explicit children order from the export. Mapping insertion
        # order is not a reliable indicator of the selected/default branch.
        kids = node.get("children")
        if not isinstance(kids, list):
            kids = children_map.get(node_id, [])
        if kids:
            stack.append(kids[-1])

    return messages


def _extract_content(msg: dict[str, Any]) -> str:
    """Extract text content from a ChatGPT message."""
    content = msg.get("content", {})
    if isinstance(content, str):
        return content
    parts = content.get("parts", [])
    text_parts = []
    for part in parts:
        if isinstance(part, str):
            text_parts.append(part)
        elif isinstance(part, dict) and part.get("content_type") == "text":
            text_parts.append(part.get("text", ""))
    return "\n".join(text_parts)


def _extract_model(conv: dict[str, Any]) -> Optional[str]:
    """Try to extract the model slug from the conversation."""
    # Check top-level
    if "default_model_slug" in conv:
        return conv["default_model_slug"]
    # Walk messages looking for model_slug in metadata
    mapping = conv.get("mapping", {})
    for node in mapping.values():
        msg = node.get("message")
        if not isinstance(msg, dict):
            continue  # ChatGPT exports may contain a root node with message=null
        meta = msg.get("metadata")
        if not isinstance(meta, dict):
            continue
        slug = meta.get("model_slug")
        if slug:
            return slug
    return None


def _ts_to_iso(ts: float | int | None) -> Optional[str]:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
