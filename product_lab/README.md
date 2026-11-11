# Cha2db · Mapa transversal do produto

A Fase 2 (207 candidatos de busca/armazenamento/entrada/memória) e a frente UX
(46 candidatos de interface) têm suas próprias evidências e rankings.
**Esta pasta não substitui nem duplica esses inventários.**

## O que foi implementado

- **PRODUCT-016**: `fronts.json` descreve 12 frentes operacionais e 71
  candidatos em contratos separados, cada um com próxima prova concreta e
  marca `NOT_TESTED_IN_PRODUCT_ROUND`.
- `rank.py`: notas provisórias com pesos publicados, ranking de prioridade das
  frentes e rankings **por subporta** de candidatos. URL normalizada para
  confrontar automaticamente Fase 2 R10 (143), R14 (+64 quando disponível) e
  UX (46). Uma URL já conhecida é sinalizada, não contada como novo produto.
- **Painel** `/product`: mesmas informações por JSON HTTP `action=product`,
  com estado, próximos testes, referências e vínculos de origem. Não precisa
  que o banco SQLite esteja inicializado para exibir catálogo.
- **PRODUCT-017**: `doctor.py`, diagnóstico SQLite **somente leitura** via
  verificações nativas `PRAGMA quick_check`, `foreign_key_check`, tabelas
  e chaves de anexos/FTS; nunca repara automaticamente.

## Como executar

```bash
bash _dev/tests/product/teste16.sh
bash _dev/tests/product/teste17.sh
python product_lab/rank.py --format md --output _dev/results/product/ranking16.md
python product_lab/rank.py --format json --output _dev/results/product/ranking16.json
python product_lab/doctor.py --db /caminho/ricoeur.db
python ux_lab/ux.py --db /caminho/ricoeur.db serve --port 8765
```

Abrir `http://127.0.0.1:8765/product` no **mesmo aparelho**. Não expor
localhost para LAN sem autenticação. O ranking é público e funciona até com
banco ausente; o doctor exige um SQLite existente e não publica conteúdo.

Na branch UX isolada, o inventário R14 está apenas em `main`; por isso,
a geração avisa que o confronto foi parcial. **Na PR virtual de merge a
CI exige R10+R14 completos (207) e UX (46).**

Resultados **locais** somente em `_dev/results/product/`, sem dados reais
nem logs privados no GitHub.

## Estados que não devem ser confundidos

- `already_catalogued`: URL apareceu em outra pesquisa; não significa
  que já foi testada funcionalmente ou que o contrato seja idêntico.
- `new_to_cha2db_inventories`: URL não apareceu nos JSON cruzados. Não
  significa descoberta inédita na Internet.
- `NOT_TESTED_IN_PRODUCT_ROUND`: todos os candidatos da rodada; as
  verificações documentais e funcionais anteriores da Fase 2 são independentes.
- `PASS PRODUCT-016`: integridade de ranking/portas/URLs e catálogo Web.
- `PASS PRODUCT-017`: diagnósticos sintéticos de cópia SQLite, NÃO
  restauração ou reparo real.

Leia `docs/product/PRODUCT-016-017-PORTFOLIO-RANKING.md`.
