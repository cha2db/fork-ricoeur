#!/usr/bin/env bash
# Publish new frontier evidence independently; never modify R13 ranking (143 baseline).
set -Eeuo pipefail
cd "$(dirname "$0")/.."
: "${GITHUB_RUN_ID:?GitHub Actions only}"
TMP="$(mktemp -d)"
trap 'git worktree remove --force "$TMP" >/dev/null 2>&1 || true' EXIT
git fetch origin ci-results
git worktree add --detach "$TMP" FETCH_HEAD
DEST="ci-output/phase2/frontier/runs/${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT:-1}"
mkdir -p "$TMP/$DEST" "$TMP/ci-output/phase2/frontier"
for file in phase2-frontier.json phase2-frontier.md phase2-frontier-audit.json phase2-frontier-audit.log phase2-frontier.log; do
  cp "_dev/results/$file" "$TMP/$DEST/$file" 2>/dev/null || true
done
if [[ -s "_dev/results/phase2-frontier.json" ]]; then
  cp "_dev/results/phase2-frontier.json" "$TMP/ci-output/phase2/frontier/latest.json"
  cp "_dev/results/phase2-frontier.md" "$TMP/ci-output/phase2/frontier/latest.md"
  cp "_dev/results/phase2-frontier-audit.json" "$TMP/ci-output/phase2/frontier/audit-latest.json"
else
  python - "$TMP/ci-output/phase2/frontier/latest.json" <<'PY'
import json,os,pathlib,sys
logs={}
for name in ("phase2-frontier.log","phase2-frontier-audit.log"):
    p=pathlib.Path("_dev/results")/name
    if p.exists():logs[name]=p.read_text(errors="replace")[-4000:]
pathlib.Path(sys.argv[1]).write_text(json.dumps({
  "status":"BLOCKED","reason":"Frontier report missing",
  "run_id":os.getenv("GITHUB_RUN_ID"),"log_tails":logs},indent=2))
PY
fi
git -C "$TMP" add ci-output/phase2/frontier
git -C "$TMP" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com commit -m "ci: phase2 frontier 226 candidates ${GITHUB_RUN_ID}" >/dev/null
for attempt in 1 2 3 4 5; do
  if git -C "$TMP" push origin HEAD:ci-results; then
    echo "Published 226 frontier and auditable upstream metadata"
    exit 0
  fi
  git -C "$TMP" fetch origin ci-results
  git -C "$TMP" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com rebase FETCH_HEAD
  sleep "$attempt"
done
echo "Could not publish frontier"
exit 1
