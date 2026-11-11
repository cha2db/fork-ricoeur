# UX-014 — Organização do conhecimento: mapa comparativo, prior art e provas

Status: implementação de LAB sobre o mesmo SQLite/FTS5 do Ricoeur. Não altera `src/ricoeur/db.py`, `src/ricoeur/retrieval.py` nem algoritmos do par. Investigação não é homologação de aplicação externa.

## 1. Taxonomia para não confundir fenômenos

| Tipo de dado/relação | Significado defensável | Nunca afirmar automaticamente |
|---|---|---|
| `literal_match` / `fts5_match` | Texto indexado pela consulta, origem = ID da mensagem | frequência de palavra dentro do texto ou significado real |
| `cooccurs_in_message` | Termos aparecem em mesma mensagem | sinonímia, causa ou concordância |
| `synset_member` | Mesmo sentido lexical conforme WordNet, sob licença e versão | identidade de todos os sentidos de uma palavra |
| `skos:altLabel` | Variante lexical aprovada para um conceito | equivalência universal fora do contexto |
| `skos:broader` / `narrower` | Relação hierárquica tipada validada | relacionamento derivado de mera similaridade |
| `skos:related` | Associação não hierárquica aprovada | direção causal ou dependência |
| `embedding_similarity` | Score de um vetor/modelo e versão específicos | equivalência factual ou semântica garantida |
| `prov:wasDerivedFrom` | Informação derivada de evidência identificada | origem omitida |
| `human_asserted` | Ligação deliberadamente cadastrada e rastreável | inferência automática |

A "cognição" que o produto pode medir é **organização observável dos registros**, não estado cognitivo cerebral de seu usuário.

## 2. Ranking por abordagem e estado real

Pontuações são hipóteses com pesos core 40%, GUI 30%, adapter 20%, licença 10%. Ordenações só fazem sentido **dentro da mesma família**. O JSON versionado gera classificações completas automaticamente, por categoria, forma de busca e apresentação.

| Família | Adoção/primeira prova | Pontuação preliminar | Estado verificável |
|---|---|---:|---|
| Histograma e timeline | Apache ECharts | 100 | Porta FTS5 + barras locais **implementadas**; ECharts opt-in via CDN, não testado no browser |
| Gráficos declarativos cruzados | Vega-Lite | 96 | Pesquisado, não implantado |
| Tag cloud | wordcloud2.js | 94 | Frequência por mensagem + HTML local **implementados**; wordcloud2 opcional |
| Tesauro tipado | W3C SKOS | 94 | **Subset implementado** em lexicon JSON externo; RDF ainda não |
| Proveniência verificável | W3C PROV-O | 88 | IDs de mensagem preservados; serialização PROV ainda não |
| Recursos em português | OpenWordnet-PT | 82 | Pesquisado; dados não importados (CC BY 4.0, sem sentidos confirmados) |
| Redes de senso comum | ConceptNet 5 | 88 | Pesquisado; API não integrada, licença CC BY-SA 4.0 |
| Corpus multilíngue | Open Multilingual Wordnet | n/a | Pesquisado; licenças por componente, falta driver |
| Co-word / mapas científicos | VOSviewer, Biblioshiny | ~78 | Pesquisados; algoritmos/GUI não executados |
| Topic evolution e embeddings | BERTopic | 76 | Pesquisado, ML opcional, avaliação humana obrigatória |
| Mapas proposicionais | IHMC CmapTools | n/a | Referência epistemológica, não incorporado |
| Intercâmbio de mapas | JSON Canvas | n/a | Estudado; exportador não implementado |
| Algoritmos de rede | NetworkX, Gephi | n/a | Estudados; sem grafo validado para medir |
| Extração de termos | YAKE, KeyBERT | n/a | Estudados; gate de custo, licenças, corpus e estabilidade |

O projeto **já usa** Textual + FTS5. Não reimplementar motor nem substituir core para conseguir visualizações.

## 3. Entrega real (UX-014)

**Contratos CLI/HTTP separados**, mesmos dados SQLite read-only:

- `timeline --query "integração contínua" --grain month`: eixo X período, Y número de **mensagens recuperadas pelo FTS5** e conversas distintas; inclui taxa normalizada por mil mensagens do período; suporte day/month/year. A duplicação de uma palavra na mesma mensagem conta **uma mensagem**, não duas menções.
- `period --query ... --period 2026-01`: clique/drill-down com IDs de mensagens, conversas, texto/role/timestamp; paginável, sem exportação de dados privados.
- `tagcloud --query ... --period 2026-01`: frequência **documental** de cada palavra entre as mensagens encontradas, amostra máxima de 2000, marca truncamento; não deduz sinonímia.
- `concept "CI pipeline" --lexicon ...`: consulta vocabulário externo explicitamente aceito; conceitos e relações tipadas com fonte, sem criar tabelas nem sinônimos automáticos.
- `/knowledge`: painel com barras locais e clique para leitura, gráfico de palavras e deep links exatos para `/?conv=ID&msg=ID`. ECharts/wordcloud2 **somente opt-in**, com alerta de execução de código de terceiro na mesma página.
- `ux_lab/lexicon.example.json`: **dados demonstrativos sintéticos**. `--expand` precisa ser ativado; sem isso a consulta permanece literal. Associação por SKOS não é incluída automaticamente na expansão de busca.

**Sem LLM obrigatória.** O projeto aceita futuros adapters para redes de termos externos (OpenWordnet, ConceptNet), embeddings e análise de tópicos, sem trocar armazenamento.

## 4. Fontes e evidências científicas

- CmapTools / Novak e Cañas — conceitos unidos por frases de ligação formam proposições: https://cmap.ihmc.us/docs/conceptmap.html
- SKOS W3C — descrições, rótulos, associações e hierarquia: https://www.w3.org/TR/skos-reference/
- PROV-O W3C — rastreabilidade e derivação: https://www.w3.org/TR/prov-o/
- SQLite FTS5 — MATCH/queries, BM25, funções auxiliares: https://www.sqlite.org/fts5.html
- ECharts — eventos, zoom e drill-down: https://echarts.apache.org/en/index.html
- wordcloud2.js — Wordle/Canvas com licença MIT: https://github.com/timdream/wordcloud2.js
- VOSviewer — coocorrência de termos e mapas bibliométricos: https://www.vosviewer.com/
- Biblioshiny — co-word, thematic mapping e evolução: https://www.bibliometrix.org/biblioshiny/
- BERTopic — modelos de temas dinâmicos: https://maartengr.github.io/BERTopic/getting_started/visualization/visualize_topics.html
- OpenWordnet-PT — léxico aberto de português (CC BY 4.0): https://github.com/own-pt/openwordnet-pt
- OMW — redes lexicais multilíngues: https://omwn.org/
- ConceptNet — relações lexicalmente tipadas; API e licença: https://github.com/commonsense/conceptnet5/wiki/relations ; https://conceptnet.io/
- OpenAlex — temas científicos e hierarquia: https://help.openalex.org/data/topics/
- Vega-Lite — seleção/brushing e visualizações declarativas: https://vega.github.io/vega-lite/docs/selection.html
- JSON Canvas / Obsidian — mapa portável: https://jsoncanvas.org/
- Collins & Loftus (1975), *A Spreading-Activation Theory of Semantic Processing*: https://eric.ed.gov/?id=EJ135579
- Constantinescu, O'Reilly & Behrens (2016), *Organizing conceptual knowledge in humans with a gridlike code*: https://pubmed.ncbi.nlm.nih.gov/27313047/
- Epstein et al. (2017), *The cognitive map in humans: spatial navigation and beyond*: https://www.nature.com/articles/nn.4656
- Callon et al. (1991) — co-word e redes: https://pascal-francis.inist.fr/vibad/index.php?action=getRecordDetail&idt=19846773
- *Evaluating Dynamic Topic Models* (ACL 2024): https://aclanthology.org/2024.acl-long.11/

**Limite epistemológico:** resultados sobre representação neural de conceitos em humanos não provam que barras de frequência, embeddings ou mapas de conversas representam processos neurais de usuários. São inspirações para navegação e hipóteses testáveis, não validação clínica ou cognitiva.

## 5. Gates para o próximo conjunto

1. **UX-014:** executar `bash _dev/tests/ux/teste14.sh`; logs e JSON em `_dev/results/ux/`; mesma base sintética para CLI/HTTP, integridade de IDs, contagem, limites, expansão opcional e read-only.
2. **UX-015 (não implementado):** avaliar OpenWordnet-PT vs ConceptNet no mesmo conjunto de frases polissêmicas PT/EN; medir precisão/recall, distinguir SINÔNIMO de ASSOCIADO, mapear licenças por aresta.
3. **UX-016 (não implementado):** comparar ECharts/Vega-Lite sob 1k períodos e 10k cliques usando JS local *vendorizado*, sem CDN em produção; medir memória e acessibilidade tablet.
4. **UX-017 (não implementado):** co-word por janela temporal, separar coocorrência factual de relação validada, estudo de métricas NetworkX.
5. **UX-018 (não implementado):** análise de tópicos BERTopic opcional, necessidade de modelo/versionamento, auditoria humana, comparações contra FTS5.
6. **UX-019 (não implementado):** JSON Canvas / Cmap proposicional com relações tipadas, exporta/prov/retorno à origem.

## 6. Handoff / integração

GitHub PR #1 pertence à frente UX; **merge somente pelo par** quando os gates relevantes terminarem com PASS e `mergeable=true` contra HEAD corrente. `_dev/tests/ux/` e `_dev/results/ux/` continuam as únicas duas subpastas de categoria. Sem testes externos em dados privados.

**Correção de expectativa:** possuir botão experimental de carregamento de lib não é adoção em produção; testes sintéticos não são benchmark real em Android; referências científicas não são prova de capacidade do software.

## 7. Ajuste metodológico: crescimento do corpus

A variação da contagem bruta pode refletir apenas aumento de importações. A porta `timeline` também emite `all_messages` e `rate_per_1000_messages`, calculada no mesmo recorte temporal e filtro de plataforma. O painel permite alternar entre número absoluto e taxa, sem afirmar que uma diferença temporal constitui mudança cognitiva. Esta normalização tem teste automatizado UX-014.