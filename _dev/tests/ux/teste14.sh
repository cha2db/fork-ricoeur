#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/../../.."
mkdir -p _dev/results/ux
PYTHON=python
[[ -x .venv/bin/python ]] && PYTHON=.venv/bin/python
set +e
"$PYTHON" -u _dev/tests/ux/teste14.py 2>&1 | tee _dev/results/ux/teste14.log
status=${PIPESTATUS[0]}
set -e
"$PYTHON" -c 'import json,sys,datetime,pathlib;pathlib.Path("_dev/results/ux/teste14.json").write_text(json.dumps({"test":"UX-014","status":"PASS" if sys.argv[1]=="0" else "FAIL","timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"log":"_dev/results/ux/teste14.log","engine":"Ricoeur existing FTS5","scope":"timeline, period drilldown, tag frequency, curated SKOS sidecar"},indent=2)+"\n")' "$status"
exit "$status"
