#!/usr/bin/env bash
# Publish CI synthetic test reports to a dedicated branch for connector review.
set -euo pipefail
cd "$(dirname "$0")/.."
[[ -n "${GITHUB_RUN_ID:-}" ]] || { echo "GitHub Actions only"; exit 2; }
[[ -d _dev/results ]] || { echo "No reports"; exit 2; }
TMP="$(mktemp -d)"
trap 'git worktree remove --force "$TMP" >/dev/null 2>&1 || true' EXIT
git fetch origin ci-results
git worktree add --detach "$TMP" FETCH_HEAD
RUN="ci-output/runs/${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT:-1}"
mkdir -p "$TMP/$RUN"
cp -R _dev/results/. "$TMP/$RUN/"
mkdir -p "$TMP/ci-output"
"$PWD/.venv/bin/python" - "$TMP/$RUN/summary.json" "$RUN" <<'PY'
import json,os,pathlib,sys
root=pathlib.Path("_dev/results")
def load(name):
    p=root/name
    if not p.exists():return None
    try:return json.loads(p.read_text())
    except (ValueError,OSError):return {"status":"ERROR","reason":"invalid report"}
result={"repository":os.environ.get("GITHUB_REPOSITORY"),
        "commit":os.environ.get("GITHUB_SHA"),
        "run_id":os.environ.get("GITHUB_RUN_ID"),
        "run_attempt":os.environ.get("GITHUB_RUN_ATTEMPT","1"),
        "report_directory":sys.argv[2],
        "autoscale":load("autoscale.json"),
        "mcp":load("teste7.json"),
        "status":"REVIEW"}
states=[(result[k] or {}).get("status") for k in ("autoscale","mcp")]
if "FAIL" in states:result["status"]="FAIL"
elif all(s in ("PASS","LIMIT") for s in states):result["status"]="PASS_WITH_LIMIT" if "LIMIT" in states else "PASS"
pathlib.Path(sys.argv[1]).write_text(json.dumps(result,ensure_ascii=False,indent=2))
PY
git fetch origin main --quiet
CURRENT_MAIN="$(git rev-parse FETCH_HEAD)"
if [[ "$GITHUB_SHA" == "$CURRENT_MAIN" ]]; then
  cp "$TMP/$RUN/summary.json" "$TMP/ci-output/latest.json"
  cp "$TMP/$RUN/autoscale.log" "$TMP/ci-output/latest.log" 2>/dev/null || true
else
  echo "Stale run $GITHUB_SHA; archived without overwriting latest result for $CURRENT_MAIN"
fi
git -C "$TMP" add ci-output
if ! git -C "$TMP" diff --cached --quiet; then
  git -C "$TMP" -c user.name='cha2db-ci' -c user.email='ci@users.noreply.github.com' \
    commit -m "ci: archive run ${GITHUB_RUN_ID} results" >/dev/null
  git -C "$TMP" push origin HEAD:ci-results
fi
echo "Report archived in ci-results: $RUN/summary.json"
