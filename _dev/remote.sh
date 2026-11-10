#!/usr/bin/env bash
# Cha2db/Ricoeur: authenticated SSH entrypoint for external MCP clients.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
case "${1:-help}" in
  setup)
    if [[ "${PREFIX:-}" != *com.termux* ]]; then
      echo "Este setup e especifico do Termux; execute no tablet."
      exit 2
    fi
    if ! command -v sshd >/dev/null; then
      pkg install -y openssh
    fi
    ssh-keygen -A
    echo "OpenSSH instalado. Use autenticacao por chave publica."
    echo "No computador cliente: ssh-keygen -t ed25519"
    echo "Depois copie a chave PUBLICA para ~/.ssh/authorized_keys do Termux."
    echo "Nunca compartilhe a chave privada."
    ;;
  start)
    command -v sshd >/dev/null || { echo "Execute: bash _dev/remote.sh setup"; exit 2; }
    sshd
    echo "SSH iniciado (Termux: porta 8022)."
    echo "Usuario: $(whoami)"
    echo "IP local: consulte as configuracoes de Wi-Fi do Android."
    echo "Para conectar: ssh -p 8022 $(whoami)@IP_DO_TABLET"
    ;;
  check)
    echo "Python MCP:"
    .venv/bin/python -c 'from mcp.server.fastmcp import FastMCP; from ricoeur.mcp_adapter import build_server; build_server(); print("MCP tools registered: OK")'
    echo "SSHD: $(command -v sshd || echo NAO_INSTALADO)"
    echo "Usuario: $(whoami)"
    echo "O acesso SSH requer chave publica autorizada no tablet."
    ;;
  serve)
    # SSH runs this command per connection. No network port for MCP is opened.
    exec .venv/bin/python -m ricoeur.mcp_adapter
    ;;
  *)
    cat <<'EOF'
Cha2db MCP remoto via SSH:
  bash _dev/remote.sh setup   # instala OpenSSH no Termux
  bash _dev/remote.sh start   # inicia SSH local na porta 8022
  bash _dev/remote.sh check   # verifica MCP e SSH
  bash _dev/remote.sh serve   # usado pelo cliente SSH, nao executar manualmente
Cliente MCP (stdio) em outro computador:
  command: ssh
  args: ["-T","-p","8022","USUARIO@IP_DO_TABLET",
         "cd ~/fork-ricoeur && bash _dev/remote.sh serve"]
Requer chave SSH publica autorizada no tablet.
Nao abrir a porta 8022 na internet; usar LAN ou VPN privada.
EOF
    ;;
esac
