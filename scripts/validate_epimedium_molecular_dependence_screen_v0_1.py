#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--screen", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.screen.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    if len(rows) != 8:
        raise SystemExit(f"expected 8 molecular taxa, found {len(rows)}")

    minus = [r for r in rows if r["molecular_anthocyanin_state"] == "A_MINUS"]
    plus = [r for r in rows if r["molecular_anthocyanin_state"] == "A_PLUS"]
    if len(minus) != 4 or len(plus) != 4:
        raise SystemExit(f"expected 4 A- and 4 A+, found {len(minus)} and {len(plus)}")

    loss_clusters = {r["conservative_dependence_cluster"] for r in minus}
    if loss_clusters != {"LOSS_FRC_COMPLEX", "LOSS_EAST_AMBIGUOUS"}:
        raise SystemExit(f"unexpected conservative loss clusters: {sorted(loss_clusters)}")

    if len(loss_clusters) >= 3:
        raise SystemExit("strict gate should not pass with current evidence")

    ep = [r for r in rows if r["taxon"] == "Epimedium epsteinii"]
    if len(ep) != 1:
        raise SystemExit("Epimedium epsteinii normalization missing")

    summary = {
        "screen_version": "v0.1",
        "molecular_taxa": len(rows),
        "a_plus_taxa": len(plus),
        "a_minus_taxa": len(minus),
        "conservative_loss_clusters": len(loss_clusters),
        "required_independent_clusters": 3,
        "mechanistic_anchor_gate": "FAIL_HOLD",
        "retained_role": "MECHANISTIC_SUPPORT_WITH_EVENT_IDENTITY_LIMIT",
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
