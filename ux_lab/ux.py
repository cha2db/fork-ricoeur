"""Read-only CLI and localhost HTTP for an existing Ricoeur SQLite database.

All text search delegates to ricoeur.retrieval.search_messages (FTS5).
No search index, migration, graph inference, or SQLite writes live here.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import json
import sqlite3
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ricoeur.retrieval import get_message_context, search_messages
from knowledge_port import load_lexicon, timeline, period_messages, tagcloud, concept_detail

VERSION = "ux.v2"


def connect(path):
    conn = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def payload(data):
    return {"schema_version": VERSION, "status": "ok", "data": data, "errors": []}


def error_payload(error):
    return {"schema_version": VERSION, "status": "error", "data": None, "errors": [str(error)]}


def expression(query, syntax="literal"):
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query_required")
    if len(query) > 2000:
        raise ValueError("query_too_long")
    if syntax == "literal":
        return '"' + query.strip().replace('"', '""') + '"'
    if syntax == "fts5":
        return query.strip()
    raise ValueError("invalid_syntax")


def _limit(value, ceiling=100):
    n = int(value)
    if n < 1 or n > ceiling:
        raise ValueError("limit_out_of_range")
    return n


def _context(value):
    n = int(value)
    if n < 0 or n > 10:
        raise ValueError("context_out_of_range")
    return n


def recent(conn, platform="", limit=30):
    limit = _limit(limit)
    rows = conn.execute(
        """SELECT * FROM conversations
           WHERE (? = '' OR platform = ?)
           ORDER BY created_at DESC, id LIMIT ?""",
        (platform, platform, limit),
    ).fetchall()
    return [_conversation(row) for row in rows]


def _conversation(row):
    fields = dict(row)
    return {k: fields.get(k) for k in
            ("id", "title", "platform", "model", "created_at", "message_count", "source_path")}


def message_hits(conn, query, platform="", limit=30, context=1, syntax="literal"):
    # IMPORTANT: Delegate all retrieval, ranking, filtering and adjacency to peer core.
    fts_query = expression(query, syntax)
    result = search_messages(
        conn, fts_query, limit=_limit(limit, 200),
        context=_context(context), platform=platform or None,
    )
    return {"query": query, "syntax": syntax, "engine": "ricoeur.retrieval/FTS5",
            "count": result["count"], "hits": result["hits"]}


def conversations(conn, query="", platform="", limit=30, syntax="literal"):
    if not query:
        return recent(conn, platform, limit)
    hits = message_hits(conn, query, platform, limit=_limit(limit, 200), syntax=syntax)["hits"]
    ordered = {}
    for hit in hits:
        c = hit["conversation"]
        cid = c["id"]
        if cid not in ordered:
            ordered[cid] = {"id": cid, "title": c["title"], "platform": c["platform"],
                            "first_match_id": hit["message"]["id"], "match_count": 0}
        ordered[cid]["match_count"] += 1
    return list(ordered.values())


def transcript(conn, cid):
    row = conn.execute("SELECT * FROM conversations WHERE id = ?", (cid,)).fetchone()
    if row is None:
        raise ValueError("conversation_not_found")
    msgs = conn.execute(
        """SELECT id,role,content,timestamp FROM messages WHERE conv_id = ?
           ORDER BY timestamp, rowid""", (cid,)
    ).fetchall()
    messages = [dict(r) for r in msgs]
    for index, message in enumerate(messages):
        message["previous_id"] = messages[index - 1]["id"] if index else None
        message["next_id"] = messages[index + 1]["id"] if index + 1 < len(messages) else None
    return {"conversation": _conversation(row), "messages": messages}


def graph(conn, query="", platform="", limit=30, syntax="literal"):
    """Evidence-backed query-to-conversation star; NO inferred semantic edges."""
    if not query:
        return {"nodes": [], "edges": [], "relation_status": "query_required_for_evidence"}
    result = message_hits(conn, query, platform, limit, context=0, syntax=syntax)
    match_ids = {}
    metadata = {}
    for hit in result["hits"]:
        cid = hit["conversation"]["id"]
        metadata[cid] = hit["conversation"]
        match_ids.setdefault(cid, []).append(hit["message"]["id"])
    nodes = [{"id": "query", "type": "query", "label": query}]
    nodes.extend({"id": cid, "type": "conversation", "label": conv.get("title") or cid,
                  "platform": conv.get("platform")} for cid, conv in metadata.items())
    edges = [{"source": "query", "target": cid, "type": "fts5_query_match",
              "evidence_message_ids": mids, "query": query,
              "method": "ricoeur.retrieval/FTS5", "semantic_claim": False}
             for cid, mids in match_ids.items()]
    return {"nodes": nodes, "edges": edges, "relation_status": "query_match_only"}


def execute(db, action, *, lexicon=None, **kw):
    with closing(connect(db)) as conn:
        if action == "capabilities":
            return payload({"ports": ["capabilities", "conversations", "search",
                                      "transcript", "message", "graph", "timeline", "period",
                                      "tagcloud", "concept", "serve"],
                            "search_core": "ricoeur.retrieval.search_messages",
                            "graph": "query_match_only", "storage": "read_only_ricoeur_sqlite"})
        if action == "conversations":
            return payload(conversations(conn, kw.get("query", ""), kw.get("platform", ""),
                                         kw.get("limit", 30), kw.get("syntax", "literal")))
        if action == "search":
            return payload(message_hits(conn, kw.get("query", ""), kw.get("platform", ""),
                                        kw.get("limit", 30), kw.get("context", 1),
                                        kw.get("syntax", "literal")))
        if action == "transcript":
            return payload(transcript(conn, kw["id"]))
        if action == "message":
            found = get_message_context(conn, kw["id"], _context(kw.get("context", 2)))
            if found is None:
                raise ValueError("message_not_found")
            return payload(found)
        if action == "graph":
            return payload(graph(conn, kw.get("query", ""), kw.get("platform", ""),
                                 kw.get("limit", 30), kw.get("syntax", "literal")))
        if action in ("timeline", "period", "tagcloud", "concept"):
            vocabulary = load_lexicon(lexicon)
            expand_text = str(kw.get("expand", "false")).strip().lower()
            if expand_text not in ("false", "true", "0", "1"):
                raise ValueError("invalid_expand")
            expand = expand_text in ("true", "1")
            if action == "timeline":
                return payload(timeline(conn, kw.get("query", ""),
                                        grain=kw.get("grain", "month"),
                                        platform=kw.get("platform", ""),
                                        expand=expand, lexicon=vocabulary))
            if action == "period":
                return payload(period_messages(conn, kw.get("query", ""),
                                               period=kw["period"],
                                               grain=kw.get("grain", "month"),
                                               platform=kw.get("platform", ""),
                                               expand=expand, lexicon=vocabulary,
                                               limit=kw.get("limit", 50),
                                               offset=kw.get("offset", 0)))
            if action == "tagcloud":
                return payload(tagcloud(conn, kw.get("query", ""),
                                        period=kw.get("period"),
                                        grain=kw.get("grain", "month"),
                                        platform=kw.get("platform", ""),
                                        expand=expand, lexicon=vocabulary,
                                        max_messages=kw.get("max_messages", 1000),
                                        top=kw.get("top", 40)))
            return payload(concept_detail(vocabulary, kw["term"]))
        raise ValueError("unsupported_action")


def handler_factory(db, lexicon=None):
    page = Path(__file__).with_name("index.html").read_bytes()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlparse(self.path)
            if url.path == "/":
                body, code, kind = page, 200, "text/html; charset=utf-8"
            elif url.path == "/api":
                args = {k: v[0] for k, v in parse_qs(url.query).items()}
                action = args.pop("action", "capabilities")
                try:
                    body = json.dumps(execute(db, action, lexicon=lexicon, **args), ensure_ascii=False).encode()
                    code = 200
                except (ValueError, KeyError, sqlite3.Error) as exc:
                    body = json.dumps(error_payload(exc), ensure_ascii=False).encode()
                    code = 400
                kind = "application/json; charset=utf-8"
            else:
                self.send_error(404)
                return
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler


def serve(db, port, lexicon=None):
    server = ThreadingHTTPServer(("127.0.0.1", int(port)), handler_factory(db, lexicon))
    print(f"UX lab: http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def main():
    parser = argparse.ArgumentParser(description="Ricoeur read-only UX CLI/GUI")
    parser.add_argument("--db", required=True)
    parser.add_argument("--lexicon", default=None, help="Optional curated SKOS-like JSON sidecar, never automatic")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("capabilities")
    for action in ("conversations", "search", "graph"):
        p = sub.add_parser(action)
        p.add_argument("--query", default="")
        p.add_argument("--platform", default="")
        p.add_argument("--limit", type=int, default=30)
        p.add_argument("--syntax", choices=["literal", "fts5"], default="literal")
        if action == "search":
            p.add_argument("--context", type=int, default=1)
    for action in ("timeline", "period", "tagcloud"):
        p = sub.add_parser(action)
        p.add_argument("--query", required=True)
        p.add_argument("--platform", default="")
        p.add_argument("--grain", choices=("year", "month", "day"), default="month")
        p.add_argument("--expand", action="store_true")
        if action == "period":
            p.add_argument("--period", required=True)
            p.add_argument("--limit", type=int, default=50)
            p.add_argument("--offset", type=int, default=0)
        if action == "tagcloud":
            p.add_argument("--period")
            p.add_argument("--max-messages", type=int, default=1000)
            p.add_argument("--top", type=int, default=40)
    sub.add_parser("concept").add_argument("term")
    sub.add_parser("transcript").add_argument("id")
    p = sub.add_parser("message")
    p.add_argument("id")
    p.add_argument("--context", type=int, default=2)
    sub.add_parser("serve").add_argument("--port", type=int, default=8765)
    args = vars(parser.parse_args())
    db, action = args.pop("db"), args.pop("action")
    lexicon = args.pop("lexicon")
    if action == "serve":
        return serve(db, args["port"], lexicon=lexicon)
    try:
        print(json.dumps(execute(db, action, lexicon=lexicon, **args), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, sqlite3.Error) as exc:
        print(json.dumps(error_payload(exc), ensure_ascii=False))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
