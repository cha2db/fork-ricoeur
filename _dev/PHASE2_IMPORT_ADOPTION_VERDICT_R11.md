# Cha2db — Fase 2 R11 · veredito de entrada com ramificações

**Escopo:** prova black-box em GH Actions sobre o mesmo JSON sintético ChatGPT, 2 conversas/5 mensagens, duas respostas alternativas no mesmo nó pai. Nenhum dado privado e nenhuma alteração do core.

## Comparação funcional confirmada

| Gate | Reweave 0.1.0 (C101) | CTK 2.20.2 (C118) |
| --- | --- | --- |
| Reconhecer 2 conversas | PASS | PASS |
| Preservar as 5 mensagens | **FAIL: 4 de 5** | PASS: 5 de 5 |
| Preservar irmãos m2 e m3 | **FAIL** | PASS |
| Recuperar marcador exclusivo de m2 | **FAIL** | PASS |
| Não criar duplicação em nova importação | PASS | PASS em salvar novamente no SQLite |
| IDs/origem rastreáveis | PASS para ramo retido | PASS para todos os ramos |
| Persistir a árvore completa no SQLite | Não oferecido pelo teste atual | **PASS: 2 caminhos, 5 mensagens** |
| Exportar formato nativo e reimportar árvore inteira | Não testado | **PASS: mesma estrutura/IDs** |

**Causa encontrada no código do Reweave:** `src/reweave/parsers/chatgpt.py` invoca `_linearize_mapping`, que escolhe o `current_node` ou segue apenas o último filho de cada nó. É um comportamento intencional de projeção em ramo ativo, mas implica perda das demais variantes na representação importada. Esta conclusão é válida para o fixture e versão testada, não para possíveis outros backups brutos produzidos pelo programa.

**Causa do PASS CTK:** `ctk/importers/openai.py` varre todos os itens de `mapping` e mantém `parent_id`. O armazenamento `ConversationDB` persiste pais e filhos, e o `JSONExporter` em `format_style='ctk'` tem inverso `CTKImporter` preservando IDs e estrutura.

## Decisão para composição

- **CTK → CANDIDATE_ADOPT_IMPORT_ADAPTER** para importação do ChatGPT e representação em árvore, condicionado a testes adicionais. Pode reduzir código próprio no Cha2db.
- **Reweave → REJECT_REPLACE_LOSSLESS_INGEST**, embora continue bom comparador de UX, insights, indexação e idempotência.
- **Não adotar CTK inteiro**: o programa inclui TUI, MCP e integrações LLM; só os contratos do importador, modelo de árvore e serializador devem ser candidatos. Respeitar MIT e dependências por versão.
- **Risco CTK:** `save_conversation` remove e reinsere mensagens ao atualizar uma conversa. Mesmo com IDs preservados, isso pode alterar rowids/FTS e apagar dados externos derivados. Precisa de gate sobre escrita idempotente com referências externas e índice incremental.
- **Gate restante:** múltiplos fornecedores, anexos, metadados/tool calls, raw bytes, importação incremental, reparo de conversas truncadas, versões editadas, 40k mensagens e Termux ARM64. Não confundir exportação nativa CTK com reexportação idêntica ao ChatGPT original.

## Evidências públicas e reproduzíveis

- [Reweave FAIL (perda de ramo)](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/reweave-latest.json)
- [CTK parser PASS](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/ctk-latest.json)
- [CTK SQLite e JSON nativo PASS](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/ctk-store-latest.json)
- [Matriz de evidência dos 143](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/census/latest.json)
- [Fonte Reweave](https://github.com/seolbbb/reweave/blob/main/src/reweave/parsers/chatgpt.py)
- [Fonte CTK](https://github.com/queelius/ctk/blob/main/ctk/importers/openai.py)

**Conclusão:** CTK resolveu a primeira lacuna fundamental que o Reweave não resolveu no teste. Isso é um resultado de prior art aproveitável, mas ainda não corresponde a implementação integrada da Fase 3.
