#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def close(observed: float, expected: float, tol: float = 1e-12) -> None:
    if abs(observed - expected) > tol:
        raise SystemExit(f"numeric drift: observed={observed} expected={expected}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--accessibility-summary", type=Path, required=True)
    ap.add_argument("--recurrence-summary", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    acc = json.loads(a.accessibility_summary.read_text(encoding="utf-8"))
    rec = json.loads(a.recurrence_summary.read_text(encoding="utf-8"))

    # Whole literature observation layer after adding Luo et al. 2016 to CJAPONICA.
    if acc["n_biological_systems"] != 12:
        raise SystemExit("expected 12 literature biological systems")
    if acc["n_dependence_clusters"] != 6:
        raise SystemExit("expected 6 dependence clusters")
    if acc["macro_transition_test"]["status"] != "blocked":
        raise SystemExit("macro gate unexpectedly reopened")

    srec = acc["system_level_recurrence_sensitivity"]
    crec = acc["dependence_collapsed_recurrence_primary"]
    close(srec["observed_recurrence"], 0.23611111111111113)
    close(srec["permutation_p_upper"], 0.033596640335966405, 1e-15)
    close(crec["observed_recurrence"], 2 / 9)
    close(crec["permutation_p_upper"], 0.16048395160483953, 1e-15)

    sasc = acc["system_level_axis_ascertainment"]
    casc = acc["dependence_collapsed_axis_ascertainment"]
    if sasc["observed_axis_coverage"] != {
        "A_change": 10, "F_change": 5, "C_change": 1, "P_change": 3
    }:
        raise SystemExit("system-level Luo coverage drift")
    if sasc["n_exact_axis_assignments"] != 127401984:
        raise SystemExit("system-level exact-null size drift")
    close(sasc["exact_p_A_enrichment"], 0.0015277862548828125, 1e-15)
    close(sasc["exact_p_any_axis_imbalance"], 0.003514796127507716, 1e-15)

    if casc["observed_axis_coverage"] != {
        "A_change": 5, "F_change": 4, "C_change": 1, "P_change": 2
    }:
        raise SystemExit("dependence-collapsed Luo coverage drift")
    if casc["n_exact_axis_assignments"] != 3456:
        raise SystemExit("dependence-collapsed exact-null size drift")
    close(casc["exact_p_A_enrichment"], 0.078125, 1e-15)
    close(casc["exact_p_any_axis_imbalance"], 0.1736111111111111, 1e-15)

    clusters = {x["cluster"]: x for x in acc["dependence_clusters"]}
    cj = clusters["CJAPONICA"]
    if cj["n_member_systems"] != 4 or cj["signature"] != "up|down|unknown|unknown":
        raise SystemExit(f"CJAPONICA collapse drift: {cj}")

    # Class-stratified matched common-set recurrence. The candidate-free measurements
    # are unchanged; only the literature-side CJAPONICA F cell is newly resolved.
    anth = rec["identified_set_contraction_on_common_clusters"]["anthocyanin_gain"]
    if anth["common_clusters"] != ["CJAPONICA", "CRETICULATA", "CSIN_WHITE_PINK"]:
        raise SystemExit("anthocyanin common-set drift")
    lit = anth["literature_common_cluster_bounds"]
    cf = anth["candidate_free_common_cluster_bounds"]
    if lit["n_unresolved_cluster_axes"] != 6 or lit["n_exact_completions"] != 729:
        raise SystemExit("Luo literature completion-space drift")
    close(lit["exact_signature_recurrence"]["minimum"], 1 / 3)
    close(lit["exact_signature_recurrence"]["maximum"], 1.0)
    close(lit["pairwise_axis_concordance"]["minimum"], 1 / 3)
    close(lit["pairwise_axis_concordance"]["maximum"], 1.0)
    close(anth["literature_width"], 2 / 3)
    close(anth["candidate_free_width"], 1 / 6)
    close(anth["width_reduction"], 0.5)

    close(cf["exact_signature_recurrence"]["minimum"], 1 / 3)
    close(cf["exact_signature_recurrence"]["maximum"], 1 / 3)
    close(cf["pairwise_axis_concordance"]["minimum"], 1 / 3)
    close(cf["pairwise_axis_concordance"]["maximum"], 0.5)

    overlap = rec["literature_vs_candidate_free_overlap"]["anthocyanin_gain"]
    if overlap["n_comparable_resolved_cells"] != 6 or overlap["n_agree"] != 2:
        raise SystemExit(f"anthocyanin overlap drift: {overlap}")
    close(overlap["agreement_fraction"], 1 / 3)
    conflicts = {(x["cluster"], x["axis"], x["literature"], x["candidate_free"]) for x in overlap["conflicts"]}
    expected_conflicts = {
        ("CJAPONICA", "A", "up", "down"),
        ("CJAPONICA", "F", "down", "up"),
        ("CRETICULATA", "P", "down", "up"),
        ("CSIN_WHITE_PINK", "A", "up", "down"),
    }
    if conflicts != expected_conflicts:
        raise SystemExit(f"anthocyanin conflict set drift: {conflicts}")

    yellow = rec["identified_set_contraction_on_common_clusters"]["yellow_development"]
    ycf = yellow["candidate_free_common_cluster_bounds"]
    close(ycf["exact_signature_recurrence"]["minimum"], 0.5)
    close(ycf["exact_signature_recurrence"]["maximum"], 0.5)
    close(ycf["pairwise_axis_concordance"]["minimum"], 0.75)
    close(ycf["pairwise_axis_concordance"]["maximum"], 0.75)

    summary = {
        "status": "paper1_luo2016_recurrence_v0_1_valid",
        "literature_systems": 12,
        "dependence_clusters": 6,
        "system_axis_coverage": "10/5/1/3",
        "cluster_axis_coverage": "5/4/1/2",
        "system_A_enrichment_p": sasc["exact_p_A_enrichment"],
        "cluster_A_enrichment_p": casc["exact_p_A_enrichment"],
        "anthocyanin_literature_exact_bounds": [1 / 3, 1.0],
        "anthocyanin_literature_pairwise_bounds": [1 / 3, 1.0],
        "anthocyanin_candidate_free_exact": 1 / 3,
        "anthocyanin_candidate_free_pairwise_bounds": [1 / 3, 0.5],
        "anthocyanin_literature_width": 2 / 3,
        "anthocyanin_candidate_free_width": 1 / 6,
        "anthocyanin_width_reduction": 0.5,
        "anthocyanin_direct_agreement": "2/6",
        "candidate_free_changed": False,
        "yellow_changed": False,
        "macro_changed": False,
        "interpretation": (
            "Luo resolves CJAPONICA F and weakens the dependence-collapsed A-only ascertainment claim, "
            "while preserving candidate-free whole-package heterogeneity and adding a new direct literature/candidate-free F conflict."
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
