#!/usr/bin/env bash
# Default: non-destructive additive corpus in existing Ricoeur database.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
[[ -x "$PY" ]] || { echo "Python .venv ausente"; exit 2; }
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
case "${1:-import}" in
 test)
  "$PY" -u _dev/corpus.py --test-only --conversations 100 --messages 40
  ;;
 import)
  "$PY" -u _dev/corpus.py --conversations 1000 --messages 40
  ;;
 *)
  echo "Uso: bash _dev/corpus.sh test|import"; exit 2;;
esac
