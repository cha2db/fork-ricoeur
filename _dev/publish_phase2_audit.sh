#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
: "${GITHUB_RUN_ID:?GitHub Actions only}"
tmp="$(mktemp -d)"
trap 'git worktree remove --force "$tmp" >/dev/null 2>&1 || true' EXIT
git fetch origin ci-results
git worktree add --detach "$tmp" FETCH_HEAD
path="ci-output/phase2/audit/runs/${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT:-1}"
mkdir -p "$tmp/$path" "$tmp/ci-output/phase2/audit"
for file in phase2-repo-audit.json phase2-repo-audit.log; do
  cp "_dev/results/$file" "$tmp/$path/$file" 2>/dev/null || true
done
if [[ -f _dev/results/phase2-repo-audit.json ]]; then
  cp _dev/results/phase2-repo-audit.json "$tmp/ci-output/phase2/audit/latest.json"
else
  printf '{"status":"BLOCKED","reason":"audit report missing"}\n' > "$tmp/ci-output/phase2/audit/latest.json"
fi
git -C "$tmp" add ci-output/phase2/audit
git -C "$tmp" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com commit -m "ci: phase2 repo audit ${GITHUB_RUN_ID}" >/dev/null
for retry in 1 2 3 4 5; do
  if git -C "$tmp" push origin HEAD:ci-results; then exit 0; fi
  git -C "$tmp" fetch origin ci-results
  git -C "$tmp" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com rebase FETCH_HEAD
  sleep "$retry"
done
exit 1
