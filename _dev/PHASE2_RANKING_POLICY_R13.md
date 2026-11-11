# Cha2db — Fase 2 · ranking mantido e plano de confrontos R13

Data de criação: 10/11/2026 (horário de São Paulo). Esta é uma **regra de decisão por contratos e evidências**, não uma declaração de superioridade universal.

**Ranking gerado automaticamente:**
- [Leitura rápida](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/ranking/latest.md)
- [JSON completo com 143 candidatos, posição, motivo, prova e 14 confrontos](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/ranking/latest.json)
- [Ledger de testes e metadados](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/census/latest.json)

O pipeline `.github/workflows/phase2-ranking.yml` atualiza os rankings após os testes de Fase 2 ou por agenda a cada 6 horas. Scripts puros `_dev/phase2_ranking.py` e `_dev/publish_phase2_ranking.sh`; logs, snapshot imutável e `latest.json/.md` na branch `ci-results`. Não altera `src`, `tests` da UX nem banco real. O ranking não depende de LLM.

## Melhor composição *provisória* entre os efetivamente testados

| Porta | Líder de referência | Desafiante / complemento | Motivo e cautela |
|---|---|---|---|
| Entrada integral/árvore | **CTK** | Polylogue / hstry ainda não testados | CTK é o único dos 3 importadores testados que preservou 5/5 mensagens incluindo dois ramos, IDs, SQLite e JSON nativo |
| Busca lexical do core | **SQLite FTS5** | **Tantivy**, depois BM25S | FTS5 já está incorporado e testado em escala; Tantivy PASS em pequena fixture mas troca requer ganho material |
| Busca JS local | **FlexSearch** | MiniSearch; Orama com verificação de licença | Todos PASS em 1k; FlexSearch com bom footprint, sem ainda comprovar serialização, acentos ou atualização |
| Índice vetorial opcional | **sqlite-vec** | LanceDB híbrido, USearch, HNSWlib, Annoy | Adoção sem trocar SQLite é mais barata; não existe validação de relevância semântica humana |
| Relações com fonte/estado | **RDFLib** (serialização) | NetworkX para análise; Semantica sem teste | RDFLib PASS em relações com evidência; não executou dedução de contradição ou supersessão |
| Contexto/memória temporal | **Nenhum aprovado** | OpenSelf e Graphiti primeiro | Algoritmos e produtos descritos, mas ainda não confrontados com fonte, tempo e revisão humana em CI |
| Qualidade da busca | **ir-measures** | ranx ainda sem teste | P@10, MRR@10 e nDCG@10 PASS em ranking controlado, evitando métricas caseiras |
| Reparação de sessões | **Nenhum aprovado** | Codex Sessions Manager, CTK como baseline parcial; IronBridge condicionado à licença | Importar árvore não é prova de repair, merge, undo ou rollback |
| Serviço de busca remoto | **Nenhum necessário ao MVP local** | Meilisearch / Typesense / outros como adapters | Serviço separado aumenta custo operacional, não substitui SQLite sem prova |

A palavra **líder** significa *melhor opção para confrontar ou consumir primeiro neste estágio*, segundo coerência arquitetural e testes disponíveis. Não é homologação do produto completo. Os números de latência publicados em CI não foram coletados com contratos de consultas equivalentes e, por isso, **não entram diretamente no escore**.

### Observação de licenças

Orama JS tem `NOASSERTION` no metadado GitHub desta rodada; requer inspeção do repositório e do pacote por versão, apesar de resultados funcionais PASS. Candidatos AGPL/GPL não ficam aptos a embutir no núcleo apenas porque o repositório é público. A licença de modelos/pesos também exige análise. Os campos `legal_gate` no ranking são bloqueios de adoção, não parecer jurídico.

## Ordem dos confrontos

A lista detalhada e atualizada está em `ranking/latest.json`. A prioridade adotada é:
1. CTK × Polylogue: integralidade de ramificações, origem e arquivos brutos.
2. CTK × hstry: importadores multi-provedor, cursores e retomada.
3. CTK × Codex Sessions Manager: reparação/rollback com fonte e sem mutações irreversíveis.
4. CTK × Loominary: versões e ramificações capturadas do navegador.
5. CTK × AI Conversation Index: esquema normalizado, idempotência, MCP e segurança.
6. OpenSelf: decisão humana e revogação em memória temporal.
7. Graphiti: proveniência episódica/temporal sem LLM obrigatória.
8. RDFLib × Semantica: relações explícitas com evidência, tipagem e abstenção.
9. FTS5 × Tantivy: *mesmo* corpus, indexação incremental, p95, disco, busca PT/EN.
10. FlexSearch × MiniSearch; depois Orama (licença): browser/Edge, consistência, atualização e RAM.
11. sqlite-vec × LanceDB: índice vetorial e busca híbrida, não mera comparação de tempo.
12. Sentence Transformers × FastEmbed: embeddings locais PT/EN, modelo licenciado e relevância humana.
13. Repair contra IronBridge condicionado a esclarecimento AGPL.

**Parâmetros obrigatórios de qualquer confronto:** fonte e hashes reproduzíveis, IDs canônicos, mesmo conjunto de documentos e consultas, ground truth humano quando relevante, precisão/recall/nDCG/p95/memória/disco, originalidade e fidelidade, execução independente sem LLM mandatória, dependências e licença. `NOT_TESTED` não é `FAIL`; ausência de prova não significa qualidade inferior.

## Governança com Fase 3 (UX) paralela

- **Fase 2 / esta sessão:** prospecta, mede e recomenda `ingest`, `search`, `vector`, `relations`, `memory`, `repair`. Mantém `_dev/phase2_*`, ranking e relatórios. Nenhuma alteração de frontend ou experiência de usuário.
- **Fase 3 / sessão parceira:** monta experiências, GUI/CLI de demonstração, jornada, componentes e testes de UX em branch própria.
- **Convergência:** UI depende de *contratos estáveis*, não de `CTK`, `Tantivy` ou `RDFLib` diretamente. A equipe de UX pode usar FTS5/Ricoeur atual e fixtures de árvore como dados de demonstração, mesmo com motor definitivo ainda em avaliação.
- [Handoff técnico ao parceiro UX](PHASE2_TO_UX_HANDOFF_R13.md), proposta sem alteração de runtime.

**Estado:** Fase 2 permanece aberta, mesmo com 143/143 triados. O ranking será reordenado quando surgirem evidências, contratos, licenças ou reprovações, preservando o histórico de cada CI.
