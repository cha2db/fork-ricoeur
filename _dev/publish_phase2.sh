#!/usr/bin/env bash
# Publish independent phase-2 engine reports without modifying source code.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
engine="${1:?usage: publish_phase2.sh <engine>}"
case "$engine" in bm25s|tantivy|usearch|orama|duckdb|lancedb|minisearch|flexsearch|reweave|ctk|ctk-store|chronicle|hnswlib|annoy|rdflib|ir-measures|portable-memory) ;; *) exit 2;; esac
: "${GITHUB_RUN_ID:?GitHub Actions only}"
tmp="$(mktemp -d)"
trap 'git worktree remove --force "$tmp" >/dev/null 2>&1 || true' EXIT
git fetch origin ci-results
git worktree add --detach "$tmp" FETCH_HEAD
runpath="ci-output/phase2/runs/${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT:-1}/$engine"
mkdir -p "$tmp/$runpath" "$tmp/ci-output/phase2"
for file in "phase2-$engine.json" "phase2-$engine.log" "phase2-$engine-install.log" "phase2-$engine-base.log"; do
  cp "_dev/results/$file" "$tmp/$runpath/$file" 2>/dev/null || true
done
python - "$tmp/ci-output/phase2/$engine-latest.json" "$engine" <<'PY'
import json,os,pathlib,sys
out=pathlib.Path(sys.argv[1]); engine=sys.argv[2]
source=pathlib.Path("_dev/results")/f"phase2-{engine}.json"
if source.exists():
    try:report=json.loads(source.read_text())
    except (ValueError,OSError):report={"status":"BLOCKED","reason":"invalid result file"}
else:
    report={"status":"BLOCKED","reason":"benchmark or dependency installation failed before report"}
report["run_id"]=os.environ.get("GITHUB_RUN_ID")
source_name="ctk" if engine=="ctk-store" else engine
source_revision=pathlib.Path("_dev/results")/f"{source_name}-upstream-commit.txt"
if source_revision.exists():report["upstream_commit"]=source_revision.read_text().strip()
report["commit"]=os.environ.get("GITHUB_SHA")
report["logs"]={}
for suffix in (".log","-install.log","-base.log"):
    p=pathlib.Path("_dev/results")/f"phase2-{engine}{suffix}"
    if p.exists():report["logs"][p.name]=p.read_text(errors="replace")[-2500:]
out.write_text(json.dumps(report,ensure_ascii=False,indent=2))
PY
git -C "$tmp" add ci-output/phase2
git -C "$tmp" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com commit -m "ci: phase2 $engine run ${GITHUB_RUN_ID}" >/dev/null
for attempt in 1 2 3 4 5; do
  if git -C "$tmp" push origin HEAD:ci-results; then
    echo "Published phase2/$engine-latest.json"
    exit 0
  fi
  git -C "$tmp" fetch origin ci-results
  git -C "$tmp" -c user.name=cha2db-ci -c user.email=ci@users.noreply.github.com rebase FETCH_HEAD
  sleep "$attempt"
done
echo "Cannot publish after retries"
exit 1
