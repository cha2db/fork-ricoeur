"""Deterministic provisional ranking, with independently comparable UX categories."""
import argparse
import json
from collections import defaultdict
from pathlib import Path


def rank(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    weights = data["weights"]
    assert sum(weights.values()) == 100
    rows = []
    for source in data["candidates"]:
        assert all(1 <= source[key] <= 5 for key in weights), source["id"]
        score = round(sum(source[key] * weight for key, weight in weights.items()) / 5, 1)
        row = {**source, "score_preliminary": score, "tested": False,
               "core_similarity": source["core"] / 5,
               "adoption_status": "existing" if source["status"] in ("adopted", "implemented")
                                  else "unverified"}
        rows.append(row)
    ordering = lambda row: (-row["score_preliminary"], row["id"])
    ordered = sorted(rows, key=ordering)
    groups = defaultdict(list)
    by_search = defaultdict(list)
    by_presentation = defaultdict(list)
    for row in rows:
        groups[row["category"]].append(row["id"])
        for mode in row["search_modes"]:
            by_search[mode].append(row["id"])
        for mode in row["presentation_modes"]:
            by_presentation[mode].append(row["id"])
    rank_of = {row["id"]: i for i, row in enumerate(ordered)}
    sort_ids = lambda ids: sorted(ids, key=lambda x: rank_of[x])
    return {
        "schema_version": data["schema_version"],
        "baseline": data["baseline"],
        "weights": weights,
        "method": "provisional manually assessed 1..5; not benchmark or license verification",
        "ranking": ordered,
        "ranking_by_category": {key: sort_ids(ids) for key, ids in sorted(groups.items())},
        "search_mode_index": {key: sort_ids(ids) for key, ids in sorted(by_search.items())},
        "presentation_mode_index": {key: sort_ids(ids) for key, ids in sorted(by_presentation.items())},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(Path(__file__).with_name("candidates.json")))
    parser.add_argument("--output")
    args = parser.parse_args()
    output = json.dumps(rank(args.manifest), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
