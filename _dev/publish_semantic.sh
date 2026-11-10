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
  printf '{"status":"BLOCKED","reason":"No semantic report; check install log"}\n' > "$TMP/ci-output/semantic/latest.json"
fi
git -C "$TMP" add ci-output/semantic
git -C "$TMP" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com commit -m "ci: semantic experiment ${GITHUB_RUN_ID}" >/dev/null
for attempt in 1 2 3; do
  if git -C "$TMP" push origin HEAD:ci-results; then exit 0; fi
  git -C "$TMP" fetch origin ci-results
  git -C "$TMP" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com rebase FETCH_HEAD
done
exit 1
