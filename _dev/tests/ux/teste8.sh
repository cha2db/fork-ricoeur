#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/../../.."
mkdir -p _dev/results/ux
PYTHON=python
[[ -x .venv/bin/python ]] && PYTHON=.venv/bin/python
echo "== UX Teste 8: CLI/GUI/grafo sobre SQLite sintético; sem tocar DB real =="
set +e
"$PYTHON" -u ux_lab/test_autonomous.py 2>&1 | tee _dev/results/ux/teste8.log
status=${PIPESTATUS[0]}
set -e
"$PYTHON" -c 'import json,sys,datetime,pathlib; p=pathlib.Path("_dev/results/ux/teste8.json"); p.write_text(json.dumps({"test":"UX-008","status":"PASS" if int(sys.argv[1])==0 else "FAIL","execution":"local synthetic sqlite","timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"log":"_dev/results/ux/teste8.log"},indent=2)+"\n")' "$status"
echo "Saida=$status | _dev/results/ux/teste8.log | _dev/results/ux/teste8.json"
exit "$status"
