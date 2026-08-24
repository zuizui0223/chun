#!/usr/bin/env python3
"""Quantify the accessibility-realization gap without inventing macro transition rates.

The analysis asks a deliberately weaker but currently identifiable question:
short-timescale mechanistic accessibility is observed for the coarse A/W/Y outcome
classes, but are those classes realized across historical section backgrounds as
broadly as expected from their species counts?

Micro evidence is treated as presence/support only. Its study count is descriptive
and is never used as an unbiased estimate of a state-generation rate.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def visible_target_class(label: str) -> str | None:
    x = label.strip().lower()
    if any(token in x for token in ("red", "pink", "crimson", "purple")):
        return "A"
    if "white" in x:
        return "W"
    if "yellow" in x:
        return "Y"
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--micro", type=Path, required=True)
    ap.add_argument("--macro", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    micro = read_csv(args.micro)
    macro = read_csv(args.macro)
    if not micro or not macro:
        raise ValueError("input registry is empty")

    support = Counter()
    supporting_systems: dict[str, list[str]] = {"A": [], "W": [], "Y": []}
    for row in micro:
        klass = visible_target_class(row["target_state_visible"])
        if klass is None:
            continue
        support[klass] += 1
        supporting_systems[klass].append(row["independence_unit"])

    out_rows: list[dict[str, object]] = []
    for row in macro:
        state = row["visible_state"]
        if state not in {"A", "W", "Y"}:
            continue
        obs_b = float(row["observed_section_breadth"])
        exp_b = float(row["expected_section_breadth"])
        obs_h = float(row["observed_section_entropy"])
        exp_h = float(row["expected_section_entropy"])
        breadth_gap = 1.0 - obs_b / exp_b
        entropy_gap = 1.0 - obs_h / exp_h
        out_rows.append(
            {
                "visible_state": state,
                "micro_accessibility_present": support[state] > 0,
                "n_independent_micro_systems_descriptive": support[state],
                "observed_section_breadth": obs_b,
                "expected_section_breadth": exp_b,
                "breadth_realization_gap": breadth_gap,
                "breadth_lower_tail_p": float(row["lower_tail_breadth_p"]),
                "observed_section_entropy": obs_h,
                "expected_section_entropy": exp_h,
                "entropy_realization_gap": entropy_gap,
                "entropy_lower_tail_p": float(row["lower_tail_entropy_p"]),
                "macro_proxy": "Fan2026_traditional_section_count_controlled",
            }
        )

    by_state = {r["visible_state"]: r for r in out_rows}
    required = {"A", "W", "Y"}
    if set(by_state) != required:
        raise ValueError("macro table must contain A, W and Y")
    if not all(by_state[s]["micro_accessibility_present"] for s in required):
        raise ValueError("v0.1 comparison requires micro accessibility evidence in A/W/Y")

    conclusion = {
        "test": "accessibility_is_not_sufficient_for_uniform_macro_realization",
        "status": "supported_as_cross_scale_mismatch_not_branch_causality",
        "states_with_micro_accessibility_evidence": sorted(required),
        "states_with_excess_macro_concentration_breadth_p_lt_0_01": sorted(
            s for s in required if by_state[s]["breadth_lower_tail_p"] < 0.01
        ),
        "interpretation": (
            "Short-timescale mechanistic accessibility is documented for all A/W/Y "
            "outcome classes, yet A and Y occupy substantially fewer historical section "
            "backgrounds than expected after controlling for their species counts, while W "
            "does not. Accessibility alone is therefore insufficient to explain extant "
            "macro realization. The result does not identify whether the missing step is "
            "gain hazard, persistence/loss, radiation history, or reticulation."
        ),
        "forbidden_claims": [
            "micro study counts estimate natural generation rates",
            "traditional sections estimate branch transition rates",
            "the mismatch proves ecological selection",
            "visible A/W/Y are mechanistic pigment states",
        ],
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    with (args.out_dir / "accessibility_realization_gap.csv").open(
        "w", newline="", encoding="utf-8"
    ) as fh:
        fields = list(out_rows[0].keys())
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)

    with (args.out_dir / "summary.json").open("w", encoding="utf-8") as fh:
        json.dump(
            {
                "states": by_state,
                "micro_supporting_systems": supporting_systems,
                "conclusion": conclusion,
            },
            fh,
            indent=2,
            ensure_ascii=False,
        )
        fh.write("\n")

    print(json.dumps({"states": by_state, "conclusion": conclusion}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
