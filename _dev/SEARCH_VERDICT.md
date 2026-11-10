# Cha2db — veredito de busca lexical (2026-11-10)

## Decisão baseada em evidência

- **MANTER / ADOTAR FTS5** como candidato principal para recuperação lexical indexada (palavras, operadores e frases).
- **MANTER LIKE/instr como fallback** para pesquisa literal por fragmento: a semântica de substring não é idêntica à tokenização FTS5.
- **NÃO DECLARAR superioridade semântica**: embeddings, similaridade e medidas de relevância anotadas por humanos não foram avaliadas neste gate.
- **NÃO DECLARAR limite físico**: 2 milhões é o maior volume planejado aprovado, não uma capacidade máxima.

## Evidência CI reproduzível

A branch separada `ci-results` contém `ci-output/latest.json` e `ci-output/runs/<run-id>-<attempt>/`, com relatórios e logs completos de cada execução. O pipeline roda com Python 3.11/3.13 e executa o MCP oficial ao final.

Registro da execução inicial verificada: commit `17c5d6daf1030c5b2470e5e23c4640358614e9fe`, run `42909209801`.
- 40 mil / 100 mil / 400 mil / 1 milhão / **2 milhões** de mensagens: PASS
- Índice FTS5: integridade, atualização, exclusão e correspondência controlada: PASS
- MCP `stdio`: descoberta de tools, pesquisa, IDs e contexto: PASS
- Banco sintético de 2 milhões no runner: ~513 MiB; última etapa ~49 segundos
- Não verificou MCP com o corpus de 2 milhões; o gate MCP usa fixture própria pequena.

## Defeito de plano encontrado e corrigido

No SQL comparativo, `ORDER BY m.rowid` após JOIN materializava `USE TEMP B-TREE FOR ORDER BY`, forçando trabalho desnecessário para tokens comuns.
O SQL revisado ordena diretamente por `messages_fts.rowid`; teste automatizado exige que `EXPLAIN QUERY PLAN` **não** mostre TEMP B-TREE.

Em experimento local de 1 milhão de mensagens, termo comum `SSH` (mediana, IDs limitados a 100):
- FTS5 com ordenação anterior: **16,237 ms**
- FTS5 com ordenação pelo índice: **0,058 ms**
- LIKE literal: **0,121 ms**

Marcador raro `marcadorunico2026`:
- FTS5 indexado: ~**0,02 ms**
- LIKE literal: ~**98 ms**

As consultas de benchmark retornam **IDs somente** e não medem a montagem de contextos nem BM25 em produção. A recuperação com BM25 exige outra avaliação específica. Comparações foram feitas no mesmo hardware/dataset durante cada experimento, mas são microbenchmarks, não SLAs.

## Execução

- `bash _dev/busca.sh`: contrato de recuperação e corretude em banco temporário.
- `.venv/bin/python _dev/autoscale.py --stages 40000,100000,400000,1000000,2000000`: escala e plano de consulta.
- `.venv/bin/python _dev/teste7.py`: contrato MCP oficial (requer dependência opcional).
- GitHub Actions `.github/workflows/search-core.yml` executa automaticamente e publica os relatórios em `ci-results`.

## Fronteiras do veredito

Nenhum dado privado é usado na carga. Os testes garantem equivalência somente nas consultas controladas do corpus; não demonstram recuperação de consultas arbitrárias, relevância humana, concorrência sob escrita, acesso remoto MCP/HTTPS ou comportamento no Termux a 2 milhões de mensagens. A interface GUI não participa de nenhum desses gates.
