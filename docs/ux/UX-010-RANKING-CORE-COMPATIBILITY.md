# UX-010 — ranking preliminar por proximidade de core

Ranking **provisório**, gerado por `python ux_lab/rank_candidates.py` com pesos 40% core, 30% GUI, 20% custo de adapter, 10% licença/adoção. Notas de 1 a 5 são hipóteses técnicas, não benchmarks; a pontuação NÃO comprova compatibilidade ou licença. Manifesto versionado `ux_lab/candidates.json`.

## Comparação com Ricoeur

- **Ricoeur + Textual**: já usa SQLite/FTS5, Click, Textual; core idêntico e GUI terminal funcional. Adotado.
- **Cytoscape.js / Vue Flow / vis-network / Sigma.js / G6**: não trazem core de armazenamento e busca; preservam Ricoeur. Cytoscape para explorar, Vue Flow para editar, vis-network para prova simples; Sigma/G6 condicionados a evidência de escala/layout.
- **LLM Chat Vault**: interface de chats e ramificações relevante, mas schema SQLite e core de navegação próprios. Não substituir core sem prova de equivalência.
- **Kept**: arquivo de chats e grafo prontos, mas modelo de armazenamento diferente (Markdown/CozoDB). Potencial de reaproveitar UI; core não equivalente.
- **msgvault / Khoj**: explorar componentes isoláveis, sem adotar núcleo ou LLM obrigatório.

## Rodada reproduzível

`bash _dev/tests/ux/teste10.sh` gera `_dev/results/ux/teste10.log`, `teste10.json` e `ranking10.json`. Não altera banco e não depende de internet. Testa ranking e rastreabilidade, **não** executa as GUIs de terceiros. Para aceitar um candidato, ainda exigimos clone com versão fixada, licença confirmada, integração sobre o MESMO corpus SQLite, medição e relatório de falha/sucesso.

## Decisão de integração

Não pedir merge ao par enquanto a GUI HTTP atual não usar a porta FTS5 existente e enquanto os testes de UX-009/010 não estiverem validados. A integração deve preservar o core do par e as pastas únicas `_dev/tests/ux` e `_dev/results/ux`.
