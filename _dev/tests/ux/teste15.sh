#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/../../.."
mkdir -p _dev/results/ux
PYTHON=python
[[ -x .venv/bin/python ]] && PYTHON=.venv/bin/python
set +e
"$PYTHON" -u _dev/tests/ux/teste15.py 2>&1 | tee _dev/results/ux/teste15.log
status=${PIPESTATUS[0]}
set -e
"$PYTHON" -c 'import json,sys,datetime,pathlib;p=pathlib.Path("_dev/results/ux/teste15.json");p.write_text(json.dumps({"test":"UX-015","status":"PASS" if sys.argv[1]=="0" else "FAIL","timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"log":"_dev/results/ux/teste15.log","scope":"dashboard, categories, fixed navbar, credits, logo opt-in, 46 candidates, HTTP and database-readonly"},indent=2)+"\n")' "$status"
exit "$status"
