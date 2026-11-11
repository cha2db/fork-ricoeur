# Cha2db — Ranking ampliado da Fase 2 R14

**207 candidatos**: 143 já triados e 64 novos da varredura.
**Fonte encontrada no GitHub:** 62 novos; fontes sem verificação: 0.
**PASS funcional dos novos: 2.** A maioria permanece descoberta/auditada, sem homologação.

## Ranking e filas por porta

### Entrada, origem e árvore de conversas (27)

| Pos. | ID | Produto | Status funcional | Status da origem | Próximo gate |
|---:|---|---|---|---|---|
| 1 | C118 | Conversation Toolkit CTK | PASS | LEGACY | Confronto do contrato existente |
| 2 | C115 | Polylogue | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 3 | C116 | hstry | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 4 | C135 | Loominary | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 5 | C113 | AI Conversation Index | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 6 | C119 | Anamnesis | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 7 | C128 | claudex | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 8 | C120 | OwnYourChat | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 9 | C122 | UCW | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 10 | C123 | AI Memory Explorer | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 11 | C126 | chatparser | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 12 | C130 | Sift macOS (native) | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 13 | C131 | deja semantic MCP | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 14 | C132 | claude-vault | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 15 | C133 | momento | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 16 | C134 | turnlog | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 17 | C176 | ThreadShelf | NOT_TESTED | SOURCE_FOUND | Confrontar CTK na fidelidade de conversa e árvore |
| 18 | C139 | DSH Chat Import | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 19 | C180 | ContextVolt | NOT_TESTED | SOURCE_FOUND | Confrontar CTK e ThreadShelf |
| 20 | C194 | Cortex Desktop | NOT_TESTED | SOURCE_FOUND | Captura e recuperação cross-provider |
| 21 | C111 | MyChatArchive | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 22 | C108 | Ricoeur upstream | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 23 | C121 | Gora | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 24 | C129 | conversation-search MCP | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 25 | C101 | Reweave | FAIL | LEGACY | Confronto do contrato existente |
| 26 | C112 | Chat Chronicle | FAIL | LEGACY | Confronto do contrato existente |
| 27 | C177 | Personal AI Memory | NOT_TESTED | SOURCE_FOUND | Captura/código de importação browser, riscos privacidade |

### Repair, deduplicação e reconstrução (5)

| Pos. | ID | Produto | Status funcional | Status da origem | Próximo gate |
|---:|---|---|---|---|---|
| 1 | C143 | Codex Sessions Manager | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 2 | C097 | Splink | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 3 | C098 | dedupe | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 4 | C127 | Sift CLI (Go) | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 5 | C117 | IronBridge | NOT_TESTED | LEGACY | Confronto do contrato existente |

### Busca textual embutida no núcleo (19)

| Pos. | ID | Produto | Status funcional | Status da origem | Próximo gate |
|---:|---|---|---|---|---|
| 1 | C001 | SQLite FTS5 | PASS | LEGACY | Confronto do contrato existente |
| 2 | C003 | Tantivy / tantivy-py | PASS | LEGACY | Confronto do contrato existente |
| 3 | C004 | BM25S | PASS | LEGACY | Confronto do contrato existente |
| 4 | C005 | rank-bm25 | PASS | LEGACY | Confronto do contrato existente |
| 5 | C002 | SQLite FTS5 trigram | PASS | LEGACY | Confronto do contrato existente |
| 6 | C008 | DuckDB FTS | PASS | LEGACY | Confronto do contrato existente |
| 7 | C206 | Infino | NOT_TESTED | SOURCE_FOUND | Confrontar LanceDB/FTS5 em corpus idêntico, indexação incremental, snapshots, S3/local e licença |
| 8 | C103 | XERJ | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 9 | C013 | Sonic | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 10 | C163 | Bleve | NOT_TESTED | SOURCE_FOUND | Contra Tantivy e FTS5, incluindo portabilidade Go |
| 11 | C164 | Searchlite | NOT_TESTED | SOURCE_FOUND | Contra FTS5/Tantivy no mesmo corpus |
| 12 | C166 | Infinity | NOT_TESTED | SOURCE_FOUND | Contra LanceDB em busca híbrida real |
| 13 | C165 | Tinysearch | NOT_TESTED | SOURCE_FOUND | Pesquisar offline em cliente sem memória |
| 14 | C102 | Summa 2 / SpaceFrontiers | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 15 | C006 | Whoosh | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 16 | C007 | Xapian | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 17 | C012 | Lucene | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 18 | C109 | Summa original (archived) | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 19 | C110 | Bichon email archive | NOT_TESTED | LEGACY | Confronto do contrato existente |

### Busca JS local para clientes e Edge (4)

| Pos. | ID | Produto | Status funcional | Status da origem | Próximo gate |
|---:|---|---|---|---|---|
| 1 | C011 | FlexSearch | PASS | LEGACY | Confronto do contrato existente |
| 2 | C010 | MiniSearch | PASS | LEGACY | Confronto do contrato existente |
| 3 | C009 | Orama | PASS | LEGACY | Confronto do contrato existente |
| 4 | C175 | Moss | NOT_TESTED | SOURCE_FOUND | Motor leve browser; testar condição de cloud/cache |

### Índices vetoriais opcionais (21)

| Pos. | ID | Produto | Status funcional | Status da origem | Próximo gate |
|---:|---|---|---|---|---|
| 1 | C028 | sqlite-vec | PASS | LEGACY | Confronto do contrato existente |
| 2 | C035 | LanceDB | PASS | LEGACY | Confronto do contrato existente |
| 3 | C031 | USearch | PASS | LEGACY | Confronto do contrato existente |
| 4 | C032 | hnswlib | PASS | LEGACY | Confronto do contrato existente |
| 5 | C034 | Annoy | PASS | LEGACY | Confronto do contrato existente |
| 6 | C172 | turbovec | NOT_TESTED | SOURCE_FOUND | Confrontar sqlite-vec em RAM/recall/ARM |
| 7 | C033 | FAISS | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 8 | C037 | Chroma | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 9 | C039 | Qdrant | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 10 | C040 | Milvus | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 11 | C173 | turbovecdb | NOT_TESTED | SOURCE_FOUND | Composição existente próxima da arquitetura alvo |
| 12 | C199 | Deep Lake | NOT_TESTED | SOURCE_FOUND | Referência de datasets sem migrar núcleo |
| 13 | C036 | DuckDB VSS | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 14 | C038 | pgvector | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 15 | C041 | Weaviate | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 16 | C042 | Redis vector search | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 17 | C029 | SQLite vec1 | UNAVAILABLE_ON_STOCK_RUNNER | LEGACY | Confronto do contrato existente |
| 18 | C030 | SQLite-Vector PyPI | BLOCKED | LEGACY | Confronto do contrato existente |
| 19 | C043 | Vald | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 20 | C044 | Vearch | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 21 | C168 | VectorChord | NOT_TESTED | SOURCE_FOUND | Alternativa a pgvector e sqlite-vec |

### Busca semântica, fuzzy e reranking (13)

| Pos. | ID | Produto | Status funcional | Status da origem | Próximo gate |
|---:|---|---|---|---|---|
| 1 | C057 | RapidFuzz | PASS | LEGACY | Confronto do contrato existente |
| 2 | C045 | Sentence Transformers | PASS | LEGACY | Confronto do contrato existente |
| 3 | C052 | CrossEncoder | PASS | LEGACY | Confronto do contrato existente |
| 4 | C046 | FastEmbed | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 5 | C053 | FlashRank | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 6 | C049 | PyLate | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 7 | C050 | ColBERT | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 8 | C054 | llama.cpp embeddings | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 9 | C055 | GLiNER | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 10 | C056 | spaCy | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 11 | C047 | BGE-M3 | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 12 | C048 | multilingual E5 | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 13 | C051 | SPLADE | NOT_TESTED | LEGACY | Confronto do contrato existente |

### Tópicos, relações e grafos auditáveis (22)

| Pos. | ID | Produto | Status funcional | Status da origem | Próximo gate |
|---:|---|---|---|---|---|
| 1 | C065 | RDFLib | PASS | LEGACY | Confronto do contrato existente |
| 2 | C059 | BERTopic | PASS | LEGACY | Confronto do contrato existente |
| 3 | C058 | NetworkX | PASS | LEGACY | Confronto do contrato existente |
| 4 | C144 | LadybugDB | NOT_TESTED | SOURCE_FOUND | Confrontar Kùzu arquivado e RDFLib com consultas por relação |
| 5 | C145 | HelixDB | NOT_TESTED | SOURCE_FOUND | Grafo+lexical+vetor sem triplicar o banco |
| 6 | C138 | Semantica | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 7 | C060 | KeyBERT | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 8 | C061 | Top2Vec | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 9 | C066 | ArcadeDB | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 10 | C062 | HDBSCAN | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 11 | C068 | Apache AGE | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 12 | C151 | Oxigraph | NOT_TESTED | SOURCE_FOUND | Proveniência relacional com IDs canônicos |
| 13 | C152 | CozoDB | NOT_TESTED | SOURCE_FOUND | Consulta multi-hop determinística; risco de manutenção |
| 14 | C197 | DataScript | NOT_TESTED | SOURCE_FOUND | Consulta explicável com local-only JS |
| 15 | C204 | Apache Jena | NOT_TESTED | SOURCE_FOUND | Alternativa Java RDFLib/Oxigraph |
| 16 | C069 | FalkorDB | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 17 | C070 | Memgraph | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 18 | C063 | Leidenalg | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 19 | C064 | igraph | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 20 | C067 | Neo4j Community | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 21 | C071 | Kùzu | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 22 | C150 | SurrealDB | NOT_TESTED | SOURCE_FOUND | Um banco vs core SQLite, custo de instalação |

### Memória, decisões e validade temporal (39)

| Pos. | ID | Produto | Status funcional | Status da origem | Próximo gate |
|---:|---|---|---|---|---|
| 1 | C114 | OpenSelf | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 2 | C072 | Graphiti | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 3 | C142 | Cortex App | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 4 | C141 | MARM Memory | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 5 | C073 | Cognee | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 6 | C074 | Mem0 | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 7 | C137 | MCP Memory Service | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 8 | C075 | HippoRAG 2 | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 9 | C076 | LightRAG | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 10 | C077 | Microsoft GraphRAG | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 11 | C078 | Letta | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 12 | C083 | AnythingLLM | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 13 | C086 | Haystack | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 14 | C087 | LlamaIndex | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 15 | C088 | txtai | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 16 | C089 | Matrix Seshat | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 17 | C106 | reactor semantic | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 18 | C107 | Soma offline | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 19 | C140 | LeanCTX | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 20 | C178 | Hearth | NOT_TESTED | SOURCE_FOUND | Nova abordagem de relação atravessando sessões |
| 21 | C179 | Lossless Memory | NOT_TESTED | SOURCE_FOUND | Comparar recall por tempo+tema com FTS5 |
| 22 | C183 | Mnemos | NOT_TESTED | SOURCE_FOUND | Tipologia de contradição com abstenção humana |
| 23 | C182 | Fieldnotes | NOT_TESTED | SOURCE_FOUND | Separar evidência de inferência com revisão |
| 24 | C185 | Engram | NOT_TESTED | SOURCE_FOUND | Transações humano-first em memória |
| 25 | C186 | DSH Living Memory | NOT_TESTED | SOURCE_FOUND | Buscar sinal temporal sem apagar origem |
| 26 | C190 | Atomic | NOT_TESTED | SOURCE_FOUND | Confrontar descoberta temática e jornada UX sem mexer na UX |
| 27 | C181 | LifeContext | NOT_TESTED | SOURCE_FOUND | Abordagem pequena e adaptável, ainda imatura |
| 28 | C187 | MemPalace | NOT_TESTED | SOURCE_FOUND | Avaliar maturidade e falsa inferência |
| 29 | C188 | Graph Memory | NOT_TESTED | SOURCE_FOUND | Auditoria/segurança sem servidor obrigatório |
| 30 | C189 | Open Brain | NOT_TESTED | SOURCE_FOUND | Referência de decisão por recência e frequência |
| 31 | C080 | Open WebUI | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 32 | C081 | Onyx CE | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 33 | C136 | Basic Memory | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 34 | C082 | Khoj | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 35 | C084 | Reor | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 36 | C085 | Microsoft semantic-kernel | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 37 | C105 | Synorive | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 38 | C184 | Memoirs | NOT_TESTED | SOURCE_FOUND | Testar portas isoladas sem curador LLM |
| 39 | C193 | MemU | NOT_TESTED | SOURCE_FOUND | Indexação por estrutura em vez de chunks |

### Métricas, datasets e controle de qualidade (9)

| Pos. | ID | Produto | Status funcional | Status da origem | Próximo gate |
|---:|---|---|---|---|---|
| 1 | C090 | ir-measures | PASS | LEGACY | Confronto do contrato existente |
| 2 | C091 | ranx | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 3 | C095 | Label Studio | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 4 | C096 | Argilla | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 5 | C094 | RAGAS | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 6 | C092 | BEIR | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 7 | C093 | MTEB | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 8 | C099 | Apache Tika | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 9 | C100 | Docling | NOT_TESTED | LEGACY | Confronto do contrato existente |

### Servidores e adapters remotos de busca (16)

| Pos. | ID | Produto | Status funcional | Status da origem | Próximo gate |
|---:|---|---|---|---|---|
| 1 | C016 | OpenSearch | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 2 | C019 | Quickwit | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 3 | C020 | Vespa | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 4 | C017 | Apache Solr | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 5 | C167 | Marqo | NOT_TESTED | SOURCE_FOUND | Buscar multimodal sem acoplar serviço |
| 6 | C174 | Kosha | NOT_TESTED | SOURCE_FOUND | Referência serviço startup; implantação local complexa |
| 7 | C104 | OramaCore | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 8 | C014 | Meilisearch CE | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 9 | C022 | PostgreSQL FTS | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 10 | C023 | pg_trgm | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 11 | C024 | ZincSearch | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 12 | C025 | Elasticsearch | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 13 | C015 | Typesense | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 14 | C018 | Manticore Search | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 15 | C021 | ParadeDB | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 16 | C205 | Turbopuffer | NOT_TESTED | EXTERNAL_REFERENCE | Comparar custos e arquitetura, não embutível |

### Referências comerciais e tecnológicas (6)

| Pos. | ID | Produto | Status funcional | Status da origem | Próximo gate |
|---:|---|---|---|---|---|
| 1 | C079 | Zep | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 2 | C124 | Chat Locker | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 3 | C125 | Recalium | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 4 | C207 | Memorial standard | NOT_TESTED | EXTERNAL_REFERENCE | Encontrar licença/API e evitar dependência SaaS |
| 5 | C026 | Azure AI Search | NOT_TESTED | LEGACY | Confronto do contrato existente |
| 6 | C027 | Algolia | NOT_TESTED | LEGACY | Confronto do contrato existente |

### Armazenamento histórico e imutável (bitemporal/branches) (8)

| Pos. | ID | Produto | Status funcional | Status da origem | Próximo gate |
|---:|---|---|---|---|---|
| 1 | C146 | SirixDB | NOT_TESTED | SOURCE_FOUND | Comparar edição e recuperação as-of sem sobrescrever mensagens |
| 2 | C147 | TerminusDB | NOT_TESTED | SOURCE_FOUND | Contratos de revisão auditável e ramificações |
| 3 | C148 | Dolt | NOT_TESTED | SOURCE_FOUND | Provar benefício diante de SQLite+audit ledger |
| 4 | C162 | XTDB | NOT_TESTED | SOURCE_FOUND | Confrontar SirixDB e SQLite event log |
| 5 | C198 | Datahike | NOT_TESTED | SOURCE_FOUND | Consultas as-of e validade com dados pequenos |
| 6 | C149 | FlureeDB | NOT_TESTED | SOURCE_FOUND | Prova de integridade de decisões e relações com fonte |
| 7 | C161 | immudb | NOT_TESTED | SOURCE_FOUND | Auditoria verificável sem substituir busca |
| 8 | C195 | KurrentDB | NOT_TESTED | SOURCE_FOUND | Referência de reparo por replay vs snapshot |

### Motor transacional embutido e mecanismos KV (8)

| Pos. | ID | Produto | Status funcional | Status da origem | Próximo gate |
|---:|---|---|---|---|---|
| 1 | C153 | Turso Database | NOT_TESTED | SOURCE_FOUND | Compatibilidade FTS5 e arquivo existente antes de migrar |
| 2 | C169 | ObjectBox Python | NOT_TESTED | SOURCE_FOUND | Confrontar Android/ARM e armazenamento |
| 3 | C154 | libSQL | NOT_TESTED | SOURCE_FOUND | Persistência local e sincronização opcional |
| 4 | C171 | TidesDB | NOT_TESTED | SOURCE_FOUND | Requer implementar indexador sobre KV; custo elevado |
| 5 | C201 | redb | NOT_TESTED | SOURCE_FOUND | Alternativa de baixo nível ao SQLite |
| 6 | C202 | SlateDB | NOT_TESTED | SOURCE_FOUND | Retenção de arquivos sem cluster |
| 7 | C203 | Fjall | NOT_TESTED | SOURCE_FOUND | Maior trabalho para indexar comparado a FTS5 |
| 8 | C200 | RocksDB | NOT_TESTED | SOURCE_FOUND | Alto custo de implementar índice próprio |

### Persistência local, navegador e sincronização (8)

| Pos. | ID | Produto | Status funcional | Status da origem | Próximo gate |
|---:|---|---|---|---|---|
| 1 | C155 | PGlite | PASS | SOURCE_FOUND | Confrontar SQLite WASM para browser/tablet |
| 2 | C157 | RxDB | NOT_TESTED | SOURCE_FOUND | Reusar portas de persistência browser |
| 3 | C158 | Dexie | NOT_TESTED | SOURCE_FOUND | Suporte de índice e uso offline da UX |
| 4 | C159 | Evolu | NOT_TESTED | SOURCE_FOUND | Conflitos entre dispositivos e integridade |
| 5 | C160 | cr-sqlite | NOT_TESTED | SOURCE_FOUND | Histórico original imutável vs merge de metadados |
| 6 | C170 | PowerSync JS | NOT_TESTED | SOURCE_FOUND | UX do par com sincronização opt-in |
| 7 | C156 | ElectricSQL | NOT_TESTED | SOURCE_FOUND | Sincronizar vistas sem misturar autoria ou origem |
| 8 | C196 | PouchDB | NOT_TESTED | SOURCE_FOUND | Tradeoff de CRDT e divergência |

### Contratos e formatos portáteis entre fornecedores (2)

| Pos. | ID | Produto | Status funcional | Status da origem | Próximo gate |
|---:|---|---|---|---|---|
| 1 | C191 | Portable Memory (MacPaw) | PASS | SOURCE_FOUND | Contratos de entrada/exportação e origem |
| 2 | C192 | PAM Portable AI Memory | NOT_TESTED | SOURCE_FOUND | Validar schemas e roundtrip de branches |

## Confrontos novos, em ordem

| Ordem | Referência | Candidatos | Critério |
|---:|---|---|---|
| 1 | C118 CTK | Portable Memory (MacPaw), PAM Portable AI Memory | Lossless branch+source hashes, 2 conversations 5 messages and schema roundtrip |
| 2 | C118 CTK | ThreadShelf, Personal AI Memory | Multiple providers, branches, browser capture, exact export roundtrip |
| 3 | C001 SQLite FTS5 | SirixDB, TerminusDB, FlureeDB | Bitemporal revisions, immutable messages, rollback, source IDs, disk budget |
| 4 | C065 RDFLib | HelixDB, LadybugDB, Oxigraph | Typed evidence links + graph traversal, embeddings, mutation safety |
| 5 | C001 SQLite FTS5 | Searchlite, Bleve, Moss, Infinity, Infino | Identical corpus, PT/EN queries, p95/memory/disk, update/delete, no cloud |
| 6 | C028 sqlite-vec | turbovec, turbovecdb, ObjectBox Python | Exact recall, 2M scale, ARM, persistence, 2/4-bit tradeoffs |
| 7 | C114 OpenSelf (untested) | Mnemos, Memoirs, Hearth, Lossless Memory | Conflict state, time-first, human approval, provenance, no mandatory model |
| 8 | C011 FlexSearch | PGlite, RxDB, Dexie, Evolu, cr-sqlite | Persisted browser search + sync without silently merging chat source branches |
| 9 | R10 data contracts | immudb, Dolt, KurrentDB, XTDB | Append-only evidence and tamper verification without losing source data |

## Garantias
A lista anterior de 143 continua preservada e auditável; toda adição tem ID independente.
Nenhum resultado novo foi classificado como PASS sem execução funcional real.
A equipe UX paralela deve consumir contratos e não depender da implementação de qualquer candidato.
