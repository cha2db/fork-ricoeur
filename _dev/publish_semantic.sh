#!/usr/bin/env bash
# CI only: archive semantic test results in branch read by the GitHub connector.
set -euo pipefail
cd "$(dirname "$0")/.."
[[ -n "${GITHUB_RUN_ID:-}" ]] || exit 2
TMP="$(mktemp -d)"
trap 'git worktree remove --force "$TMP" >/dev/null 2>&1 || true' EXIT
git fetch origin ci-results
git worktree add --detach "$TMP" FETCH_HEAD
DIR="ci-output/semantic/runs/${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT:-1}"
mkdir -p "$TMP/$DIR" "$TMP/ci-output/semantic"
cp _dev/results/semantic.json "$TMP/$DIR/semantic.json" 2>/dev/null || true
cp _dev/results/semantic.log "$TMP/$DIR/semantic.log" 2>/dev/null || true
cp _dev/results/semantic-install.log "$TMP/$DIR/semantic-install.log" 2>/dev/null || true
if [[ -f _dev/results/semantic.json ]]; then
  cp _dev/results/semantic.json "$TMP/ci-output/semantic/latest.json"
else
  python - "$TMP/ci-output/semantic/latest.json" <<'PY'
import json,os,pathlib,sys
logs={}
for name in ("semantic-install.log","prior-base.log","semantic.log"):
    p=pathlib.Path("_dev/results")/name
    if p.exists():logs[name]=p.read_text(errors="replace")[-12000:]
pathlib.Path(sys.argv[1]).write_text(json.dumps({
  "status":"BLOCKED","reason":"No semantic report; inspect log tails",
  "run_id":os.environ.get("GITHUB_RUN_ID"),"commit":os.environ.get("GITHUB_SHA"),
  "log_tails":logs},ensure_ascii=False,indent=2))
PY
fi
python - "$TMP/ci-output/semantic/latest.json" <<'PY'
import json,os,pathlib,sys
target=pathlib.Path(sys.argv[1])
report=json.loads(target.read_text())
report["run_id"]=os.environ.get("GITHUB_RUN_ID")
report["commit"]=os.environ.get("GITHUB_SHA")
logs={}
for name in ("semantic-install.log","prior-base.log","semantic.log"):
    p=pathlib.Path("_dev/results")/name
    if p.exists():logs[name]=p.read_text(errors="replace")[-12000:]
report["log_tails"]=logs
if report.get("status")=="RUNNING":
    report["status"]="BLOCKED"
    report["reason"]="Test did not reach final verdict; inspect logs"
target.write_text(json.dumps(report,ensure_ascii=False,indent=2))
PY
git -C "$TMP" add ci-output/semantic
git -C "$TMP" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com commit -m "ci: semantic experiment ${GITHUB_RUN_ID}" >/dev/null
for attempt in 1 2 3; do
  if git -C "$TMP" push origin HEAD:ci-results; then exit 0; fi
  git -C "$TMP" fetch origin ci-results
  git -C "$TMP" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com rebase FETCH_HEAD
done
exit 1
