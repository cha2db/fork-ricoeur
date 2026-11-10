# Cha2db — Fase 2 R10 · pesquisa ampliada e portas remanescentes

Este documento complementa [a avaliação R09](PHASE2_CORE_COMPETITIVE_VERDICT_R09.md). O universo agora tem **143 candidatos** em [R10 JSON](PHASE2_MARKET_UNIVERSE_R10.json), sete famílias. Nenhum motor novo foi integrado ao pacote `ricoeur`.

## Evidências mais recentes

- **MiniSearch (JavaScript, MIT)**: PASS em CI, P@10=1, mediana **0,290 ms** no conjunto sintético de 1.000 documentos. [JSON](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/minisearch-latest.json).
- **FlexSearch (JavaScript, Apache-2.0)**: PASS em CI, P@10=1, mediana **0,021 ms**, mesmo conjunto simplificado. [JSON](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/flexsearch-latest.json).
- Os motores tiveram parâmetros de consulta diferentes, sem teste de gravação incremental nem índice persistido; os tempos **não autorizam substituição** do FTS5.
- **GitHub discovery automatizado**: 9 buscas públicas, 287 repositórios únicos apresentados, **90 novos nomes pontuados heurística e NÃO revisados** contra o inventário R08 de 134. Não são 90 concorrentes aprovados. [Relatório](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/discovery/latest.json).
- Uma triagem manual do resultado acrescentou à R09: Basic Memory (AGPL-3), Loominary (histórico de branches), MCP Memory Service (Apache-2.0), Semantica (grafo e raciocínio determinístico), DSH Chat Import (~25 importadores, dependência de plataforma) e LeanCTX.
- A varredura dirigida posterior acrescentou: [MARM Memory](https://github.com/Lyellr88/marm-memory) (escrita durável com outbox + grafo), [Cortex App](https://github.com/trace-cortex/cortex-app) (revisão humana e memória citada) e [Codex Sessions Manager](https://github.com/1939869736luosi/codex-sessions-manager) (repair com rollback e auditoria).
- A última auditoria GH de licenças obtida anteriormente só confirmou 83 de 100 repositórios do inventário R05. **Não extrapolar** esse resultado para 143; o fluxo da auditoria mais recente permanece independente e sua atualização deve ser verificada.

## Descobertas que ameaçam o diferencial

1. **Preservação da origem, estrutura e branches** já é descrita por Polylogue, CTK e Loominary.
2. **Repair de histórico, sessões órfãs e rollback** já aparece em IronBridge, Codex Sessions Manager e CTK.
3. **Memória aprovada por humanos e auditoria contextual** já aparece em OpenSelf e Cortex.
4. **Grafo de conhecimento temporal/proveniência** já aparece em Graphiti, Cognee, MARM e Semantica.
5. **Busca local de conversas via CLI/MCP, sem LLM obrigatório** já aparece em MyChatArchive, hstry, AI Conversation Index, Chat Chronicle e no Ricoeur original.

São **capacidades declaradas por autores**, ainda sem experimento equivalente de integridade e qualidade. Não usar essas linhas como veredito de superioridade funcional.

## Critério efetivo de saturação

Fase 2 permanece **OPEN / NOT_EXHAUSTED**. As três últimas rodadas encontraram candidatos com capacidades novas para o desenho do Cha2db. Uma pesquisa em repositórios públicos não comprova que o mundo foi exaurido; duas rodadas consecutivas sem *novo candidato viável que altere a decisão de uma porta P0*, após inspeção manual de candidatos com pontuação alta, aproximam o gate de saturação. Repositórios apenas nomeados ou reposicionados sem mudança de escopo não devem se acumular como trabalho infinito.

## Decisão de arquitetura

**Não criar novo motor de busca.** Manter FTS5 baseline até os candidatos equivalentes passarem consultas difíceis, medidas justas e licença. Avaliar reuso de importação/repair (Polylogue/CTK/IronBridge), memória/revisão (OpenSelf/Cortex), grafos (Graphiti/Semantica/MARM) e motores opcionais (Tantivy, BM25S, sqlite-vec, Orama, MiniSearch, FlexSearch, LanceDB). Toda proposta deve preservar as mensagens, origem, timestamps, branches, contratos e revisão humana sem LLM obrigatória.

Links das execuções e processos estão registrados na [R09](PHASE2_CORE_COMPETITIVE_VERDICT_R09.md). Fase 3 ainda não autorizada.
