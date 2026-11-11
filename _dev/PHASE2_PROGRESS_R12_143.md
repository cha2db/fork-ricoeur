# Cha2db — Fase 2 R12: avanço verificável dos 143 candidatos

Data: 2026-11-10/11 (GitHub Actions UTC). Fonte de verdade: [matriz de evidências R10 dinâmica](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/census/latest.json).

## Indicadores reais

| Indicador | Valor | Significado |
| --- | ---: | --- |
| Candidatos de mercado catalogados | 143 | Universo fechado R10 para revisão; descoberta geral continua distinta |
| Candidatos com disposição registrada | **143/143** | Triagem concluída, NÃO aprovação |
| Repositórios GitHub distintos consultados | 123 | Metadata/licença README; 20 links não GitHub |
| PASS funcional verificado | **22** | Em gates específicos sintéticos/CI |
| FAIL funcional verificado | **2** | Reweave e Chat Chronicle, perda de ramo |
| Bloqueios técnicos comprovados | **2** | SQLite vec1 indisponível, SQLite-Vector PyPI com API incompatível |
| Sem teste funcional | **117** | Inclui referência, serviços e opções legalmente não elegíveis |
| Testes comparativos acionáveis ainda pendentes | **81** | 22 gates P0, 59 comparações nas demais prioridades |
| Decisões documentadas de triagem | 143 | Toda entrada aponta motivo/nível de evidência |

Os números representam o snapshot do ledger validado nesta rodada. A pesquisa de novos produtos e a revisão jurídica de licenças NÃO estão encerradas.

## Descobertas decisivas para o núcleo

### Entrada, reparação e preservação integral (mesmo fixture sintético)
**CTK 2.20.2: PASS** no importador ChatGPT, ramo alternativo, 5/5 mensagens, IDs e parent links, dois caminhos em SQLite, gravação repetida sem duplicar IDs, exportação JSON canônica e reimportação de árvore.

**Reweave 0.1.0: FAIL** 4/5 mensagens no formato normalizado do teste; descarta ramo alternativo (parser escolhe apenas ramo ativo).

**Chat Chronicle: FAIL** 4/5 mensagens; normalizador lineariza cadeia ao invés de preservar todas as ramificações.

Veredito parcial: CTK passa a candidato líder para **porta import/árvore**, não como substituto integral do Cha2db, sujeito à fidelidade dos bytes originais, anexos, outros provedores e atualização realmente incremental. Evitar inventar novo parser se CTK puder ser adotado com contrato e licença compatíveis.

### Medição, vetores e grafos (4 novas provas técnicas)
- **HNSWlib:** PASS, recall@10=1,00 nas seis consultas com TF-IDF/SVD32 e jitter determinístico.
- **Annoy:** PASS, recall@10=1,00 nas mesmas consultas.
- **RDFLib:** PASS, round-trip exato de 2 relações explícitas com evidência; zero aprovação inferida.
- **ir-measures:** PASS, P@10 / RR@10 / nDCG@10 = 1 em ranking correto e 0 no adversarial. Candidato à adoção para métricas de recuperação, reduzindo manutenção de fórmulas próprias.

Os resultados NÃO provam superioridade na semântica real nem que vetores substituem FTS5.

## CI: evitar repetição improdutiva
Corrigidos gatilhos que antes executavam novamente o estresse de **2 milhões de mensagens** em cada push de documentação e que reexecutavam motor lexical quando apenas scripts de publicação mudavam. Agora suites de pesquisa são executadas por mudança material nos respectivos arquivos de fonte/teste, ou disparo manual `workflow_dispatch`. Veredictos já estáveis são mantidos no `ci-results`.

## Próximos gates com evidência necessária — sem autorização de produção
Portas P0 ainda sem homologação comparável: Polylogue, hstry, Loominary, OpenSelf, Reweave para UX, IronBridge para repair (licença AGPL condiciona adoção), Grafos temporal/revisão com Graphiti/Cognee/Mem0/Semantica. Fonte/semântica/branches/validade e contratos precisam ser comparados em cenários adversariais, sem cloud e sem LLM obrigatória. Atualização dos casos e licenças separada.

## Artefatos reproduzíveis
- [Ledger 143 candidatos](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/census/latest.json)
- [Reweave FAIL](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/reweave-latest.json)
- [Chat Chronicle FAIL](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/chronicle-latest.json)
- [CTK SQLite/JSON PASS](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/ctk-store-latest.json)
- [HNSWlib PASS](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/hnswlib-latest.json)
- [Annoy PASS](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/annoy-latest.json)
- [RDFLib PASS](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/rdflib-latest.json)
- [ir-measures PASS](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/ir-measures-latest.json)

**Fase 2: aberta.** Uma disposição para 143/143 significa `nenhum item sem triagem`, NÃO `143 produtos homologados`. A decisão final de composição deve seguir contratos, licença, resultado relevante e custo de manutenção, não quantidade de motores disponíveis.
