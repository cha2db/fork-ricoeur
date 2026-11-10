#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
mkdir -p _dev/results
PYTHON=python
[[ -x .venv/bin/python ]] && PYTHON=.venv/bin/python
echo "== Teste 7: MCP no Termux, versoes fixadas =="
"$PYTHON" --version
# MCP 1.9.4 relies on a Pydantic internal removed/changed in newer releases.
# Use an older coherent dependency set, without touching the Ricoeur source.
"$PYTHON" -m pip install --upgrade --force-reinstall \
  'mcp==1.9.4' 'pydantic==2.10.6' 'pydantic-core==2.27.2'
echo "== Imports =="
"$PYTHON" -c 'from mcp.server.fastmcp import FastMCP; from mcp import ClientSession; print("MCP imports OK")'
echo "== Protocolo stdio =="
set +e
"$PYTHON" -u _dev/teste7.py 2>&1 | tee _dev/results/teste7.log
status=${PIPESTATUS[0]}
set -e
echo "Saida=$status | _dev/results/teste7.log"
exit "$status"
