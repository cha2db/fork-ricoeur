# UX Lab — portas isoladas sobre Ricoeur

**Versão ux.v2**. CLI + HTTP localhost + GUI usam o **mesmo** `ricoeur.retrieval.search_messages`/FTS5 já presente em `src/ricoeur/retrieval.py`, sem duplicar índice nem modificar o banco.

## Rodar na base existente (somente leitura)

```sh
python ux_lab/ux.py --db /caminho/para/ricoeur.db capabilities
python ux_lab/ux.py --db /caminho/para/ricoeur.db conversations --limit 30
python ux_lab/ux.py --db /caminho/para/ricoeur.db search --query docker --platform chatgpt
python ux_lab/ux.py --db /caminho/para/ricoeur.db search --query 'docker OR linux' --syntax fts5
python ux_lab/ux.py --db /caminho/para/ricoeur.db transcript ID_CONVERSA
python ux_lab/ux.py --db /caminho/para/ricoeur.db message ID_MENSAGEM
python ux_lab/ux.py --db /caminho/para/ricoeur.db graph --query docker
python ux_lab/ux.py --db /caminho/para/ricoeur.db serve --port 8765
```

A GUI fica em `http://127.0.0.1:8765` na **mesma máquina**. Não expor a LAN; o servidor de laboratório não possui autenticação. A porta SQL usa URI SQLite `mode=ro`; sem escrita/migração. A busca retorna **mensagens** com IDs e contexto; o grafo é estrela consulta → conversas e cada ligação traz os IDs exatos das mensagens recuperadas.

### Drivers visuais

- Padrão: SVG local sem dependências, compatível com Termux/offline.
- Opcional: botão explícito para carregar `vis-network@9.1.9` via CDN. Executa JavaScript externo no mesmo navegador que exibe conversas. **Não usar com dados privados**; é apenas demonstração com corpus sintético. A adoção offline/produção de vis-network depende de empacotamento local com pin de versão, licença e testes próprios.
- Cytoscape.js, Vue Flow, Sigma.js etc. **pesquisados**, ainda não instalados nem executados. Não há grafo semântico nem edição de relações.

## Testes e evidências

```sh
bash _dev/tests/ux/teste8.sh
bash _dev/tests/ux/teste9.sh
bash _dev/tests/ux/teste10.sh
bash _dev/tests/ux/teste11.sh
bash _dev/tests/ux/teste12.sh
```

Os relatórios locais ficam **somente** em `_dev/results/ux/`. A Action `.github/workflows/ux-lab.yml` executa todos os scripts em Python 3.11. Isso comprova contratos Python/HTTP/HTML, mas **não** testa a GUI em navegador real nem aplicações terceiras. A base sintética de testes não contém conversas privadas.

## Matriz de adoção

`python ux_lab/rank_candidates.py --output _dev/results/ux/ranking12.json`. São 27 candidatos e ranking **preliminar**, com seções por categoria, mecanismo de pesquisa e apresentação. Consultar `docs/ux/UX-013-ADOPTION-AND-MERGE-GATES.md`.

Branch `feat/ux-cli-gui-p1-0003`; PR #1 para `main`. Merge exclusivo do par após verificação dos gates e da compatibilidade com mudanças posteriores em `main`.
