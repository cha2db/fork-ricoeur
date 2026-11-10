#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
mkdir -p _dev/results
if ! command -v uv >/dev/null; then
  echo "ERRO: uv nao instalado. Instale uv antes de executar."
  exit 2
fi
# Python 3.12 isolated by uv; does not modify the Termux Python or the existing venv.
uv run --python 3.12 --with 'mcp>=1.28,<2' --with-editable . python _dev/teste7.py 2>&1 | tee _dev/results/teste7.log
