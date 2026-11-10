# Sessão — Cha2db / fork-ricoeur

Data: 2026-11-10
Repositório: cha2db/fork-ricoeur
Papel: laboratório de prior art e evolução incremental do importador ChatGPT.
Origem: decisões humanas desta sessão. Não representa execução formal validada pelo InitProj.

## Objetivo
Aproveitar Ricoeur como base experimental para o Cha2db, com entrada fiel,
contratos/adapters, importação incremental e busca por mensagens.

## Evidências observadas no Android
- Busca por mensagem e correção de termos com hífen: PASS visual.
- 1.000 conversas / 99.000 mensagens: PASS, 229,7 MB.
- 2.000 conversas / 198.000 mensagens: PASS, 459,5 MB.
- 4.000 conversas / 396.000 mensagens: processo caiu com carga integral.
- Mesma carga após streaming: PASS, 918,9 MB, 92,195 s de importação.
- ZIP sintético multipartes: 8 conversas, 40 mensagens: PASS do importador atual.
- Barra de percentual: PASS visual.
- Reimportação dentro de uma execução: PASS; cada execução anterior usava DB novo.

## Lacunas abertas
- 8 mensagens vazias descartadas no ZIP sintético.
- Ramificação alternativa não preservada.
- Anexos no ZIP não importados nem vinculados.
- Ainda não há auditoria integral do material de origem nem pico de RAM medido.
- A exportação real de conta e seus formatos precisam de inspeção local segura.
- Importador ZIP com múltiplos JSONs: validado apenas com fixture sintética.

## Decisões
1. Input-first; fidelidade antes de novos recursos de interface.
2. Reutilizar componentes existentes e prior art com licença compatível.
3. Testes incrementais, scripts curtos e relatórios versionados.
4. Não publicar backups reais ou dados privados no GitHub.
5. Separar PASS de idempotência de PASS de fidelidade.

## Próxima entrega
Teste 3: quatro importações sequenciais no MESMO banco SQLite persistente
durante a execução, com evidência de ausência de duplicações.
Depois: preservação de mensagens vazias, árvore completa e anexos.

## Rastreabilidade
- Código: _dev/teste3.py
- Execução Android: bash _dev/teste3.sh
- Evidência local: _dev/results/teste3.json
- Status: publicado; execução pendente no Android.
\n## Atualização — Teste 3\n- Evidência visual Android: PASS; quatro importações no mesmo banco, 8 conversas e 40 mensagens estáveis, novas = 8/0/0/0.\n- Após esse resultado, importador alterado para persistir mensagens vazias e árvore completa em chatgpt_nodes.\n- Teste 3 atualizado para novo comportamento esperado (48 mensagens); exige revalidação.\n- Teste 4 criado para verificar 48 mensagens, 8 vazias, 57 nós e ramo alternativo, inclusive reimportação.\n- Anexos ainda não resolvidos; nenhum PASS de fidelidade integral.\n\n## Atualização — decisão de adoção e Teste 5\n- Teste 4: PASS visual Android: 8 conversas, 48 mensagens (8 vazias), 57 nós, 1 ramo alternativo, reimportação sem duplicação.\n- Decisão humana: priorizar testes que possam alterar adoção; evitar novos testes de fidelidade e carga sem impacto decisório.\n- Veredicto provisório: SQLite, FTS5 e importação incremental são candidatos de adoção; contratos por mensagem, navegação e MCP ainda em avaliação.\n- Teste 5: diagnóstico funcional de busca cruzada, granularidade por mensagem, IDs/contexto e evidência preliminar de MCP.\n- Gate: distinguir API pública de acesso SQL direto; ausência de servidor MCP não reprova núcleo se adapter for barato.\n
## Teste 5 — evidência Android (10/11/2026)
- Diagnóstico executado: 2 conversas e 4 mensagens coincidentes.
- PASS: busca cruzada, snippets, consulta SQL por mensagem e contexto estruturado.
- Lacunas da API de busca: agrupa por conversa, não expõe todos os hits nem IDs de mensagem.
- MCP: nenhum arquivo de servidor identificado pelo teste heurístico; integração real ainda não testada.
- Decisão provisória: manter SQLite/FTS5 e busca como candidatos de adoção; avaliar adapter MCP fino, sem substituir motor.
- Próximo gate: teste 6, contrato de busca por mensagem com IDs, vizinhança e múltiplas ocorrências.

## Teste 6 — composição mínima / Frankenstein (10/11/2026)
- Teste 5: diagnóstico Android validado; FTS5 recupera 4 mensagens em 2 conversas, mas API pública agrupa resultados e omite IDs.
- Implementado src/ricoeur/retrieval.py: contrato read-only search_messages e get_message_context; resultados por mensagem, IDs, provedor, vizinhos, filtro, JSON.
- Adapter MCP opcional src/ricoeur/mcp_adapter.py usa SDK oficial MIT v2, Python >=3.11; NÃO testado no Android Python 3.10, não instalar no Termux atual.
- Prior art pesquisada: modelcontextprotocol/python-sdk (MIT, MCP); sqlite-utils (Apache-2.0, alternativa para utilitários, não necessário substituir SQLite/FTS5); FastMCP standalone (Apache-2.0, alternativa).
- Teste 6 publicado, execução Android pendente. Gate: não confundir contrato local com conformidade MCP.
- Objetivo: composição de componentes por portas, sem reimplementação de SQLite/FTS5/MCP.

## Teste 6 — evidência Android
- PASS visual: 3 ocorrências por mensagem, 2 provedores, IDs estáveis, vizinhança, filtro por provedor e JSON estruturado.
- MCP ainda não testado; corrigida importação do SDK para mcp.server.fastmcp.FastMCP (antes MCPServer incorreto).
- Veredicto: recuperar por mensagem usando SQLite/FTS5; não reimplementar motor. Próximo gate: cliente MCP real.

## Teste 7 — MCP real
- Cliente e servidor reais sobre stdio, usando SDK oficial MCP v1 com API FastMCP.
- Usa uv com Python 3.12 isolado para não modificar o ambiente Python 3.10 do Termux.
- Avalia descoberta de tools, busca por mensagens, IDs e contexto em chamadas MCP.
- Estado: scripts publicados, não executados no Android. O uv pode não disponibilizar Python 3.12 no Termux; nesse caso registrar bloqueio de plataforma e usar host Linux compatível, sem confundir com falha de arquitetura.
- SDK v2 possui API distinta; migração de adapter deve ser feita separadamente.

## Teste 7 — correção Termux (10/11/2026)
- Execução Android bloqueada ANTES do MCP: uv não encontrou Python 3.12.
- Script alterado para reutilizar Python existente (.venv ou python), instalar SDK MCP 1.x (<1.10) se necessário e executar cliente/servidor reais via stdio.
- Evita exigir uv e Python 3.12. Instalação do SDK em Termux ainda pode falhar por dependências nativas; não validado até retorno do tablet.
- Não confundir falha de instalação com falha do protocolo.
