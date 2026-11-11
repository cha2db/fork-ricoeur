# UX — testes por rodada

Cada rodada nova recebe somente um script `testeN.sh` nesta pasta. Não duplicar as pastas de categorias.

- `bash _dev/tests/ux/teste8.sh`: CLI JSON, leitura, filtros, anterior/próxima e grafo coocorrência, corpus sintético de 3 chats/6 mensagens.
- Evidências geradas **localmente** em `_dev/results/ux/teste8.log` e `teste8.json`. Não comitar dados de execução.
- Para testar no tablet Termux: `git switch feat/ux-cli-gui-p1-0003 && bash _dev/tests/ux/teste8.sh`.
- Para testar a GUI no próprio aparelho: `python ux_lab/ux.py --db CAMINHO_DO_DB serve --port 8765`, abrir `http://127.0.0.1:8765` no navegador do mesmo aparelho.
- Sem mudanças no core, no banco ou nos algoritmos do par. As portas de aplicação continuam em `ux_lab/`.
