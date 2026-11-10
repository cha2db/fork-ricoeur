# Cha2db — Fase 2: varredura competitiva do núcleo de pesquisa (R05, 10/11/2026)

## Escopo da investigação
Encontrar **produtos, motores, bibliotecas, plataformas de memória e sistemas de ligação de assuntos** que já resolvam cada parte do Cha2db. **Não passar à Fase 3** até comparar candidatos existentes e avaliar a lacuna real. O inventário auditável está em [`PHASE2_MARKET_UNIVERSE_R05.json`](PHASE2_MARKET_UNIVERSE_R05.json): **100 candidatos, 7 famílias**, com links, prioridade e razão. Este inventário é extenso, mas não demonstra que todo software existente foi descoberto.

A arquitetura-alvo é local-first, determinística, human-first, com IDs e proveniência estáveis. MCP/A2A/API são portas, não requisitos de motores de busca. GUI e LLM são opcionais. Licenças precisam ser verificadas por versão, edição, modelo e transitive dependencies ANTES de integrar código.

## Risco de originalidade: anterioridade séria
- **Graphiti** (Apache 2.0): episódios como fontes, temporalidade, invalidação histórica de fatos, grafo + híbrido. Link: https://github.com/getzep/graphiti
- **Cognee** (Apache 2.0 código OSS): conversas/documentos/decisões, grafo persistente, MCP e modo local sem API key; atenção ao modo Postgres em demonstração comercial. https://github.com/topoteretes/cognee
- **Mem0** (Apache 2.0 OSS): memória multi-sessão, temporalidade, grafos/vetores. https://github.com/mem0ai/mem0
- **HippoRAG 2** (MIT): grafo, PageRank personalizado, recuperação multi-hop, MCP. https://github.com/OSU-NLP-Group/HippoRAG
- **LightRAG**: recuperação conjunta grafo + vetores; exige verificar dependências, LLM/modelos e licenciamento. https://github.com/HKUDS/LightRAG
- **Microsoft GraphRAG**: ótimo comparador metodológico, mas a própria README diz que está em **modo manutenção**; não selecionar como base estratégica sem avaliação. https://github.com/microsoft/graphrag
- **Open WebUI**: busca em histórico com filtros, mensagens, conversa compartilhada; já implementa parte do valor de descoberta. https://docs.openwebui.com/features/chat-conversations/chat-features/history-search/

Portanto, afirmar que 'grafo de assuntos com proveniência' seria *por si só* novidade é **NÃO ACEITÁVEL**. O possível diferencial do Cha2db precisa ser especificado com um cenário que os acima não atendam (por ex. normalização preservando a origem, reconstrução/repair de conversas entre provedores, validade de decisões, decisão humana formal e reprodução por CLI **sem dependência de LLM**). Até testar, isso é uma *hipótese*, não marketing.

## Famílias e cobertura (100 candidatos)
| Família | Quantidade | Prioridade |
| --- | ---: | --- |
| Motores lexicais embedded | 13 | P0 — Tantivy, BM25S, FTS5, Orama |
| Servidores de busca | 14 | P2 — Meilisearch CE, Typesense, Manticore, OpenSearch |
| Vetores e ANN | 17 | P0 — sqlite-vec, USearch, LanceDB, hnswlib |
| Modelos/ranking/extração | 13 | P1 — FastEmbed, BGE-M3, ColBERT/PyLate, GLiNER |
| Grafos e tópicos | 14 | P1 — NetworkX, BERTopic, ArcadeDB, RDFLib, Leiden |
| Produtos de memória, GraphRAG e conversa | 18 | **P0 de prior art** — Graphiti, Cognee, Mem0, HippoRAG, LightRAG, Onyx CE |
| Métricas, rotulagem e normalização | 11 | P0 — ir-measures, ranx, BEIR, Label Studio, Splink |

## Diferença entre adoção e comparação
1. **Motor embedded**: pode ser biblioteca interna, mas deve operar sobre a *mesma base*, retornar IDs canônicos, respeitar filtro e ACL, sobreviver à atualização do banco, instalar sem infraestrutura nova.
2. **Serviço externo**: pode ser adapter de backend/homologação, mas não deve tornar o produto local-first dependente de Docker ou rede.
3. **Produto de memória já pronto**: é candidato até a substituir funções inteiras; comparar contratos públicos e propriedades de proveniência, temporalidade, revisão humana e reversão.
4. **Modelo neural**: o software ser Apache/MIT não libera automaticamente os pesos, dados de treinamento ou direitos de implantação.
5. **Ferramenta de teste**: preferir ir-measures/ranx/BEIR a escrever métricas de recuperação próprias.

## Gates que precisam ser satisfatórios
- **Entrada e origem**: importação incremental idempotente, múltiplos formatos/provedores, integridade, IDs, branches, carimbos de tempo e reparação rastreável.
- **Lexical**: BM25, expressões, operadores, proximidade, filtros, Unicode/acentos, typos, indexação incremental, p50/p95, uso de RAM/disco.
- **Semântico**: conjunto gold humano PT/EN com paráfrases e negativos difíceis; nDCG@10, MRR@10, recall@k, latência e custo CPU/disco, licença modelo.
- **Híbrido**: qualidade e custo de RRF, ponderações e rankers, duplicação de mensagens, rastreabilidade dos scores.
- **Tópico e relações**: precisão por tipo `same_topic`, `follows_up`, `refines`, `contradicts`, `supersedes`, `references`; exigir evidência de mensagens, validade temporal, abstenção quando não houver referência.
- **Memória**: impedir falsa reescrita de decisões antigas, revisão humana de candidatos, audit trail, explicação 'de onde veio?', reversão.
- **Portabilidade**: GH Linux Python 3.11/3.13, Windows, Termux ARM64, WASM/JS quando aplicável.
- **Licença**: legalidade de embutir versus consumir remoto, licença da distribuição específica e dos pesos.

## Testes e execução já publicados
- FTS5: núcleo atual, escala 2M mensagens sintéticas em GitHub Actions.
- FTS5 trigram, RapidFuzz, TF-IDF, rank-bm25, RRF, sqlite-vec, NetworkX, BERTopic, CrossEncoder e Sentence Transformers: rodadas anteriores em `ci-results`.
- **Nova matriz** `.github/workflows/phase2-embedded.yml`: `bm25s`, `tantivy-py` e `usearch` em instalações isoladas, sobre o *mesmo banco temporário* criado por `_dev/build_prior_base.py`; os resultados são separados e guardados em `ci-results/ci-output/phase2/`.

Links automáticos (podem retornar 404 até primeiro run concluído):
- https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/bm25s-latest.json
- https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/tantivy-latest.json
- https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/usearch-latest.json

## Critério de esgotamento honesto
Não existe certificação de 'todos os produtos do mundo'. Fechamento exige: (1) nenhuma família funcional importante sem cobertura; (2) ao menos dois candidatos viáveis com contratos comparáveis para cada porta P0; (3) critérios de licença/instalação e qualidade checados; (4) dois ciclos consecutivos de descoberta sem candidatos novos que mudem ranking ou decisão; (5) lacunas/remanescentes documentadas. Produtos somente *localizados* não contam como *testados*.

## Veredito atual
Fase 2 expandida. Núcleo existente ainda FTS5; novas ferramentas são **candidatos isolados**, não agregação integrada. A interligação temporal e proveniência de dados possui forte anterioridade em Graphiti/Cognee/Mem0, que precisam ser comparados antes de alegar diferencial do Cha2db. Foco agora é exaurir valor já existente e evitar implementações próprias.
