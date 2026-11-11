# UX-002 — Varredura OSS: aplicações completas antes de bibliotecas

- Branch: `feat/ux-cli-gui-p1-0003`
- Escopo: apenas pesquisa e decisão de adoção da experiência; não tocar banco, importadores ou algoritmos do par
- Estado: **research/spec**, sem ADOPT aprovado; resultados de documentação pública não equivalem a testes locais
- Regra: preferir aplicação ou módulo já pronto → wrapper → componente → implementação residual

## Prioridade 1: aplicações diretamente relacionadas a histórico de chats

| Candidato | Recursos declarados | Adoção potencial | Lacunas a testar |
|---|---|---|---|
| Kept https://github.com/egroup-labs/kept | desktop, múltiplas IAs, busca FTS5, tópicos, projetos, grafo, MCP | ADOPT/WRAP candidato forte para GUI integral | licença e modularidade dos componentes, compatibilidade com CLI ricoeur, provenance |
| LLM Chat Vault https://github.com/shuruili77/llm-chat-vault | desktop/web, SQLite, DAG de branches, leitor, timeline, busca | REUSE_PART candidato para leitura de chats e ramificações | licença, isolamento dos componentes, fidelidade IDs |
| msgvault https://www.msgvault.io/ | arquivo de mensagens, interface browser/terminal, pesquisa e anexos | ADOPT/WRAP candidato para UX de arquivo e pesquisa | modelo de chats de IA e relações entre tópicos |
| Khoj https://docs.khoj.dev/features/chat/ | busca em notas/documentos e referências | REUSE_PART somente após avaliar acoplamento de LLM | não introduzir LLM obrigatória |
| Ricoeur (base) | Click CLI, Textual TUI, SQLite FTS5, busca híbrida | KEEP base; evitar reconstruir | UX de grafo e filtros visuais |

## Prioridade 2: bibliotecas gráficas prontas

| Biblioteca | Finalidade | Decisão preliminar |
|---|---|---|
| @xyflow/vue (Vue Flow 2.0) https://next.vueflow.dev/ | editor visual tipo n8n; nós customizáveis, arestas, zoom, minimapa | EVALUATE se a jornada requer editar relações |
| Cytoscape.js https://js.cytoscape.org/ | exploração de rede e análise de relações | EVALUATE para grafo de assuntos e conversas |
| Sigma.js https://www.sigmajs.org/ | renderização WebGL de grafos grandes | EVALUATE se Cytoscape falhar em escala |
| vis-network https://visjs.github.io/vis-network/ | grafo interativo simples com física | EVALUATE para prova de integração mínima |
| AntV G6 https://g6.antv.antgroup.com/ | grafos e diagramas interativos | EVALUATE se layouts e UX especializados justificarem |
| Graphology https://graphology.github.io/ | estruturas/algoritmos de grafos | NÃO duplicar backend; só usar se adaptador visual necessitar |

## Comparação que decide, não preferência estética

1. **Aplicação integral primeiro:** executar Kept e LLM Chat Vault com três conversas sintéticas, avaliar instalação, busca, leitura, grafo, abertura da origem e interoperabilidade. Registrar versão, licença, screenshots e testes reproduzíveis.
2. **Se aplicação não puder ser adotada:** extrair apenas componente isolável com licença compatível; sem copiar lógica de armazenamento ou algoritmos.
3. **Grafo de descoberta:** testar Cytoscape.js vs vis-network com exatamente o mesmo JSON `nodes/edges/evidence_refs`.
4. **Grafo editável:** testar @xyflow/vue só se o requisito de criação/edição de relações for real.
5. **Escala:** Sigma.js apenas se houver evidência de lentidão com L1/L2, sem benchmark redundante.

## Contrato de UX e rastreabilidade

- CLI é fonte única para consultas; GUI usa wrapper e não SQL próprio.
- Uma aresta deve ter `source_id`, `target_id`, `relation_type`, `evidence_refs`, `origin_refs`, `method`; se não houver prova, não exibir como fato.
- Clique no nó abre a conversa/mensagem original; clique na aresta mostra a justificativa; retorno conserva estado de busca e seleção.
- Interface de leitura e busca deve funcionar mesmo com grafo indisponível.
- Respeitar `unknown` e não fabricar papéis, identidade, timestamps ou relações.
- Licença, maturidade, manutenção, acessibilidade, bundle e testes de contrato precedem adoção.

## Gates

- `UX-APP-002` **pending**: avaliar Kept/LLM Chat Vault em execução antes de escolher componentes próprios. Owner: frente UX .0003.
- `UX-READ-002` **pending**: validar leitura fiel e ramificações contra 3 chats com IDs e origem. Owner: frente UX .0003.
- `UX-GRAPH-002` **pending**: comparar Cytoscape/vis-network; não desenhar relações inexistentes. Owner: frente UX .0003; contrato de relações do par.
- `UX-CLI-002` **pending**: GUI equivalente à CLI, com JSON versionado e erros explícitos. Owner: frente UX .0003.

Nenhum candidato é vencedor sem teste reproduzível. Não alterar branch `main`, `dev`, banco ou busca do par. Próxima entrega: provas de instalação e análise de extraibilidade de Kept/LLM Chat Vault; depois escolha de biblioteca de grafo com benchmark.
