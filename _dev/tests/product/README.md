# Categoria PRODUCT — testes autônomos por rodada

Uma única categoria para testes `_dev/tests/product/` e uma única categoria
para seus resultados locais `_dev/results/product/`.

- `bash _dev/tests/product/teste16.sh`: ranking de 12 frentes/71 candidatos,
  confronto real R10 (143), R14 (+64) e UX (46). Inclui a prova HTTP
  `test_portfolio_ui.py`: página `/product`, JSON da CLI, navegação fixa
  e **nenhum arquivo SQLite criado** ao abrir o ranking.
- `bash _dev/tests/product/teste17.sh`: diagnóstico estrutural de banco
  Ricoeur com fixtures saudável, órfã, sem FTS e arquivo ausente, sem escrita
  e sem conteúdo privado nos resultados.
- Os scripts geram `teste16.{json,log}`, `ranking16.{json,md}` e
  `teste17.{json,log}` em `_dev/results/product/` local, sem publicar
  evidências de bases reais.
- Teste `16` em checkout de PR exige R14 completo; na branch UX isolada
  registra cobertura parcial e não inventa os 64 itens do par.
- Nenhum teste instala terceiros; bibliotecas candidatas seguem
  `NOT_TESTED_IN_PRODUCT_ROUND` até cenários comparativos de suas subportas.
