# PRODUCT-016/017 — Varredura transversal de Cha2db e ranking de adoção

**Escopo**: novas frentes do produto, não uma terceira cópia da pesquisa de mecanismos Fase 2 nem do ranking de UX. Publicado em `feat/ux-cli-gui-p1-0003`. O merge pertence ao par mediante todos os gates.

## Inventário cruzado real

| Conjunto | Total | Cobertura / ressalva |
|---|---:|---|
| Fase 2 — R10 | 143 | `_dev/PHASE2_MARKET_UNIVERSE_R10.json` |
| Fase 2 — expansão R14 | +64 = **207** | `main/_dev/PHASE2_MARKET_EXPANSION_R14.json`; no checkout isolado da UX pode estar ausente, então o PR deve testar o merge virtual |
| UX | 46 | `ux_lab/candidates.json`; GUIs, mapas e referências científicas |
| PRODUCT-016 | **71** | distribuídos em 12 frentes; **10 URLs já inventariadas nos dois conjuntos anteriores e 61 novas nesses inventários** ao cruzar R10+R14+UX |

**Novo neste inventário não significa projeto inédito na Internet ou não mencionado em conversas.** A deduplicação usa URL canônica, não identidade de nome; alias, forks e licenças por módulo ainda exigem revisão humana. Não reivindicar 207+46+71 projetos únicos.

## Ranking de prioridade das frentes (hipótese para testar primeiro)

Pesos **frente**: impacto no produto 40%, lacuna atual 25%, segurança 25%, facilidade de prova 10%. Pesos distintos para **candidato**: compatibilidade com core 35%, adapter 25%, soberania 20%, plataforma 10%, confiança preliminar na licença 10%.

| Ordem | Frente | Prioridade | Estado atual observado | Primeiro contrato a provar |
|---:|---|---:|---|---|
| 1 | Backup, exportação e restauração | 100 | Sem backup/restore integral comprovado | `encrypted_backup`: restic × Borg; `file_encryption`: age |
| 2 | Privacidade e proteção | 98 | Sem criptografia ou políticas de acesso homologadas | `secret_scanning`: Gitleaks × detect-secrets; `at_rest_encryption`: SQLCipher |
| 3 | Reparação e diagnóstico | 98 | Não há motor de repair aprovado | `db_recovery`: SQLite .recover; `db_snapshot`: backup API |
| 4 | Qualidade de entrada | 95 | Importação e ramos sintéticos testados; contrato total incompleto | `schema_validation`: Pydantic × jsonschema |
| 5 | Avaliação de produto | 90 | IR e carga estudadas, mas não validação de jornadas humanas | `deterministic_ir`: ir-measures × ranx; invariantes Hypothesis |
| 6 | Instalação multiplataforma | 90 | uv e Termux usados, instalador de produto não homologado | `cli_installer`: pipx × PEX; `desktop_packager`: PyInstaller × Nuitka |
| 7 | Permissões/delegações | 88 | Não implementado como política de produto | `embedded_policy`: Casbin × Cedar; serviço separado opcional |
| 8 | Captura multiformato | 85 | ACE/CTK/Ricoeur estudados, anexos e normas de entrada pendentes | `document_converter`: MarkItDown × Docling × Tika |
| 9 | Governança humana | 85 | Subset SKOS sem fluxo de aprovação | `human_annotation`: Label Studio × doccano |
| 10 | Observabilidade | 82 | CI e logs, sem rastreamento de operações comum | `instrumentation`: OpenTelemetry e exportadores opcionais |
| 11 | Interoperabilidade | 72 | MCP stdio sintético PASS; A2A ainda não | `tool_protocol`: MCP; `agent_protocol`: A2A; `http_contract`: OpenAPI |
| 12 | Sincronização | 65 | Candidatos CRDT analisados na Fase 2; sem merge offline aceito | `crdt_annotations`: Automerge × Yjs; arquivos brutos imutáveis |

**Nenhuma pontuação prova vitória técnica nem autoriza adoção.** Candidatos são comparados **por subporta**. Não comparar `age` (cifra) com `restic` (backup), nem `A2A` (agentes) com `MCP` (ferramentas).

O ranking completo e atualizado é gerado do manifesto:

```sh
bash _dev/tests/product/teste16.sh
python product_lab/rank.py --format md --output _dev/results/product/ranking16.md
python product_lab/rank.py --format json --output _dev/results/product/ranking16.json
```

Os resultados locais ficam em **uma única pasta** `_dev/results/product`. A análise contém URL, porta, estado, ocorrência nos inventários anteriores, criticidade e teste seguinte para cada um dos 71 candidatos.

## Abordagens já cobertas: não reinventar

- **Entrada/árvores e preservação de IDs**: o par demonstrou CTK mais fiel que Reweave no cenário ramificado. Dados originais e identidade nativa prevalecem sobre layouts JSON normalizados.
- **Busca lexical**: Ricoeur SQLite/FTS5; `src/ricoeur/retrieval.py` já permite mensagem, IDs, contexto e filtro.
- **Busca vetorial**: sqlite-vec e outros confrontados na Fase 2; nenhuma seleção de produto completo justificada.
- **Relações**: RDFLib/formatos tipados prior art; UX já possui subset SKOS e grafo de evidências, mas não grafo cognitivo automaticamente validado.
- **Interface**: UX 46 referências; sete rodadas de testes anteriores; não reimplementar a GUI neste pacote.
- **MCP**: a sessão do par registrou PASS de cliente/servidor stdio em fixture; isso não é teste de A2A nem implantação multiusuário.
- **Memória e chat repair**: Fase 2 R14/R15 estudou muitos motores e modelos temporais, sem motor aprovado. Não transformar um ranking de bibliotecas de memória em memória já extraída do usuário.
- **Sincronização**: RxDB, Dexie, cr-sqlite, etc. já foram catalogados pelo par. A nova frente só estuda o fluxo do produto e seus contratos.

## Entrega executável além do ranking (PRODUCT-017)

`product_lab/doctor.py` usa **recursos nativos do SQLite**, com conexão somente leitura, sem novo motor e sem reparo automático. Checa integridade estrutural (`PRAGMA quick_check` ou `integrity_check`), chaves estrangeiras, tabelas essenciais, órfãos de mensagens e anexos, presença de triggers FTS5. **Não exibe conteúdo de conversas ou arquivos nem grava no banco.**

```sh
python product_lab/doctor.py --db /caminho/ricoeur.db
python product_lab/doctor.py --db /caminho/ricoeur.db --full
bash _dev/tests/product/teste17.sh
```

**Limite:** integridade estrutural não prova integridade de índice FTS, fidelidade da árvore original nem recuperação de anexos no filesystem. Em falha, preservar banco/WAL/SHM original e testar reparação **somente numa cópia**.

## Primeira fila de gates que podem alterar adoção

1. **PRODUCT-018 (não executado):** snapshot transacional SQLite + arquivo bruto/anexos e manifesto SHA-256, restauração em diretório novo, reimportação e idempotência; confrontar restic/Borg/age conforme contrato.
2. **PRODUCT-019 (não executado):** schema v1 de entrada com `unknown` explícito e captura de anexos, sem data ou papéis inventados; Pydantic × jsonschema.
3. **PRODUCT-020 (não executado):** instalação limpa `uv tool install`/pipx + SQLite/FTS5 + TUI/GUI em Windows, Linux e Termux; documentar bloqueios de dependências.
4. **PRODUCT-021 (não executado):** fixture de vazamento sintético para Gitleaks/detect-secrets; reportar apenas metadados, sem exportar prompts.
5. **PRODUCT-022 (não executado):** autorizar leitura por recurso (root/grupo/usuário), falhar fechado e explicar permissão em cenários humanos; Casbin × Cedar.
6. **PRODUCT-023 (não executado):** revisão humana de relações inferidas com editor independente, `candidate`→`accepted/rejected`, prova de origem e reversão.

Os testes de terceiros não devem instalar componentes em produção sem gates de licença e controle sobre dados.

## Fontes primárias importantes

- Captura: [ACE](https://github.com/Covai-Labs/ace), [Microsoft MarkItDown](https://github.com/microsoft/markitdown), [Docling](https://github.com/docling-project/docling).
- Integridade: [SQLite recover](https://www.sqlite.org/recovery.html), [SQLite Backup API](https://www.sqlite.org/backup.html), [Litestream](https://litestream.io/how-it-works/).
- Backup: [restic](https://github.com/restic/restic), [age](https://github.com/FiloSottile/age), [rclone](https://github.com/rclone/rclone).
- Proteção: [SQLCipher](https://github.com/sqlcipher/sqlcipher), [Microsoft Presidio](https://microsoft.github.io/presidio/), [OPA](https://github.com/open-policy-agent/opa), [Cedar](https://github.com/cedar-policy/cedar), [OpenFGA](https://openfga.dev/), [SpiceDB](https://authzed.com/docs).
- Integração: [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk), [A2A Python SDK](https://github.com/a2aproject/a2a-python), [AG-UI](https://ag-ui.ai/en/technologies/ag-ui).
- Distribuição: [uv](https://docs.astral.sh/uv/), [PyInstaller](https://github.com/pyinstaller/pyinstaller), [BeeWare Briefcase](https://briefcase.beeware.org/en/stable/).
- Operação/CI: [OpenTelemetry Python](https://github.com/open-telemetry/opentelemetry-python), [OpenRefine](https://github.com/OpenRefine/OpenRefine), [ir-measures](https://github.com/terrierteam/ir_measures), [ranx](https://github.com/AmenRa/ranx), [BEIR](https://github.com/beir-cellar/beir).

## Entrega e governança

- Fonte da pesquisa: `product_lab/fronts.json`, versão estável.
- Algoritmo de comparação: `product_lab/rank.py`, com deduplicação cruzada.
- Interfaces: `/product` (painel) via porta JSON; `/` permanece painel UX.
- Tests: `_dev/tests/product/teste16.sh`, `teste17.sh` e seus `*.py`.
- CI: `.github/workflows/product-fronts.yml` mais gate compartilhado UX, sem GitHub token obrigatório.
- No merge solicitado ao par até aprovação de todos os gates e ausência de conflitos na HEAD; não alterar `src/ricoeur/` nem versões da Fase 2.

**Status desta entrega:** inventário/ranking e médico estrutural read-only **implementados**, bibliotecas de terceiros **pesquisadas** e testes de integração previstos em gates próprios; produto completo não homologado.
