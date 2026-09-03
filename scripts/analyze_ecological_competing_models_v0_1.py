#!/usr/bin/env python3
"""Self-contained competing-model test for the Camellia ecological-cause question.

This analysis deliberately does not add new literature weights or historical branch
assignments. It recombines already-frozen repository outputs under a fixed contract
and asks which coarse causal models survive their own predictions.

Models:
  M_DIRECT_ANNUAL_CLIMATE
  M_VISIBLE_HUE_SYNDROME
  M_POLLINATOR_FILTER

The output is a constraint-survival audit, not a likelihood ratio across models.
Heterogeneous source designs are never pooled into one omnibus P value.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def fnum(x: str | None) -> float | None:
    s = (x or "").strip()
    if not s:
        return None
    return float(s)


def split_taxa(x: str) -> set[str]:
    return {p.strip() for p in x.split(";") if p.strip()}


def rr(row: dict[str, str]) -> float | None:
    a = fnum(row.get("numerator"))
    b = fnum(row.get("denominator"))
    if a is None or b is None or b <= 0:
        return None
    return a / b


def gm(values: list[float]) -> float:
    assert values and all(v > 0 for v in values)
    return math.exp(sum(math.log(v) for v in values) / len(values))


def extract_p(pattern: str, text: str) -> float:
    m = re.search(pattern, text)
    if not m:
        raise AssertionError(f"could not parse {pattern!r} from {text!r}")
    return float(m.group(1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--climate-models", type=Path, required=True)
    ap.add_argument("--ultimate", type=Path, required=True)
    ap.add_argument("--pollination-summary", type=Path, required=True)
    ap.add_argument("--chain", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    contract = read_csv(args.contract)
    assert len(contract) == 9, "contract row-count drift"
    assert len({r["constraint_id"] for r in contract}) == len(contract)

    # ------------------------------------------------------------------
    # Negative control 1: does coarse A/W hue improve climate prediction?
    # ------------------------------------------------------------------
    climate = read_csv(args.climate_models)
    aw = [r for r in climate if r["scope"] == "AW_only"]
    frozen_metrics = ["bio1_median", "bio6_median", "bio6_q05", "bio1_iqr"]
    climate_diag = []
    colour_aic_wins = 0
    for metric in frozen_metrics:
        rows = [r for r in aw if r["metric"] == metric]
        by_model = {r["model"]: r for r in rows}
        assert {"null", "colour"}.issubset(by_model)
        null_aic = float(by_model["null"]["aic"])
        colour_aic = float(by_model["colour"]["aic"])
        win = colour_aic < null_aic
        colour_aic_wins += int(win)
        climate_diag.append({
            "metric": metric,
            "null_aic": null_aic,
            "colour_aic": colour_aic,
            "colour_minus_null_aic": colour_aic - null_aic,
            "colour_beats_null": win,
        })
    assert colour_aic_wins == 0, "frozen AW AIC result drift"

    # History-blocked direct-cold test and within-section divergence test.
    ultimate = {r["hypothesis"]: r for r in read_csv(args.ultimate)}
    h2 = ultimate["H2_direct_cold_adaptation"]
    assert h2["status"] == "not_supported"
    h2_text = h2["primary_result"]
    blocked_cold_p = extract_p(r"section-block cold P=([0-9.]+)", h2_text)
    within_divergence_p = extract_p(r"within-section multivariate different-minus-same climate distance=[^;]+, one-sided P=([0-9.]+)", h2_text)
    direct_history_support = blocked_cold_p < 0.05 and within_divergence_p < 0.05
    assert not direct_history_support

    # ------------------------------------------------------------------
    # Negative control 2: does coarse visible hue determine pollinator function?
    # ------------------------------------------------------------------
    poll_rows = read_csv(args.pollination_summary)
    poll = {r["metric"]: r for r in poll_rows}
    hue_pollinator_p = float(poll["exact_association_p"]["value"])
    hetero_fraction = float(poll["fraction_multitaxon_visible_states_heterogeneous"]["value"])
    hetero_states = int(poll["multitaxon_visible_states_with_functional_heterogeneity"]["value"])
    n_multitaxon_states = int(poll["multitaxon_visible_states"]["value"])
    deterministic_hue = hetero_states == 0
    exact_hue_association = hue_pollinator_p < 0.05
    assert not deterministic_hue

    # ------------------------------------------------------------------
    # Positive mechanistic chain: environment -> pollinator/sensory -> fitness.
    # ------------------------------------------------------------------
    chain = [
        r for r in read_csv(args.chain)
        if r["admission_status"] in {"admit_primary", "admit_mediation"}
    ]
    by_link: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in chain:
        by_link[row["link_class"]].append(row)

    env = by_link["environment_to_pollinator_reliability"]
    sensory = by_link["sensory_state_to_pollinator_choice"]
    service = by_link["pollinator_service_to_reproductive_success"]

    env_taxa = set().union(*(split_taxa(r["taxon"]) for r in env))
    env_studies = {r["study_id"] for r in env}
    sensory_studies = {r["study_id"] for r in sensory}
    service_taxa = set().union(*(split_taxa(r["taxon"]) for r in service))

    assert len(env_studies) == 5 and len(env_taxa) == 4
    assert len(sensory_studies) == 2

    cross_ids = {
        "SERVICE_JAPONICA_2004",
        "SERVICE_PETELOTII_2017",
        "SERVICE_OLEIFERA_2024",
    }
    cross = [r for r in service if r["evidence_id"] in cross_ids]
    cross_rr = [rr(r) for r in cross]
    assert len(cross) == 3 and all(v is not None and v > 1 for v in cross_rr)
    cross_gm = gm([float(v) for v in cross_rr if v is not None])
    assert 3.52 < cross_gm < 3.54

    # Same-taxon bridge without historical branch reconstruction.
    env_simple_taxa = set().union(*(split_taxa(r["taxon"]) for r in env))
    sensory_simple_taxa = set().union(*(split_taxa(r["taxon"]) for r in sensory))
    service_simple_taxa = set().union(*(split_taxa(r["taxon"]) for r in service))
    env_service_bridge_taxa = sorted(env_simple_taxa & service_simple_taxa)
    full_three_link_taxa = sorted(env_simple_taxa & sensory_simple_taxa & service_simple_taxa)
    assert env_service_bridge_taxa
    assert not full_three_link_taxa

    # ------------------------------------------------------------------
    # Leave-one-evidence-unit robustness.
    # A replicated link must retain >=2 independent taxa/studies after deletion.
    # ------------------------------------------------------------------
    loo_rows: list[dict[str, object]] = []

    def env_ok(rows: list[dict[str, str]]) -> bool:
        taxa = set().union(*(split_taxa(r["taxon"]) for r in rows)) if rows else set()
        return len(taxa) >= 2

    def sensory_ok(rows: list[dict[str, str]]) -> bool:
        return len({r["study_id"] for r in rows}) >= 2

    def service_ok(rows: list[dict[str, str]]) -> bool:
        taxa = set().union(*(split_taxa(r["taxon"]) for r in rows)) if rows else set()
        positive_taxa = set()
        for r in rows:
            value = rr(r)
            if value is not None and value > 1:
                positive_taxa |= split_taxa(r["taxon"])
        return len(positive_taxa) >= 2 and len(taxa) >= 2

    link_specs = [
        ("environment_to_pollinator_reliability", env, env_ok),
        ("sensory_state_to_pollinator_choice", sensory, sensory_ok),
        ("pollinator_service_to_reproductive_success", service, service_ok),
    ]
    fragility = {}
    for link, rows, criterion in link_specs:
        failures = 0
        for i, omitted in enumerate(rows):
            kept = [r for j, r in enumerate(rows) if j != i]
            survives = criterion(kept)
            failures += int(not survives)
            loo_rows.append({
                "link_class": link,
                "omitted_evidence_id": omitted["evidence_id"],
                "survives_replication_rule": survives,
            })
        fragility[link] = {
            "n_deletions": len(rows),
            "n_failures": failures,
            "failure_fraction": failures / len(rows),
        }

    assert fragility["environment_to_pollinator_reliability"]["n_failures"] == 0
    assert fragility["sensory_state_to_pollinator_choice"]["n_failures"] == len(sensory)
    assert fragility["pollinator_service_to_reproductive_success"]["n_failures"] == 0

    # ------------------------------------------------------------------
    # Contract decisions. These are constraints, not independent Bernoulli trials.
    # ------------------------------------------------------------------
    decisions = [
        {
            "model": "M_DIRECT_ANNUAL_CLIMATE",
            "constraint_id": "DC1",
            "status": "not_supported" if colour_aic_wins == 0 else "supported",
            "observed": f"colour model AIC wins {colour_aic_wins}/{len(frozen_metrics)} frozen AW metrics",
        },
        {
            "model": "M_DIRECT_ANNUAL_CLIMATE",
            "constraint_id": "DC2",
            "status": "supported" if direct_history_support else "not_supported",
            "observed": f"section-block cold P={blocked_cold_p}; within-section divergence P={within_divergence_p}",
        },
        {
            "model": "M_VISIBLE_HUE_SYNDROME",
            "constraint_id": "VH1",
            "status": "supported" if deterministic_hue else "not_supported",
            "observed": f"{hetero_states}/{n_multitaxon_states} multi-taxon visible states are functionally heterogeneous",
        },
        {
            "model": "M_VISIBLE_HUE_SYNDROME",
            "constraint_id": "VH2",
            "status": "supported" if exact_hue_association else "unresolved",
            "observed": f"exact hue-function association P={hue_pollinator_p}",
        },
        {
            "model": "M_POLLINATOR_FILTER",
            "constraint_id": "PF1",
            "status": "supported" if len(env_taxa) >= 2 else "unresolved",
            "observed": f"{len(env_studies)} studies across {len(env_taxa)} taxa",
        },
        {
            "model": "M_POLLINATOR_FILTER",
            "constraint_id": "PF2",
            "status": "supported" if len(sensory_studies) >= 2 else "unresolved",
            "observed": f"{len(sensory_studies)} independent behavioural studies; LOO failure fraction={fragility['sensory_state_to_pollinator_choice']['failure_fraction']:.3f}",
        },
        {
            "model": "M_POLLINATOR_FILTER",
            "constraint_id": "PF3",
            "status": "supported" if len(cross) >= 2 and all(float(v) > 1 for v in cross_rr if v is not None) else "unresolved",
            "observed": f"3 independent A/Y/W taxa; geometric-mean fruit-set RR={cross_gm:.6f}",
        },
        {
            "model": "M_POLLINATOR_FILTER",
            "constraint_id": "PF4",
            "status": "supported" if env_service_bridge_taxa else "unresolved",
            "observed": ";".join(env_service_bridge_taxa),
        },
        {
            "model": "M_POLLINATOR_FILTER",
            "constraint_id": "PF5",
            "status": "supported" if full_three_link_taxa else "unresolved",
            "observed": ";".join(full_three_link_taxa) if full_three_link_taxa else "none",
        },
    ]

    contract_ids = {(r["model"], r["constraint_id"]) for r in contract}
    decision_ids = {(r["model"], r["constraint_id"]) for r in decisions}
    assert contract_ids == decision_ids, "decision/contract mismatch"

    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in decisions:
        counts[row["model"]][row["status"]] += 1

    model_summary = []
    for model in ["M_DIRECT_ANNUAL_CLIMATE", "M_VISIBLE_HUE_SYNDROME", "M_POLLINATOR_FILTER"]:
        model_summary.append({
            "model": model,
            "supported_constraints": counts[model]["supported"],
            "not_supported_constraints": counts[model]["not_supported"],
            "unresolved_constraints": counts[model]["unresolved"],
            "total_constraints": sum(counts[model].values()),
        })

    summary = {
        "analysis": "ecological_competing_model_self_test_v0.1",
        "interpretation_rule": "constraint-survival audit only; counts are not treated as independent probabilities",
        "negative_controls": {
            "AW_visible_colour_climate": {
                "colour_AIC_wins": colour_aic_wins,
                "n_frozen_metrics": len(frozen_metrics),
                "history_blocked_cold_p": blocked_cold_p,
                "within_section_greater_divergence_p": within_divergence_p,
            },
            "visible_hue_pollinator_function": {
                "exact_association_p": hue_pollinator_p,
                "heterogeneous_multitaxon_state_fraction": hetero_fraction,
            },
        },
        "pollinator_filter": {
            "environment_studies": len(env_studies),
            "environment_taxa": len(env_taxa),
            "sensory_studies": len(sensory_studies),
            "cross_species_service_taxa": len(cross),
            "cross_species_service_geometric_mean_RR": cross_gm,
            "environment_service_bridge_taxa": env_service_bridge_taxa,
            "full_three_link_taxa": full_three_link_taxa,
        },
        "leave_one_out_fragility": fragility,
        "model_constraint_summary": model_summary,
        "decision": {
            "best_surviving_model": "M_POLLINATOR_FILTER",
            "why": "4/5 preregistered component constraints are supported, while the direct annual-climate and deterministic visible-hue models fail their permissive negative-control predictions",
            "weakest_link": "sensory_state_to_pollinator_choice",
            "weakest_link_reason": "the two-study replication criterion fails after deleting either sensory study",
            "remaining_decisive_gap": "one same-system sensory/spectral state -> pollinator response -> fruit/seed fitness chain",
            "historical_branch_causation": "still_unidentified",
        },
    }

    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(args.out_dir / "climate_negative_control.csv", climate_diag)
    write_csv(args.out_dir / "constraint_decisions.csv", decisions)
    write_csv(args.out_dir / "model_summary.csv", model_summary)
    write_csv(args.out_dir / "leave_one_out.csv", loo_rows)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
