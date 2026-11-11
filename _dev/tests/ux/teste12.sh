#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/../../.."
mkdir -p _dev/results/ux
PYTHON=python
[[ -x .venv/bin/python ]] && PYTHON=.venv/bin/python
set +e
"$PYTHON" -u _dev/tests/ux/teste12.py 2>&1 | tee _dev/results/ux/teste12.log
status=${PIPESTATUS[0]}
set -e
"$PYTHON" ux_lab/rank_candidates.py --output _dev/results/ux/ranking12.json
"$PYTHON" -c 'import json,sys,datetime,pathlib;pathlib.Path("_dev/results/ux/teste12.json").write_text(json.dumps({"test":"UX-012","status":"PASS" if sys.argv[1]=="0" else "FAIL","timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"ranking":"_dev/results/ux/ranking12.json","type":"metadata and compatibility; not third-party app execution"},indent=2)+"\n")' "$status"
exit "$status"
