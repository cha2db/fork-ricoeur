# Cha2db — Ranking contínuo da Fase 2 (R13)

Este ranking é de **prioridade de confronto por porta**, não uma classificação universal de qualidade.
**A Fase 3 de UX pertence à sessão paralela; nenhuma alteração de UI é autorizada por esta matriz.**

Atualizado (UTC): 2026-11-12T23:41:22.849388+00:00

**143/143 candidatos classificados em 11 portas; 22 PASS, 2 FAIL e 2 bloqueios técnicos.**

PASS significa exclusivamente um gate técnico específico em fixture sintética. Não prova desempenho real, licença apta nem integração no Cha2db.

## Quem lidera cada porta entre os efetivamente testados

| Porta | Melhor evidência disponível | Próximo sem teste equivalente |
| --- | --- | --- |
| Entrada, origem e árvore de conversas | Conversation Toolkit CTK (C118, PASS) | Polylogue (C115) |
| Repair, deduplicação e reconstrução | Ninguém homologado nesta porta | Codex Sessions Manager (C143) |
| Busca textual embutida no núcleo | SQLite FTS5 (C001, PASS) | XERJ (C103) |
| Busca JS local para clientes e Edge | FlexSearch (C011, PASS) | — |
| Índices vetoriais opcionais | sqlite-vec (C028, PASS) | FAISS (C033) |
| Busca semântica, fuzzy e reranking | RapidFuzz (C057, PASS) | FastEmbed (C046) |
| Tópicos, relações e grafos auditáveis | RDFLib (C065, PASS) | Semantica (C138) |
| Memória, decisões e validade temporal | Ninguém homologado nesta porta | OpenSelf (C114) |
| Métricas, datasets e controle de qualidade | ir-measures (C090, PASS) | ranx (C091) |
| Servidores e adapters remotos de busca | Ninguém homologado nesta porta | OpenSearch (C016) |
| Referências comerciais e tecnológicas | Ninguém homologado nesta porta | — |

## Ranking por porta (todos os candidatos)

### Entrada, origem e árvore de conversas

| Posição | ID | Candidato | Evidência funcional | Elegibilidade |
| ---: | --- | --- | --- | --- |
| 1 | C118 | Conversation Toolkit CTK | PASS | PASS_CANDIDATE |
| 2 | C115 | Polylogue | NOT_TESTED | UNTESTED_CANDIDATE |
| 3 | C116 | hstry | NOT_TESTED | UNTESTED_CANDIDATE |
| 4 | C135 | Loominary | NOT_TESTED | UNTESTED_CANDIDATE |
| 5 | C113 | AI Conversation Index | NOT_TESTED | UNTESTED_CANDIDATE |
| 6 | C119 | Anamnesis | NOT_TESTED | UNTESTED_CANDIDATE |
| 7 | C128 | claudex | NOT_TESTED | UNTESTED_CANDIDATE |
| 8 | C120 | OwnYourChat | NOT_TESTED | UNTESTED_CANDIDATE |
| 9 | C122 | UCW | NOT_TESTED | UNTESTED_CANDIDATE |
| 10 | C123 | AI Memory Explorer | NOT_TESTED | UNTESTED_CANDIDATE |
| 11 | C126 | chatparser | NOT_TESTED | UNTESTED_CANDIDATE |
| 12 | C130 | Sift macOS (native) | NOT_TESTED | UNTESTED_CANDIDATE |
| 13 | C131 | deja semantic MCP | NOT_TESTED | UNTESTED_CANDIDATE |
| 14 | C132 | claude-vault | NOT_TESTED | UNTESTED_CANDIDATE |
| 15 | C133 | momento | NOT_TESTED | UNTESTED_CANDIDATE |
| 16 | C134 | turnlog | NOT_TESTED | UNTESTED_CANDIDATE |
| 17 | C139 | DSH Chat Import | NOT_TESTED | UNTESTED_CANDIDATE |
| 18 | C111 | MyChatArchive | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 19 | C108 | Ricoeur upstream | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 20 | C121 | Gora | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 21 | C129 | conversation-search MCP | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 22 | C101 | Reweave | FAIL | INELIGIBLE_OR_BLOCKED |
| 23 | C112 | Chat Chronicle | FAIL | INELIGIBLE_OR_BLOCKED |

### Repair, deduplicação e reconstrução

| Posição | ID | Candidato | Evidência funcional | Elegibilidade |
| ---: | --- | --- | --- | --- |
| 1 | C143 | Codex Sessions Manager | NOT_TESTED | UNTESTED_CANDIDATE |
| 2 | C097 | Splink | NOT_TESTED | UNTESTED_CANDIDATE |
| 3 | C098 | dedupe | NOT_TESTED | UNTESTED_CANDIDATE |
| 4 | C127 | Sift CLI (Go) | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 5 | C117 | IronBridge | NOT_TESTED | INELIGIBLE_OR_BLOCKED |

### Busca textual embutida no núcleo

| Posição | ID | Candidato | Evidência funcional | Elegibilidade |
| ---: | --- | --- | --- | --- |
| 1 | C001 | SQLite FTS5 | PASS | BASELINE |
| 2 | C003 | Tantivy / tantivy-py | PASS | PASS_CANDIDATE |
| 3 | C004 | BM25S | PASS | PASS_CANDIDATE |
| 4 | C005 | rank-bm25 | PASS | PASS_CANDIDATE |
| 5 | C103 | XERJ | NOT_TESTED | UNTESTED_CANDIDATE |
| 6 | C013 | Sonic | NOT_TESTED | UNTESTED_CANDIDATE |
| 7 | C002 | SQLite FTS5 trigram | PASS | LICENCE_VERIFY_BEFORE_EMBED |
| 8 | C102 | Summa 2 / SpaceFrontiers | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 9 | C008 | DuckDB FTS | PASS | LICENCE_VERIFY_BEFORE_EMBED |
| 10 | C006 | Whoosh | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 11 | C007 | Xapian | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 12 | C012 | Lucene | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 13 | C109 | Summa original (archived) | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 14 | C110 | Bichon email archive | NOT_TESTED | INELIGIBLE_OR_BLOCKED |

### Busca JS local para clientes e Edge

| Posição | ID | Candidato | Evidência funcional | Elegibilidade |
| ---: | --- | --- | --- | --- |
| 1 | C011 | FlexSearch | PASS | PASS_CANDIDATE |
| 2 | C010 | MiniSearch | PASS | PASS_CANDIDATE |
| 3 | C009 | Orama | PASS | LICENCE_VERIFY_BEFORE_EMBED |

### Índices vetoriais opcionais

| Posição | ID | Candidato | Evidência funcional | Elegibilidade |
| ---: | --- | --- | --- | --- |
| 1 | C028 | sqlite-vec | PASS | PASS_CANDIDATE |
| 2 | C035 | LanceDB | PASS | PASS_CANDIDATE |
| 3 | C031 | USearch | PASS | PASS_CANDIDATE |
| 4 | C032 | hnswlib | PASS | PASS_CANDIDATE |
| 5 | C034 | Annoy | PASS | PASS_CANDIDATE |
| 6 | C033 | FAISS | NOT_TESTED | UNTESTED_CANDIDATE |
| 7 | C037 | Chroma | NOT_TESTED | UNTESTED_CANDIDATE |
| 8 | C039 | Qdrant | NOT_TESTED | UNTESTED_CANDIDATE |
| 9 | C040 | Milvus | NOT_TESTED | UNTESTED_CANDIDATE |
| 10 | C036 | DuckDB VSS | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 11 | C038 | pgvector | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 12 | C041 | Weaviate | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 13 | C042 | Redis vector search | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 14 | C029 | SQLite vec1 | UNAVAILABLE_ON_STOCK_RUNNER | INELIGIBLE_OR_BLOCKED |
| 15 | C030 | SQLite-Vector PyPI | BLOCKED | INELIGIBLE_OR_BLOCKED |
| 16 | C043 | Vald | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 17 | C044 | Vearch | NOT_TESTED | INELIGIBLE_OR_BLOCKED |

### Busca semântica, fuzzy e reranking

| Posição | ID | Candidato | Evidência funcional | Elegibilidade |
| ---: | --- | --- | --- | --- |
| 1 | C057 | RapidFuzz | PASS | PASS_CANDIDATE |
| 2 | C045 | Sentence Transformers | PASS | PASS_CANDIDATE |
| 3 | C046 | FastEmbed | NOT_TESTED | UNTESTED_CANDIDATE |
| 4 | C053 | FlashRank | NOT_TESTED | UNTESTED_CANDIDATE |
| 5 | C049 | PyLate | NOT_TESTED | UNTESTED_CANDIDATE |
| 6 | C050 | ColBERT | NOT_TESTED | UNTESTED_CANDIDATE |
| 7 | C054 | llama.cpp embeddings | NOT_TESTED | UNTESTED_CANDIDATE |
| 8 | C055 | GLiNER | NOT_TESTED | UNTESTED_CANDIDATE |
| 9 | C056 | spaCy | NOT_TESTED | UNTESTED_CANDIDATE |
| 10 | C052 | CrossEncoder | PASS | LICENCE_VERIFY_BEFORE_EMBED |
| 11 | C047 | BGE-M3 | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 12 | C048 | multilingual E5 | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 13 | C051 | SPLADE | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |

### Tópicos, relações e grafos auditáveis

| Posição | ID | Candidato | Evidência funcional | Elegibilidade |
| ---: | --- | --- | --- | --- |
| 1 | C065 | RDFLib | PASS | PASS_CANDIDATE |
| 2 | C059 | BERTopic | PASS | PASS_CANDIDATE |
| 3 | C138 | Semantica | NOT_TESTED | UNTESTED_CANDIDATE |
| 4 | C060 | KeyBERT | NOT_TESTED | UNTESTED_CANDIDATE |
| 5 | C061 | Top2Vec | NOT_TESTED | UNTESTED_CANDIDATE |
| 6 | C066 | ArcadeDB | NOT_TESTED | UNTESTED_CANDIDATE |
| 7 | C062 | HDBSCAN | NOT_TESTED | UNTESTED_CANDIDATE |
| 8 | C068 | Apache AGE | NOT_TESTED | UNTESTED_CANDIDATE |
| 9 | C058 | NetworkX | PASS | LICENCE_VERIFY_BEFORE_EMBED |
| 10 | C069 | FalkorDB | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 11 | C070 | Memgraph | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 12 | C063 | Leidenalg | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 13 | C064 | igraph | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 14 | C067 | Neo4j Community | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 15 | C071 | Kùzu | NOT_TESTED | INELIGIBLE_OR_BLOCKED |

### Memória, decisões e validade temporal

| Posição | ID | Candidato | Evidência funcional | Elegibilidade |
| ---: | --- | --- | --- | --- |
| 1 | C114 | OpenSelf | NOT_TESTED | UNTESTED_CANDIDATE |
| 2 | C072 | Graphiti | NOT_TESTED | UNTESTED_CANDIDATE |
| 3 | C142 | Cortex App | NOT_TESTED | UNTESTED_CANDIDATE |
| 4 | C141 | MARM Memory | NOT_TESTED | UNTESTED_CANDIDATE |
| 5 | C073 | Cognee | NOT_TESTED | UNTESTED_CANDIDATE |
| 6 | C074 | Mem0 | NOT_TESTED | UNTESTED_CANDIDATE |
| 7 | C137 | MCP Memory Service | NOT_TESTED | UNTESTED_CANDIDATE |
| 8 | C075 | HippoRAG 2 | NOT_TESTED | UNTESTED_CANDIDATE |
| 9 | C076 | LightRAG | NOT_TESTED | UNTESTED_CANDIDATE |
| 10 | C077 | Microsoft GraphRAG | NOT_TESTED | UNTESTED_CANDIDATE |
| 11 | C078 | Letta | NOT_TESTED | UNTESTED_CANDIDATE |
| 12 | C083 | AnythingLLM | NOT_TESTED | UNTESTED_CANDIDATE |
| 13 | C086 | Haystack | NOT_TESTED | UNTESTED_CANDIDATE |
| 14 | C087 | LlamaIndex | NOT_TESTED | UNTESTED_CANDIDATE |
| 15 | C088 | txtai | NOT_TESTED | UNTESTED_CANDIDATE |
| 16 | C089 | Matrix Seshat | NOT_TESTED | UNTESTED_CANDIDATE |
| 17 | C106 | reactor semantic | NOT_TESTED | UNTESTED_CANDIDATE |
| 18 | C107 | Soma offline | NOT_TESTED | UNTESTED_CANDIDATE |
| 19 | C140 | LeanCTX | NOT_TESTED | UNTESTED_CANDIDATE |
| 20 | C080 | Open WebUI | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 21 | C081 | Onyx CE | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 22 | C136 | Basic Memory | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 23 | C082 | Khoj | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 24 | C084 | Reor | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 25 | C085 | Microsoft semantic-kernel | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 26 | C105 | Synorive | NOT_TESTED | INELIGIBLE_OR_BLOCKED |

### Métricas, datasets e controle de qualidade

| Posição | ID | Candidato | Evidência funcional | Elegibilidade |
| ---: | --- | --- | --- | --- |
| 1 | C090 | ir-measures | PASS | PASS_CANDIDATE |
| 2 | C091 | ranx | NOT_TESTED | UNTESTED_CANDIDATE |
| 3 | C095 | Label Studio | NOT_TESTED | UNTESTED_CANDIDATE |
| 4 | C096 | Argilla | NOT_TESTED | UNTESTED_CANDIDATE |
| 5 | C094 | RAGAS | NOT_TESTED | UNTESTED_CANDIDATE |
| 6 | C092 | BEIR | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 7 | C093 | MTEB | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 8 | C099 | Apache Tika | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 9 | C100 | Docling | NOT_TESTED | INELIGIBLE_OR_BLOCKED |

### Servidores e adapters remotos de busca

| Posição | ID | Candidato | Evidência funcional | Elegibilidade |
| ---: | --- | --- | --- | --- |
| 1 | C016 | OpenSearch | NOT_TESTED | UNTESTED_CANDIDATE |
| 2 | C019 | Quickwit | NOT_TESTED | UNTESTED_CANDIDATE |
| 3 | C020 | Vespa | NOT_TESTED | UNTESTED_CANDIDATE |
| 4 | C017 | Apache Solr | NOT_TESTED | UNTESTED_CANDIDATE |
| 5 | C014 | Meilisearch CE | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 6 | C022 | PostgreSQL FTS | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 7 | C023 | pg_trgm | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 8 | C024 | ZincSearch | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 9 | C025 | Elasticsearch | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 10 | C015 | Typesense | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 11 | C018 | Manticore Search | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 12 | C021 | ParadeDB | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 13 | C104 | OramaCore | NOT_TESTED | INELIGIBLE_OR_BLOCKED |

### Referências comerciais e tecnológicas

| Posição | ID | Candidato | Evidência funcional | Elegibilidade |
| ---: | --- | --- | --- | --- |
| 1 | C079 | Zep | NOT_TESTED | LICENCE_VERIFY_BEFORE_EMBED |
| 2 | C124 | Chat Locker | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 3 | C125 | Recalium | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 4 | C026 | Azure AI Search | NOT_TESTED | INELIGIBLE_OR_BLOCKED |
| 5 | C027 | Algolia | NOT_TESTED | INELIGIBLE_OR_BLOCKED |

## Ordem fixa de próximos confrontos

| Ordem | Porta | Incumbente | Desafiante | Prova exigida | Situação |
| ---: | --- | --- | --- | --- | --- |
| 1 | ingest_tree | Conversation Toolkit CTK | Polylogue | All branches, IDs, raw input hashes, repeated imports and missing nodes | CANDIDATE_UNTESTED |
| 2 | ingest_tree | Conversation Toolkit CTK | hstry | Multi-provider import, incremental cursor, cross-platform packaging | CANDIDATE_UNTESTED |
| 3 | repair_merge | Conversation Toolkit CTK | Codex Sessions Manager | Truncated/duplicated sessions, dry-run repair, rollback and provenance | CANDIDATE_UNTESTED |
| 4 | ingest_tree | Conversation Toolkit CTK | Loominary | ChatGPT regenerated responses, browser capture fidelity and original history | CANDIDATE_UNTESTED |
| 5 | ingest_tree | Conversation Toolkit CTK | AI Conversation Index | Normalized interchange, stable IDs, idempotent imports and MCP read-only | CANDIDATE_UNTESTED |
| 6 | memory_temporal | Sem solução PASS na porta | OpenSelf | Human approval, time validity, decision citation and scope without cloud | CANDIDATE_UNTESTED |
| 7 | memory_temporal | Sem solução PASS na porta | Graphiti | Episode/fact provenance and retractions, no mandatory remote LLM | CANDIDATE_UNTESTED |
| 8 | topic_relations | RDFLib | Semantica | Typed relations with source-evidence, no inference as fact | CANDIDATE_UNTESTED |
| 9 | lexical_core | SQLite FTS5 | Tantivy / tantivy-py | Whole 40k and 2M corpora, p95, index update/delete, disk and ARM | HEAD_TO_HEAD_PENDING |
| 10 | browser_index | FlexSearch | MiniSearch | Same tokenizer and query set, serialized index, accent, RAM/browser | HEAD_TO_HEAD_PENDING |
| 11 | browser_index | FlexSearch | Orama | JS hybrid functionality versus legal packaging and offline build | HEAD_TO_HEAD_PENDING |
| 12 | vector_index | sqlite-vec | LanceDB | Same vectors, recall@k, writes, persisted index, CPU/RAM/size | HEAD_TO_HEAD_PENDING |
| 13 | semantic_ranking | Sentence Transformers | FastEmbed | Human-labeled paraphrase relevance PT/EN, local CPU and model license | CANDIDATE_UNTESTED |
| 14 | repair_merge | Codex Sessions Manager | IronBridge | Repair provenance and rollback; AGPL distribution gate first | CANDIDATE_UNTESTED |

## Regras de atualização

A atualização é automática por GitHub Actions após os workflows de comparação e por agenda.
A ordenação não usa a menor latência de fixtures desiguais como escore: exige mesmo corpus, mesmo contrato, p95, memória, persistência, proveniência, estabilidade e custo.
Licenças, pesos de modelo e edições precisam ser verificados antes de embutir código. Sem LLM obrigatória.
O arquivo JSON contém os **143 IDs**, evidências pontuais, licença, ranking por porta e agenda de confrontos.
O contrato para a equipe UX é proposta de interface, não alteração funcional publicada.
