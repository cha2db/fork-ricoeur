"""Manifest-driven central dashboard: classify all candidates, never claim untested adoption.

No network fetch and no SQLite writes. Data is versioned in the repository.
A manifest category's 'implemented' refers to local UX features, not to
adoption of all third-party candidates listed under that category.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ADOPTION_STATES = {
    "ricoeur": "adopted_core",
    "textual": "adopted_core",
    "skos": "implemented_subset",
    "echarts": "experimental_opt_in",
    "visnetwork": "experimental_opt_in",
    "wordcloud2": "experimental_opt_in",
}
ALLOWED_STATES = {"implemented", "partial", "research"}
ALLOWED_ADOPTION = set(ADOPTION_STATES.values()) | {"researched_only"}


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dashboard(catalog_path=None, candidate_path=None):
    catalog = _load(catalog_path or ROOT / "dashboard_catalog.json")
    manifest = _load(candidate_path or ROOT / "candidates.json")
    if catalog.get("schema_version") != "ux.dashboard.v1":
        raise ValueError("invalid_dashboard_schema")
    if manifest.get("schema_version") != "ux.candidates.v1":
        raise ValueError("invalid_candidate_schema")
    records = manifest["candidates"]
    by_id = {c["id"]: c for c in records}
    if len(records) != len(by_id):
        raise ValueError("duplicate_candidate")
    groups = catalog["groups"]
    ids = [i for g in groups for i in g["ids"]]
    if len(groups) < 1 or len(set(g["id"] for g in groups)) != len(groups):
        raise ValueError("invalid_category_id")
    if len(ids) != len(set(ids)) or set(ids) != set(by_id):
        raise ValueError("catalog_must_cover_every_candidate_once")
    if not all(g["state"] in ALLOWED_STATES for g in groups):
        raise ValueError("invalid_category_state")

    weights = manifest["weights"]
    if sum(weights.values()) != 100:
        raise ValueError("invalid_weights")
    footnotes = []
    buckets = []
    for group in groups:
        ranked = []
        for candidate_id in group["ids"]:
            candidate = by_id[candidate_id]
            score = round(sum(candidate[k] * weight for k, weight in weights.items()) / 5, 1)
            adoption = ADOPTION_STATES.get(candidate_id, "researched_only")
            if adoption not in ALLOWED_ADOPTION:
                raise ValueError("invalid_adoption_state")
            candidate_result = {
                "id": candidate_id,
                "name": candidate["name"],
                "url": candidate["url"],
                "category": candidate["category"],
                "core_relation": candidate["core_relation"],
                "status": adoption,
                "score_preliminary": score,
                "license_status": candidate.get("license_status", "verify-upstream"),
                "search_modes": candidate["search_modes"],
                "presentation_modes": candidate["presentation_modes"],
            }
            ranked.append(candidate_result)
            footnotes.append({
                "id": candidate_id,
                "name": candidate["name"],
                "url": candidate["url"],
                "category_id": group["id"],
                "license_status": candidate_result["license_status"],
                "logo": catalog.get("logos", {}).get(candidate_id),
            })
        ranked.sort(key=lambda x: (-x["score_preliminary"], x["id"]))
        buckets.append({
            "id": group["id"], "title": group["title"],
            "subtitle": group["subtitle"], "icon": group["icon"],
            "href": group["href"], "state": group["state"],
            "adopted": group.get("adopted"), "implementation": group["implementation"],
            "candidates": ranked, "count": len(ranked),
        })
    footnotes.sort(key=lambda x: x["name"].casefold())
    return {
        "schema_version": catalog["schema_version"],
        "navigation": "fixed",
        "baseline": manifest["baseline"],
        "criteria": {"weights": weights, "mode": "preliminary_not_runtime_verified"},
        "categories": buckets,
        "candidate_count": len(ids),
        "credits": footnotes,
        "logo_policy": "opt_in_external_assets_only",
        "adoption_policy": "adopted_core / implemented_subset / experimental_opt_in / researched_only",
    }


if __name__ == "__main__":
    print(json.dumps(dashboard(), ensure_ascii=False, indent=2))
