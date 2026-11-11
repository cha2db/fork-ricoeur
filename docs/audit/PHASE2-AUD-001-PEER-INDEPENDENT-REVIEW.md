# PHASE2-AUD-001 — Revisão independente da implementação do par

**Escopo:** `main` do `cha2db/fork-ricoeur` em 10/11/2026, Fase 2 (entrada, armazenamento, busca, API/MCP, prior art, avaliação). **Não** foram examinadas entregas de UX do outro agente como evidência do par. Nenhum arquivo `src/ricoeur/**` foi alterado nesta auditoria.

**Prova reproduzível:** `_dev/tests/peer_review/peer_phase2_adversarial.py` em `audit/phase2-independent-review-20261110`; [CI de reprodução](https://github.com/cha2db/fork-ricoeur/actions/runs/42944618429): **7/7 REPRODUCED** sobre código original. `REPRODUCED` significa que as falhas/limitações puderam ser reproduzidas; **não é PASS de qualidade**, e não representa frequência do problema em dados reais. Tudo sintético.

## 1. Acertos que devem ser preservados

1. **Prioridade correta:** entrada fiel, SQLite/FTS5, buscas por mensagem, IDs e contexto antes de trocar banco ou adotar novos algoritmos. Testes `_dev/teste4.py`, `teste6.py`, `teste7.py` mostraram benefícios reais de importação, busca e MCP em corpus sintético e Termux.
2. **Separação por adapters:** `src/ricoeur/retrieval.py` é independente do MCP e o código do servidor chama `search_messages` e `get_message_context`; essa composição deve continuar.
3. **Pesquisa de mercado com cautela:** R14 preservou 143 candidatos anteriores, adicionou 64, identificou 24 provas funcionais específicas de candidatos e **não** reivindicou homologação integral. `main/_dev/PHASE2_DISCOVERY_VERDICT_R14.md` registra que PGlite foi testado em Node, **não no browser**, e Portable Memory **perde vínculo explícito da árvore ChatGPT**.
4. **Sem reinvenção do FTS:** o núcleo usa a extensão integrada ao SQLite, com triggers. Evitar substituição até prova no mesmo corpus, ARM e cenário de instalação.

## 2. Achados reproduzidos (ordenados por risco ao contrato)

| ID | Gravidade | Evidência no código/teste | Efeito sobre Cha2db | Melhor correção de baixo risco | Gate para aceitar |
|---|---|---|---|---|---|
| **IDENTITY-001** | **P0** | `conversations.id TEXT PRIMARY KEY`; `insert_conversation` testa somente `id`. Fixture com ChatGPT/Claude mesmo ID externo: segundo é descartado. | Mistura ou perda de conversas de fontes distintas. | Introduzir chave interna estável e identidade de origem com `(provider, source_account/source_id, external_conv_id)`, sem sobrescrever IDs nativos. Planejar migração, colisões antigas e aliases. | Mesmo ID externo em dois provedores gera duas conversas distintas, múltiplas importações idempotentes. |
| **TREE-002** | **P0** | `chatgpt_nodes` contém alternativas; `_walk_messages()` escolhe apenas `kids[-1]`, e `messages_fts` só indexa `messages`. Mensagem alternativa aparece no bruto e não na busca. | Promessa de busca cruzada incompleta. | Preservar a árvore bruta e acrescentar projeção indexável de **todos** os nós/mensagens, com `node_id`, `parent_id`, `branch_type`, vínculo ao original; não misturar alternativas na sequência linear. | Buscar termo exclusivo do ramo não selecionado retorna sua mensagem e cadeia de ancestrais com origem. |
| **REIMPORT-003** | **P0** | `--update` usa `INSERT OR IGNORE` na árvore e nas mensagens. Ao trocar ramo selecionado, duas mensagens ficam pesquisáveis e `children_json` fica com a ordem antiga. | Estado do índice e topologia divergem do novo export. | Reconciliação transacional por snapshot/hash de origem, diff versionado de ramos; não sobrescrever conteúdo bruto sem evidência. | Reimportar árvore alterada atualiza projeção, preserva histórico e explica alterações. |
| **READONLY-006** | **P0** | `mcp_adapter.py` chama `get_connection()` que faz `PRAGMA journal_mode=WAL` e `migrate(conn)`. Fixture v1 é efetivamente migrada ao abrir. | Ferramenta anunciada como consulta pode alterar banco antes de autorizar. | Separar `open_for_read()` (SQLite URI `mode=ro`, `PRAGMA query_only=ON`, sem `migrate` ou criação automática) e operações explícitas de admin. | Hash/schema de banco v1 idênticos após consulta; caminho inexistente não cria DB; erro estruturado de versão incompatível. |
| **ATOMICITY-005** | **P1** | Importador confirma cada 25 conversas. Fixture com 26ª defeituosa falha após 25 persistidas. **Comportamento é deliberado para escalabilidade**, mas falta recibo de conclusão/retomada confiável. | Carga incompleta pode ser confundida com carga finalizada. | Manifesto de importação com estado `RUNNING/PARTIAL/COMPLETE/FAILED`, lote, hash da origem, resume e contagens, sem transação gigante. | Falhar no 26º arquivo exibe `PARTIAL` auditável e reexecução conclui sem duplicação. |
| **DRYRUN-004** | **P1** | Dry-run contabiliza item `new` após `_extract_model`, mas antes da normalização de conteúdo. Fixture aceita formato que a execução real rejeita. | Usuário recebe estimativa de viabilidade enganosa. | Fatorar `parse/validate/normalize` sem escrita e fazer dry-run percorrer o mesmo caminho lógico da importação. | Fixture inválida rejeitada em ambos os modos com mesmo erro e sem dados persistidos. |
| **RETRIEVAL-007** | **P1** | `search_messages` faz `SELECT * messages WHERE conv_id = ? ORDER BY ...` para **cada hit**. Fixture de 20 hits repete 20 consultas de toda a mesma conversa. | Amplificação de CPU/RAM/latência para conversas extensas. | Recuperar apenas janela por ID/ordem; `ROW_NUMBER`/keyset ou cache agrupado por `conv_id`; manter contrato JSON igual. | Medir p50/p95/RSS com 10k/100k mensagens, 1/20/200 hits, e equivalência da vizinhança. |

### Riscos adicionais observados no código — ainda sem reprodução independente

- `_walk_messages` não consulta `current_node` ao escolher o caminho principal: pode selecionar a resposta errada mesmo que árvore bruta esteja correta. Confirmar contra export real conhecido.
- `chatgpt_nodes` é criada **dentro do importador**, em vez de migração formal do modelo. Requer schema versionado, migração reversível e chaves de origem.
- O modelo `attachments` existe, mas a `_import_one()` do ChatGPT não o alimenta; o próprio `_dev/teste4.py` registra `attachment_fidelity=NOT TESTED`. Garantir referência ao arquivo, hash, tipo, multipartes e reportar ausências.
- Fonte de ChatGPT e hash de export original não aparecem no modelo persistido pela chamada `insert_conversation()`. Recomenda-se recibo de ingestão por fonte e itens/erros, além de comparação ao bruto.
- O MCP expõe resultados completos via stdio, sem autorização por conversa/mensagem nesse adapter; adequado ao teste local explícito, **não** um servidor multiusuário seguro. Fazer acesso negado por padrão antes de oferecer remoto.
- `pyproject.toml` declara `mcp>=1.0` sem teto; a evidência Termux `_dev/SESSION.md` fixa versões funcionais de SDK/Pydantic. Registrar matriz e arquivo de lock reprodutível por plataforma.
- O índice FTS5 de conteúdo externo pode divergir de `messages` embora `PRAGMA quick_check` não acuse: SQLite documenta `integrity-check` FTS5 com `rank=1` para verificar conteúdo externo. **Executar só em snapshot descartável**, porque esse comando escreve no índice.

## 3. Melhorias de pesquisa/evidência antes de continuar o universo

| Domínio Fase 2 | Já feito pelo par | Lacuna de comparação que vale mais que descobrir novos nomes |
|---|---|---|
| Entrada/CTK | Árvores e ramos estudados; CTK líder testado | Corpus adversarial com IDs iguais entre provedores, alternativas, mensagens vazias, arquivos, anexos e proveniência |
| Busca lexical | SQLite FTS5 baseline e motores alternativos ranqueados | Gold-set de consultas difíceis PT/EN, recall@k, nDCG, negativos e custo p95/Termux; confrontar Tantivy no **mesmo corpus** |
| Busca vetorial | sqlite-vec candidato verificado, outros listados | Matriz recall × RAM × disco × modelo/versionamento × CPU ARM; modelo opcional, sem LLM obrigatória |
| Relações/conexões | RDFLib com provas de serialização | Contradict/supersedes semânticos exigem origem e aprovação humana; separar aresta proposta da aceita |
| Memória temporal/repair | Grande prior art sem motor homologado | Primeiro baseline simples SQLite+eventos; só depois comparar OpenSelf/Aura/Mnemos no mesmo caso e sem LLM |
| Armazenamento histórico | SirixDB/TerminusDB/Dolt e muitos descobertos | Baseline append-only versionado vs migrar DB; preservar source raw e rollback |
| Portabilidade | Portable Memory 13/13 PASS de formato | `parent_id` ausente na árvore exportada; manter formato como **memory package**, não substituto de chat bruto |
| Browser/local storage | PGlite 6/6 em Node WASM | IndexedDB/performance e reinício offline em Android; não tratar Node como browser |
| Integrações | MCP stdio PASS no Termux sintético | Cliente externo, permissões, versão pinada, fechamento/read-only e teste negativo |
| Ranking/descoberta | 207 candidatos; R15 detectou 197 heurísticas adicionais | Definir critérios de saturação; exigir proof por contrato, licença/versionamento e custo de integração. Evitar promover README keyword a prova funcional |

## 4. Melhor sequência de execução para o par

**GATE A — Corrigir contrato de entrada antes de novas pesquisas de motores:** ID composto, árvore consultável completa, selected `current_node`, reimport diff, anexos e recibos. Não lançar migração sem plano de compatibilidade com bases já importadas.

**GATE B — Fechar fronteira de leitura:** abrir SQLite em read-only verdadeiro no MCP, erro se schema precisar de migração, permissões por recurso, e testes negativos sobre DB ausente/legado.

**GATE C — Index/recuperação com evidência:** otimizar N+1, auditoria FTS em snapshot, testes de carga e qualidade de busca em corpus idêntico PT-BR/EN com juízo humano de relevância.

**GATE D — Só depois decidir ferramentas novas:** bateria curta com CTK × Portable Memory, FTS5 × Tantivy, sqlite-vec × turbovec, RDFLib × grafo temporal, PGlite no navegador. Aumentar catálogo R15 somente quando revelar capacidade/abordagem realmente inédita.

## 5. Condições de revisão independente

1. Cada correção deve ter teste RED (reprodução), patch do par e teste GREEN (contrato atendido); manter fixtures na categoria `_dev/tests/phase2/` se o par aprovar a organização.
2. Toda decisão de adoção exige ID do candidato, versão/commit, licença do módulo e pesos, hash da fixture, ambiente (incluindo Termux/ARM), parâmetros e medidas comparáveis. O código `_dev/phase2_r14_review.py` reusa relatórios em `ci-results`, mas não amarra cada PASS a commit e versão da ferramenta testada.
3. Monitoria do par deve continuar de forma autônoma: corrigir bugs técnicos dentro do mandato sem pedir decisão humana, escalando somente mudança de modelo/risco de migração/segurança/política.
4. Nada aqui autoriza merge da branch de auditoria. Seu objetivo é propor correções ao **par**, não reimplementar o core pela frente UX.

**Conclusão:** o maior risco não é faltar outra biblioteca; é tratar `dados preservados`, `dados pesquisáveis`, `histórico coerente` e `fonte auditável` como se fossem equivalentes. A recomendação é fechar o contrato de entrada e os gates read-only/performance antes de ampliar mais mecanismos.

### Evidências primárias

- [schema SQLite e migrações](https://github.com/cha2db/fork-ricoeur/blob/main/src/ricoeur/db.py)
- [importador ChatGPT](https://github.com/cha2db/fork-ricoeur/blob/main/src/ricoeur/importers/chatgpt.py)
- [funções de importação compartilhadas](https://github.com/cha2db/fork-ricoeur/blob/main/src/ricoeur/importers/base.py)
- [busca por mensagem](https://github.com/cha2db/fork-ricoeur/blob/main/src/ricoeur/retrieval.py)
- [adapter MCP](https://github.com/cha2db/fork-ricoeur/blob/main/src/ricoeur/mcp_adapter.py)
- [veredito Fase 2 R14](https://github.com/cha2db/fork-ricoeur/blob/main/_dev/PHASE2_DISCOVERY_VERDICT_R14.md)
- [triagem Fase 2 R15](https://github.com/cha2db/fork-ricoeur/blob/main/_dev/PHASE2_DISCOVERY_PRESCREEN_R15.md)
- [docs SQLite FTS5](https://www.sqlite.org/fts5.html)
