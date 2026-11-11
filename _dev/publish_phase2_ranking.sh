#!/usr/bin/env bash
# Auto-publish reproducible ranking snapshots, never UI source or candidate code.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
: "${GITHUB_RUN_ID:?GitHub Actions only}"
test -s _dev/results/phase2-ranking.json
test -s _dev/results/phase2-ranking.md
tmp="$(mktemp -d)"
trap 'git worktree remove --force "$tmp" >/dev/null 2>&1 || true' EXIT
git fetch origin ci-results
git worktree add --detach "$tmp" FETCH_HEAD
runpath="ci-output/phase2/ranking/runs/${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT:-1}"
mkdir -p "$tmp/$runpath" "$tmp/ci-output/phase2/ranking"
cp _dev/results/phase2-ranking.json "$tmp/$runpath/ranking.json"
cp _dev/results/phase2-ranking.md "$tmp/$runpath/ranking.md"
cp _dev/results/phase2-ranking.json "$tmp/ci-output/phase2/ranking/latest.json"
cp _dev/results/phase2-ranking.md "$tmp/ci-output/phase2/ranking/latest.md"
git -C "$tmp" add ci-output/phase2/ranking
git -C "$tmp" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com commit -m "ci: phase2 ranking 143 and confrontations run ${GITHUB_RUN_ID}" >/dev/null
for retry in 1 2 3 4 5; do
  if git -C "$tmp" push origin HEAD:ci-results; then
    echo "Published ranked 143 snapshot (JSON + Markdown)"
    exit 0
  fi
  git -C "$tmp" fetch origin ci-results
  git -C "$tmp" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com rebase FETCH_HEAD
  sleep "$retry"
done
echo "Failed to publish ranking after retries"
exit 1
