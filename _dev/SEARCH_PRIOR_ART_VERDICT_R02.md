# Cha2db — Prior Art search comparison (R02)

Tested in GitHub Actions with the **same persisted-for-the-job SQLite snapshot** built by `_dev/build_prior_base.py` from the existing deterministic `_dev/corpus.py` generator.

## Data identity (verifiable)
- 1,000 conversations; 40,000 messages, synthetic, not private user history.
- 1,000 representative messages ranked with the same candidate IDs by FTS5, Python BM25, TF-IDF word/character, RapidFuzz+FTS5 and RRF.
- Logical SHA-256: `f47d08ac38de1e2260b8ebe833803a32b10481fd8ee5dca667bd037fe9061eb6`.
- The 2M-message stress DB from a previous CI run was temporary and was **not available** as a persistent database.
- Snapshot itself is stored in GitHub Actions run artifacts, not committed as a large SQLite binary.

## Confirmed gates
- FTS5, RapidFuzz, rank-bm25, TF-IDF, RRF: PASS on controlled topical queries.
- Exact queries: all strategies P@10=1 in repetitive fixture. Typos: FTS5 P@10=.3333; candidate corrections and TF-IDF variants P@10=1 in three fixture queries. **Not a human relevance verdict.**
- NetworkX: 10/10 topic communities, adjusted Rand score 1.0, 198 candidate similarity edges; proves fixture grouping only.
- sqlite-vec 0.1.9: PASS; 1,000 TF-IDF/SVD32 vectors indexed, six nearest-neighbor checks against brute force; this does **not** validate neural semantic embeddings.
- Explicit relations: PASS on seven inserted test messages, 4/4 expected cross-provider links found, 0 false positives, evidence ID preserved and review status candidate. This does **not** discover implicit contradiction or supersession.

## Provisional adoption decisions
- **KEEP** SQLite FTS5 (previous scale tests approved up to 2M messages).
- **CANDIDATE** RapidFuzz for tolerant user-facing query correction (MIT), not replacement of FTS5.
- **CANDIDATE** TF-IDF/character n-grams and RRF for hybrid retrieval; no measured quality gain on simple exact queries.
- **CANDIDATE** sqlite-vec as optional VectorIndex adapter; installation/runtime/semantic value still to be assessed across targets.
- **CANDIDATE** NetworkX for evidence-based relation graphs; do not interpret similarity as `supersedes` or `contradicts`.
- **NOT YET APPROVED** neural embeddings, BERTopic, and CrossEncoder for general Cha2db use until external models, licensing, cost and human relevance are judged.

## Evidence
- [Auditable snapshot manifest](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/prior-art/base-latest.json)
- [Lexical/fuzzy/hybrid comparisons](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/prior-art/latest.json)
- [SQLite vector index](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/prior-art/vector-latest.json)
- [Cross-conversation explicit relation graph](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/prior-art/relations-latest.json)
- [Optional neural model experiment](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/semantic/latest.json)

## Limits / hypothesis to test
All topic labels and explicit links are synthetic or author-constructed. Scores cannot justify claims of real-world semantic quality. A blind human-annotated evaluation and cross-chat relation review are required before an acceptance verdict. Model weights may have separate licensing requirements. No UI or MCP integration was necessary for these algorithmic gates.
