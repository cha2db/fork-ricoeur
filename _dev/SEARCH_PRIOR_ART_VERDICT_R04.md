# Cha2db — Prior Art extension verdict R04 (2026-11-10)

All tested in GitHub Actions with the same deterministic, materialized, synthetic SQLite corpus of **1,000 conversations / 40,000 messages**. Base manifest: [SHA-256 and counts](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/prior-art/base-latest.json).

## Added extension gates

| Candidate | Executed finding | Decision |
| --- | --- | --- |
| FTS5 trigram | PASS: all 10 substring query counts and first 100 IDs equal to SQLite LIKE; index build ~2 s; database grew ~42.5 MiB on the 40k snapshot | **OPTIONAL CANDIDATE**, not the default; poor space tradeoff for short/easy queries |
| FTS5 trigram rare term | `agulha-mcp-2026`: ~1.02 ms vs plain LIKE ~16.3 ms. Nonexistent `zzyyxxnotfound`: ~0.08 ms vs ~8.5 ms. Common terms sometimes slower than LIKE | Adopt only if substring workloads and storage budget warrant it |
| sqlite-vec 0.1.9 | PASS: 1,000 SVD32 vectors, six KNN checks against brute force | **CANDIDATE** vector adapter |
| SQLite-Vector PyPI 0.0.1a6 | BLOCKED by API mismatch. Extension loads, but functions exposed are legacy `vector0`, `vector_from_json`, etc.; expected documented `vector_init`, `vector_full_scan` not exported by available PyPI wheel | **DO NOT ADOPT** this packaged version |
| SQLite official vec1 | UNAVAILABLE on stock GitHub runner (`no such module: vec1`). Official documentation requires separately compiling C extension. No vector search test was run | **NOT YET TESTED**, external build/deployment cost |
| Sentence Transformers multilingual | PASS execution; mean paraphrase MRR@10 .611 vs TF-IDF .700 on 100-message synthetic sample | **NOT ADOPTED** on current quality evidence |
| BERTopic | PASS execution; ten known fixture topics, ARI 1 | **CANDIDATE**, simplistic corpus |
| CrossEncoder | PASS execution; helped one hard query, not a consistent improvement across four queries | **NOT ADOPTED** on current evidence |
| NetworkX | PASS graph grouping, ARI 1 with known fixture labels; explicit anchored cross-chat links PASS 4/4 with zero false positives | **CANDIDATE** for human-reviewed evidence graphs |

## Baselines retained
FTS5/BM25 lexical is maintained and approved by prior scale gates to 2 million messages. RapidFuzz typo correction is a promising optional adapter. Python `rank-bm25` duplicates the existing algorithm without demonstrated superiority. TF-IDF and RRF remain interchangeable candidates behind contracts; no new mandatory dependency.

## Decision boundary
Technical PASS on repetitive synthetic data is not a human semantic-quality verdict. Retrieval similarity, community structure and a reranker cannot assert `follows_up`, `supersedes` or `contradicts` without evidence. The genuinely unproven Cha2db-specific hypothesis is provenance-preserving continuity of decisions/topics across chats, with human approval and revision history.

## Reports
- [Trigram experiment](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/prior-art/trigram-latest.json)
- [SQLite-Vector API incompatibility and log tails](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/prior-art/sqlite-vector-latest.json)
- [SQLite vec1 stock-runner probe](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/prior-art/vec1-probe-latest.json)
- [Multilingual model evaluation](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/semantic/latest.json)
- [FTS5/RapidFuzz/BM25/TF-IDF/RRF/NetworkX](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/prior-art/latest.json)
- [Evidence-linked relation graph](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/prior-art/relations-latest.json)

## Runtime scope
All experiments use reproducible CI runs and independent adapters. GUI and MCP have not been invoked in these algorithmic comparisons. Python, native extensions, external model weights and licenses require target-specific checks prior to installing them in the Cha2db production core.
