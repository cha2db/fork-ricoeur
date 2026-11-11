#!/usr/bin/env bash
# Publish R14 without replacing the historical 143-entry R13 latest snapshot.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
: "${GITHUB_RUN_ID:?GitHub Actions only}"
tmp="$(mktemp -d)"
trap 'git worktree remove --force "$tmp" >/dev/null 2>&1 || true' EXIT
git fetch origin ci-results
git worktree add --detach "$tmp" FETCH_HEAD
dir="ci-output/phase2/r14/runs/${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT:-1}"
mkdir -p "$tmp/$dir" "$tmp/ci-output/phase2/r14" "$tmp/ci-output/phase2/ranking"
for name in phase2-r14.json phase2-r14.md phase2-r14.log; do
  cp "_dev/results/$name" "$tmp/$dir/$name" 2>/dev/null || true
done
if [[ -s _dev/results/phase2-r14.json ]]; then
  cp _dev/results/phase2-r14.json "$tmp/ci-output/phase2/r14/latest.json"
  cp _dev/results/phase2-r14.md "$tmp/ci-output/phase2/r14/latest.md"
  cp _dev/results/phase2-r14.json "$tmp/ci-output/phase2/ranking/expanded-latest.json"
  cp _dev/results/phase2-r14.md "$tmp/ci-output/phase2/ranking/expanded-latest.md"
else
  python - "$tmp/ci-output/phase2/r14/latest.json" <<'PY'
import json,pathlib,sys,os
p=pathlib.Path('_dev/results/phase2-r14.log')
pathlib.Path(sys.argv[1]).write_text(json.dumps({
 "status":"BLOCKED","run_id":os.getenv('GITHUB_RUN_ID'),
 "reason":"R14 source audit or ranking script failed",
 "log_tail":p.read_text(errors="replace")[-10000:] if p.exists() else None},indent=2))
PY
fi
git -C "$tmp" add ci-output/phase2/r14 ci-output/phase2/ranking/expanded-latest.*
git -C "$tmp" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com commit -m "ci: R14 expanded 207-candidate phase2 evidence ranking ${GITHUB_RUN_ID}" >/dev/null
for attempt in 1 2 3 4 5; do
  if git -C "$tmp" push origin HEAD:ci-results; then
    echo "Published R14 expanded ranking and preserved R13 baseline"
    exit 0
  fi
  git -C "$tmp" fetch origin ci-results
  git -C "$tmp" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com rebase FETCH_HEAD
  sleep "$attempt"
done
exit 1
