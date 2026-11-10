#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
git pull --ff-only
mkdir -p stress-results
PYTHON=python
if [[ -x .venv/bin/python ]]; then PYTHON=.venv/bin/python; fi
set +e
"$PYTHON" -u tests/run_account_zip_android.py 2>&1 | tee stress-results/account-zip-latest.log
STATUS=${PIPESTATUS[0]}
set -e
echo "Exit code: $STATUS"
echo "Report: stress-results/account-zip-report.json"
exit "$STATUS"
