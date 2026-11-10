#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
mkdir -p _dev/results
PYTHON=python
[[ -x .venv/bin/python ]] && PYTHON=.venv/bin/python
echo "== Teste 7: MCP stdio no Python local =="
"$PYTHON" --version
if ! "$PYTHON" -c 'from mcp.server.fastmcp import FastMCP; from mcp import ClientSession' 2>/dev/null; then
  echo "== Instalando SDK MCP 1.x compativel com Python 3.10 =="
  "$PYTHON" -m pip install 'mcp>=1.0,<1.10'
fi
echo "== Executando cliente e servidor MCP reais =="
set +e
"$PYTHON" -u _dev/teste7.py 2>&1 | tee _dev/results/teste7.log
status=${PIPESTATUS[0]}
set -e
echo "Saida=$status | _dev/results/teste7.log"
exit "$status"
