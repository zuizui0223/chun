#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def require_row(rows: list[dict[str, str]], row_id: str) -> dict[str, str]:
    matches = [row for row in rows if row["row_id"] == row_id]
    if len(matches) != 1:
        raise SystemExit(f"expected exactly one row_id={row_id}, found {len(matches)}")
    return matches[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.data.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    required = {
        "CAMELLIA_VISIBLE",
        "EPIMEDIUM_INNER_SEPAL",
        "EPIMEDIUM_PETAL_SPUR",
        "LINOIDEAE_COROLLA",
        "HYDRANGEA_DISPLAY_PERIANTH",
        "MIMULUS_PETAL_LOBE_GAIN",
    }
    observed = {row["row_id"] for row in rows}
    missing = required - observed
    if missing:
        raise SystemExit(f"missing required constraint rows: {sorted(missing)}")

    hyd = require_row(rows, "HYDRANGEA_DISPLAY_PERIANTH")
    hyd_w_to_c = float(hyd["white_to_coloured_mean"])
    hyd_c_to_w = float(hyd["coloured_to_white_mean"])
    hyd_ratio = hyd_c_to_w / hyd_w_to_c
    hyd_share = hyd_c_to_w / (hyd_c_to_w + hyd_w_to_c)
    if not math.isclose(hyd_w_to_c, 6.712, rel_tol=0, abs_tol=1e-12):
        raise SystemExit("Hydrangea white->coloured QC total drifted")
    if not math.isclose(hyd_c_to_w, 22.691, rel_tol=0, abs_tol=1e-12):
        raise SystemExit("Hydrangea coloured->white QC total drifted")
    if hyd_ratio <= 1:
        raise SystemExit("Hydrangea no longer falsifies a universal white->colour direction rule")

    epi_sepal = require_row(rows, "EPIMEDIUM_INNER_SEPAL")
    epi_spur = require_row(rows, "EPIMEDIUM_PETAL_SPUR")
    if epi_sepal["system_id"] != epi_spur["system_id"]:
        raise SystemExit("Epimedium organ rows must refer to one radiation")
    if epi_sepal["ancestral_state"] != "WHITE" or epi_spur["ancestral_state"] != "YELLOW":
        raise SystemExit("Epimedium organ-specific ancestral-state contrast drifted")

    mim = require_row(rows, "MIMULUS_PETAL_LOBE_GAIN")
    if mim["ancestral_state"] != "YELLOW":
        raise SystemExit("Mimulus non-white ancestral control drifted")
    if "3/3" not in mim["repeatability_evidence"] or "PATHWAY_SPECIFIC_REGULATOR" not in mim["repeatability_evidence"]:
        raise SystemExit("Mimulus module-level recurrence benchmark drifted")

    common_reestimated = sum(
        row["comparability_class"] == "COMMON_REESTIMATED_TRANSITION_POSTERIOR"
        for row in rows
    )
    systems = sorted({row["system_id"] for row in rows})
    white_like_systems = sorted({
        row["system_id"] for row in rows if row["baseline_class"] == "WHITE_LIKE"
    })
    if len(white_like_systems) < 3:
        raise SystemExit("constraint layer must represent at least three white-like systems")

    summary = {
        "version": "v0.1",
        "systems_represented": systems,
        "white_like_systems_represented": white_like_systems,
        "hydrangea_published_direction_qc": {
            "white_to_coloured_mean": hyd_w_to_c,
            "coloured_to_white_mean": hyd_c_to_w,
            "return_gain_ratio": hyd_ratio,
            "return_to_white_share": hyd_share,
        },
        "constraint_tests": {
            "universal_white_to_colour_direction": {
                "status": "REJECTED_BY_PUBLISHED_HYDRANGEA_QC",
                "reason": "Published Hydrangea stochastic maps report substantially more coloured-to-white than white-to-coloured transitions.",
            },
            "single_whole_flower_ancestral_colour": {
                "status": "REJECTED_AS_CROSS_CLADE_CODING_RULE",
                "reason": "Epimedium has a white ancestral inner-sepal state but a yellow ancestral petal/spur state.",
            },
            "module_reuse_is_white_specific": {
                "status": "NOT_SUPPORTED_AS_WHITE_SPECIFIC",
                "reason": "Three independent Chilean Mimulus gains from a yellow ancestral context all map to the pathway-specific regulatory module.",
            },
        },
        "retained_candidate_rule": "ANCESTRAL_BASELINE_CONSTRAINS_TRANSITION_ARCHITECTURE_WITHOUT_FIXING_DIRECTION; REPEATABILITY_IS_HIERARCHICAL_AND_DISPLAY_COMPARTMENT_SPECIFIC",
        "pooled_common_rate_model_ready": common_reestimated >= 3,
        "common_reestimated_transition_posterior_systems": common_reestimated,
        "next_raw_gate": "INGEST_AND_REESTIMATE_HYDRANGEA_OR_LINOIDEAE_TERMINAL_STATES_UNDER_COMMON_MODEL",
        "claim_boundary": "This is an executable constraint synthesis over source-backed published/repository evidence, not a pooled cross-clade transition-rate estimate.",
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
