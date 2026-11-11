# UX-001 — Adoção antes de construção (branch independente)

- Owner: INITPROJ_C2D-MPO.P1.0003 (frente UX, sem alterar o trabalho do par)
- Base: `cha2db/fork-ricoeur@main`, consultada em 2026-11-10
- Status: **spec**; candidatos não homologados por benchmark; nenhuma alteração em banco, importação ou busca
- Regra: **CLI como contrato executável; GUI apenas cliente da CLI**. Nenhuma duplicação do algoritmo.

## Inventário comprovado no código

| Capacidade | Evidência | Decisão inicial |
| --- | --- | --- |
| CLI Click com import, search, show, stats, index | `src/ricoeur/cli.py` | **KEEP-CANDIDATE**: estender, não substituir |
| Busca FTS5/BM25, semântica e RRF | `src/ricoeur/search.py` | **KEEP-CANDIDATE**: consumo somente; algoritmos pertencem ao par |
| SQLite e índices de conversas/mensagens | `src/ricoeur/db.py` | **KEEP-CANDIDATE**: não migrar nesta frente |
| TUI Textual: lista, busca, leitura Markdown e contexto | `src/ricoeur/tui.py` | **ADOPT-CANDIDATE**: aproveitar antes de nova GUI |
| `search --format json` | `src/ricoeur/cli.py` | **KEEP-CANDIDATE**: ponto inicial; falta contrato JSON versionado |
| FastAPI/uvicorn opcionais | `pyproject.toml` | **EVALUATE**: servidor local opcional, não criar API paralela |
| Grafo visual de correlações | não verificado nos arquivos inspecionados | **GAP-UNVERIFIED**: verificar restante do repo antes de implementar |

Não interpretar candidatos como vereditos definitivos. Adoção requer prova executável, licença e acessibilidade.

## Prior art — matriz de decisão

1. **Textual** (já dependência opcional): manter TUI existente. Critério: navegação por teclado, busca e leitura com origem.
2. **Click** (já dependência): manter CLI e adicionar operações de UX por contratos, sem copiar regras de negócio.
3. **Cytoscape.js** (candidato para grafo web): preferir pela interação, layout e eventos; validar licença e bundle antes de adotar.
4. **Sigma.js + Graphology** (alternativa para grafos grandes): comparar só se Cytoscape falhar em escala/acessibilidade.
5. **Vue 3 CDN** (candidato de shell GUI): avaliar integração com grafo; não impor Nuxt nem build complexo antes de necessidade.
6. **FastAPI** (já extra opcional): usar somente como adaptador de transporte localhost se subprocesso CLI for inadequado.

## Contrato CLI → GUI (proposto, não implementado)

- `ricoeur ux capabilities --format json`: comandos, formatos, versões e limitações detectadas.
- `ricoeur ux conversations --query ... --platform ... --since ... --until ... --limit ... --format json`: consulta com filtros, `conversation_id`, `source_ref` quando disponível, modo efetivo de busca e score.
- `ricoeur ux transcript <id> --format json`: mensagens ordenadas, papel original, texto, IDs, anterior/próxima, origem.
- `ricoeur ux relations <id> --depth 1 --format json`: nós/arestas **somente com evidência de relação**; `relation_type`, `evidence_refs`, `method`, `confidence` opcional. Sem arestas inventadas.
- `ricoeur ux graph --query ... --format json`: subgrafo limitado e paginado, nunca varredura total por padrão.
- Todos: `schema_version`, `status`, `data`, `errors`; saída JSON somente stdout; logs stderr; códigos de saída documentados. JSON v1 não promete campos que o banco ainda não possui.

**Arquitetura:** GUI (Vue/HTML) → adaptador local (subprocesso CLI ou FastAPI como wrapper) → CLI/serviços existentes → DB/search do par. GUI não abre SQLite, não reimplementa SQL, não infere relações. TUI usa os mesmos serviços.

## Jornadas e cortes de valor

- **UX0 — Leitura**: lista → conversa → mensagens, origem e anterior/próxima; reutilizar `show` e Textual. Prova: 3 chats distintos, retorno ao mesmo ID.
- **UX1 — Busca avançada**: filtros visíveis + resultados com trechos + modo keyword/semantic/hybrid explícito; comparar CLI/GUI no mesmo corpus. Prova: IDs e ordenação equivalentes.
- **UX2 — Grafo**: pesquisa → nós de assunto/conversa → arestas com justificativa clicável → abrir mensagem de origem. Prova: 2 relações verificadas, 1 par sem relação não conectado.
- **UX3 — Navegação cruzada**: de uma mensagem para assunto relacionado e volta ao ponto exato. Prova: ida/volta determinística.
- **UX4 — Escala**: grafo limitado, paginação, filtros e alternativa tabular acessível. Prova: teste L0/L1/L2 sem travar interface.

## Gates de adoção, sem repetição de testes

| Gate | Critério | Estado |
| --- | --- | --- |
| UX-ADOPT-01 | TUI atual satisfaz UX0 sem fork novo | pending |
| UX-CLI-01 | JSON versionado, IDs estáveis, CLI e GUI equivalentes | pending |
| UX-GRAPH-01 | visualização com arestas rastreáveis, sem correlações inventadas | blocked (contrato de relações pendente do par) |
| UX-PERF-01 | L0/L1/L2 com tempos medidos e limites explícitos | pending |

Para cada candidato registrar `ADOPT / WRAP / KEEP / DEFER / REJECT`, evidência, versão, licença, custo de integração e **condição objetiva de reabertura**. Não repetir teste que já tenha veredito com mesmo código+fixture+ambiente; executar somente quando mudar evidência, requisito ou versão.

## Coordenação

O par mantém propriedade de **banco, importação, busca, ranking e geração de relações**. Esta branch cuida exclusivamente de apresentação, CLI de experiência e adaptadores de interface; integrações só após contrato acordado. Nenhum merge ou release automático.

**Próximo passo técnico:** testar a TUI existente contra UX0; se passar, preservar. Em seguida implementar o envelope CLI UX0/UX1 como wrapper, sem tocar no algoritmo. Validar Cytoscape.js contra um subgrafo sintético claramente rotulado, sem afirmar que há relações reais.

**Decisão humana:** nenhuma necessária para o experimento reversível nesta branch; a escolha final da stack GUI permanece aberta até benchmark.
