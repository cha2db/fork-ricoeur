# UX-015 — Painel central, navegação fixa, tipos de GUI e créditos

Data: 2026-11-10. Branch: `feat/ux-cli-gui-p1-0003`. PR #1 para revisão/merge **pelo par**. Estado: laboratório implementado, sujeito a CI e teste manual Android.

## Decisão e topologia

O usuário determinou painel único com **navegação fixa**, categorias de UX, indicação explícita do candidato já implantado em cada tipo e referências no footer, com logotipos e atribuição quando houver fonte oficial.

- `/`: painel central, oito categorias com implantação real, candidatos e ranking preliminar por categoria.
- `/chats`: leitor de transcrições, busca existente FTS5/Click/JSON, grafo de evidências.
- `/knowledge`: incidência temporal, drilldown para IDs de mensagens, tags e subconjunto SKOS.
- `/nav.js`: driver de navegação compartilhada, barra lateral fixa no desktop e faixa superior fixa/visível no tablet.
- `/api?action=dashboard`: contrato JSON gerado de `ux_lab/dashboard_catalog.json` (classificações) + `ux_lab/candidates.json` (46 candidatos e URLs), **sem uma segunda fonte de ranking**.
- `_dev/tests/ux/teste15.sh`: testes de categorias, créditos, links, rotas, navegação fixa e preservação do SQLite. Registros locais em `_dev/results/ux/`.

## Critério para chamar de implantado

- `adopted_core`: **somente** Ricoeur (SQLite/FTS5 + Click) e Textual, já presentes no núcleo. Mantidos, não recriados.
- `implemented_subset`: SKOS-like JSON para relações tipadas e rótulos alternativos, **não** um interpretador RDF/SKOS completo.
- `experimental_opt_in`: vis-network, Apache ECharts e wordcloud2.js. Há carregamento opcional via CDN, mas não instalação/homologação de navegador ou uso em produção.
- `researched_only`: demais bibliotecas, aplicações e estudos. Sua existência upstream não significa integração à base do Cha2db.

As **categorias** podem ser `implemented`, `partial` ou `research`. A presença de candidatos futuros **não altera** o estado da categoria. Cada uma possui `adopted` e `implementation`, separados da lista de candidatos estudados.

## Licenças, créditos e logos

O rodapé lista **todos os 46 candidatos** com URL, família e estado de licença a verificar. Logos são carregados **somente mediante ação explícita** no botão, para não expor requisições externas durante o uso local de conversas privadas.

Logos identificados na documentação upstream:

- **Apache ECharts**: imagem oficial `asset/logo.png` referenciada no README do próprio projeto, fonte: https://github.com/apache/echarts/blob/master/asset/logo.png. Titular: Apache Software Foundation; projeto Apache-2.0. Imagem usada apenas para identificar e creditar o projeto.
- **Textual**: imagem `textual-splash` incluída no README oficial do repositório, fonte: https://github.com/Textualize/textual. Titular: Textualize; marca pertence aos respectivos titulares. Identificar como imagem de identidade, não assumir que é um símbolo vetorial oficialmente licenciado.

Não criar marcas semelhantes ou copiar logotipos sem conferir origem. Quando não há logo verificável, exibir o nome do projeto e o link — nunca inventar representação visual. External logos do not load by default. URL de imagem com `referrerPolicy=no-referrer`; fallback textual offline.

## Como testar em qualquer base Ricoeur (após merge)

```sh
python ux_lab/ux.py --db /caminho/real/ricoeur.db serve --port 8765
# Abrir NO MESMO DISPOSITIVO: http://127.0.0.1:8765/
bash _dev/tests/ux/teste15.sh
```

A porta HTTP está vinculada a 127.0.0.1 e não exige autenticação; não publicar na rede local nem internet. Para acesso remoto ao tablet, apenas túnel autenticado. Não iniciar logs com conversas privadas.

## Gates autônomos

1. O catálogo precisa ter 8 categorias, **46 IDs únicos** e 46 referências, sem órfãos ou duplicados.
2. Só Ricoeur/Textual podem ostentar adoção no núcleo. Outras bibliotecas mantêm indicação experimental ou pesquisada.
3. Navegação fixa e URLs para `/`, `/chats`, `/knowledge` precisam responder por HTTP, sem scripts externos em carregamento padrão.
4. Rodapé precisa expor link oficial e licença/status por candidato, e logos devem exigir ação explícita.
5. API JSON `dashboard` e CLI precisam devolver o mesmo catálogo; banco SQLite deve permanecer bit a bit igual.
6. Executar as rodadas UX-008/009/010/011/012/014/015 e os gates compartilhados do par antes do merge. Se GitHub tiver conflitos, parar e comunicar em vez de mesclar automaticamente.

## Fonte de verdade e oportunidades seguintes

- Componentes do núcleo e inventário: `src/ricoeur/`, `ux_lab/candidates.json`.
- Classificação por experiência: `ux_lab/dashboard_catalog.json`, com 8 famílias e ponteiros para os 46 IDs.
- GUI sem dependências externas obrigatórias: `dashboard.html`, `nav.js`, `index.html`, `knowledge.html`.
- Próximas adições de valor **não implementadas**: miniaturas reais do piloto por categoria, layout de árvore de ramificações, perfis e critérios A/B mensurados em tablet, bundling local das visualizações opcionais e importadores para OpenWordnet/ConceptNet.

Nenhuma mudança foi feita em esquema SQLite, indexação ou no motor de busca do par.
