#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
mkdir -p _dev/results
PYTHON=python
[[ -x .venv/bin/python ]] && PYTHON=.venv/bin/python
set +e
"$PYTHON" -u _dev/teste4.py 2>&1 | tee _dev/results/teste4.log
code=${PIPESTATUS[0]}
set -e
echo "Resultado: _dev/results/teste4.json | saída=$code"
exit "$code"
