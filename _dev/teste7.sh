#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
mkdir -p _dev/results
PYTHON=python
[[ -x .venv/bin/python ]] && PYTHON=.venv/bin/python
echo "== Teste 7: MCP real no Python do Termux =="
"$PYTHON" --version
echo "== Diagnostico Pydantic =="
"$PYTHON" -m pip show pydantic pydantic-core mcp | grep -E '^(Name|Version):' || true
# Previous partial builds can leave incompatible pydantic and pydantic-core versions.
# Install both from a single resolver transaction, rather than fixing one alone.
if ! "$PYTHON" -c 'from mcp.server.fastmcp import FastMCP; from mcp import ClientSession' >/dev/null 2>&1; then
  echo "== Reparando SDK e dependencias em conjunto =="
  "$PYTHON" -m pip install --upgrade --force-reinstall 'pydantic>=2.7,<3' 'mcp>=1.0,<1.10'
fi
echo "== Validacao de imports =="
"$PYTHON" -c 'from mcp.server.fastmcp import FastMCP; from mcp import ClientSession; print("SDK MCP: imports OK")'
echo "== Cliente e servidor MCP via stdio =="
set +e
"$PYTHON" -u _dev/teste7.py 2>&1 | tee _dev/results/teste7.log
status=${PIPESTATUS[0]}
set -e
echo "Saida=$status | _dev/results/teste7.log"
exit "$status"
