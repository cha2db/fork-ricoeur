# Rodadas UX — categoria única de testes

Scripts de cada rodada nesta pasta, resultados em **uma única** `_dev/results/ux/`.

| Rodada | Script | Gate |
|---|---|---|
| 008 | `bash _dev/tests/ux/teste8.sh` | CLI FTS5/graph/transcript com 3 conversas e 6 mensagens |
| 009 | `bash _dev/tests/ux/teste9.sh` | Adaptação direta ao core `ricoeur.retrieval` |
| 010 | `bash _dev/tests/ux/teste10.sh` | Ranking preliminar reproduzível |
| 011 | `bash _dev/tests/ux/teste11.sh` | Contrato CLI = HTTP e evidência de UI HTML, sem writes |
| 012 | `bash _dev/tests/ux/teste12.sh` | 46 candidatos e matriz de tipos de busca e apresentação |

**GitHub Actions UX Lab:** todas as cinco rodadas passaram em execução Python 3.11 no PR #1 (10/11/2026), sujeito a nova execução após alterações. Isso **não** prova integração real de navegador, addon externo nem desempenho em tablet.

**Tablet somente depois de merge pelo par.** No Termux, executar a partir da branch compartilhada: `bash _dev/tests/ux/teste11.sh` e então iniciar a GUI com a base desejada no próprio dispositivo. A porta localhost não foi exposta à LAN.

| 014 | `bash _dev/tests/ux/teste14.sh` | Série temporal por termo, normalização por mil, drill-down, nuvem, SKOS demonstrativo |

As evidências UX-014 não inferem aprendizagem ou estrutura cerebral; documentam apenas conteúdo de mensagens e o tesauro explícito. A execução de GUI ECharts/wordcloud em navegador real continua pendente de teste manual posterior ao merge.
