"""Deterministic realistic multi-provider chat corpus. No private user data."""
import argparse
import json
import tempfile
from pathlib import Path

from ricoeur.db import get_connection, init_db
from ricoeur.retrieval import search_messages, get_message_context

TOPICS = [
 ("AUoK","dependência pedagógica","A unidade atômica AUoK precisa de regressão guiada e retorno à origem."),
 ("FremUX","contrato declarativo","O XComponent comunica por métodos e contratos com validação em build."),
 ("Cha2db","busca cruzada","A recuperação de conversas exige rastreabilidade de mensagens e busca cruzada."),
 ("DevOps","pipeline CI/CD","O pipeline Jenkins executa testes antes do deploy em homologação."),
 ("PostgreSQL","índice de banco","O índice B-tree acelera consultas por chave no PostgreSQL."),
 ("Redes","conexão SSH","O protocolo SSH estabelece conexão segura entre cliente e servidor."),
 ("Android","aplicativo móvel","O Android Studio compila o aplicativo com testes automatizados."),
 ("Segurança","permissões","A autorização segue menor privilégio e registra auditoria."),
 ("Educação","avaliação formativa","A avaliação formativa acompanha o progresso da aprendizagem."),
 ("Web","API REST","A API REST separa contrato de transporte e implementação."),
]
PLATFORMS = ["chatgpt","claude","gemini","copilot"]
ROLES = ["user","assistant"]
PREFIX = "fixture-cha2db-v1-"

def populate(conn, conversations=1000, messages=40):
    """Insert only missing IDs; never delete or overwrite existing records."""
    added_c = 0
    for i in range(conversations):
        name, term, explanation = TOPICS[i % len(TOPICS)]
        cid = f"{PREFIX}c{i:06d}"
        platform = PLATFORMS[i % len(PLATFORMS)]
        cur = conn.execute(
            """INSERT OR IGNORE INTO conversations
               (id,title,platform,created_at,updated_at)
               VALUES (?,?,?,?,?)""",
            (cid,f"[Corpus teste] {name} — sessão {i:04d}",platform,
             "2026-01-01T00:00:00","2026-01-02T00:00:00"))
        added_c += cur.rowcount
        batch = []
        for j in range(messages):
            text = (
                f"Conversa {i}, mensagem {j}. Tema: {name}. {explanation} "
                f"Pergunta sobre {term}. A equipe compara alternativas, registra "
                f"decisões e preserva evidências para revisão independente. "
                f"Critério de aceitação: resposta rastreável, IDs estáveis, "
                f"histórico completo e sem dependência de interface gráfica."
            )
            if j == 7 and i % 10 == 0:
                text += " Marcador exclusivo: agulha-mcp-2026."
            if j == 9 and i % 10 == 1:
                text += " Marcador exclusivo: orquidea-violeta-2026."
            batch.append((f"{PREFIX}m{i:06d}-{j:04d}",cid,ROLES[j % 2],
                          text,f"2026-01-01T{j//3600:02d}:{(j//60)%60:02d}:{j%60:02d}"))
        conn.executemany(
            "INSERT OR IGNORE INTO messages(id,conv_id,role,content,timestamp) VALUES (?,?,?,?,?)",
            batch)
    conn.commit()
    return added_c

def run_tests(conn, conversations, messages):
    total = conn.execute("SELECT count(*) FROM messages WHERE id LIKE ?",(PREFIX+"%",)).fetchone()[0]
    convs = conn.execute("SELECT count(*) FROM conversations WHERE id LIKE ?",(PREFIX+"%",)).fetchone()[0]
    exact = conn.execute("SELECT count(*) FROM messages WHERE content LIKE ?",("%agulha-mcp-2026%",)).fetchone()[0]
    phrase = search_messages(conn,'"agulha-mcp-2026"',limit=200,context=1)
    ctx = get_message_context(conn,f"{PREFIX}m000000-0007",context=2)
    checks = {
      "conversation_count":convs == conversations,
      "message_count":total == conversations*messages,
      "literal_marker_count":exact == (conversations+9)//10,
      "fts_marker_count":phrase["count"] == min(200,(conversations+9)//10),
      "cross_conversation":len({h["conversation"]["id"] for h in phrase["hits"]}) == phrase["count"],
      "context":ctx is not None and len(ctx["before"])==2 and len(ctx["after"])==2,
      "provider_diversity":len({h["conversation"]["platform"] for h in phrase["hits"]}) >= 2,
    }
    return {"status":"PASS" if all(checks.values()) else "FAIL","checks":checks,
            "conversations":convs,"messages":total,"marker_hits":exact}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--conversations",type=int,default=1000)
    p.add_argument("--messages",type=int,default=40)
    p.add_argument("--test-only",action="store_true")
    args=p.parse_args()
    if args.conversations<10 or args.messages<12:
        p.error("minimum: 10 conversations, 12 messages")
    if args.test_only:
        with tempfile.TemporaryDirectory(prefix="cha2db-corpus-") as folder:
            conn=init_db(Path(folder))
            populate(conn,args.conversations,args.messages)
            report=run_tests(conn,args.conversations,args.messages)
            conn.close()
    else:
        conn=get_connection()
        populate(conn,args.conversations,args.messages)
        report=run_tests(conn,args.conversations,args.messages)
        conn.close()
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if report["status"]!="PASS":
        raise SystemExit(1)

if __name__=="__main__":
    main()
