#!/usr/bin/env bash
# One command, reproducible headless gate. Keeps reports even when tests fail.
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p _dev/results
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG="_dev/results/busca-${STAMP}.log"
SUMMARY="_dev/results/busca-${STAMP}.json"
DETAIL="_dev/results/busca-${STAMP}-benchmark.json"
PY=.venv/bin/python
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
{
 echo "Cha2db search suite"
 echo "Date: $(date -Iseconds)"
 echo "Commit: $(git rev-parse --short HEAD)"
 echo "Python: $("$PY" --version 2>&1)"
 echo "=== retrieval contract ==="
 "$PY" -u _dev/teste6.py
 RETRIEVAL=$?
 echo "RETRIEVAL_EXIT=$RETRIEVAL"
 echo "=== isolated corpus ==="
 "$PY" -u _dev/corpus.py --test-only --conversations 100 --messages 40
 CORPUS=$?
 echo "CORPUS_EXIT=$CORPUS"
 echo "=== benchmark correctness / performance ==="
 "$PY" -u _dev/benchmark.py --conversations "${CONVERSATIONS:-300}" --messages "${MESSAGES:-40}" --output "$DETAIL"
 BENCHMARK=$?
 echo "BENCHMARK_EXIT=$BENCHMARK"
 echo "=== end ==="
} > "$LOG" 2>&1
"$PY" - "$LOG" "$SUMMARY" "$DETAIL" <<'PY'
import json,pathlib,re,sys
log=pathlib.Path(sys.argv[1]).read_text(errors="replace")
checks={k:int(m.group(1)) if (m:=re.search(k+r"_EXIT=(\d+)",log)) else None
        for k in ("RETRIEVAL","CORPUS","BENCHMARK")}
report={"status":"PASS" if all(v==0 for v in checks.values()) else "FAIL",
        "checks":checks,"log":sys.argv[1],"benchmark":sys.argv[3]}
pathlib.Path(sys.argv[2]).write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))
PY
echo "Log: $LOG"
echo "Resumo: $SUMMARY"
echo "Metricas: $DETAIL"
echo "Anexe o .log e o -benchmark.json para analise."
grep -q '"status": "PASS"' "$SUMMARY"
