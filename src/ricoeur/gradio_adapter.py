"""Optional Gradio chat frontend. Deterministic retrieval, no LLM required."""
from __future__ import annotations

from .db import get_connection
from .retrieval import search_messages, get_message_context


def answer(question: str, history: list) -> str:
    """Return traceable FTS5 hits; history is presentation-only, not sent to a model."""
    query = (question or "").strip()
    if not query:
        return "Digite uma consulta FTS5, por exemplo: SQLite ou \"banco de dados\"."
    conn = get_connection()
    try:
        result = search_messages(conn, query, limit=12, context=1)
    except Exception as exc:
        if isinstance(exc, ValueError) or exc.__class__.__name__ == "OperationalError":
            return f"Consulta inválida: {exc}"
        raise
    finally:
        conn.close()
    if not result["hits"]:
        return "Nenhuma mensagem encontrada. A consulta procura no conteúdo importado, sem inventar respostas."
    lines = [f"**{result['count']} mensagem(ns) encontrada(s)** — resultados por mensagem, sem LLM."]
    for i, hit in enumerate(result["hits"], 1):
        m, c = hit["message"], hit["conversation"]
        snippet = (m["content"] or "").strip().replace("\\r", " ")
        if len(snippet) > 900:
            snippet = snippet[:900] + "…"
        lines.extend([
            f"### {i}. {c['title'] or c['id']}",
            f"**Plataforma:** {c['platform']} · **Papel:** {m['role']} · **ID:** `{m['id']}`",
            snippet or "*(mensagem vazia)*",
        ])
        if hit["before"]:
            lines.append("**Anterior:** " + (hit["before"][-1]["content"] or "")[:240])
        if hit["after"]:
            lines.append("**Posterior:** " + (hit["after"][0]["content"] or "")[:240])
    return "\\n\\n".join(lines)


def build_demo():
    import gradio as gr
    return gr.ChatInterface(
        fn=answer,
        title="Cha2db · Laboratório de chat",
        description="Pesquisa rastreável em conversas importadas. SQLite/FTS5; sem LLM.",
        examples=["SQLite", '"banco de dados"', "Android", "SQLite OR Android"],
    )


def build_app():
    import gradio as gr
    from .http_adapter import app
    return gr.mount_gradio_app(app, build_demo(), path="/chat")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(build_app(), host="127.0.0.1", port=8766)
