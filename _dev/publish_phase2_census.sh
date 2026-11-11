#!/usr/bin/env bash
# Publish one accountable census of all 143 R10 candidates.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
: "${GITHUB_RUN_ID:?GitHub Actions only}"
TEMP="$(mktemp -d)"
trap 'git worktree remove --force "$TEMP" >/dev/null 2>&1 || true' EXIT
git fetch origin ci-results
git worktree add --detach "$TEMP" FETCH_HEAD
DEST="ci-output/phase2/census/runs/${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT:-1}"
mkdir -p "$TEMP/$DEST" "$TEMP/ci-output/phase2/census"
for file in phase2-143-ledger.json phase2-143-ledger.summary.md phase2-143-ledger.log phase2-repo-audit.json phase2-repo-audit.log; do
  cp "_dev/results/$file" "$TEMP/$DEST/$file" 2>/dev/null || true
done
if [[ -s _dev/results/phase2-143-ledger.json ]]; then
  cp _dev/results/phase2-143-ledger.json "$TEMP/ci-output/phase2/census/latest.json"
  cp _dev/results/phase2-143-ledger.summary.md "$TEMP/ci-output/phase2/census/latest.md" 2>/dev/null || true
else
  python - "$TEMP/ci-output/phase2/census/latest.json" <<'PY'
import json,os,pathlib,sys
logs={}
for name in ('phase2-143-ledger.log','phase2-repo-audit.log'):
    p=pathlib.Path('_dev/results')/name
    if p.exists():logs[name]=p.read_text(errors='replace')[-8000:]
pathlib.Path(sys.argv[1]).write_text(json.dumps({
    'status':'BLOCKED','reason':'143-candidate census failed before producing result',
    'run_id':os.getenv('GITHUB_RUN_ID'),'commit':os.getenv('GITHUB_SHA'),
    'log_tails':logs},ensure_ascii=False,indent=2))
PY
fi
git -C "$TEMP" add ci-output/phase2/census
git -C "$TEMP" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com commit -m "ci: phase2 census 143 run ${GITHUB_RUN_ID}" >/dev/null
for try in 1 2 3 4 5; do
  if git -C "$TEMP" push origin HEAD:ci-results; then
    echo "Census published at ci-output/phase2/census/latest.json"
    exit 0
  fi
  git -C "$TEMP" fetch origin ci-results
  git -C "$TEMP" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com rebase FETCH_HEAD
  sleep "$try"
done
exit 1
