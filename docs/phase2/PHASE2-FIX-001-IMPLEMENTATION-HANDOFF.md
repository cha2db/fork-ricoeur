# PHASE2-FIX-001 — Correções de fidelidade e segurança (implementadas em PR #3)

**Base:** `main` do `cha2db/fork-ricoeur` (Fase 2 do par). **Branch isolada** `fix/phase2-integrity-p0-20261111`. **Não executar merge automaticamente.** O par é responsável por revisão, integração e testes no tablet.

## Comparação com a auditoria independente

| Achado | Entrega concreta | Evidência autônoma | Limites remanescentes |
|---|---|---|---|
| IDENTITY-001 | IDs conflitantes entre ChatGPT/Claude/Claude Code recebem namespace **reversível** por provedor, conversa e ID nativo. IDs antigos não conflitantes são preservados. | `test_fix002_source_identity.py` | Falta modelar múltiplas contas do mesmo provedor; requer fonte/conta no contrato canônico |
| TREE-002 | `chatgpt_branch_messages` e `chatgpt_branch_fts` indexam **somente alternativas**, mantendo caminho atual em `messages` e árvore bruta em `chatgpt_nodes`; recuperação por `branch:v1` e ancestrais. | `test_fix003_branch_projection.py` | Escores BM25 das duas tabelas **não podem ser misturados**; resultados de ramos ficam em `branch_hits`; UX precisa exibi-los após merge |
| REIMPORT-003 | `current_node` define o caminho ativo; `--update` reconcilia projeção principal, raw nodes e índice alternativo; `chatgpt_node_versions` mantém versões imutáveis e `chatgpt_selection_versions` preserva a seleção por hash da origem. | `test_fix003_branch_projection.py` | Ainda falta contrato formal de supersedência de conversas inteiras e origem por conta |
| READONLY-006 | `get_read_connection()` usa `mode=ro` e `query_only=ON`, verifica versão e nunca migra. MCP, CLI show/stats/search e dry-run usam esse port. | `test_fix001_readonly_retrieval.py` | Permissões por usuário/grupo ainda não foram implantadas. MCP stdio continua exposto ao processo local autorizado |
| RETRIEVAL-007 | Contextos via **uma consulta SQL windowed por lote**; não faz 20 releituras completas para 20 resultados. JSON e ordem anterior/próxima mantidos. | `test_fix001_readonly_retrieval.py`; `_dev/teste6.py` | Falta benchmark p50/p95/RSS em Termux/ARM e corpus grande |
| ATOMICITY-005 | Savepoint por conversa + commit de 25 + `import_jobs` com `RUNNING/PARTIAL/COMPLETE/INTERRUPTED`, SHA-256 do arquivo e contagens sem conteúdo privado. | `test_fix004_import_receipts.py` | Interrupção SIGKILL deixa RUNNING até próxima tentativa do mesmo hash, que o classifica INTERRUPTED |
| DRYRUN-004 | Dry-run ChatGPT usa a **mesma validação estrutural** antes de contar novos/atualizados e a CLI o abre em modo de leitura. | `test_fix003_branch_projection.py`, `test_fix004_import_receipts.py` | Estender equivalência de validação aos importadores Claude/Claude Code, ainda não verificados neste gate |
| FTS5 consistency | Verificação do índice de conteúdo externo (`rank=1`) numa **cópia SQLite via Online Backup API**; nunca insere comando de integridade no banco original. | `test_fix005_fts_snapshot.py` | É diagnóstico, **não** reparo automático. Restaurar/reindexar apenas numa cópia |

## Mudança de esquema — v2 → v3, ADITIVA e com snapshot

A migração cria `chatgpt_branch_messages`, `chatgpt_branch_fts`, triggers FTS5, `chatgpt_node_versions`, `chatgpt_selection_versions` e `import_jobs`, **sem renomear nem remover** `conversations`, `messages` ou `chatgpt_nodes`. Ramo não selecionado preservado em versão antiga é backfilled por um scan das informações brutas.

- Antes da primeira operação de **escrita** que exija migração, `get_connection` usa a **SQLite Online Backup API** e `PRAGMA quick_check` para criar um snapshot local privado em `.migration-backups/ricoeur-v2-....sqlite3`. Rejeita migração sem espaço ou se o backup falhar. O backup contém dados pessoais e deve permanecer privado.
- Uma chamada **somente leitura** a banco v2 **recusa o acesso**, em vez de alterá-lo automaticamente. Executar migração de modo explícito em ambiente controlado, com backup adicional e verificação de espaço.
- A versão anterior continua recuperável pelo snapshot; a ferramenta não executa rollback automático.
- **Não** rodar testes de migração sobre a única cópia da base real. O processo de homologação do par deve primeiro duplicar o arquivo transacionalmente e depois importar/cotejar a amostra.

## Contratos externos

```python
from ricoeur.db import get_read_connection
from ricoeur.retrieval import search_messages, get_message_context
from ricoeur.importers.branch_index import search_branch_messages

conn = get_read_connection()
result = search_messages(conn, '"agulha"')
# result["hits"] — mensagens do caminho principal
# result["branch_hits"] — alternativas, com source_message_id e parent_id
# result["branch_count"] — total retornado na página do índice alternativo
conn.close()
```

**MCP stdio** expõe `search_chat_messages`, `read_chat_message` e, adicionalmente, `search_chat_branches` e `read_chat_branch`. Todas as ferramentas usam a abertura read-only. Não afirmar autenticação multiusuário.

## Testes executáveis

```bash
python -m pip install -e .
python _dev/tests/phase2/test_fix001_readonly_retrieval.py
python _dev/tests/phase2/test_fix002_source_identity.py
python _dev/tests/phase2/test_fix003_branch_projection.py
python _dev/tests/phase2/test_fix004_import_receipts.py
python _dev/tests/phase2/test_fix005_fts_snapshot.py
python _dev/teste6.py
```

CI: `.github/workflows/phase2-fix-p0.yml` e gate existente `Cha2db headless search gates`. Testes usam bases temporárias sintéticas, não conversas privadas. Evidência de PASS do GitHub Actions depende da HEAD do PR no momento da execução.

Comando para diagnosticar **somente o índice FTS5**, explicitamente:

```bash
python -m ricoeur.health --db /caminho/ricoeur.db
```

O comando cria cópia temporária local privada para verificar correspondência entre índice e mensagens, remove a cópia em seguida e não altera o original.

## Gates ainda exigidos do par antes do merge

1. Todos os testes em PR #3 e `Cha2db headless search gates` precisam passar **na mesma HEAD**; revalidar conflitos com `main`.
2. Validar migração com snapshot de banco **realista**, inclusive múltiplos exports e ramos alterados; verificar bytes de anexos, relações, hashes e tamanho final.
3. Medir p95 e RAM de recuperação em 10k/100k/1M mensagens e 1/20/200 hits em CPU ARM/Termux; a redução de queries, isoladamente, não é prova de ganho em todo cenário.
4. Confirmar **contas distintas do mesmo provedor** e anexos como próximo gate da identidade do produto.
5. Distinguir `PARTIAL` de `COMPLETE` na interface de operação; histórico de origem deve ser exibido sem revelar conteúdo privado em logs.
6. Só o par faz o merge. Não solicitar teste humano no tablet antes da integração.

## Referências

- [SQLite URI read-only](https://www.sqlite.org/uri.html)
- [SQLite FTS5 external-content consistency](https://www.sqlite.org/fts5.html)
- [SQLite Online Backup API](https://www.sqlite.org/backup.html)
- [Auditoria original, PR #2](https://github.com/cha2db/fork-ricoeur/pull/2)
