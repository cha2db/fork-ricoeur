#!/usr/bin/env bash
# Do not publish untrusted dependency source; only generated CI evidence.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
: "${GITHUB_RUN_ID:?CI only}"
tmp="$(mktemp -d)"
trap 'git worktree remove --force "$tmp" >/dev/null 2>&1 || true' EXIT
git fetch origin ci-results
git worktree add --detach "$tmp" FETCH_HEAD
folder="ci-output/phase2/r14/runs/${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT:-1}/pglite"
mkdir -p "$tmp/$folder" "$tmp/ci-output/phase2/r14"
for file in phase2-r14-pglite.json phase2-r14-pglite.log phase2-r14-pglite-install.log phase2-r14-pglite-base.log; do
 cp "_dev/results/$file" "$tmp/$folder/$file" 2>/dev/null || true
done
if [[ -s _dev/results/phase2-r14-pglite.json ]]; then
 cp _dev/results/phase2-r14-pglite.json "$tmp/ci-output/phase2/r14/pglite-latest.json"
else
 python - "$tmp/ci-output/phase2/r14/pglite-latest.json" <<'PY'
import json,os,pathlib,sys
logs={}
for suffix in ("log","install.log","base.log"):
 p=pathlib.Path("_dev/results")/f"phase2-r14-pglite-{suffix}"
 if p.exists():logs[p.name]=p.read_text(errors="replace")[-5000:]
pathlib.Path(sys.argv[1]).write_text(json.dumps({
 "status":"BLOCKED","candidate":"PGlite","run_id":os.getenv("GITHUB_RUN_ID"),
 "reason":"No completed PGlite fixture report","logs":logs},indent=2))
PY
fi
git -C "$tmp" add ci-output/phase2/r14
git -C "$tmp" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com commit -m "ci: test PGlite comparison on shared chat source ${GITHUB_RUN_ID}" >/dev/null
for attempt in 1 2 3 4 5; do
 if git -C "$tmp" push origin HEAD:ci-results; then exit 0; fi
 git -C "$tmp" fetch origin ci-results
 git -C "$tmp" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com rebase FETCH_HEAD
 sleep "$attempt"
done
exit 1
