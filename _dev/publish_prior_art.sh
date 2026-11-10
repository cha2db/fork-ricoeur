#!/usr/bin/env bash
# CI-only publish reports to connector-readable branch, never to source main.
set -euo pipefail
cd "$(dirname "$0")/.."
[[ -n "${GITHUB_RUN_ID:-}" ]] || { echo "GitHub Actions only"; exit 2; }
DIR="ci-output/prior-art/runs/${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT:-1}"
TMP="$(mktemp -d)"
trap 'git worktree remove --force "$TMP" >/dev/null 2>&1 || true' EXIT
git fetch origin ci-results
git worktree add --detach "$TMP" FETCH_HEAD
mkdir -p "$TMP/$DIR" "$TMP/ci-output/prior-art"
cp _dev/results/prior-art.json "$TMP/$DIR/prior-art.json" 2>/dev/null || true
cp _dev/results/prior-base.manifest.json "$TMP/$DIR/base.manifest.json" 2>/dev/null || true
cp _dev/results/prior-art.log "$TMP/$DIR/prior-art.log" 2>/dev/null || true
cp _dev/results/sqlite-vec.json "$TMP/$DIR/sqlite-vec.json" 2>/dev/null || true
cp _dev/results/sqlite-vec.log "$TMP/$DIR/sqlite-vec.log" 2>/dev/null || true
cp _dev/results/relations.json "$TMP/$DIR/relations.json" 2>/dev/null || true
cp _dev/results/relations.log "$TMP/$DIR/relations.log" 2>/dev/null || true
for file in trigram.json trigram.log sqlite-vector.json sqlite-vector.log sqlite-vector-install.log vec1-probe.json; do
  cp "_dev/results/$file" "$TMP/$DIR/$file" 2>/dev/null || true
done
if [[ -f _dev/results/prior-art.json ]]; then
  cp _dev/results/prior-art.json "$TMP/ci-output/prior-art/latest.json"
else
  printf '{"status":"FAIL","reason":"prior-art report missing"}\n' > "$TMP/ci-output/prior-art/latest.json"
fi
if [[ -f _dev/results/sqlite-vec.json ]]; then
  cp _dev/results/sqlite-vec.json "$TMP/ci-output/prior-art/vector-latest.json"
fi
if [[ -f _dev/results/relations.json ]]; then
  cp _dev/results/relations.json "$TMP/ci-output/prior-art/relations-latest.json"
fi
if [[ -f _dev/results/prior-base.manifest.json ]]; then
  cp _dev/results/prior-base.manifest.json "$TMP/ci-output/prior-art/base-latest.json"
fi
for file in trigram.json sqlite-vector.json vec1-probe.json; do
  if [[ -f "_dev/results/$file" ]]; then
    cp "_dev/results/$file" "$TMP/ci-output/prior-art/${file%.json}-latest.json"
  fi
done
git -C "$TMP" add ci-output/prior-art
git -C "$TMP" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com commit -m "ci: archive prior art run ${GITHUB_RUN_ID}" >/dev/null
for attempt in 1 2 3; do
  if git -C "$TMP" push origin HEAD:ci-results; then
    echo "Published: ci-output/prior-art/latest.json"
    exit 0
  fi
  git -C "$TMP" fetch origin ci-results
  git -C "$TMP" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com rebase FETCH_HEAD || exit 1
done
echo "FAIL: could not publish report after 3 attempts"
exit 1
