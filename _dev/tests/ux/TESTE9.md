# UX-009 — Adoção do core de busca existente

A implementação anterior em `ux_lab/ux.py` fazia busca literal via LIKE para um protótipo de interface. **Não é equivalente ao core de busca do par** e não deve ser homologada como busca avançada. Esta rodada implementa `ux_lab/retrieval_port.py`, um adaptador independente que chama diretamente `ricoeur.retrieval.search_messages` e `get_message_context`, com FTS5, IDs, filtros e contexto já implementados pelo par.

Teste autônomo: `bash _dev/tests/ux/teste9.sh`; usa SQLite sintético, 3 conversas e 4 mensagens; não grava na base real. Resultados em `_dev/results/ux/teste9.*`.

Com base existente: `python ux_lab/retrieval_port.py --db ~/.ricoeur/ricoeur.db search docker --platform chatgpt`; `python ux_lab/retrieval_port.py --db ~/.ricoeur/ricoeur.db context ID_MENSAGEM`.

**Gate de merge**: a GUI HTTP atual ainda usa a porta de protótipo LIKE, não esta porta FTS5. Não solicitar teste humano integrado nem merge até que GUI e CLI utilizem o mesmo adapter e os testes passem. Branch UX permanece isolada para o par integrar quando autorizado.
