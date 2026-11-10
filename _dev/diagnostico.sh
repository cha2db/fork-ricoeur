#!/usr/bin/env bash
# Run headless tests and save portable reports, even on failure.
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p _dev/results
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG="_dev/results/diagnostico-${STAMP}.log"
REPORT="_dev/results/diagnostico-${STAMP}.json"
PY=.venv/bin/python
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
{
 echo "Cha2db headless diagnostics"
 echo "Date: $(date -Iseconds)"
 echo "Python: $("$PY" --version 2>&1)"
 echo "Git: $(git rev-parse --short HEAD)"
 echo "=== isolated corpus (100 conversations / 4000 messages) ==="
 "$PY" -u _dev/corpus.py --test-only --conversations 100 --messages 40
 corpus_status=$?
 echo "CORPUS_EXIT=$corpus_status"
 echo "=== existing retrieval contract ==="
 "$PY" -u _dev/teste6.py
 retrieval_status=$?
 echo "RETRIEVAL_EXIT=$retrieval_status"
 echo "=== HTTP adapter import ==="
 "$PY" -c 'from ricoeur.http_adapter import app; print("HTTP routes:", len(app.routes))'
 http_status=$?
 echo "HTTP_EXIT=$http_status"
 echo "=== end ==="
} >"$LOG" 2>&1
# Exit markers are extracted without depending on third-party packages.
"$PY" - "$LOG" "$REPORT" <<'PY'
import json, pathlib, re, sys
log=pathlib.Path(sys.argv[1]).read_text(errors="replace")
checks={key:int(m.group(1)) if (m:=re.search(key+r"_EXIT=(\d+)",log)) else None
        for key in ("CORPUS","RETRIEVAL","HTTP")}
result={"status":"PASS" if all(v==0 for v in checks.values()) else "FAIL",
        "exit_codes":checks,"log":sys.argv[1]}
pathlib.Path(sys.argv[2]).write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps(result,indent=2))
PY
echo "Log: $LOG"
echo "Relatorio: $REPORT"
echo "Envie o arquivo .log ou .json aqui no chat."
grep -q '"status": "PASS"' "$REPORT"
