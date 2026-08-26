#!/usr/bin/env python3
"""Score preregistered pigment modules and frozen candidate-free contrasts.

Input is a tidy *family-level* expression table. Transcript/gene-to-family mapping and
paralog aggregation happen upstream and must not depend on visible colour or source-paper
candidate lists.

Required expression columns:
  dataset_id, dependence_cluster, sample_id, condition_id, gene_family, expression

`expression` may be log2(TPM+1) or another documented within-dataset normalized scale.
This script z-standardizes each gene family within dataset, averages available families
within each frozen module, enforces >=50% module completeness, and computes signed
Hedges' g for frozen two-group contrasts (target minus source).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

REQ_EXPR = {
    "dataset_id",
    "dependence_cluster",
    "sample_id",
    "condition_id",
    "gene_family",
    "expression",
}
REQ_SCHEMA = {"module_id", "axis", "gene_family", "in_primary_score"}
REQ_CONTRAST = {
    "contrast_id",
    "dependence_cluster",
    "dataset_target_id",
    "source_condition",
    "target_condition",
    "independence_role",
    "primary_for_cluster",
    "module_axes",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError(f"empty input: {path}")
    return rows


def require_columns(rows: list[dict[str, str]], required: set[str], label: str) -> None:
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"{label}: missing columns {sorted(missing)}")


def as_bool(x: str) -> bool:
    value = x.strip().lower()
    if value in {"true", "1", "yes"}:
        return True
    if value in {"false", "0", "no"}:
        return False
    raise ValueError(f"invalid boolean: {x!r}")


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)


def sample_sd(xs: list[float]) -> float:
    if len(xs) < 2:
        return float("nan")
    return statistics.stdev(xs)


def zscore_family_expression(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    """Z-standardize each family within each dataset across all admitted samples."""
    groups: dict[tuple[str, str], list[tuple[int, float]]] = defaultdict(list)
    parsed: list[dict[str, object]] = []
    seen: set[tuple[str, str, str]] = set()

    for i, row in enumerate(rows):
        key = (row["dataset_id"], row["sample_id"], row["gene_family"])
        if key in seen:
            raise ValueError(
                "expression input must be one family-level value per dataset/sample/family; "
                f"duplicate {key}"
            )
        seen.add(key)
        try:
            value = float(row["expression"])
        except ValueError as exc:
            raise ValueError(f"non-numeric expression in row {i+2}") from exc
        if not math.isfinite(value):
            raise ValueError(f"non-finite expression in row {i+2}")
        rec: dict[str, object] = dict(row)
        rec["expression"] = value
        parsed.append(rec)
        groups[(row["dataset_id"], row["gene_family"])].append((i, value))

    for (_dataset, _family), indexed in groups.items():
        vals = [v for _, v in indexed]
        mu = mean(vals)
        sd = sample_sd(vals)
        if not math.isfinite(sd) or sd == 0:
            for idx, _ in indexed:
                parsed[idx]["family_z"] = 0.0
                parsed[idx]["family_z_status"] = "zero_variance"
        else:
            for idx, value in indexed:
                parsed[idx]["family_z"] = (value - mu) / sd
                parsed[idx]["family_z_status"] = "ok"
    return parsed


def build_primary_modules(schema: list[dict[str, str]]) -> dict[str, dict[str, object]]:
    modules: dict[str, dict[str, object]] = {}
    family_to_module: dict[str, str] = {}
    for row in schema:
        if not as_bool(row["in_primary_score"]):
            continue
        module_id = row["module_id"].strip()
        axis = row["axis"].strip()
        family = row["gene_family"].strip()
        if not module_id or not axis or not family:
            raise ValueError("primary module rows require module_id, axis and gene_family")
        if family in family_to_module and family_to_module[family] != module_id:
            raise ValueError(
                f"gene family {family!r} occurs in multiple primary modules; "
                "family-level input cannot be double-counted"
            )
        family_to_module[family] = module_id
        info = modules.setdefault(module_id, {"axis": axis, "families": []})
        if info["axis"] != axis:
            raise ValueError(f"module {module_id} spans multiple axes")
        info["families"].append(family)
    if not modules:
        raise ValueError("no primary modules in schema")
    return modules


def score_modules(
    zrows: list[dict[str, object]],
    modules: dict[str, dict[str, object]],
    completeness_threshold: float,
) -> list[dict[str, object]]:
    family_module: dict[str, str] = {}
    for module_id, info in modules.items():
        for fam in info["families"]:
            family_module[str(fam)] = module_id

    grouped: dict[tuple[str, str, str, str, str], list[tuple[str, float]]] = defaultdict(list)
    sample_meta: dict[tuple[str, str], tuple[str, str]] = {}
    for row in zrows:
        fam = str(row["gene_family"])
        if fam not in family_module:
            continue
        dataset = str(row["dataset_id"])
        sample = str(row["sample_id"])
        cluster = str(row["dependence_cluster"])
        condition = str(row["condition_id"])
        sm_key = (dataset, sample)
        if sm_key in sample_meta and sample_meta[sm_key] != (cluster, condition):
            raise ValueError(f"sample metadata inconsistent for {sm_key}")
        sample_meta[sm_key] = (cluster, condition)
        module_id = family_module[fam]
        axis = str(modules[module_id]["axis"])
        grouped[(dataset, cluster, sample, condition, module_id)].append(
            (fam, float(row["family_z"]))
        )

    scores: list[dict[str, object]] = []
    for key, pairs in sorted(grouped.items()):
        dataset, cluster, sample, condition, module_id = key
        expected = [str(x) for x in modules[module_id]["families"]]
        observed_families = sorted({fam for fam, _ in pairs})
        completeness = len(observed_families) / len(expected)
        axis = str(modules[module_id]["axis"])
        admitted = completeness >= completeness_threshold
        score = mean([z for _, z in pairs]) if admitted else None
        scores.append(
            {
                "dataset_id": dataset,
                "dependence_cluster": cluster,
                "sample_id": sample,
                "condition_id": condition,
                "module_id": module_id,
                "axis": axis,
                "n_families_observed": len(observed_families),
                "n_families_expected": len(expected),
                "completeness": completeness,
                "module_score": score,
                "score_status": "admitted" if admitted else "below_50pct_completeness",
                "observed_families": ";".join(observed_families),
            }
        )
    return scores


def hedges_g(source: list[float], target: list[float]) -> dict[str, float | int | None]:
    n0, n1 = len(source), len(target)
    if n0 < 2 or n1 < 2:
        return {
            "n_source": n0,
            "n_target": n1,
            "mean_source": mean(source) if source else None,
            "mean_target": mean(target) if target else None,
            "hedges_g": None,
            "effect_status": "insufficient_replication",
        }
    s0, s1 = sample_sd(source), sample_sd(target)
    df = n0 + n1 - 2
    pooled_var = ((n0 - 1) * s0 * s0 + (n1 - 1) * s1 * s1) / df
    if pooled_var <= 0:
        return {
            "n_source": n0,
            "n_target": n1,
            "mean_source": mean(source),
            "mean_target": mean(target),
            "hedges_g": 0.0 if mean(source) == mean(target) else None,
            "effect_status": "zero_pooled_variance",
        }
    d = (mean(target) - mean(source)) / math.sqrt(pooled_var)
    # Small-sample correction J using df. Valid for the intended n>=2 per group.
    j = 1.0 - 3.0 / (4.0 * df - 1.0)
    g = j * d
    return {
        "n_source": n0,
        "n_target": n1,
        "mean_source": mean(source),
        "mean_target": mean(target),
        "hedges_g": g,
        "effect_status": "ok",
    }


def compute_contrasts(
    scores: list[dict[str, object]], contrasts: list[dict[str, str]]
) -> list[dict[str, object]]:
    by_cluster_condition_axis: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in scores:
        if row["score_status"] != "admitted" or row["module_score"] is None:
            continue
        key = (
            str(row["dependence_cluster"]),
            str(row["condition_id"]),
            str(row["axis"]),
        )
        by_cluster_condition_axis[key].append(float(row["module_score"]))

    out: list[dict[str, object]] = []
    for c in contrasts:
        axes = [a.strip() for a in c["module_axes"].split(";") if a.strip()]
        for axis in axes:
            src = by_cluster_condition_axis.get(
                (c["dependence_cluster"], c["source_condition"], axis), []
            )
            tgt = by_cluster_condition_axis.get(
                (c["dependence_cluster"], c["target_condition"], axis), []
            )
            eff = hedges_g(src, tgt)
            g = eff["hedges_g"]
            if isinstance(g, float) and math.isfinite(g):
                direction = "up" if g > 0 else "down" if g < 0 else "same"
            else:
                direction = "unresolved"
            out.append(
                {
                    "contrast_id": c["contrast_id"],
                    "dependence_cluster": c["dependence_cluster"],
                    "source_condition": c["source_condition"],
                    "target_condition": c["target_condition"],
                    "axis": axis,
                    "independence_role": c["independence_role"],
                    "primary_for_cluster": as_bool(c["primary_for_cluster"]),
                    **eff,
                    "direction_target_minus_source": direction,
                }
            )
    return out


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"no rows to write: {path}")
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--expression", type=Path, required=True)
    ap.add_argument("--modules", type=Path, required=True)
    ap.add_argument("--contrasts", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--completeness-threshold", type=float, default=0.5)
    args = ap.parse_args()

    if not 0 < args.completeness_threshold <= 1:
        raise ValueError("completeness threshold must be in (0,1]")

    expr = read_csv(args.expression)
    schema = read_csv(args.modules)
    contrasts = read_csv(args.contrasts)
    require_columns(expr, REQ_EXPR, "expression")
    require_columns(schema, REQ_SCHEMA, "module schema")
    require_columns(contrasts, REQ_CONTRAST, "contrast registry")

    modules = build_primary_modules(schema)
    zrows = zscore_family_expression(expr)
    scores = score_modules(zrows, modules, args.completeness_threshold)
    effects = compute_contrasts(scores, contrasts)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "sample_module_scores.csv", scores)
    write_csv(args.out_dir / "contrast_effects.csv", effects)

    summary = {
        "status": "candidate_free_module_contract_executable",
        "input_level": "one family-level expression value per dataset/sample/gene_family",
        "standardization": "gene-family z score within dataset across admitted samples",
        "module_completeness_threshold": args.completeness_threshold,
        "n_primary_modules": len(modules),
        "primary_modules": {
            k: {"axis": v["axis"], "families": v["families"]}
            for k, v in sorted(modules.items())
        },
        "n_sample_module_rows": len(scores),
        "n_contrast_axis_rows": len(effects),
        "n_effects_ok": sum(e["effect_status"] == "ok" for e in effects),
        "forbidden_inference": [
            "visible colour cannot fill missing gene families or module axes",
            "secondary correlated contrasts cannot become independent transitions",
            "between-dataset raw expression values are not pooled directly",
        ],
    }
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
