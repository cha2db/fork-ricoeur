#!/usr/bin/env bash
# One-command Android/Termux stress test. Run from anywhere inside the clone.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
echo "== Updating fork =="
git pull --ff-only
if [[ -x .venv/bin/python ]]; then
  PYTHON=.venv/bin/python
else
  PYTHON=python
fi
mkdir -p stress-results
STAMP="$(date +%Y%m%d-%H%M%S)"
REPORT="stress-results/fire-${STAMP}.log"
echo "== Fire test: 2000 conversations x 100 messages x 2048 chars =="
echo "== Log: $REPORT =="
set +e
"$PYTHON" tests/stress_fire.py --conversations 2000 --messages 100 --size 2048 2>&1 | tee "$REPORT"
STATUS=${PIPESTATUS[0]}
set -e
echo "== Exit code: $STATUS; saved: $REPORT =="
exit "$STATUS"
