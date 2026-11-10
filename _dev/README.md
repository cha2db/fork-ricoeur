# _dev — laboratório Cha2db

Artefatos de desenvolvimento, decisões, evidências e testes.
Esta organização é uma adaptação local, **não uma certificação InitProj**.

| Teste | Escopo | Comando | Estado |
|---|---|---|---|
| 1 | Carga e importação incremental | `bash tests/run_fire_android.sh` | PASS observado |
| 2 | ZIP sintético de conta | `bash tests/run_account_zip_android.sh` | PASS parcial observado |
| 3 | Idempotência persistente (4 importações) | `bash _dev/teste3.sh` | A executar |

| 4 | Mensagens vazias e árvore completa | `bash _dev/teste4.sh` | A executar |\n\n| 5 | Busca entre conversas, mensagens e prontidão MCP | `bash _dev/teste5.sh` | A executar |\n\n| 6 | Busca por mensagem, contexto, filtro e contrato JSON | `bash _dev/teste6.sh` | Publicado, pendente Android |\n\nNão comitar `_dev/results/`: contém dados temporários de execução.
Resumo e decisões: [SESSION.md](SESSION.md).
