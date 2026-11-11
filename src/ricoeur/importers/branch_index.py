"""ChatGPT alternate-branch search projection (SQLite FTS5, no LLM).

This table is a *derived* projection.  Original chatgpt_nodes remains the
source of truth, and selected-path messages remain in ricoeur.messages.
Each alternate result carries a reversible reference to (conv_id,node_id).
"""
from __future__ import annotations

import base64
import json
import sqlite3


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS chatgpt_branch_messages (
    conv_id TEXT NOT NULL REFERENCES conversations(id),
    node_id TEXT NOT NULL,
    parent_id TEXT,
    source_message_id TEXT,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT,
    PRIMARY KEY(conv_id,node_id)
);
CREATE INDEX IF NOT EXISTS idx_chatgpt_branch_messages_conv
    ON chatgpt_branch_messages(conv_id);
CREATE VIRTUAL TABLE IF NOT EXISTS chatgpt_branch_fts USING fts5(
    content, content='chatgpt_branch_messages', content_rowid='rowid'
);
CREATE TRIGGER IF NOT EXISTS chatgpt_branch_ai AFTER INSERT ON chatgpt_branch_messages
BEGIN
    INSERT INTO chatgpt_branch_fts(rowid,content) VALUES (new.rowid,new.content);
END;
CREATE TRIGGER IF NOT EXISTS chatgpt_branch_ad AFTER DELETE ON chatgpt_branch_messages
BEGIN
    INSERT INTO chatgpt_branch_fts(chatgpt_branch_fts,rowid,content)
        VALUES ('delete',old.rowid,old.content);
END;
CREATE TRIGGER IF NOT EXISTS chatgpt_branch_au AFTER UPDATE ON chatgpt_branch_messages
BEGIN
    INSERT INTO chatgpt_branch_fts(chatgpt_branch_fts,rowid,content)
        VALUES ('delete',old.rowid,old.content);
    INSERT INTO chatgpt_branch_fts(rowid,content) VALUES (new.rowid,new.content);
END;
"""


def _parts(message):
    content = message.get("content")
    if isinstance(content, str):
        return content
    if not isinstance(content, dict):
        raise ValueError("invalid message content")
    fragments = content.get("parts", [])
    if not isinstance(fragments, list):
        raise ValueError("invalid message parts")
    texts = []
    for part in fragments:
        if isinstance(part, str):
            texts.append(part)
        elif isinstance(part, dict) and part.get("content_type") == "text":
            value = part.get("text", "")
            if not isinstance(value, str):
                raise ValueError("invalid text part")
            texts.append(value)
    return "\n".join(texts)


def _to_iso(value):
    if value is None:
        return None
    from datetime import datetime, timezone
    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()


def _normalize(node):
    if not isinstance(node, dict):
        raise ValueError("invalid ChatGPT node")
    message = node.get("message")
    if message is None:
        return None
    if not isinstance(message, dict):
        raise ValueError("invalid ChatGPT message")
    author = message.get("author") or {}
    if not isinstance(author, dict):
        raise ValueError("invalid ChatGPT author")
    role = author.get("role", "unknown")
    content = _parts(message)
    return {
        "source_message_id": message.get("id"),
        "role": role,
        "content": content,
        "timestamp": _to_iso(message.get("create_time")),
    }


def selected_nodes(conv):
    """Return the explicit root-to-current_node chain, or deterministic fallback.

    The fallback is needed for older export formats; explicit current_node
    always wins even when it is *not* the last child.
    """
    mapping = conv.get("mapping") or {}
    if not isinstance(mapping, dict):
        raise ValueError("invalid ChatGPT mapping")
    for node in mapping.values():
        if not isinstance(node, dict):
            raise ValueError("invalid ChatGPT node")
    current = conv.get("current_node")
    if current in mapping:
        chain = []
        seen = set()
        node_id = current
        while node_id in mapping and node_id not in seen:
            seen.add(node_id)
            chain.append(node_id)
            parent = mapping[node_id].get("parent")
            if parent is None:
                return list(reversed(chain))
            node_id = parent
        raise ValueError("selected branch has broken ancestry or cycle")

    roots = [node_id for node_id,node in mapping.items() if node.get("parent") is None]
    if not roots:
        return []
    node_id = roots[0]
    chain = []
    seen = set()
    while node_id in mapping and node_id not in seen:
        chain.append(node_id)
        seen.add(node_id)
        kids = mapping[node_id].get("children", [])
        if not isinstance(kids, list) or not kids:
            break
        node_id = kids[-1]
    return chain


def validate_snapshot(conv):
    """Fully validate the same snapshot before dry-run and before persistence."""
    mapping = conv.get("mapping") or {}
    if not isinstance(mapping, dict):
        raise ValueError("invalid ChatGPT mapping")
    selected = set(selected_nodes(conv))
    nodes = []
    for node_id, node in mapping.items():
        if not isinstance(node_id, str):
            raise ValueError("node ID must be text")
        message = _normalize(node)
        nodes.append((node_id,node,message))
    return nodes, selected


def sync_projection(conn, conv_id, conv, *, selected=None):
    """Replace only the derived alternative index for a single source snapshot."""
    nodes, selected_ids = validate_snapshot(conv)
    if selected is not None:
        selected_ids = set(selected)
    conn.execute("DELETE FROM chatgpt_branch_messages WHERE conv_id=?", (conv_id,))
    inserted = 0
    for node_id, node, message in nodes:
        if message is None or node_id in selected_ids:
            continue
        if message["role"] not in ("user", "assistant", "system", "tool"):
            continue
        if not message["content"]:
            continue
        conn.execute(
            """INSERT INTO chatgpt_branch_messages(
                   conv_id,node_id,parent_id,source_message_id,role,content,timestamp)
               VALUES (?,?,?,?,?,?,?)""",
            (conv_id,node_id,node.get("parent"),message["source_message_id"],
             message["role"],message["content"],message["timestamp"]),
        )
        inserted += 1
    return inserted


def backfill_existing(conn):
    """Migrate older, preserved raw nodes into search without editing source tree.

    Existing selected message IDs are used to avoid duplicate selected-path
    results. This is an approximation for legacy imports missing current_node:
    the raw tree is retained and the unknown selection is never invented.
    """
    known = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='chatgpt_nodes'"
    ).fetchone()
    if not known:
        return 0
    source_ids = {}
    for row in conn.execute("SELECT conv_id,id FROM messages"):
        source_ids.setdefault(row[0], set()).add(row[1])
    count = 0
    for row in conn.execute(
        "SELECT conv_id,node_id,parent_id,message_json FROM chatgpt_nodes"
    ):
        conv_id,node_id,parent_id,payload = row
        if not payload:
            continue
        message = json.loads(payload)
        if message is None:
            continue
        normalized = _normalize({"message": message})
        if normalized["source_message_id"] in source_ids.get(conv_id, set()):
            continue
        if not normalized["content"] or normalized["role"] not in (
                "user", "assistant", "system", "tool"):
            continue
        conn.execute(
            """INSERT OR IGNORE INTO chatgpt_branch_messages(
                   conv_id,node_id,parent_id,source_message_id,role,content,timestamp)
               VALUES (?,?,?,?,?,?,?)""",
            (conv_id,node_id,parent_id,normalized["source_message_id"],
             normalized["role"],normalized["content"],normalized["timestamp"]),
        )
        count += 1
    return count


def branch_ref(conv_id: str, node_id: str) -> str:
    payload=json.dumps([conv_id,node_id],ensure_ascii=False,separators=(",",":")).encode()
    return "branch:v1:" + base64.urlsafe_b64encode(payload).rstrip(b"=").decode()


def parse_branch_ref(value: str):
    if not isinstance(value,str) or not value.startswith("branch:v1:"):
        return None
    raw=value[len("branch:v1:"):]
    try:
        parts=json.loads(base64.urlsafe_b64decode(
            raw+"="*(-len(raw)%4)).decode())
    except (ValueError,UnicodeDecodeError):
        return None
    if not isinstance(parts,list) or len(parts)!=2 or not all(
            isinstance(x,str) for x in parts):
        return None
    return tuple(parts)


def search_branch_messages(conn,query,limit=20,platform=None):
    """Search alternate nodes only. Results are separate from main FTS ranking."""
    if not query or not query.strip() or not 1 <= limit <= 200:
        raise ValueError("invalid branch search request")
    available=conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='chatgpt_branch_fts'"
    ).fetchone()
    if not available:
        return {"query":query,"count":0,"hits":[],"index_status":"not_built"}
    sql="""SELECT b.conv_id,b.node_id,b.parent_id,b.source_message_id,
                  b.role,b.content,b.timestamp,c.title,c.platform,
                  bm25(chatgpt_branch_fts) AS rank
           FROM chatgpt_branch_fts
           JOIN chatgpt_branch_messages b ON b.rowid=chatgpt_branch_fts.rowid
           JOIN conversations c ON c.id=b.conv_id
           WHERE chatgpt_branch_fts MATCH ?"""
    args=[query]
    if platform:
        sql+=" AND c.platform=?"
        args.append(platform)
    sql+=" ORDER BY rank,b.rowid LIMIT ?"
    args.append(limit)
    hits=[]
    for row in conn.execute(sql,args):
        mid=branch_ref(row["conv_id"],row["node_id"])
        hits.append({
            "message":{"id":mid,"conv_id":row["conv_id"],"role":row["role"],
                       "content":row["content"],"timestamp":row["timestamp"],
                       "source_message_id":row["source_message_id"]},
            "conversation":{"id":row["conv_id"],"title":row["title"],
                            "platform":row["platform"]},
            "branch":{"node_id":row["node_id"],"parent_id":row["parent_id"],
                      "selected":False,"kind":"chatgpt_alternative"},
            "before":[],"after":[],"rank":row["rank"],
            "rank_scope":"alternate_branch_index",
        })
    return {"query":query,"count":len(hits),"hits":hits,"index_status":"ready",
            "rank_note":"BM25 scores for alternate and main indexes are not comparable"}


def get_branch_context(conn, reference, context=20):
    parsed=parse_branch_ref(reference)
    if parsed is None:
        return None
    conv_id,node_id=parsed
    row=conn.execute(
        "SELECT * FROM chatgpt_branch_messages WHERE conv_id=? AND node_id=?",
        (conv_id,node_id)).fetchone()
    if row is None:
        return None
    conv=conn.execute(
        "SELECT id,title,platform FROM conversations WHERE id=?", (conv_id,)).fetchone()
    ancestors=[]
    current=row["parent_id"]
    seen={node_id}
    while current and current not in seen and len(ancestors)<context:
        seen.add(current)
        node=conn.execute(
            "SELECT parent_id,message_json FROM chatgpt_nodes WHERE conv_id=? AND node_id=?",
            (conv_id,current)).fetchone()
        if node is None:
            break
        if node["message_json"]:
            src=json.loads(node["message_json"])
            if src:
                normalized=_normalize({"message":src})
                ancestors.append({
                    "id":branch_ref(conv_id,current),"conv_id":conv_id,
                    "role":normalized["role"],"content":normalized["content"],
                    "timestamp":normalized["timestamp"],
                })
        current=node["parent_id"]
    ancestors.reverse()
    return {
        "message":{"id":reference,"conv_id":conv_id,"role":row["role"],
                   "content":row["content"],"timestamp":row["timestamp"],
                   "source_message_id":row["source_message_id"]},
        "conversation":dict(conv),"before":ancestors,"after":[],
        "branch":{"node_id":node_id,"parent_id":row["parent_id"],
                  "selected":False,"kind":"chatgpt_alternative"},
    }
