# Cha2db — Triagem dirigida após busca R14: fila R15 (sem homologação)

Fonte: [GitHub Actions: descoberta 21 consultas contra 207 URLs](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/discovery/latest.json). Reportado: **630 repositórios distintos** apareceram nos resultados amostrados, **197 ainda não presentes no inventário R14** obtiveram pontuação heurística suficiente para análise humana e **0 falhas de consulta**. **197 não são produtos válidos/comparáveis até revisão independente.**

**Trilha R15**: projetos inspecionados diretamente por README e metadados GitHub; são **pré-candidatos**, não integram ainda a contagem/ranking validado de 207 e **nenhum teve teste funcional Cha2db**. Decidir admissão somente quando compararmos esquema, dependências, licença e funções por porta. Descoberta ainda **NOT_EXHAUSTED**.

## Pré-candidatos avaliados nesta varredura

| Ordem de análise | Nome / origem | Porta possível | Mecanismo e razão para confronto | Licença do GitHub | Decisão de triagem |
|---:|---|---|---|---|---|
| 1 | [Aura Memory](https://github.com/teolex2020/aura-memory) | `memory_temporal` | Runtime Rust local determinístico e sem LLM/embeddings obrigatórios; memória durável, revisão, contradição e proveniência | MIT | **P0 TESTAR CONTRATOS**, confrontar OpenSelf e Mnemos |
| 2 | [Agentic Data Kernel](https://github.com/Jason-Doyle/agentic-data-kernel) | `versioned_storage` | Contratos sobre SQLite/Postgres para fatos temporais, autorizações, efeitos externos, verificação/rollback e reconciliação | Apache-2.0 | **P0 INVESTIGAR** replay e logs de evidência; README avisa documentação gerada por IA e sujeito a erro |
| 3 | [Agent Memory](https://github.com/agent-memory-lab/agent-memory) | `memory_temporal` | Python 3.13+ sem dependências obrigatórias, SQLite, procedência, validade temporal, abstenção, histórico de correções, MCP opcional | NOASSERTION no metadado REST; README diz Apache-2.0 | **P0 GATE DE LICENÇA + CONTRATO** |
| 4 | [INITE Brain](https://github.com/inite-ai/inite-brain-service) | `memory_temporal` | Grafo de conhecimento bitemporal, conflitos no ingresso, esquecimento governado, MCP/REST, builds ARM64 | AGPL-3.0 | **P0 COMPARAR COMO REFERÊNCIA/API EXTERNA**; não embutir sem licença |
| 5 | [Remnic](https://github.com/joshuaswarren/remnic) | `interoperability_formats` | Markdown com frontmatter YAML e SQLite JSON local, limites de contexto, correção, MCP/HTTP | MIT | **P1** verificar esquema e origem, exportação humana |
| 6 | [taOSmd](https://github.com/jaylfc/taosmd) | `memory_temporal` | Arquivo append-only de conversas + fatos verificados contra fonte, busca híbrida e grafo; autor relata métricas próprias LongMemEval | AGPL-3.0 | **P0 DE PRIOR ART**, não de inclusão direta; repetir benchmark externo e verificar licença |
| 7 | [Mnemo Cortex](https://github.com/GuyMannDude/mnemo-cortex) | `memory_temporal` | Memória local com proveniência, fatos verificados, sincronização offline via USB e MCP, processos opcionais de síntese | MIT | **P2** confrontar componente local isolado, sem obrigar LLM |

## Descartes/limites observados

- `franken_accounting`: aplicação contábil bitemporal especializada, não substitui diretamente armazenamento/search de conversas. Sua arquitetura de evidência pode servir como referência; autor declara gate geral incompleto e licença MIT com rider.
- `anythingmcp`: gateway empresarial AGPL com muitas integrações, não substituto embedded de busca. Candidato apenas adapter remoto opcional.
- `Utopia`: grafo/world model empresarial amplo; alto acoplamento e claims extensos, não elegível como núcleo mínimo sem prova.

## Regras de admissão no ranking consolidado

1. Conferir URL/repositório, licença **do módulo adotável**, manutenção e duplicatas entre 207 existentes.
2. Registrar contrato exato por porta e cenário observável, não propaganda de README.
3. Testar no mesmo corpus e fixtures de ramificações e decisões, com fonte/ID/tempo.
4. Não implementar motor novo sem confronto com CTK/FTS5/sqlite-vec/RDFLib ou baseline SQLite+audit-log.
5. Adicionar candidato na próxima revisão de inventário com ID estável somente após a triagem do código; até lá, `NOT_TESTED` e sem pontuação de desempenho.

**Status:** R15_PRESCREEN, 7 pré-candidatos priorizados, 197 achados heurísticos ainda não exauridos. A Fase 2 mantém ranking R14 de 207 e não altera a branch Fase 3 de UX.
