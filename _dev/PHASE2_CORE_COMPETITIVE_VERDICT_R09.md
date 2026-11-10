# Cha2db — Fase 2 · varredura competitiva e decisão de núcleo R09 (10/11/2026)

## Regras de interpretação

**Não é um produto composto ainda.** `cha2db/fork-ricoeur` continua executando FTS5 diretamente no código `src/ricoeur/retrieval.py`; candidatos abaixo só foram medidos em jobs isolados ou estudados por seus repositórios. O universo da Fase 2 tem **140 candidatos em sete famílias** (`_dev/PHASE2_MARKET_UNIVERSE_R09.json`). Isto não equivale a 140 candidatos instalados, homologados, licenciados ou comparados.

A mesma base sintética verificável, com 1.000 conversas e 40.000 mensagens, foi reconstruída no GitHub Actions para experimentos de indexação e busca; os motores externos receberam **1.000 mensagens representativas**, uma por conversa. A lista de consultas é simples e repetitiva, derivada dos tópicos do gerador. Nenhum P@10=1 nesse ensaio prova qualidade real, desempenho competitivo ou capacidade de processar o arquivo inteiro.

## Resultados de motores EMBEDDED efetivamente executados

| Núcleo | Status de execução GH | P@10 médio na amostra | Latência mediana, ms | Parecer Fase 2 |
| --- | --- | ---: | ---: | --- |
| SQLite FTS5/BM25 | PASS, já exercitado até 2M mensagens em teste distinto | 1,00 em consultas exatas | benchmark próprio | **MANTER baseline**; baixo custo e já incorporado |
| Tantivy-py (Rust) | PASS | 1,00 | 0,046 | **Candidato fortíssimo** para porto lexical opcional; provar escrita incremental e 40k/1M antes de trocar |
| BM25S | PASS | 1,00 | 0,063 | Candidato alternativo lexical em Python; evitar duplicação com FTS5 |
| Orama (JS) | PASS | 1,00 | 0,469 | **Candidato JS/browser/edge** independente |
| MiniSearch (JS) | PASS | 1,00 | consultar relatório | Candidato leve JS MIT com fuzzy e sugestão |
| FlexSearch (JS) | PASS | 1,00 | consultar relatório | Candidato JS Apache-2.0; avaliar custo de persistência |
| LanceDB (biblioteca) | PASS FTS + vetorial + híbrido | 1,00 cada modo | 2,620 / 3,037 / 5,501 | **Candidato de agregação**: experimentos em 1k, não vence FTS5 por esse teste |
| USearch (Rust/ANN) | PASS | 1,00 com TF-IDF/SVD32 | 0,576 | Candidato índice vetorial, não modelo semântico |
| sqlite-vec | PASS | ver teste KNN | 0,04–0,11 (poucas consultas) | Candidato vetor local opcional |
| DuckDB FTS | PASS | 1,00 | 6,463 | Sem motivo atual para migrar núcleo operacional |
| FTS5 trigram | PASS sobre 40k | equivalência LIKE em 10 consultas | variável | Candidato substring; cresce índice em ~42,5 MiB |
| rank-bm25, RapidFuzz, TF-IDF, RRF, NetworkX, BERTopic, CrossEncoder | PASS técnico em baterias específicas | ver métricas | ver relatório anterior | Componentes opcionais, não núcleo integrado |

Os resultados entre jobs/motores **não** são benchmarking equivalente de capacidade, limites de memória ou p95; usam tokenização, consulta e lógica de ranking diferentes. Links: [Tantivy](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/tantivy-latest.json), [BM25S](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/bm25s-latest.json), [Orama](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/orama-latest.json), [MiniSearch](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/minisearch-latest.json), [FlexSearch](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/flexsearch-latest.json), [LanceDB](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/lancedb-latest.json).

## Concorrentes diretos ao comportamento de produto (NÃO testados de ponta a ponta)

| Produto | Capacidade já descrita no projeto | Qual parte do Cha2db ameaça substituir | Limitação ou gate |
| --- | --- | --- | --- |
| [Ricoeur upstream](https://ricoeur.cc/) | CLI, importação ChatGPT/Claude e arquivo SQLite FTS | Base que o fork implementa | Verificar roadmap e bugs upstream antes de divergir |
| [Reweave](https://github.com/seolbbb/reweave) | Fonte da mensagem, contexto de decisões, correções versionadas/undo, busca local | Histórico/revisão contextual | MIT, Windows/inicial; análise profunda de contexto pode depender de modelos |
| [Polylogue](https://github.com/Sinity/polylogue) | Arquivo bruto, normalização de sessões/linhagem, busca/MCP e anotações auditáveis | Normalização, fonte, continuidade da sessão | Extrair contrato de importação e testar preservação real |
| [CTK](https://github.com/queelius/ctk) | Importadores plugin, árvore/branches, diff/merge/dedupe, FTS5, embeddings | Importação, reparo e agrupamento | Validar API/contratos, formato árvore e licença por versão |
| [IronBridge](https://github.com/nervosys/IronBridge) | Recuperação de sessões órfãs, merge cronológico e FTS/MCP | **Repair** e recuperação da história | Validar provas de não duplicação e origem entre workspaces |
| [Loominary](https://github.com/Laumss/loominary) | Versões antigas de respostas e branches, memória contextual e múltiplas plataformas | Captura de branches e memória original | Browser/extension específico; testar formato e política de privacidade |
| [hstry](https://github.com/byteowlz/hstry) | Rust MIT, SQLite, importação de agentes/web, CLI/TUI/MCP, retomada | Motor operacional multi-provedor | Comparar adapters e esquema de armazenamento |
| [OpenSelf](https://github.com/Open-Self/Open-Self) | Contexto por escopo/tempo/confiabilidade, aprovação humana, auditoria encadeada e MCP | Governança da memória e rastreabilidade | MIT declarado; confirmar integração e semântica de políticas |
| [Graphiti](https://github.com/getzep/graphiti) | Grafo temporal com episódios, proveniência, invalidação e recuperação | Interligação temporal de fatos | Apache-2.0, depende de Neo4j/OpenAI por padrão; não é núcleo SQLite mínimo |
| [Cognee](https://github.com/topoteretes/cognee) | Grafo e memória de conversas/documentos com embeddings CPU locais | Composição de memória/grafos | Apache-2.0 mas stack pesada; modelos/regras separados |
| [Mem0](https://github.com/mem0ai/mem0) | Memória entre sessões, datas e vetores | Persistência de contexto | Apache-2.0, serviços/deps de vetor e OpenAI no pacote; comparar operação offline |
| [MyChatArchive](https://github.com/1ch1n/mychatarchive) | ChatGPT/Claude/Grok import, SQLite, vetor local, ferramentas MCP | Archive+search+MCP completo | AGPL-3.0/comercial requer análise; offline sem modelo em camada básica |
| [AI Conversation Index](https://github.com/davidjbeveridge/chat-history-index-mcp) | SQLite FTS, embeddings determinísticos, importação idempotente e MCP com auth | Entrada, proveniência e transporte | Testar exportação de contratos e ACL |
| [Basic Memory](https://github.com/basicmachines-co/basic-memory) | Markdown memória 2 vias, grafo e MCP | Contexto compartilhado humano/agente | AGPL-3.0; adoção no core comercial requer avaliação |
| [MCP Memory Service](https://github.com/doobidoo/mcp-memory-service) | REST/MCP/OAuth, decisões e grafos causais | Memória acessível por adapters | API pode substituir parte do orquestrador se acoplável |
| [Semantica](https://github.com/semantica-agi/semantica) | Grafo RDF/LPG, contexto, raciocínio determinístico e proveniência | Ligações e verificação explicável de assuntos | MIT declarado; testar robustez factual das relações |
| [Summa 2](https://github.com/SpaceFrontiers/summa) | Busca Rust embedded, BM25, vetores híbridos, gRPC, WASM | Motor de busca de nova geração | MIT; build/cross compile complexos, ainda não medido no corpus |
| [XERJ](https://github.com/xerj-org/xerj) | Motor Rust offline, BM25/kNN/híbrido, MCP, memória | Pode substituir busca e API inteiras | Apache-2.0; validar CLI, performance e restrições dos componentes |
| [Chat Chronicle](https://github.com/TzurV/mcp-chat-chronicle) | Normalização SQLite/FTS e importação + MCP read-only | Fluxo principal de entrada e busca | Comparar formatos de exportação e estabilidade dos IDs |
| [Anamnesis](https://github.com/Trapezohe/Anamnesis) | Agregação Rust de memorias com linhagem, watch, CLI+MCP e busca híbrida | Importação incremental e continuidade | Verificar implantação sem dependência de modelo |
| [Sift](https://github.com/hrishikeshs/sift) | Indexação incremental por byte offset e arquivo diário comprimido | Resiliência contra truncamento e perda de dados | Go single binary, MIT; origem por provedor restrita |
| [claudex](https://github.com/utensils/claudex) | Histórico aditivo de onze agentes no SQLite, filtros e JSON | Suporte de formatos e auditoria de coding agents | Confirmar fidelidade e filtros cross-provider |

**Nível de evidência desses produtos**: leitura de README, manifests e documentação dos autores, *não homologação funcional ou legal*. Requisitos do Cha2db como human-first, visão das decisões e contrato de adaptadores ainda podem não ser cobertos — hipóteses a serem testadas, não diferencial automático.

## Riscos jurídicos e de implantação

1. Não confundir **Orama JS Apache-2.0** com **OramaCore AGPL-3.0**; são produtos distintos.
2. Não incorporar MyChatArchive, Basic Memory ou outros AGPL/GPL sob licença supostamente permissiva. Avaliação legal e política de distribuição são gates separados.
3. Licença código ≠ licença de pesos de modelo, de serviços externos, de componentes e das edições comercial/enterprise.
4. Não contam como aptos a embedded local-first produtos que só funcionem como servidor pesado, cloud obrigatório ou com LLM/API obrigatória. Podem existir adapters remotos opcionais.
5. Projetos `kuzudb/kuzu` e `reorproject/reor` foram identificados arquivados no audit anterior; confirmar o status novamente na próxima auditoria antes de adoção.

## Pesquisa até saturação — evidência e restrições

- Inventário [R09 JSON](PHASE2_MARKET_UNIVERSE_R09.json) com **140** candidatos identificados.
- [Audit GitHub](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/audit/latest.json): verifica metadata; pode apontar inventário anterior quando CI ainda não concluiu.
- [Descoberta automática](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/discovery/latest.json): nove buscas públicas no GitHub, deduplicação de candidatos e priorização heurística. Reportou **90 repositórios desconhecidos da R08** que exigiam revisão humana. 90 NÃO é contagem de produtos válidos ou melhores.
- Saturação só quando houver **dois ciclos independentes sucessivos sem novos candidatos que mudem um gate P0**, cobertura de licenças e contratos, e benchmark qualitativo dos principais candidatos de mesma porta. A fase 2 **continua aberta** e a existência de novos concorrentes relevantes prova que ainda não saturou.

## Decisão provisória de núcleo (NÃO autoriza Fase 3)

- **Manter SQLite FTS5 do Ricoeur como baseline**, pois não surgiu ganho demonstrado suficiente para troca e ele já passou testes de escala.
- **Porta LexicalSearch**: priorizar comparação mais forte Tantivy, BM25S, Orama, MiniSearch/FlexSearch contra FTS5 no banco inteiro e workloads difíceis; não integrar até veredito.
- **Porta VectorIndex**: sqlite-vec, USearch, LanceDB. Sem modelo LLM como obrigação.
- **Portas Ingest/Repair**: priorizar CTK, Polylogue, IronBridge, hstry e Loominary: área com maior potencial de reaproveitamento e impacto de origem.
- **Portas TopicGraph/Memory/Temporal**: avaliar Graphiti, OpenSelf, Semantica, Cognee e Reweave contra relações rotuladas, confiança e evidências. Similaridade NÃO significa relação factual.
- **Portas MCP/HTTP/A2A**: seguir independentes do motor; já existe integração MCP na base.
- **NÃO reivindicar novidade** para busca cruzada, recuperação MCP, fontes, grafo temporal ou revisão humana isoladamente. A novidade precisa ser demonstrada em combinação com cenários concretos não cobertos pelo prior art.

## Próxima evidência exigível
Conjunto de transcrições variado com casos difíceis, consultas PT/EN humanas, branches, interrupções, histórico reescrito, importação repetida e pares de relações com gabarito auditável. Avaliação incremental por porta contra a base com mesmos IDs, sem falsa conclusão a partir da fixture repetitiva de 40k.
