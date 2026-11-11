"""Read-only knowledge views on the EXISTING Ricoeur FTS5 index.

Timeline and period drilldown use FTS5 SQL aggregation, not a second search
engine. Typed relations require a separate, human-curated SKOS-like lexicon.
All SQL bind parameters; dates use message timestamp or conversation fallback.
"""
from collections import Counter
import json
from pathlib import Path
import re

GRAINS = {"year": 4, "month": 7, "day": 10}
STOPWORDS = set("""a o as os um uma de da do das dos e em no na nos nas por para com sem 
que se ao aos é são foi ser ter não mais menos eu você ele ela eles elas meu minha
nós vocês the and for from with this that you your are was were has have will they
their not can its como onde quando sobre uma uns umas pra pelos pelas esse essa isto
este aquele também apenas entre todo todos muito cada então isso pela pelo
to of in on at or is it as be by an we i do did what why how from our""".split())
MAX_TERMS = 8


def load_lexicon(path):
    if not path:
        return {"schema_version": "ux.lexicon.v1", "concepts": []}
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if doc.get("schema_version") != "ux.lexicon.v1" or not isinstance(doc.get("concepts"), list):
        raise ValueError("invalid_lexicon_schema")
    ids = set()
    for item in doc["concepts"]:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item.get("prefLabel"):
            raise ValueError("invalid_concept")
        if item["id"] in ids:
            raise ValueError("duplicate_concept_id")
        ids.add(item["id"])
        aliases = item.get("altLabels", [])
        if not isinstance(aliases, list) or not all(isinstance(t, str) for t in aliases):
            raise ValueError("invalid_alt_labels")
        for edge in item.get("relations", []):
            if edge.get("type") not in {"skos:related", "skos:broader", "skos:narrower",
                                        "skos:exactMatch", "skos:closeMatch"}:
                raise ValueError("unsupported_relation_type")
            if not isinstance(edge.get("target"), str) or not edge.get("source"):
                raise ValueError("relation_requires_target_and_source")
    for item in doc["concepts"]:
        for edge in item.get("relations", []):
            if edge["target"] not in ids:
                raise ValueError("unknown_relation_target")
    return doc


def _labels(term, lexicon, expand):
    if not isinstance(term, str) or not term.strip() or len(term) > 200:
        raise ValueError("invalid_term")
    term = term.strip()
    if not expand:
        return [term], None
    match = next((c for c in lexicon["concepts"] if term.casefold() in
                  {name.casefold() for name in [c["prefLabel"], *c.get("altLabels", [])]}), None)
    if match is None:
        return [term], None
    terms = list(dict.fromkeys([match["prefLabel"], *match.get("altLabels", [])]))
    if len(terms) > MAX_TERMS or any(not t.strip() or len(t) > 200 for t in terms):
        raise ValueError("lexicon_expansion_too_large")
    return terms, match["id"]


def _fts_query(terms):
    # FTS5 phrase quoting, never raw operators in synonym labels.
    return " OR ".join('"' + term.replace('"', '""') + '"' for term in terms)


def _source_date():
    return "COALESCE(NULLIF(m.timestamp, ''), NULLIF(c.created_at, ''))"


def _where(period=None, grain="month", platform=""):
    if grain not in GRAINS:
        raise ValueError("invalid_grain")
    parts = ["messages_fts MATCH ?"]
    values = []
    if platform:
        parts.append("c.platform = ?")
        values.append(platform)
    if period is not None:
        if period == "unknown":
            parts.append("(" + _source_date() + " IS NULL OR " + _source_date() + " = '')")
        else:
            expected = GRAINS[grain]
            if not isinstance(period, str) or len(period) != expected:
                raise ValueError("invalid_period")
            if not re.fullmatch({4:r"\d{4}",7:r"\d{4}-\d{2}",10:r"\d{4}-\d{2}-\d{2}"}[expected], period):
                raise ValueError("invalid_period")
            parts.append("substr(" + _source_date() + ", 1, ?) = ?")
            values.extend([expected, period])
    return " AND ".join(parts), values


def _base():
    return """ FROM messages_fts
      JOIN messages m ON m.rowid = messages_fts.rowid
      JOIN conversations c ON c.id = m.conv_id """


def timeline(conn, term, grain="month", platform="", expand=False, lexicon=None):
    terms, concept_id = _labels(term, lexicon or {"concepts":[]}, expand)
    expression = _fts_query(terms)
    where, extra = _where(grain=grain, platform=platform)
    date = _source_date()
    bucket = f"COALESCE(NULLIF(substr({date},1,{GRAINS[grain]}),''),'unknown')"
    sql = (f"SELECT {bucket} AS period, COUNT(*) AS matching_messages, "
           f"COUNT(DISTINCT m.conv_id) AS matching_conversations "
           + _base() + " WHERE " + where + " GROUP BY period ORDER BY period")
    points = [dict(row) for row in conn.execute(sql, [expression, *extra])]
    return {"query": term, "terms": terms, "concept_id": concept_id,
            "expanded": bool(expand and concept_id), "grain": grain, "platform": platform,
            "unit": "messages_containing_query", "date_policy": "message_timestamp_else_conversation_created_at",
            "points": points, "total_messages": sum(row["matching_messages"] for row in points),
            "aggregation": "existing_SQLite_FTS5_no_new_index"}


def period_messages(conn, term, period, grain="month", platform="", expand=False,
                    lexicon=None, limit=50, offset=0):
    limit, offset = int(limit), int(offset)
    if not 1 <= limit <= 200 or not 0 <= offset <= 100000:
        raise ValueError("invalid_pagination")
    terms, concept_id = _labels(term, lexicon or {"concepts":[]}, expand)
    where, extra = _where(period=period, grain=grain, platform=platform)
    params = [_fts_query(terms), *extra]
    total = conn.execute("SELECT COUNT(*) " + _base() + " WHERE " + where, params).fetchone()[0]
    sql = ("SELECT m.id AS message_id, m.conv_id, m.role, m.content, m.timestamp,"
           " c.title, c.platform" + _base() + " WHERE " + where
           + " ORDER BY " + _source_date() + ", m.rowid LIMIT ? OFFSET ?")
    matches = [dict(row) for row in conn.execute(sql, [*params, limit, offset])]
    return {"query": term, "terms": terms, "concept_id": concept_id, "period": period,
            "grain": grain, "total_messages": total, "offset": offset, "limit": limit,
            "messages": matches, "unit": "messages_containing_query"}


def tagcloud(conn, term, period=None, grain="month", platform="", expand=False,
             lexicon=None, max_messages=1000, top=40):
    if not 1 <= int(max_messages) <= 2000 or not 1 <= int(top) <= 100:
        raise ValueError("invalid_sample_limits")
    terms, concept_id = _labels(term, lexicon or {"concepts":[]}, expand)
    where, extra = _where(period=period, grain=grain, platform=platform)
    total = conn.execute("SELECT COUNT(*) " + _base() + " WHERE " + where,
                         [_fts_query(terms), *extra]).fetchone()[0]
    sql = ("SELECT m.content " + _base() + " WHERE " + where +
           " ORDER BY m.rowid LIMIT ?")
    counts = Counter()
    for row in conn.execute(sql, [_fts_query(terms), *extra, int(max_messages)]):
        # Document frequency (distinct messages mentioning a token), not word mentions.
        words = set(re.findall(r"[^\W_][\w-]{2,}", row["content"] or "", flags=re.UNICODE))
        counts.update(w.casefold() for w in words if w.casefold() not in STOPWORDS
                      and not w.isdigit())
    ordered = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:int(top)]
    return {"query": term, "terms": terms, "concept_id": concept_id, "period": period,
            "unit": "sampled_message_document_frequency",
            "sampled_messages": min(total, int(max_messages)), "total_matched_messages": total,
            "is_truncated": total > int(max_messages),
            "terms_frequency": [{"term": word, "message_count": amount} for word, amount in ordered],
            "note": "cooccurrence_in_matching_messages_is_not_semantic_similarity"}


def concept_detail(lexicon, term):
    concepts = lexicon["concepts"]
    concept = next((c for c in concepts if term.casefold() in
                    {name.casefold() for name in [c["id"],c["prefLabel"],*c.get("altLabels",[])]}),
                   None)
    if concept is None:
        raise ValueError("concept_not_found")
    by_id = {c["id"]: c for c in concepts}
    relations = []
    for edge in concept.get("relations", []):
        relations.append({**edge, "target_label": by_id[edge["target"]]["prefLabel"],
                          "verified_in_chat": False})
    return {"id": concept["id"], "preferred": concept["prefLabel"],
            "altLabels": concept.get("altLabels", []), "language": concept.get("language"),
            "relations": relations,
            "note": "curated_external_lexicon_only_no_inferred_semantics"}
