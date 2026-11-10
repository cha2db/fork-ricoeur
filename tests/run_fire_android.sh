#!/usr/bin/env bash
# Android/Termux stress runner: checkpointed and isolated.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p stress-results
STAMP="$(date +%Y%m%d-%H%M%S)"
REPORT="stress-results/fire-${STAMP}.log"
STATUSFILE="stress-results/latest-status.txt"
echo "START ${STAMP}: 3000 conversations x 100 messages x 2048 chars" | tee "$STATUSFILE"
echo "Log: $REPORT"
if [[ -x .venv/bin/python ]]; then PYTHON=.venv/bin/python; else PYTHON=python; fi
echo "RUNNING ${STAMP}" > "$STATUSFILE"
set +e
"$PYTHON" -u tests/stress_fire.py --conversations 3000 --messages 100 --size 2048 2>&1 | tee "$REPORT"
STATUS=${PIPESTATUS[0]}
set -e
if [[ "$STATUS" -eq 0 ]]; then
  echo "PASS ${STAMP}: $REPORT" | tee "$STATUSFILE"
else
  echo "FAIL exit=${STATUS} ${STAMP}: $REPORT" | tee "$STATUSFILE"
fi
exit "$STATUS"
