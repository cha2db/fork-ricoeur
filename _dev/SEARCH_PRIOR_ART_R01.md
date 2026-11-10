# Cha2db — Prior art e portas de recuperação/ligação entre assuntos (R01, 2026-11-10)

## Princípio
Adotar primeiro, comparar com corpus anotado, implementar somente lacunas demonstradas. Um algoritmo encontrar texto semelhante NÃO comprova que duas conversas tratam do mesmo assunto, nem que uma decisão substitui outra. Preservar sempre message_id, conv_id, plataforma, timestamp, versão e evidência textual.

## Matriz de candidatos (não homologados neste estudo)

| Capacidade | Prior art / licença indicativa | Contrato de porta | Gate de adoção |
| --- | --- | --- | --- |
| Busca lexical | SQLite FTS5 (integrado; domínio público SQLite) | LexicalSearch | Recall@k, nDCG@10, p95, custo e índice |
| Substrings | FTS5 trigram / LIKE (SQLite) | SubstringSearch | unicode, fragmentos, memória, p95 |
| Erros ortográficos | RapidFuzz (MIT) | CandidateCorrection | recall com erros, falsos positivos, overhead |
| Embeddings | Sentence Transformers (Apache-2.0 código; conferir licença de cada modelo) | EmbeddingProvider | PT/EN, recall, CPU/RAM, offline, privacidade |
| Vetores locais | sqlite-vec (MIT/Apache-2.0; pré-v1), SQLite vec1, SQLite-Vector (Apache-2.0) | VectorIndex | recall@k contra busca exata, ingestão, update, Android, RAM |
| Fusão | RRF conforme OpenSearch (algoritmo conhecido) | RankFusion | nDCG@10 e MRR versus BM25/vetorial |
| Reordenação | CrossEncoder do Sentence Transformers (licença do modelo separada) | Reranker | ganho nDCG@10, p95, RAM |
| Assuntos | BERTopic (MIT; dependências e modelos verificados individualmente) | TopicClusterer | estabilidade, purity, coerência, incremental |
| Comunidades | NetworkX Louvain/Leiden (BSD-3-Clause) | TopicGraph | modularidade, precisão das arestas, escala |

Links: https://sqlite.org/fts5.html ; https://github.com/rapidfuzz/RapidFuzz ; https://www.sbert.net/docs/sentence_transformer/usage/usage.html ; https://github.com/asg017/sqlite-vec ; https://sqlite.org/vec1.html ; https://github.com/sqliteai/sqlite-vector ; https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/rrf/ ; https://bertopic.readthedocs.io/en/latest/ ; https://networkx.org/documentation/stable/reference/algorithms/community.html

## Contratos independentes
- QueryRequest: query, mode, filters, limit, corpus_snapshot, version.
- RetrievalHit: message_id, conv_id, rank, score, source_adapter, evidence_span.
- TopicAssignment: topic_id, message_id, confidence, algorithm_version, evidence.
- TopicLink: source_topic_id, target_topic_id, relation_type, evidence_message_ids, confidence, reviewer_status.
- Relation types (não inferir sem prova): same_topic, related_topic, follows_up, refines, contradicts, supersedes, references.
- Human review first: links sugeridos ficam como candidates até confirmação; adapters LLM opcionais, nunca obrigatórios.
- Persistência e protocolo: portas independentes de SQLite, FastAPI, MCP e GUI.

## Benchmark e controle de qualidade
1. Conjunto gold com consultas PT/EN, sinônimos, paráfrases, termos raros, negações, ambiguidades, conversas intercaladas e decisões contraditórias; anotação humana por mensagem e por par de tópicos.
2. Separar split de desenvolvimento e avaliação, registrar seed, modelo, versão, hardware, dataset, tempo de indexação, p50/p95, memória e recall/nDCG/MRR.
3. Não aceitar benchmark sintético repetitivo como evidência de relevância semântica. Testes de carga existentes só aprovam corretude/escala lexical.
4. Benchmark de links: precision/recall/F1 por relation_type, taxa de falsos 'supersedes' e consistência temporal. Abstenção explícita quando não há evidência.
5. Gate de adoção: candidato deve superar baseline em qualidade sem violar limite de custo, privacidade, instalação ou licença. Empate favorece biblioteca adotável e menor código próprio.
6. Candidatos podem ser aprovados por componente e congelados; evitar repetir benchmarks sem alteração material de versão, corpus ou contrato.

## O que possivelmente sobra ao Cha2db
Não um novo algoritmo de BM25, embeddings ou clustering. A hipótese de diferenciação a validar é a composição rastreável de fragmentos de chats em uma linha de evolução de assunto: decisões, correções, contradições, substituições, fontes, recuperação e reconstrução entre plataformas. Atribuir autoria/proveniência sem inventar relações; apresentar confiança e evidência; permitir revisão humana e histórico de versões.

## Status
Pesquisa inicial de prior art; **não** é veredito de desempenho ou homologação de nenhum candidato semântico. Próximo gate técnico: criar corpus gold com anotação humana e harness de métricas, depois testar candidatos em isolamento e por adapter.
