#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/../../.."
mkdir -p _dev/results/product
PYTHON=python
[[ -x .venv/bin/python ]] && PYTHON=.venv/bin/python
set +e
"$PYTHON" -u _dev/tests/product/teste16.py 2>&1 | tee _dev/results/product/teste16.log
status=${PIPESTATUS[0]}
set -e
if [[ "$status" -eq 0 ]]; then
 "$PYTHON" product_lab/rank.py --format json --output _dev/results/product/ranking16.json
 "$PYTHON" product_lab/rank.py --format md --output _dev/results/product/ranking16.md
fi
"$PYTHON" -c 'import json,sys,datetime,pathlib;p=pathlib.Path("_dev/results/product/teste16.json");p.write_text(json.dumps({"test":"PRODUCT-016","status":"PASS" if sys.argv[1]=="0" else "FAIL","timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"log":"_dev/results/product/teste16.log","ranking_json":"_dev/results/product/ranking16.json","ranking_md":"_dev/results/product/ranking16.md","execution":"inventory + ranking metadata, no third-party runtime tests"},indent=2)+"\n")' "$status"
exit "$status"
