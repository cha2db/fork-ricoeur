# Cha2db — Fronteira de pesquisa R16

Gerado (UTC): 2026-11-11T03:25:30.941804+00:00

**235 candidatos únicos** — 143 baseline previamente triados e 92 novas opções ainda sem testes funcionais.

**Apenas prioridade de testes, não ranking de qualidade e NÃO homologação.** O ranking R13 dos 143 permanece separado.

## Ranking de confronto da fronteira

| Ordem | ID | Produto | Prioridade | Forma de armazenamento | Mecanismo de consulta |
| ---: | --- | --- | --- | --- | --- |
| 1 | C206 | [Infino](https://github.com/infino-ai/infino) | P0 | append_only_Parquet_BM25_vector_embedded | BM25 + vetor/RRF em arquivos Parquet com snapshot imutável e SQL; sem servidor |
| 2 | C146 | [SirixDB](https://github.com/sirixdb/sirix) | P0 | append_only_bitemporal_tree | Revisão imutável + consulta bitemporal + diff |
| 3 | C147 | [TerminusDB](https://github.com/terminusdb/terminusdb) | P0 | versioned_document_graph | Branch/merge/diff + JSON-LD + grafo |
| 4 | C216 | [sqlite-graph](https://github.com/shwetarkadam/sqlite-graph) | P0 | SQLite único com edges e vetores BLOB | Recursive CTE + FTS5 + vetor+RRF |
| 5 | C144 | [LadybugDB](https://github.com/LadybugDB/ladybug) | P0 | embedded_graph_columnar | Cypher + FTS + vetor + WASM |
| 6 | C145 | [HelixDB](https://github.com/helixdb/helix-db) | P0 | transactional_graph_object_store | Grafo + BM25 + vetor pré-filtrado |
| 7 | C149 | [FlureeDB](https://github.com/fluree/db) | P0 | immutable_RDF_graph | Commit imutável + origem por relação + política |
| 8 | C217 | [Threadline](https://github.com/terra901/Threadline) | P0 | IndexedDB + chrome.storage.local; embeddings locais | Busca semântica no navegador com árvore de ramos |
| 9 | C218 | [Personal AI Memory](https://github.com/marswangyang/personal-ai-memory) | P0 | IndexedDB/ONNX no navegador | BM25 + vetores + time decay + RRF |
| 10 | C220 | [Kalan DB](https://github.com/Abhinivesh2729/kalan-db) | P0 | Um arquivo .vdb memory-mapped local | HNSW+BM25+RRF, ONNX no Android |
| 11 | C228 | [Aura Memory](https://github.com/teolex2020/aura-memory) | P0 | Rust offline memory store | Bounded recall + source-backed correction |
| 12 | C229 | [Agentic Data Kernel](https://github.com/Jason-Doyle/agentic-data-kernel) | P0 | SQLite dev / PostgreSQL production event/effect state | Temporal and causal queries |
| 13 | C232 | [Agent Memory (Lab)](https://github.com/agent-memory-lab/agent-memory) | P0 | SQLite with optional PostgreSQL adapter | Evidence-aware temporal recall |
| 14 | C233 | [YantrikDB](https://github.com/yantrikos/yantrikdb) | P0 | Embedded SQLite inside Rust | HNSW hybrid memory + temporal decay |
| 15 | C234 | [Engraphis](https://github.com/Coding-Dev-Tools/engraphis) | P0 | SQLite local with temporal history | Bounded source-cited context retrieval |
| 16 | C155 | [PGlite](https://github.com/electric-sql/pglite) | P0 | PostgreSQL_WASM_IndexDB | Postgres+FTS em WASM/Node/IndexedDB |
| 17 | C172 | [turbovec](https://github.com/RyanCodrai/turbovec) | P0 | compressed_2bit_4bit_index | Busca diretamente em 2/4 bits ARM+x86 |
| 18 | C175 | [Moss](https://github.com/usemoss/moss) | P0 | runtime_WASM_index | Busca semântica/BM25 edge e browser |
| 19 | C176 | [ThreadShelf](https://github.com/ChrystianSchutz/ThreadShelf) | P0 | LanceDB_local_archive | Chat multi-provider + texto/semântico + CLI HTTP MCP |
| 20 | C177 | [Personal AI Memory](https://github.com/pairojvrh/ai-memory) | P0 | IndexedDB_ONNX_MiniSearch | Captura passiva + vetor decaimento + RRF |
| 21 | C178 | [Hearth](https://github.com/reallyreallyryan/hearth) | P0 | SQLite_FTS5_sqlite_vec | Linhas de investigação/tensões/revisão humana |
| 22 | C179 | [Lossless Memory](https://github.com/aru-labs/lossless-memory) | P0 | append_only_timeline | Busca temporal primeiro, nunca sumariza origem |
| 23 | C183 | [Mnemos](https://github.com/Sohamp2809/mnemos) | P0 | SQLite_typed_conflict_log | Supersede/replace/coexist no ingresso |
| 24 | C184 | [Memoirs](https://github.com/misaelzapata/memoirs) | P0 | SQLite_FTS5_sqlite_vec_bitemporal | Proveniência, time-travel, ACL e grafo PPR |
| 25 | C191 | [Portable Memory (MacPaw)](https://github.com/MacPaw/portable-memory) | P0 | JSONL_manifest_checksum | Memória portátil inter-app com tombstones e checksums |
| 26 | C192 | [PAM Portable AI Memory](https://github.com/portable-ai-memory/portable-ai-memory) | P0 | JSON_Schema_export | Padrão de conversas e memórias cross-provider |
| 27 | C163 | [Bleve](https://github.com/blevesearch/bleve) | P1 | Go_disk_index | FTS com analisadores PT e vetor |
| 28 | C227 | [INITE Brain](https://github.com/inite-ai/inite-brain-service) | P1 | Bitemporal knowledge graph | Hybrid semantic+graph REST/MCP |
| 29 | C230 | [taOSmd](https://github.com/jaylfc/taosmd) | P1 | Verbatim append-only source archive + derived graph | Hybrid retrieval + evidence verification |
| 30 | C231 | [Remnic](https://github.com/joshuaswarren/remnic) | P1 | Markdown files with structured memory metadata | Scoped context retrieval |
| 31 | C214 | [OpenLineage](https://github.com/OpenLineage/OpenLineage) | P1 | Eventos/metadata de jobs, runs e datasets | Busca de linhagem de pipeline |
| 32 | C209 | [LiveStore](https://github.com/livestorejs/livestore) | P1 | Event sourcing local-first + SQLite derivado | SQL reativo e replay de eventos |
| 33 | C208 | [DoltgreSQL](https://github.com/dolthub/doltgresql) | P1 | Banco PostgreSQL-compatível versionado | SQL+branch/merge |
| 34 | C213 | [Zoekt](https://github.com/sourcegraph/zoekt) | P1 | Índice invertido trigrama em disco | Regex, substring, filtros e ranking por código |
| 35 | C219 | [Threadback](https://threadback.dev/) | P1 | Browser local conforme fabricante | Busca lexical e semântica on-device |
| 36 | C148 | [Dolt](https://github.com/dolthub/dolt) | P1 | git_versioned_SQL_tables | Git de tabelas com merge/conflicts/rollback |
| 37 | C150 | [SurrealDB](https://github.com/surrealdb/surrealdb) | P1 | embedded_multimodel | Documento+grafo+BM25+vetor+WASM |
| 38 | C151 | [Oxigraph](https://github.com/oxigraph/oxigraph) | P1 | embedded_RDF_RocksDB | SPARQL com triplas persistentes |
| 39 | C153 | [Turso Database](https://github.com/tursodatabase/turso) | P1 | rust_SQLite_reimplementation | SQLite-like em Rust, concorrência e vetor |
| 40 | C157 | [RxDB](https://github.com/pubkey/rxdb) | P1 | pluggable_local_first_storage | Adapters IndexedDB OPFS SQLite e replicação |
| 41 | C158 | [Dexie](https://github.com/dexie/Dexie.js) | P1 | IndexedDB_wrapper | Schema+queries+persistência IndexedDB |
| 42 | C159 | [Evolu](https://github.com/evoluhq/evolu) | P1 | encrypted_SQLite_CRDT | Sincronização SQLite E2EE e CRDT |
| 43 | C160 | [cr-sqlite](https://github.com/vlcn-io/cr-sqlite) | P1 | SQLite_CRDT_extension | Merge offline multiwriter via CRDT |
| 44 | C161 | [immudb](https://github.com/codenotary/immudb) | P1 | Merkle_immutable_event_log | Histórico e prova criptográfica |
| 45 | C162 | [XTDB](https://github.com/xtdb/xtdb) | P1 | bitemporal_immutable_SQL | Transação e validade bitemporais |
| 46 | C164 | [Searchlite](https://github.com/davidkelley/searchlite) | P1 | Rust_WAL_BM25 | Motor pequeno BM25 + filtro e fuzzy |
| 47 | C166 | [Infinity](https://github.com/infiniflow/infinity) | P1 | embedded_CPP_hybrid | BM25+vetor denso/esparso+late interaction |
| 48 | C169 | [ObjectBox Python](https://github.com/objectbox/objectbox-python) | P1 | on_device_object_Vector | Objetos nativos com vetor HNSW |
| 49 | C170 | [PowerSync JS](https://github.com/powersync-ja/powersync-js) | P1 | sync_SQLite_mobile | SQLite offline sincronizado para web/Vue |
| 50 | C173 | [turbovecdb](https://github.com/kostadis/turbovecdb) | P1 | compressed_vector_SQLite_sidecar | turbovec + SQLite para documentos, filtros e exato |
| 51 | C180 | [ContextVolt](https://github.com/Rithvickkr/contextvolt) | P1 | local_hybrid_vault | Continuidade de chats entre providers com MCP |
| 52 | C182 | [Fieldnotes](https://github.com/mmlac/fieldnotes) | P1 | personal_knowledge_graph | MCP timeline e ligações cruzadas sugeridas |
| 53 | C185 | [Engram](https://github.com/HBarefoot/engram) | P1 | SQLite_semantic_graph | Import preview/commit, conflitos auditáveis |
| 54 | C186 | [DSH Living Memory](https://github.com/dearbld/dsh-living-memory) | P1 | SQLite_FTS5_graph | Decaimento, RRF multi-sinal, conflitos para revisão |
| 55 | C190 | [Atomic](https://github.com/kenforthewin/atomic) | P1 | SQLite_sqlite_vec_Tauri | Wiki citada + grafo + busca local |
| 56 | C193 | [MemU](https://github.com/drnrzs/memu) | P1 | hierarchical_file_memory | Resources→items→categories e recuperação dupla |
| 57 | C194 | [Cortex Desktop](https://github.com/shubhsaxena2020/cortex) | P1 | SQLite_FTS5_vec | Captura extensão+grafo+digest local |
| 58 | C221 | [ObjectBox C](https://github.com/objectbox/objectbox-c) | P1 | Armazenamento de objetos nativo | ANN e filtros por relação |
| 59 | C152 | [CozoDB](https://github.com/cozodb/cozo) | P2 | embedded_datalog_KV | Datalog+grafo+vetores, API <1.0 |
| 60 | C212 | [Pagefind](https://github.com/Pagefind/pagefind) | P2 | Artefatos de índice estático por chunks | Full-text local JS/WASM com filtros |
| 61 | C154 | [libSQL](https://github.com/tursodatabase/libsql) | P2 | fork_SQLite_replication | SQLite com réplicas e vetor |
| 62 | C156 | [ElectricSQL](https://github.com/electric-sql/electric) | P2 | sync_shapes_Postgres | Sincronização parcial e reativa |
| 63 | C165 | [Tinysearch](https://github.com/tinysearch/tinysearch) | P2 | WASM_static_index | Índice diminuto de termos+posting |
| 64 | C167 | [Marqo](https://github.com/marqo-ai/marqo) | P2 | service_tensor_search | Texto+imagem+tensor+Vespa |
| 65 | C168 | [VectorChord](https://github.com/supervc-stack/VectorChord) | P2 | PostgreSQL_vector_disk_index | IVF/RaBitQ disco, índice Postgres |
| 66 | C171 | [TidesDB](https://github.com/tidesdb/tidesdb) | P2 | MVCC_LSM_Btree | KV transacional com baixo write amplification |
| 67 | C174 | [Kosha](https://github.com/decover-tech/kosha) | P2 | S3_segments_NVMe_cache | BM25+HNSW com computação descartável |
| 68 | C181 | [LifeContext](https://github.com/MSIH/life-context) | P2 | SQLite_sqlite_vec | Memória local via REST/MCP |
| 69 | C187 | [MemPalace](https://github.com/kvn3toj/mempalace) | P2 | ChromaDB_SQLite | Contradição experimental com checagem factual |
| 70 | C188 | [Graph Memory](https://github.com/stevepridemore/graph-memory) | P2 | Neo4j_temporal_graph | Grafo temporal protegido OAuth e multi-device |
| 71 | C189 | [Open Brain](https://github.com/bluto447/open-brain) | P2 | Postgres_pgvector_graph | Pontuação de tempo e tipagem de memória |
| 72 | C195 | [KurrentDB](https://github.com/kurrent-io/KurrentDB) | P2 | append_only_event_stream | Event sourcing imutável com projeções |
| 73 | C196 | [PouchDB](https://github.com/pouchdb/pouchdb) | P2 | CouchDB_document_replication | Réplica offline de documentos JSON |
| 74 | C197 | [DataScript](https://github.com/tonsky/datascript) | P2 | in_memory_immutable_Datalog | Datalog/tuplas imutáveis ClojureScript |
| 75 | C198 | [Datahike](https://github.com/replikativ/datahike) | P2 | immutable_Datalog_persistent | Histórico de fatos por transação |
| 76 | C199 | [Deep Lake](https://github.com/activeloopai/deeplake) | P2 | tensor_columnar_object_store | Dataset multimodal, versionamento e vetor |
| 77 | C201 | [redb](https://github.com/cberner/redb) | P2 | ACID_Btree_Rust | KV ACID embutido arquivo único |
| 78 | C204 | [Apache Jena](https://github.com/apache/jena) | P2 | RDF_TDB2_SPQRL | Graficos RDF/Sparql com reasoning |
| 79 | C207 | [Memorial standard](https://www.widemem.ai/) | P2 | hosted_memory_SQLite_audit | Startup com conflict resolution e audit trail |
| 80 | C210 | [Automerge](https://github.com/automerge/automerge) | P2 | Documento JSON CRDT com histórico de alterações | Consulta por documento (sem FTS nativo) |
| 81 | C211 | [Yjs](https://github.com/yjs/yjs) | P2 | CRDT em documentos com persistência pluggable | Consulta por APIs Yjs, não é engine de busca |
| 82 | C222 | [TinyBase](https://github.com/tinyplex/tinybase) | P2 | Armazenamento reativo local-first com adaptadores | Queries e relacionamentos JS |
| 83 | C223 | [PowerSync](https://github.com/powersync-ja/powersync-service) | P2 | SQLite cliente, serviço de sync | Query SQL local sobre réplica |
| 84 | C226 | [Recall browser extension](https://chromewebstore.google.com/detail/recall/nidolkbndiellihjabcmmioiohjagepk) | P2 | IndexedDB/browser conforme listagem | Busca full-text/fuzzy, linha do tempo |
| 85 | C235 | [Bitemporal Postgres Engine](https://github.com/andreiu77/bitemporal-postgres-engine) | P2 | Append-only bitemporal relational tables | Bitemporal SQL as-of |
| 86 | C200 | [RocksDB](https://github.com/facebook/rocksdb) | P3 | LSM_KeyValue | Armazenamento KV robusto com write batches |
| 87 | C202 | [SlateDB](https://github.com/slatedb/slatedb) | P3 | object_storage_LSM | LSM sobre S3 para tier frio |
| 88 | C203 | [Fjall](https://github.com/fjall-rs/fjall) | P3 | Rust_LSM_KV | KV LSM embutível com transações |
| 89 | C205 | [Turbopuffer](https://turbopuffer.com/) | P3 | hosted_object_storage_search | Serviço gerenciado lexical+vetor em object storage |
| 90 | C215 | [Marquez](https://github.com/MarquezProject/marquez) | P3 | PostgreSQL com serviço de metadados | Grafo de proveniência de jobs/datasets |
| 91 | C224 | [GUN](https://github.com/amark/gun) | P3 | Grafo P2P e eventual consistency | Travessia por grafo |
| 92 | C225 | [lakeFS](https://github.com/treeverse/lakeFS) | P3 | Data lake versionado, snapshots por metadata | Consulta de histórico de objetos, não busca textual |

## Próximos confrontos definidos

| Ordem | Portabilidade / capacidade | Desafiante | Baseline | Gate |
| ---: | --- | --- | --- | --- |
| 1 | hybrid_parquet | Infino | C035 | Same 40k->2M messages, keyword+vector+SQL, chunk updates, file size, p95 and RAM |
| 2 | temporal_state | SirixDB | C001 | Branch/recovery as-of, time of observation vs validity, no loss of original message |
| 3 | temporal_state | XTDB | C001 | XTDB system-time vs valid-time revisions and Java runtime footprint |
| 4 | temporal_state | TerminusDB | C065 | TerminusDB branches, merges, typed relations with evidence and license |
| 5 | graph_sqlite | sqlite-graph | C065 | sqlite-graph recursive SQLite edges vs RDFLib on typed source-cited paths |
| 6 | graph_sqlite | LadybugDB | C065 | LadybugDB graph traversal/FTS/vector vs SQLite evidence-first prototype |
| 7 | graph_sqlite | HelixDB | C065 | HelixDB graph+hybrid versus same normalized 40k messages |
| 8 | graph_sqlite | CozoDB | C065 | CozoDB Datalog multi-hop joins and memory/platform maturity |
| 9 | browser_capture | Threadline | C118 | Threadline browser branches vs CTK exported ChatGPT trees |
| 10 | browser_capture | Personal AI Memory | C118 | Personal AI Memory capture+recency vs CTK lossless export |
| 11 | android_hybrid | Kalan DB | C028 | Kalan DB Android real ARM64 on synthetic 40k vs SQLite FTS5/sqlite-vec |
| 12 | temporal_retrieval | Threadback | C118 | Threadback browser semantic/keyword against CTK branches and provenance |
| 13 | lineage | OpenLineage | C118 | OpenLineage event model for source->adapter->normalization->index receipts |
| 14 | substring | Zoekt | C002 | Zoekt positional trigram vs FTS5 trigram: regex and partial terms |
| 15 | browser_static | Pagefind | C010 | Pagefind chunk index vs MiniSearch at 40k results and offline read-only |
| 16 | event_log | LiveStore | C001 | LiveStore event-log replay vs SQLite existing importer idempotence |
| 17 | versioned_sql | Dolt | C001 | Dolt SQL branch/merge/rollback vs SQLite snapshot and repair ledger |
| 18 | memory_governance | Aura Memory | C114 | Aura Memory offline deterministic correction, provenance and human approval |
| 19 | causal_lineage | Agentic Data Kernel | C118 | Agentic Data Kernel uncertain import result, idempotence and causal repair receipt |
| 20 | memory_governance | Agent Memory (Lab) | C072 | Agent Memory alpha source erasure leads to unknown; temporal and scoped evidence |
| 21 | memory_governance | YantrikDB | C065 | YantrikDB contradiction proposals require evidence and explicit human approval |
| 22 | memory_governance | Engraphis | C114 | Engraphis abstention on weak evidence, source scopes and temporal recall |
| 23 | memory_governance | INITE Brain | C072 | INITE Brain bitemporal conflict handling; AGPL compliance gate first |
| 24 | lossless_archive | taOSmd | C118 | taOSmd append-only verbatim source and unsupported-fact detection, AGPL gate |
| 25 | memory_governance | Remnic | C114 | Remnic corrections, portable markdown and human-edit reconciliation |
| 26 | temporal_sql | Bitemporal Postgres Engine | C162 | Experimental Postgres temporal tables against XTDB validity/observation models |

## Fronteiras de responsabilidade

A Fase 2 só avalia bibliotecas, contratos e dados. Fase 3/UX continua independente.
Nenhum dos candidatos adicionais foi instalado ou integrado no núcleo por esta varredura.
Saturação de mercado não comprovada: a pesquisa deve prosseguir até ciclos sem novas abordagens capazes de alterar uma porta.
