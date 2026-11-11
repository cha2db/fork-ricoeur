# Cha2db — Handoff Fase 2 → Fase 3 UX (R13)

**Status:** especificação de interfaces proposta, **NÃO API já implementada**. Este arquivo comunica ao par da Fase 3 o que o núcleo poderá oferecer sem decidir frameworks, componentes ou layout da interface.

**Mandatos isolados:** Fase 2 continua na branch `main`, arquivos `_dev/phase2_*`, relatórios e `ci-results`. A Fase 3 constrói UX em sua própria branch (observada no GH Actions: `feat/ux-cli-gui-p1-0003`), sem depender de CTK/Orama/Tantivy. Esta entrega não toca arquivos do parceiro.

## Estado técnico que a UX pode assumir hoje

- Ricoeur/SQLite FTS5 é o baseline de consulta, com wrappers REST/MCP em testes anteriores.
- `CTK` passou como **comparador de importação** de árvores, preservando duas alternativas de resposta e seus IDs, com SQLite+JSON nativo no teste. **Não está incorporado** no Cha2db: não chamar sua API diretamente da UI.
- `Reweave` e `Chat Chronicle` perderam ramos na normalização do fixture; jamais assumir que todos os adaptadores preservam a história integral.
- Relações `references`, `refines`, `contradicts`, `supersedes` dependem de evidência; similaridade calculada não equivale a fato aprovado.
- Vetores e semântica são opcionais, com substituição futura e degradação graciosa para busca textual.

## Portas de intenção (propostas)

As interfaces abaixo são *funções conceituais*, não URLs a serem tratadas como rotas reais:

| Porta | Entrada proposta | Saída proposta | Estado de implementação |
|---|---|---|---|
| `SearchPort.search` | texto, filtros de origem, data, limite, cursor | hits com `message_id`, `conversation_id`, score e proveniência | FTS5 real; contrato tipado proposto |
| `ConversationPort.getTree` | `conversation_id` | lista de nós, `parent_id`, `children`, branch atual e alternativos | somente fixture CTK validada, não integrado |
| `ContextPort.getContext` | `message_id`, janela e modo | mensagens anteriores/posteriores com proveniência e permissões | núcleo existente parcialmente testado |
| `RelationPort.find` | `source_ref`, tipos, status | relações com evidências, revisão e estado | RDFLib só passou em serialização de relação sintética |
| `RepairPort.preview` | conjunto de IDs, estratégia e escopo | plano/efeito esperado sem alterar dados | NÃO IMPLEMENTADO |
| `RepairPort.commit` | plano previamente aprovado e autorização | recibo reversível, justificativa, hashes | NÃO IMPLEMENTADO |
| `MemoryPort.list` | escopo temporal, origem e revisão | memórias e decisões aprovadas e sugestões pendentes | NÃO IMPLEMENTADO |

## Estrutura mínima proposta para mocks e visualização

```json
{
  "query": {
    "text": "regressão guiada",
    "filters": {"providers": ["chatgpt"], "conversation_ids": []},
    "limit": 20,
    "cursor": null
  },
  "hits": [
    {
      "message_id": "source-message-42",
      "conversation_id": "source-conversation-17",
      "provider": "chatgpt",
      "node_id": "node-42",
      "parent_id": "node-41",
      "branch_id": "branch-2",
      "excerpt": "trecho original com origem",
      "source_ref": "provider-export://fixture/17/42",
      "rank_score": 0.83,
      "ranker": "fts5",
      "evidence_status": "source",
      "metadata": {"timestamp": "2026-11-10T10:00:00Z"}
    }
  ],
  "next_cursor": null,
  "warning": null
}
```

**JSON acima é mock, não uma resposta real:** valores exemplificativos e não autorizam inferir `branch_id` ou `rank_score` de um backend que não exponha esses atributos. Se ausentes, usar `null` e manter o dado original intacto.

## Critérios de aceite para a UX

1. Exibir vários chats coexistentes, seus IDs, fornecedor e mensagens sem misturá-los.
2. Exibir a árvore com ramos alternativos e permitir trocar de caminho sem apagar os outros.
3. Mostrar fonte/evidência em cada resultado e relação; nunca confundir candidato semântico com decisão humana aprovada.
4. Diferenciar `search`, `related`, `same_topic`, `contradicts`, `supersedes`: são ações distintas, não sinônimos visuais.
5. Repair apenas em **prévia** até existir commit reversível, auditoria e autorização.
6. Interface trabalhar via adapter REST/MCP/CLI quando disponível, com fallback para mocks determinísticos em teste; jamais depender do motor selecionado em Fase 2.
7. Os mesmos scripts devem testar jornadas no GH sem interação manual; Android/Termux só nos limites do CI.

## Ordem atual e ponto de sincronização

A Fase 2 mantém ranking e confrontos em:
- [Ranking atualizado e todos os 143](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/ranking/latest.md)
- [Matriz auditável em JSON](https://github.com/cha2db/fork-ricoeur/blob/ci-results/ci-output/phase2/ranking/latest.json)
- [Ranking policy R13](PHASE2_RANKING_POLICY_R13.md)

O parceiro da Fase 3 só precisa definir seus adapters em torno dessas intenções, respeitando que **nenhuma adoção de produto novo no core foi homologada**. Trocar a biblioteca de pesquisa na Fase 2 não deve obrigar reescrever a UX.
