#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

EXPECTED = {
    ("RED", "WHITE"): (18.011, 12.0, 23.0),
    ("PURPLE", "WHITE"): (4.680, 1.0, 7.0),
    ("WHITE", "RED"): (4.939, 1.0, 8.0),
    ("WHITE", "PURPLE"): (1.773, 0.0, 4.0),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transitions", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.transitions.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    observed = {
        (r["source_state"], r["target_state"]): (
            float(r["mean_transitions"]),
            float(r["hpd_low"]),
            float(r["hpd_high"]),
        )
        for r in rows
    }
    if observed != EXPECTED:
        raise SystemExit(f"published transition table drifted: {observed}")

    red_to_white = EXPECTED[("RED", "WHITE")]
    purple_to_white = EXPECTED[("PURPLE", "WHITE")]
    white_to_red = EXPECTED[("WHITE", "RED")]
    white_to_purple = EXPECTED[("WHITE", "PURPLE")]

    return_mean = red_to_white[0] + purple_to_white[0]
    gain_mean = white_to_red[0] + white_to_purple[0]
    total_mean = return_mean + gain_mean
    nominal_ratio = return_mean / gain_mean
    nominal_return_share = return_mean / total_mean

    # Conservative rectangular sensitivity calculation using marginal HPD endpoints.
    # This is NOT a joint credible interval because covariance among transition counts
    # is unavailable in the publication-level summary.
    return_box_min = red_to_white[1] + purple_to_white[1]
    gain_box_max = white_to_red[2] + white_to_purple[2]
    box_min_ratio = return_box_min / gain_box_max
    box_min_return_share = return_box_min / (return_box_min + gain_box_max)

    red_pair_box_robust = red_to_white[1] > white_to_red[2]
    purple_pair_box_robust = purple_to_white[1] > white_to_purple[2]
    aggregate_box_robust = return_box_min > gain_box_max

    if not math.isclose(total_mean, 29.403, rel_tol=0, abs_tol=1e-12):
        raise SystemExit("reported transition means no longer sum to 29.403")
    if round(total_mean, 1) != 29.4:
        raise SystemExit("published ~29.4 total-transition consistency check failed")
    if not aggregate_box_robust:
        raise SystemExit("aggregate return-to-white direction no longer survives marginal-HPD box sensitivity")
    if not red_pair_box_robust:
        raise SystemExit("red<->white direction no longer survives marginal-HPD box sensitivity")
    if purple_pair_box_robust:
        raise SystemExit("purple<->white pair unexpectedly became box-robust; re-audit source values")

    summary = {
        "version": "v0.1",
        "source_doi": "10.3389/fpls.2021.661522",
        "published_mean_internal_consistency": {
            "summed_transition_mean": total_mean,
            "paper_reported_rounded_total": 29.4,
            "rounded_match": round(total_mean, 1) == 29.4,
        },
        "nominal_direction": {
            "coloured_to_white_mean": return_mean,
            "white_to_coloured_mean": gain_mean,
            "return_gain_ratio": nominal_ratio,
            "return_share": nominal_return_share,
        },
        "marginal_hpd_box_sensitivity": {
            "coloured_to_white_min": return_box_min,
            "white_to_coloured_max": gain_box_max,
            "minimum_return_gain_ratio": box_min_ratio,
            "minimum_return_share": box_min_return_share,
            "aggregate_direction_survives": aggregate_box_robust,
            "red_white_pair_survives": red_pair_box_robust,
            "purple_white_pair_survives": purple_pair_box_robust,
        },
        "interpretation": "RETURN_TO_WHITE_ASYMMETRY_IS_AGGREGATE_AND_STATE_DEPENDENT_NOT_UNIVERSALLY_PAIRWISE",
        "statistical_boundary": "Marginal HPD endpoints are combined as a conservative rectangular sensitivity check only; they are not a joint posterior interval and do not provide a posterior probability for the aggregate ratio.",
        "atlas_reestimate": False,
        "paper1_science_changed": False,
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
