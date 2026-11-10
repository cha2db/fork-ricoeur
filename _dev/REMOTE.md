# Cha2db — MCP remoto seguro no tablet (Termux)

## Objetivo
Usar o tablet como nó de dados e servidor MCP sem reimplementar o protocolo e sem expor um endpoint HTTP público. O cliente remoto lança o adapter MCP por SSH, mantendo o transporte MCP **stdio** já validado no Teste 7.

## Tablet
1. `git pull --ff-only`
2. `bash _dev/remote.sh setup`
3. `bash _dev/remote.sh check`
4. `bash _dev/remote.sh start`

## Autenticação
O computador cliente precisa ter um par de chaves SSH. Autorize **somente a chave pública** no arquivo `~/.ssh/authorized_keys` do Termux, com permissões 700 no diretório e 600 no arquivo. A instalação não habilita acesso anônimo, não gera credenciais compartilhadas nem configura exposição pública. Faça o primeiro acesso na mesma rede Wi-Fi.

## Configuração do cliente MCP externo
Use transporte stdio com executável `ssh` e argumentos:
`-T -p 8022 USUARIO@IP_DO_TABLET cd ~/fork-ricoeur && bash _dev/remote.sh serve`

Os argumentos finais da chamada SSH devem ser enviados como **um único comando remoto** quando o cliente exigir um array de argumentos.

Exemplo JSON (substitua usuário e IP):
```json
{
  "mcpServers": {
    "cha2db-tablet": {
      "command": "ssh",
      "args": ["-T", "-p", "8022", "USUARIO@IP_DO_TABLET", "cd ~/fork-ricoeur && bash _dev/remote.sh serve"]
    }
  }
}
```

## Segurança e limites
- SSH autentica e cifra o canal; o MCP continua em stdio. Não há serviço HTTP público.
- Evite habilitar encaminhamento de portas do roteador.
- Para acesso fora da LAN, configurar VPN privada (ex.: Tailscale ou WireGuard) em etapa separada; não automatizar abertura pública.
- A execução `serve` usa a base configurada pelo Ricoeur. O adapter é **somente leitura**.
- Android pode suspender processos em segundo plano; validar disponibilidade antes de considerar serviço 24/7.
- Não há evidência ainda de integração com um cliente MCP externo; Teste 7 validou cliente e servidor locais.
