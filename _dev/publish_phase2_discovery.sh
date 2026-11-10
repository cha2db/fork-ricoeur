#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
: "${GITHUB_RUN_ID:?CI only}"
tmp="$(mktemp -d)"
trap 'git worktree remove --force "$tmp" >/dev/null 2>&1 || true' EXIT
git fetch origin ci-results
git worktree add --detach "$tmp" FETCH_HEAD
runpath="ci-output/phase2/discovery/runs/${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT:-1}"
mkdir -p "$tmp/$runpath" "$tmp/ci-output/phase2/discovery"
for name in phase2-discovery.json phase2-discovery.log; do
  cp "_dev/results/$name" "$tmp/$runpath/$name" 2>/dev/null || true
done
if [[ -f _dev/results/phase2-discovery.json ]]; then
  cp _dev/results/phase2-discovery.json "$tmp/ci-output/phase2/discovery/latest.json"
else
  printf '{"status":"BLOCKED","reason":"discovery result missing"}\n' > "$tmp/ci-output/phase2/discovery/latest.json"
fi
git -C "$tmp" add ci-output/phase2/discovery
git -C "$tmp" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com commit -m "ci: phase2 discovery ${GITHUB_RUN_ID}" >/dev/null
for attempt in 1 2 3 4 5; do
  if git -C "$tmp" push origin HEAD:ci-results; then exit 0; fi
  git -C "$tmp" fetch origin ci-results
  git -C "$tmp" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com rebase FETCH_HEAD
  sleep "$attempt"
done
exit 1
