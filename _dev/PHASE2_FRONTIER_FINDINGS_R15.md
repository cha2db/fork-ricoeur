# Cha2db — Fase 2 | Descobertas de busca e armazenamento R15

Data da consolidação: 11/11/2026. **Escopo exclusivo de pesquisa Fase 2**; não altera a Fase 3 de experiência de usuário.

## Governança do inventário e da evidência

O inventário de origem da Fase 2 (`_dev/PHASE2_MARKET_UNIVERSE_R10.json`) possui 143 candidatos. Um levantamento já publicado na mesma branch (`_dev/PHASE2_MARKET_EXPANSION_R14.json`) identificou 64 novas alternativas. Uma busca adicional cobrindo bancos temporais, busca local/Android, CRDT, indexação estática e linhagem de dados identificou 29 nomes; **10 já estavam no R14**, restando **19 inéditos após deduplicação por URL**.

Resultado único: **226 candidatos / IDs C001–C226** em [PHASE2_MARKET_UNIVERSE_R15.json](PHASE2_MARKET_UNIVERSE_R15.json). Ambos os R14 originais foram preservados como evidência histórica; **R15 é o inventário canônico para novas descobertas**. O ranking R13 e o census de 143 produtos testados/triados permanecem intactos, para não criar métricas fictícias.

**Estado dos 83 candidatos adicionais: `NOT_TESTED_IN_THIS_ROUND`.** Verificação documental e de existência/licença não constitui homologação ou integração.

## Oito abordagens que alteram as perguntas de pesquisa

| Mecanismo novo | Candidatos | Por que confrontar |
| --- | --- | --- |
| Banco bitemporal e dados versionados | SirixDB C146, XTDB C162, TerminusDB C147, Dolt C148, DoltgreSQL C208 | Recuperar decisões como eram conhecidas e como eram válidas, preservar correções sem sobrescrever fatos originais |
| Um arquivo com dados+índices híbridos | Infino C206; Kalan DB C220 (Android `.vdb`) | Evitar manter SQLite, índice textual, índice vetorial e metadados em stores separados; testar troca de layout e custos de atualização |
| Consulta declarativa multi-hop sem LLM | CozoDB C152, sqlite-graph C216, LadybugDB C144, HelixDB C145 | Encontrar dependências entre mensagens, conceitos, decisões e evidências sem gerar afirmações falsas |
| Captura local e preservação de branches | Threadline C217, Personal AI Memory C218, Loominary C135, CTK C118 (baseline funcional) | Confrontar export integral com captura passiva, incluindo variantes de respostas e versões que o ZIP não revele |
| Navegador sem backend SQL/Python | PGlite C155, Pagefind C212, LiveStore C209, TinyBase C222 | Consultar dados em browser/offline, com índices fragmentados ou materializações locais |
| Proveniência de pipelines (não apenas conteúdo) | OpenLineage C214, Marquez C215, Lossless Memory C179 | Rastrear de qual arquivo e qual execução surgiu cada mensagem normalizada, e reproduzir repair/erros |
| Sincronização/merge sem conflitos de escrita | Automerge C210, Yjs C211, ElectricSQL C156, PowerSync C223 | Human-first: sincronizar *anotações e revisões* sem alterar conversas brutas; distinguir leitura e escrita |
| Busca lexical por índice especializado | Zoekt C213 e Pagefind C212 versus FTS5 C001 | Regex/substrings em históricos técnicos e índices de leitura estática com pouco download |

Alguns nomes pertencem a famílias e maturidades diferentes; **não devem competir no mesmo placar de latência**.

## Primeiros confrontos recomendados

1. **Infino × LanceDB × FTS5+sqlite-vec**: data+index colocalizado, zero ETL, ingestão em lotes, 40k/2M, p95 e ARM. Biblioteca em nível 0.x; não trocar núcleo antes de validar.
2. **SirixDB / XTDB / TerminusDB × SQLite+log de proveniência**: decisões reescritas ou contrariadas, histórico e duas dimensões de tempo, custo de JVM/servidor.
3. **sqlite-graph × RDFLib/NetworkX**: mesmas mensagens, referências explícitas, consultas multi-hop, evidências e revisão humana.
4. **CTK × Threadline / Personal AI Memory**: branches, arquivos originais, captura incremental e perdas de contexto.
5. **Kalan DB × FTS5/sqlite-vec no Android ARM64**: viabilidade real num tablet, RAM e corretude; o autor marca Kalan como prova de conceito.
6. **Zoekt × FTS5 trigram**: termos parciais, regex, filtro de origem, índice persistente.
7. **OpenLineage × modelo de recibos atual**: contrato de importador/normalizador/indexador, audit trail sem backend obrigatório.
8. **PGlite/LiveStore/Automerge × SQLite e contratos atuais**: apenas leitura local/revisão e sincronização, sem introduzir dependência desnecessária.

**Não transformar princípios como CRDT, event sourcing ou bitemporalidade em tecnologia obrigatória.** São alternativas com testes e limites próprios. Para dados originais, prioridade é preservação literal; para evidências derivadas, rastreabilidade e reversibilidade; para UX, liberdade de adaptação por contrato.

## Rastreamento e execução

- [Inventário R15 completo](PHASE2_MARKET_UNIVERSE_R15.json)
- [Ranking R13 já homologado em gates sintéticos](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/ranking/latest.json)
- [Fronteira R15, ranking de confrontos e relatório de metadados CI](https://github.com/cha2db/fork-ricoeur/tree/ci-results/ci-output/phase2/frontier)
- `.github/workflows/phase2-frontier.yml`: audita repositórios/arquivamento/SPDX, verifica unicidade e gera fila de confrontos; pode mostrar BLOCKED enquanto CI não terminar.
- `.github/workflows/phase2-discovery.yml`: continua procurando novas alternativas em múltiplas categorias, deduplicando contra R15; agendado duas vezes por semana no repositório.

Nenhum candidato adicional obteve PASS funcional neste levantamento. **Fase 2 continua aberta**; chamar a Internet de “esgotada” sem ciclos de saturação e validação seria incorreto.
