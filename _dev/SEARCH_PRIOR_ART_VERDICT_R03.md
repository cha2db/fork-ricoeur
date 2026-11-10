# Cha2db — Prior Art search and topic linkage verdict (R03, 2026-11-10)

## Scope and repeatability
All experiments below executed in **GitHub Actions** using the existing `_dev/corpus.py` generator materialized as a 1,000-conversation/40,000-message SQLite snapshot. Candidate comparisons sampled 1,000 representative messages for lexical ranking and 100 for multilingual embeddings/topic clustering; all were synthetic, NOT actual user conversations or independently human-annotated data.

Shared base: `ci-output/prior-art/base-latest.json`, logical SHA-256 `f47d08ac38de1e2260b8ebe833803a32b10481fd8ee5dca667bd037fe9061eb6`. The previous 2-million-message stress DB was ephemeral and was not the input to these experiments.

## Verified results

| Technology | Gate and data | Result | Decision |
| --- | --- | --- | --- |
| SQLite FTS5/BM25 | 10 exact and 3 typo queries, P@10 | Exact 1.0; typo .3333 | **KEEP** core lexical |
| RapidFuzz+FTS5 | 10 exact + 3 typo queries | Exact 1.0; typo 1.0 | **CANDIDATE** query correction |
| rank-bm25 | Same queries, same IDs | Exact 1.0; typo 1.0 | No demonstrated advantage over FTS5 |
| TF-IDF word/char | Same queries, same IDs | Exact 1.0; typo 1.0 | **CANDIDATE** cheap alternatives |
| RRF | Fusion of FTS5 + TF-IDF | Exact 1.0; typo 1.0 | No lift on simple fixture; retain as fusion baseline |
| NetworkX communities | 100 messages from same base | 10 clusters, ARI 1.0, 198 similarity edges | **CANDIDATE** grouping, not relation proof |
| sqlite-vec 0.1.9 | 1,000 SVD32 vectors, 6 brute-force KNN checks | PASS; six checks within expected nearest neighbor cutoff | **CANDIDATE** optional index; no neural embedding value claim |
| Explicit reference relation graph | 7 constructed messages over copied existing base | 4/4 expected relations, zero false positives; review pending | **CANDIDATE** evidence-first linkage |
| Multilingual MiniLM embeddings | 10 paraphrase queries over 100 representative messages | MRR@10 **.611**; TF-IDF baseline **.700** | **NOT ADOPTED** on present evidence |
| BERTopic 0.17.4 | 100 representative messages | 10 clusters, ARI 1.0, 0 outliers | **CANDIDATE**; repeated fixture too easy |
| Multilingual CrossEncoder | 4 reranking cases | Improved one poor case, unchanged two, reduced P@10 in one | **NOT ADOPTED** on present evidence |

Model details: Sentence Transformers 5.7.0 with `paraphrase-multilingual-MiniLM-L12-v2`; CrossEncoder `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`. Neural models are **optional**, CPU tests only. Model-specific licenses, artifact size, memory, reproducibility and deployment portability remain unapproved.

## Measured example: semantic model is not uniformly better
Paraphrase “preciso acessar um computador remoto de forma protegida”: embeddings found Redes in top 10 (P@10 1.0), TF-IDF missed (0.0). However, in the overall 10 paraphrase queries, TF-IDF mean MRR was .700 versus .611 for multilingual embeddings. This does not prove either model is globally better: labels reflect 10 synthetic topics and a 100-message sample. Both fail some hard cases. Reranking may help individual misses but cannot recover a relevant item not retrieved into its candidate set.

## Hypothesis: what could be Cha2db-specific
Do not implement another FTS/BM25/vector/clustering engine. The plausible differentiated feature is **evidence-based topic continuity across multiple conversations**: stable message IDs, topic/decision links, dated provenance, contradictions and supersession as unverified candidates, independent human approval, audit log and repair of conversation history. Similarity/graph communities alone must never assert `supersedes` or `contradicts`.

## Evidence links
- [Identical SQLite base manifest](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/prior-art/base-latest.json)
- [Lexical/fuzzy/RRF + NetworkX ranking metrics](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/prior-art/latest.json)
- [sqlite-vec KNN experiments](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/prior-art/vector-latest.json)
- [Explicit cross-chat relation test](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/prior-art/relations-latest.json)
- [Multilingual embeddings + BERTopic + CrossEncoder](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/semantic/latest.json)

## Verdict status
**Experiment suite: PASS for technical execution.** **Semantic quality / real-life inter-topic relation classification: NOT APPROVED.** Higher-confidence selection requires independently human-labeled PT/EN chat fragments, difficult negative examples, source/chronology consistency and measured deployment cost. Libraries remain separate candidate adapters; no new runtime dependency was added to the Cha2db core.
