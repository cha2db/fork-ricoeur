"""Product-wide adoption screening without replacing Phase-2 or UX rankings.

This is a *research ranking*: all new tool gates remain NOT_TESTED.
The cross-reference distinguishes candidates already inventoried by Phase-2
(143/207) and UX (46); it never inflates those original counts.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from urllib.parse import urlsplit

REPO = Path(__file__).resolve().parents[1]
MANIFEST = Path(__file__).with_name("fronts.json")


def canonical_url(url):
    url = url.strip()
    parsed = urlsplit(url)
    host = (parsed.hostname or "").casefold().removeprefix("www.")
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if host == "github.com" and len(parts) >= 2:
        return "github.com/" + parts[0].casefold() + "/" + parts[1].removesuffix(".git").casefold()
    return host + "/" + "/".join(parts).casefold()


def load(filename):
    return json.loads(Path(filename).read_text(encoding="utf-8"))


def source_index(root=REPO):
    paths = {
        "phase2_r10": root / "_dev/PHASE2_MARKET_UNIVERSE_R10.json",
        "phase2_r14": root / "_dev/PHASE2_MARKET_EXPANSION_R14.json",
        "ux": root / "ux_lab/candidates.json",
    }
    sources = {}
    cover = {}
    for family, path in paths.items():
        if not path.is_file():
            cover[family] = {"present": False, "candidate_count": 0}
            continue
        doc = load(path)
        entries = doc.get("candidates", [])
        cover[family] = {"present": True, "candidate_count": len(entries)}
        for row in entries:
            url = row.get("url")
            if url:
                sources.setdefault(canonical_url(url), []).append({
                    "survey": family, "id": row.get("id"),
                    "name": row.get("name"),
                })
    if not cover["phase2_r10"]["present"] or not cover["ux"]["present"]:
        raise ValueError("missing_existing_survey_sources")
    if cover["phase2_r10"]["candidate_count"] != 143:
        raise ValueError("phase2_r10_baseline_changed")
    if cover["phase2_r14"]["present"] and cover["phase2_r14"]["candidate_count"] != 64:
        raise ValueError("phase2_r14_expansion_inconsistent")
    if cover["ux"]["candidate_count"] != 46:
        raise ValueError("ux_survey_baseline_changed")
    return sources, cover


def _score(values, weights):
    if set(values) != set(weights) or any(type(v) is not int or not 1 <= v <= 5
                                            for v in values.values()):
        raise ValueError("invalid_scoring_dimensions")
    if sum(weights.values()) != 100:
        raise ValueError("invalid_scoring_weights")
    return round(sum(values[k] * weight for k, weight in weights.items()) / 5, 1)


def generate(root=REPO, manifest=None):
    doc = load(manifest or root / "product_lab/fronts.json")
    if doc["schema_version"] != "cha2db.product.fronts.v1":
        raise ValueError("unsupported_manifest_schema")
    source_map, coverage = source_index(root)
    seen_ids, by_front, source_counts = set(), [], Counter()
    candidate_weights = doc["ranking"]["weight"]
    front_weights = doc["front_priority"]["weights"]
    for front in doc["fronts"]:
        candidates = []
        for row in front["candidates"]:
            if row["id"] in seen_ids:
                raise ValueError("duplicate_product_id")
            seen_ids.add(row["id"])
            if not row["url"].startswith("https://") or not row["next_gate"]:
                raise ValueError("candidate_requires_secure_source_and_gate")
            if row["execution_status"] != "NOT_TESTED_IN_PRODUCT_ROUND":
                raise ValueError("functional_claim_without_test")
            if row["adoption_status"] != "RESEARCH_ONLY":
                raise ValueError("adoption_without_gate")
            overlap = source_map.get(canonical_url(row["url"]), [])
            surveys = sorted({s["survey"] for s in overlap})
            evidence_state = "already_catalogued" if surveys else "new_to_cha2db_inventories"
            source_counts[evidence_state] += 1
            candidates.append({
                **row,
                "priority_preliminary": _score(row["scores"], candidate_weights),
                "seen_elsewhere": overlap,
                "prior_surveys": surveys,
                "inventory_position": evidence_state,
                "functional_verdict": "NOT_TESTED",
                "license_verdict": "VERIFY_COMPONENT_LICENSE",
            })
        candidates.sort(key=lambda c: (-c["priority_preliminary"], c["id"]))
        # Only candidates serving the same technical port are direct alternatives.
        by_port = {}
        for candidate in candidates:
            by_port.setdefault(candidate["subport"], []).append(candidate)
        comparison_groups = [
            {"subport": port, "candidate_count": len(items), "candidates": items}
            for port, items in by_port.items()
        ]
        comparison_groups.sort(key=lambda g: (-g["candidates"][0]["priority_preliminary"],
                                              g["subport"]))
        by_front.append({
            "id": front["id"], "title": front["title"],
            "objective": front["objective"],
            "existing_evidence": front["existing_evidence"],
            "observed_state": front["observed_state"],
            "gate": front["gate"],
            "priority_preliminary": _score(front["priority_hypothesis"], front_weights),
            "candidate_count": len(candidates),
            "new_to_inventories": sum(not x["prior_surveys"] for x in candidates),
            "previously_catalogued": sum(bool(x["prior_surveys"]) for x in candidates),
            "candidates": candidates,
            "comparison_groups": comparison_groups,
        })
    by_front.sort(key=lambda f: (-f["priority_preliminary"], f["id"]))
    return {
        "schema_version": doc["schema_version"],
        "purpose": "product_capability_gaps_and_adoption_gates",
        "scores_are": "hypotheses_only_not_measured",
        "basis": doc["baseline"],
        "source_coverage": coverage,
        "cross_reference_policy": "normalized_software_or_spec_url; does_not_imply_contract_equivalence",
        "front_weights": front_weights,
        "candidate_weights": candidate_weights,
        "front_count": len(by_front),
        "candidate_count": len(seen_ids),
        "new_to_existing_inventories": source_counts["new_to_cha2db_inventories"],
        "overlapping_existing_inventories": source_counts["already_catalogued"],
        "front_ranking": by_front,
    }


def markdown(result):
    lines = [
        "# Cha2db — ranking de frentes do produto",
        "",
        "**Pontuações provisórias, não testes ou homologações de componentes.**",
        "",
        f"Inventário: {result['front_count']} frentes, {result['candidate_count']} comparações; "
        f"{result['overlapping_existing_inventories']} sobreposições com inventários prévios "
        f"e {result['new_to_existing_inventories']} URLs novas para esses inventários.",
        "",
        "| Prioridade | Frente | Estado observado | 1º candidato para confronto | Quantidade | Novos |",
        "|---:|---|---|---|---:|---:|",
    ]
    for i, front in enumerate(result["front_ranking"], 1):
        first = front["candidates"][0]
        lines.append(
            f"| {i} ({front['priority_preliminary']}/100) | {front['title']} | "
            f"{front['observed_state']} | [{first['name']}]({first['url']}) "
            f"({first['priority_preliminary']}/100) | {front['candidate_count']} | "
            f"{front['new_to_inventories']} |"
        )
    for front in result["front_ranking"]:
        lines.extend([
            "", f"## {front['title']}", "", front["objective"],
            f"**Evidência já existente:** {front['existing_evidence']}",
            f"**Gate seguinte:** {front['gate']}", "",
            "| Ordem | Candidato | Porta | Score prévio | Já visto | Próxima prova |",
            "|---:|---|---|---:|---|---|",
        ])
        for group in front["comparison_groups"]:
            lines.append(f"| **Porta: {group['subport']}** | | | | | |")
            for pos, x in enumerate(group["candidates"], 1):
                elsewhere = ", ".join(x["prior_surveys"]) or "não encontrado"
                lines.append(
                    f"| {pos} | [{x['name']}]({x['url']}) | {x['subport']} | "
                    f"{x['priority_preliminary']} | {elsewhere} | {x['next_gate']} |"
                )
    lines.extend([
        "", "## Limites", "",
        "- As categorias não substituem a pesquisa Fase 2 (207) nem UX (46).",
        "- Novo = URL não presente nos inventários carregados, não descoberta inédita da Internet.",
        "- Candidatos já estudados mantêm o ID e a evidência de suas frentes de origem.",
        "- Nunca aprovar motor, liberar licença, instalar pacote ou publicar dados reais apenas por pontuação.",
    ])
    if not result["source_coverage"]["phase2_r14"]["present"]:
        lines.append("- **Atenção:** R14 não existe nesta branch; verificação cruzada parcial (143 + 46). "
                     "O checkout de merge do PR precisa confrontar os 207.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Rank other Cha2db product fronts")
    parser.add_argument("--format", choices=("json","md"), default="json")
    parser.add_argument("--output")
    args = parser.parse_args()
    result = generate()
    output = (json.dumps(result, ensure_ascii=False, indent=2) + "\n"
              if args.format == "json" else markdown(result))
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
