#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
mkdir -p _dev/results
PYTHON=python
[[ -x .venv/bin/python ]] && PYTHON=.venv/bin/python
"$PYTHON" -u _dev/teste5.py | tee _dev/results/teste5.log
