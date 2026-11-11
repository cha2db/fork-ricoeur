# UX-013 — Consolidação de candidatos, equivalência de core e merge

## 1. Baseline do par (não tocar)

Ricoeur `src/ricoeur/db.py` usa SQLite, `conversations.id TEXT`, `messages.id TEXT`, `messages.conv_id`, `messages.content`, `messages.timestamp`, e `messages_fts` FTS5 com triggers. `src/ricoeur/retrieval.py` fornece `search_messages` e `get_message_context` por mensagem. Esse é o **único core** da integração UX.

## 2. Evidência real de comparação de cores

- **CentralChat** `https://github.com/daveonkels/centralchat/blob/main/backend/app/database.py`: também SQLite/FTS5 e IDs TEXT; mas usa `messages.conversation_id`, `messages.created_at`, `search_fts`, campos de ramificação `parent_id` e schema de importação específico. **Não é core idêntico**, mesmo com stack praticamente igual.
- **LLM Chats Archive** `https://github.com/nuxdie/llm-chats-archive/blob/main/backend/app/db.py`: SQLite/FTS5/FastAPI, mas IDs INTEGER internos, `provider_conversation_id`, conteúdo normalizado em `text/content_json` e sequências. **Não é core idêntico**. A GUI React de leitura e anexos é material de reaproveitamento, não autorização para importar schema.
- **Kept** `https://github.com/egroup-labs/kept`: arquivo Markdown como fonte de verdade, FTS5 de recuperação e CozoDB para grafo; difere do armazenamento canônico Ricoeur.
- **LLM Chat Vault** `https://github.com/shuruili77/llm-chat-vault`: SQLite+FTS5, mas grafo DAG e resolução de ramificações próprios; equivalência de esquema não demonstrada.
- **ThreadShelf** `https://github.com/ChrystianSchutz/ThreadShelf`: LanceDB e pipeline de embeddings; diferencial forte de CLI+HTTP+MCP sobre mesmo índice, porém core diferente.

**Conclusão:** sem autorização para trocar core; máxima reutilização do contrato Ricoeur e integração apenas de apresentação/adapters. Os 46 candidatos restantes têm análises com status explícito no manifesto `ux_lab/candidates.json`; não confundir stack semelhante com contrato idêntico.

## 3. Ranking preliminar por família (peso core=40, GUI=30, adapter=20, licença=10)

| Tipo | Primeiro(s) a confrontar | O que pode ser adotado | Estado |
|---|---|---|---|
| Core e TUI | Ricoeur + Textual | Já existentes, manter | **ADOTADO NA BASE** |
| Web GUI e leitura | CentralChat (80), LLM Chats Archive (78) | UX de duas colunas, destaques, busca e jump | **PESQUISADO; UI própria mínima implementada** |
| Grafo exploratório | Cytoscape.js (96), vis-network (94) | Layout de redes por adapter de visualização | **SVG funcional; vis-network apenas opt-in CDN** |
| Editor visual tipo n8n | Vue Flow (96) | Edição de nós e relações | **NÃO IMPLEMENTADO; sem requisito de escrita** |
| Grafo grande | Sigma.js (86), G6 (86) | WebGL/layout de alto volume | **NÃO IMPLEMENTADO; sem gate de escala** |
| Árvore de mensagens/ramificações | ContextFlow (68), Threadline (pontuação dinâmica) | Branch-aware graph, timeline e salto à origem | **PESQUISADO; origem e ordem linear implementadas** |
| Busca tolerante a erro | ChatSearch (68) | Busca substring/fuzzy e prévia | **PESQUISADO; não substituir FTS5** |
| Busca semântica e agentes | ThreadShelf (68), Agent History (pontuação dinâmica) | Busca multidriver, referências persistentes, CLI/MCP | **PESQUISADO; core Ricoeur já tem caminhos próprios** |
| Comercial/proprietário | Threadback, Stowlet | Padrões de UX sem copiar código | **REFERÊNCIA SOMENTE** |

Pontuações são avaliações provisórias por compatibilidade e não benchmarks. O ranking canônico, inclusive por modo de busca e apresentação, é recalculado por `python ux_lab/rank_candidates.py`; nenhum dos candidatos novos recebeu `tested=true`.

## 4. Entrega implementada

- `ux_lab/ux.py`: HTTP localhost e CLI JSON, banco somente leitura, busca delegada à `ricoeur.retrieval.search_messages`, lista, transcrição com ID e anterior/próxima, contexto por mensagem.
- `ux_lab/index.html`: lista, filtro de plataforma, pesquisa literal/expressão FTS5, painel de mensagem, jump exato, grafo de evidência, SVG offline e visualizador experimental vis-network com carregamento externo **manual**.
- `ux_lab/retrieval_port.py`: adapter independente para o contrato já existente.
- `ux_lab/candidates.json`, `rank_candidates.py`: 46 candidatos e classificação reproduzível.
- Scripts `_dev/tests/ux/teste8.sh` até `teste12.sh`; relatórios na única categoria `_dev/results/ux/`.
- `.github/workflows/ux-lab.yml`: gates sintéticos Python e HTTP.

## 5. Merge pelo par — critérios

1. UX-008..012 PASS em GitHub Actions no PR #1 (e novamente se o head mudar).
2. GitHub deve informar PR `mergeable=true` contra `main` atual; foi **observado true** na verificação inicial, mas o par está atualizando `main`.
3. Validar que novos commits do par não mudam `ricoeur.retrieval.search_messages` ou o schema sem adaptar testes.
4. O **par realiza o merge**; esta frente não fará merge automaticamente.
5. **Somente depois** solicitar o teste humano no tablet. Não afirmar que o navegador/vis-network foi validado em dispositivo real.

## 6. Limites e próximos confrontos

- Nenhum aplicativo completo de terceiro foi implantado sobre o banco Ricoeur; apenas consulta a arquivos-fonte e adoção dos componentes já existentes no core.
- Não há grafo semântico ou DAG editável até existir relação tipada, identidade de ramo e `evidence_refs` no contrato de dados.
- Frontend JavaScript não tem teste automatizado de navegador (Playwright), apenas contrato HTTP e presença dos elementos de integração. Esse é gate futuro de produção, não bloqueio do laboratório.
- SVG local não expõe dados a CDN. Opt-in vis-network carrega código de terceiro; testar com corpus sintético, nunca com conversas pessoais reais.

Decisão técnica: entregar como **laboratório UX de read-only e ranking de adoção**, preservando completamente a evolução de importação/busca do par.

## Adendo — UX-014

Inventário expandido para **46** candidatos, agora incluindo taxonomias, cognição, tesauros, mapas conceituais, co-word, topic evolution e séries temporais. Ver documento `UX-014-COGNITIVE-KNOWLEDGE-MAPS-PRIOR-ART.md`. Implementada porta somente leitura `ux_lab/knowledge_port.py`, dashboard `/knowledge`, normalização por mil, drill-down e vocabulário opcional; testados sinteticamente pelo `teste14.sh`. Não há adoção de WordNet/ConceptNet ou inferência de cognição efetiva.
