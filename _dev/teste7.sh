#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
mkdir -p _dev/results
PYTHON=python
[[ -x .venv/bin/python ]] && PYTHON=.venv/bin/python
echo "== Teste 7: MCP real em Termux =="
"$PYTHON" --version
if ! "$PYTHON" -c 'from mcp.server.fastmcp import FastMCP; from mcp import ClientSession' 2>/dev/null; then
  if [[ -n "${TERMUX_VERSION:-}" || "${PREFIX:-}" == *com.termux* ]]; then
    echo "== Dependencias nativas Termux (Rust, maturin) =="
    pkg install -y rust clang
    "$PYTHON" -m pip install maturin
    export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
    export CARGO_BUILD_JOBS=2
  fi
  echo "== SDK MCP oficial =="
  "$PYTHON" -m pip install 'mcp>=1.0,<1.10'
fi
echo "== Cliente/servidor MCP via stdio =="
set +e
"$PYTHON" -u _dev/teste7.py 2>&1 | tee _dev/results/teste7.log
status=${PIPESTATUS[0]}
set -e
echo "Saida=$status | _dev/results/teste7.log"
exit "$status"
