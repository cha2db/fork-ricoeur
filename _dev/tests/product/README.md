# Categoria PRODUCT — testes autônomos por rodada

**Uma subpasta** `_dev/tests/product/` para todos os testes de produto, e
**uma subpasta** `_dev/results/product/` para as evidências locais. Não criar
subpastas por candidato.

- `bash _dev/tests/product/teste16.sh` — confronta 12 frentes/71 candidatos com
  Fase2 143 + expansão R14 64 **quando presente** e UX 46, mede duplicatas e
  valida ranking documental sem claims de homologação.
- `_dev/results/product/teste16.{log,json}` e
  `ranking16.{json,md}` gerados localmente, não subir logs privados.
- Este teste **não** instala executáveis externos, não altera SQLite, não executa
  benchmarks e não eleva candidato pesquisado a ADOPT.
- No checkout da PR virtual merge, a expansão R14 (207) **deve** estar presente;
  o teste reprova se faltar. Na branch UX isolada, a R14 ainda está só em `main`,
  portanto o relatório explicitamente sinaliza cobertura parcial.
