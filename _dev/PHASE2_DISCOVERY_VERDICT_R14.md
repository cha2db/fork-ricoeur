# Cha2db · Fase 2 R14 — varredura por mecanismo, armazenamento e produto emergente

**Execução:** pesquisa e verificação de fontes no GitHub Actions, novembro de 2026. **Responsabilidade:** Fase 2 somente; branch da UX / Fase 3 preservada, sem modificações.

## Cobertura e estado verificável

- **207 candidatos no total**, preservando os **143 da R10** e acrescentando **64 candidatos distintos (C144–C207)**, com URL e ID próprios.
- Auditoria automática de fontes novas em GitHub: **62/64 repositórios GitHub verificados** e **2 referências externas de mercado**; **0 fontes GitHub sem verificação**. Metadata e README **não** equivalem a teste funcional.
- **24 PASS funcionais específicos de candidatos**: 22 herdados do conjunto R13 + 2 novos verificados na R14. Não são 24 homologações de produto completo, mas gates técnicos reproduzíveis. Os demais 62 novos continuam `NOT_TESTED`.
- **207/207 candidatos posicionados no ranking ampliado**; manter o ranking R13 de 143 como baseline histórico sem sobrescrever. O R14 usa 15 portas técnicas e 9 grupos novos de confrontos, somados aos 14 anteriores.
- **Não houve adoção ou migração do core**, que permanece SQLite FTS5/Ricoeur. **Não houve alteração da UX**.
- A lista não foi declarada “exaustiva da Internet”. O volume e a variedade de novos produtos confirmam que a descoberta de abordagens ainda não saturou.

**Artefatos autoritativos:**
[Inventário dos 64 novos, tipados por armazenamento e busca](PHASE2_MARKET_EXPANSION_R14.json) ·
[Ranking ampliado em Markdown](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/ranking/expanded-latest.md) ·
[Ranking ampliado em JSON com verificação de fonte e resultado](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/ranking/expanded-latest.json) ·
[Histórico do ranking R13 com os 143 originais](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/ranking/latest.md).

## Principais abordagens descobertas

| Tipo | Produtos-chave | Ponto distinto do armazenamento ou busca | Prioridade |
| --- | --- | --- | --- |
| Versões temporais imutáveis | [SirixDB](https://github.com/sirixdb/sirix), [TerminusDB](https://github.com/terminusdb/terminusdb), [Dolt](https://github.com/dolthub/dolt), [XTDB](https://github.com/xtdb/xtdb) | Bitemporalidade, branches, diff/merge, consultas as-of; comparar com SQLite + eventos, não substituir por marketing | **P0** |
| Grafo + texto + vetor em um núcleo | [HelixDB](https://github.com/HelixDB/helix-db), [LadybugDB](https://github.com/LadybugDB/ladybug), [Oxigraph](https://github.com/oxigraph/oxigraph) | Arestas, fatos versionados e busca no mesmo banco | **P0** |
| Índices híbridos embutidos em arquivo | [Infino](https://github.com/infino-ai/infino) | Rust/Python/Node: arquivos Parquet e busca BM25/vetor/SQL, manifesto e object storage opcional | **P0** |
| Vetores comprimidos | [turbovec](https://github.com/RyanCodrai/turbovec) | Quantização 2/4 bits, potencial de RAM/CPU/ARM menor, a ser medido contra sqlite-vec | **P0** |
| Biblioteca SQLite-like no browser | [PGlite](https://github.com/electric-sql/pglite) | Postgres em WASM, texto indexado com GIN, persistência offline via JS, sem servidor no modo Node | **P0** |
| Sincronização e dados locais com conflito | [RxDB](https://github.com/pubkey/rxdb), [Dexie](https://github.com/dexie/Dexie.js), [Evolu](https://github.com/evoluhq/evolu), [cr-sqlite](https://github.com/vlcn-io/cr-sqlite) | Metadados sincronizados com idempotência/CRDT; origem de chats deve permanecer imutável | **P1** |
| Memória portátil padronizada | [MacPaw Portable Memory](https://github.com/MacPaw/portable-memory), [PAM](https://github.com/portable-ai-memory/portable-ai-memory) | JSONL, checksums/manifesto, proveniência e schemas entre provedores | **P0** |
| Produtos de arquivo cross-provider | [ThreadShelf](https://github.com/ChrystianSchutz/ThreadShelf) | Arquivo híbrido local, CLI/MCP, prova de importação ainda ausente | **P0** |
| Memória temporal e conflitos | [Mnemos](https://github.com/Sohamp2809/mnemos), [Memoirs](https://github.com/misaelzapata/memoirs), [Hearth](https://github.com/reallyreallyryan/hearth), [Lossless Memory](https://github.com/aru-labs/lossless-memory) | Supersedência tipada, busca primeiro no tempo, tensões e aprovação humana | **P0** |
| Busca leve no navegador | [Moss](https://github.com/usemoss/moss) | Candidato distinto dos índices JS FlexSearch/MiniSearch/Orama, ainda sem teste de integração | **P0** |
| Auditoria criptográfica / eventos | [immudb](https://github.com/codenotary/immudb), [KurrentDB](https://github.com/kurrent-io/KurrentDB) | Log imutável e prova de não adulteração como complemento de provenance, não motor principal de busca | **P1/P2** |

**Fonte da alegação de capacidades:** descrições, repositórios e documentação dos autores. Todos os P0 sem relatório próprio no `ci-results` permanecem **candidatos identificados, não aprovados**.

## Testes funcionais realmente concluídos nesta R14

### C155 — PGlite: PASS técnico, sem browser

[Relatório CI e checks reproduzíveis](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/r14/pglite-latest.json)

PGlite passou **6/6 gates** em GitHub Actions Node.js com PostgreSQL WebAssembly armazenado em filesystem:
1. importação repetida sem duplicação;
2. consulta lexical `to_tsvector/plainto_tsquery` com índice GIN;
3. preservação das duas respostas alternativas com `parent_id`;
4. fechamento e reabertura do banco;
5. preservação de 1.000 IDs canônicos da amostra do corpus SQLite de 40 mil mensagens;
6. marcador exclusivo recuperado uma vez.

Carga adicional: fixture de 2 conversas e 5 mensagens ramificadas. Tempo observado de importação: **2,494 s**, armazenamento resultante: **41.623.731 bytes** no teste; **não comparar a métrica diretamente** com SQLite FTS5, pois banco, formatos, harness, ambiente e escopo diferem. **Ainda não testado no navegador/IndexedDB ou Android**. Decisão: **candidato de porta de persistência local do browser**, não substituto do backend por padrão.

### C191 — Portable Memory MacPaw: PASS de portabilidade, não de árvore

[Relatório CI e checks reproduzíveis](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/portable-memory-latest.json)

SDK oficial Python 0.3.0 MIT passou **13/13 gates** de conteúdo e formato: cinco mensagens, os dois conteúdos alternativos, IDs, metadados de origem, exportação `.mem` com JSONL/manifesto/checksums, validação, importação repetida sem duplicados, integridade e detecção de adulteração.

**Limitação material encontrada:** o adapter ChatGPT mantém ambos os episódios alternativos, mas **não preserva o `parent_id`/vínculo dos irmãos como estrutura recuperável**. Assim, não pode substituir a árvore importada pelo **CTK** em um contrato *lossless conversation tree*. A combinação a investigar é **CTK para árvores completas + Portable Memory para exportação auditável de memória**. Nunca confundir um episódio de memória com mensagem/ramo fiel ao original.

## Ranking de decisão — não é pódio de velocidade

- **Entrada:** CTK permanece líder testado; contrastar Polylogue/hstry e padrões portáteis. Portal de memórias não substitui entrada crua completa.
- **Core lexical:** SQLite FTS5 permanece baseline, Tantivy é primeiro desafiante interno. Infino ganha confronto de busca híbrida em Parquet.
- **Browser/Edge:** FlexSearch e MiniSearch ainda lideram os ensaios JS; PGlite abre a categoria de **persistência local PostgreSQL WASM**.
- **Vetores:** sqlite-vec referência testada; comparar turbovec em disco/RAM/recall e portar para ARM antes de adoção.
- **Relações:** RDFLib mantém a melhor prova de serialização com evidência, mas não prova conflitos semânticos. LadybugDB/HelixDB precisam de testes reais.
- **Histórico e versão:** nenhum backend bitemporal novo homologado; SirixDB/TerminusDB e um baseline SQLite+eventos precisam de confronto honesto.
- **Memória e repair:** nenhum motor aprovado; OpenSelf, Graphiti, Mnemos, Memoirs, Hearth e outros são prior art com hipóteses relevantes.

## Critério de seleção e próximos confrontos

1. Preservação **exata** do bruto, todos os ramos, anexos, autor, provedor, timestamps e IDs sem perda silenciosa; hash de origem, idempotência e rollback.
2. Latência p50/p95, memória, disco, custo de instalação e prova de reindexação incremental **na mesma base**.
3. Recuperação humana PT-BR/EN com consultas difíceis e negativos contraditórios; `ir-measures` para métricas.
4. Relações `supersedes`/`contradicts` apenas com evidência rastreável, candidato primeiro e aprovação humana.
5. Licença do pacote, serviços externos, modelos e possibilidade de distribuição local/Termux; não confundir licença OSS do código com dos pesos.
6. Desacoplamento da Fase 3 UX: interface consome contratos, não liga diretamente ao produto candidato.

**Manutenção:** `.github/workflows/phase2-r14-survey.yml` executa reauditoria às segundas/quintas e em mudanças relevantes; fontes são verificadas e rankings publicados em `ci-results`. Isso **não** executa automaticamente testes funcionais de todas as dependências novas. Pesquisa geral segue aberta; esgotamento depende de saturação real, não de contar nomes.

**Veredito R14:** há 64 abordagens adicionais, duas novas execuções técnicas com PASS de escopo explícito e nenhum motivo suficiente para substituir o core SQLite FTS5 por um único produto. Os melhores próximos experimentos são *CTK × formatos de interoperabilidade*, *FTS5 × Infino* e *grafo temporal × histórico de decisões*, além de *turbovec × sqlite-vec*.
