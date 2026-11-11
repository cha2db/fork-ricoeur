# Cha2db — Fase 2 · Varredura de arquiteturas e produtos experimentais (R16)

**Data:** 11/11/2026. **Mandato:** pesquisa da Fase 2; a Fase 3/UX não foi alterada.

## Inventário reconciliado

- Inventário histórico: 143 candidatos em `PHASE2_MARKET_UNIVERSE_R10.json`.
- Ampliação anterior R14: 64 candidatos adicionais.
- Nova pesquisa de busca, armazenamento, grafo, browser, P2P e Android: 29 produtos listados, **10 duplicados**, 19 inéditos.
- Descoberta estruturada no GitHub: **21 consultas**, 631 repositórios distintos retornados, 196 nomes com pontuação heurística fora do inventário R15; **nenhum desses 196 foi aprovado automaticamente**.
- Revisão manual dirigida: nove candidatos com abordagens de memória causal, bitemporal e verificável adicionados.
- **R16 = 235 candidatos únicos**, IDs `C001..C235`; 143 anteriores + 92 ainda na fronteira experimental. Fases e rankings históricos preservados.

A fonte canônica do inventário é [`PHASE2_MARKET_UNIVERSE_R16.json`](PHASE2_MARKET_UNIVERSE_R16.json). A evidência operacional e a fila de confronto ficam no [ranking da fronteira (ci-results)](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/frontier/latest.json). A descoberta programada busca novidades duas vezes por semana, agora deduplicando contra R16.

## Hipóteses de arquitetura além de BM25, embeddings e RRF

| Enfoque | Projetos | Ganho potencial a testar | Alerta / gate |
| --- | --- | --- | --- |
| **Fonte bruta imutável + memória derivada verificável** | [taOSmd](https://github.com/jaylfc/taosmd), [CTK](https://github.com/queelius/ctk) | Manter prova do original enquanto índices e decisões são reconstruídos | taOSmd AGPL-3.0; métricas relatadas pelo autor não são evidência independente |
| **Bitemporalidade e versões** | [XTDB](https://github.com/xtdb/xtdb), [SirixDB](https://github.com/sirixdb/sirix), [TerminusDB](https://github.com/terminusdb/terminusdb), [INITE Brain](https://github.com/inite-ai/inite-brain-service) | Responder o que era válido em uma data *e* o que o sistema sabia naquele instante | Contrato e custo; INITE Brain AGPL-3.0 |
| **Memória determinística com abstenção e correção** | [Aura Memory](https://github.com/teolex2020/aura-memory), [Agent Memory](https://github.com/agent-memory-lab/agent-memory), [Engraphis](https://github.com/Coding-Dev-Tools/engraphis) | Decisões com fonte/escopo, não inventar fato sem prova e preservar revisões | Todos só têm evidência documental nesta rodada, não PASS do Cha2db |
| **Efeitos e causalidade verificáveis** | [Agentic Data Kernel](https://github.com/Jason-Doyle/agentic-data-kernel) e [OpenLineage](https://github.com/OpenLineage/OpenLineage) | Rastrear importação, transformação, indexação, erro, rollback e recibo do agente | Projeto incipiente, documentação admite IA e potenciais erros |
| **Detecção de conflitos e memória temporal** | [YantrikDB](https://github.com/yantrikos/yantrikdb) | Criar candidatos `contradicts` e `supersedes` sem atribuir-lhes veracidade automaticamente | Aprovação humana obrigatória; runtime SQLite embutido exige prevenção de corrupção entre conexões |
| **Busca e grafo integrados sem vários stores** | [Infino](https://github.com/infino-ai/infino), [LadybugDB](https://github.com/LadybugDB/ladybug), [HelixDB](https://github.com/helixdb/helix-db), [sqlite-graph](https://github.com/shwetarkadam/sqlite-graph) | Mesmo banco para texto/índice/vetor/relação; reduzir custo de sincronização | Indexação incremental e integridade da fonte precisam ser testadas |
| **Consulta multi-hop declarativa** | [CozoDB](https://github.com/cozodb/cozo), [DataScript](https://github.com/tonsky/datascript) | Perguntar por decisões dependentes de premissas refutadas, com trilha | Consultar relações explícitas não equivale a inferir contradições |
| **Captura do que o backup pode omitir** | [Threadline](https://github.com/terra901/Threadline), [Personal AI Memory](https://github.com/marswangyang/personal-ai-memory) | Capturar branches e revisões durante a conversa, mantendo IDs e origem | Browser/serviços suportados e privacidade precisam ser validados |
| **Motor Android autônomo** | [Kalan DB](https://github.com/Abhinivesh2729/kalan-db) | Teste ARM64 real de BM25+HNSW+ONNX local sem Python pesado | Prova de conceito, sem benchmark Cha2db |
| **Outros modelos sem servidor** | [PGlite](https://github.com/electric-sql/pglite), [LiveStore](https://github.com/livestorejs/livestore), [Pagefind](https://github.com/Pagefind/pagefind), [Automerge](https://github.com/automerge/automerge) | Separar histórico imutável, leitura offline, sincronização de anotações e índices no navegador | Não substituir o SQLite atual sem ganho de valor mensurável |

## Confrontos prioritários da R16

O ranking automatizado anterior R13 para 143 tecnologias **continua intocado**. A fila experimental atualiza os 17 confrontos R15 e adiciona nove de memória:
1. **Aura Memory × OpenSelf**: correção, confiança e modo offline sem embeddings nem LLM exigidas.
2. **Agent Memory × Graphiti**: esquecimento de fonte deve resultar em resposta desconhecida, tempo válido e proveniência.
3. **YantrikDB × RDFLib**: separar detecção *candidata* de contradição e decisão humana confirmada, com SQLite seguro.
4. **Engraphis × OpenSelf**: abstenção com evidência fraca, escopos e histórico temporal.
5. **Agentic Data Kernel × CTK**: recibo de importação incerta, duas execuções e rollback causal.
6. **INITE Brain × Graphiti**: conflito bitemporal; bloqueio de licença antes de embutir.
7. **taOSmd × CTK**: preservação exata de bytes, perdas de ramos, hash e verificabilidade da informação extraída.
8. **Remnic × OpenSelf**: revisão humana, formatos portáveis e escopos.
9. **Bitemporal PostgreSQL experimental × XTDB**: valid-time e transaction-time em consultas as-of.

**Todos são confrontos planejados, não testes concluídos.** Tecnologias novas só passam ao ranking de adoção após repetir a mesma fixture, custo operacional, corretude, licença e integração por porta. Um projeto com 0–2 estrelas ou sem release não é desqualificado automaticamente: deve, porém, demonstrar concretamente o mecanismo que promete.

## Controles

- Fonte e bytes originais imutáveis; índices e memórias são derivados e reversíveis.
- Human-first: nenhuma inferência, remoção ou decisão automática aprovada por LLM sem revisão humana.
- Modelos, vetores, MCP, A2A, servidor e GUI são adapters opcionais.
- GitHub Actions com logs, teste isolado, IDs canônicos e benchmark sob condições equivalentes.
- Não reivindicar anterioridade exclusiva para grafo temporal, auditoria de contexto ou relações entre chats: há implementações anteriores.
- Fase 3 continua independente e consome apenas contratos de leitura estáveis.

**Conclusão:** R16 amplia o universo de pesquisa e evidencia lacunas ainda não comparadas. Nem a Internet nem a Fase 2 estão comprovadamente esgotadas; não substituir o núcleo SQLite/FTS5 até haver ganho verificável.
