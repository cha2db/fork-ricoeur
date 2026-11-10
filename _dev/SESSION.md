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
\n## Atualização — Teste 3\n- Evidência visual Android: PASS; quatro importações no mesmo banco, 8 conversas e 40 mensagens estáveis, novas = 8/0/0/0.\n- Após esse resultado, importador alterado para persistir mensagens vazias e árvore completa em chatgpt_nodes.\n- Teste 3 atualizado para novo comportamento esperado (48 mensagens); exige revalidação.\n- Teste 4 criado para verificar 48 mensagens, 8 vazias, 57 nós e ramo alternativo, inclusive reimportação.\n- Anexos ainda não resolvidos; nenhum PASS de fidelidade integral.\n