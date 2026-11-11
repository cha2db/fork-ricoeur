#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/../../.."
mkdir -p _dev/results/product
PYTHON=python
[[ -x .venv/bin/python ]] && PYTHON=.venv/bin/python
set +e
"$PYTHON" -u _dev/tests/product/teste17.py 2>&1 | tee _dev/results/product/teste17.log
status=${PIPESTATUS[0]}
set -e
"$PYTHON" -c 'import json,sys,datetime,pathlib;p=pathlib.Path("_dev/results/product/teste17.json");p.write_text(json.dumps({"test":"PRODUCT-017","status":"PASS" if sys.argv[1]=="0" else "FAIL","timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"log":"_dev/results/product/teste17.log","scope":"native read-only SQLite health, FK, FTS triggers, attachments, no PII"},indent=2)+"\n")' "$status"
exit "$status"
