#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transitions", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.transitions.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 4:
        raise SystemExit(f"expected four frozen transition rows, found {len(rows)}")

    vals = {}
    for r in rows:
        key = (r["source_state"], r["target_state"])
        if key in vals:
            raise SystemExit(f"duplicate transition {key}")
        vals[key] = float(r["mean_transitions"])

    expected = {("RED", "WHITE"), ("PURPLE", "WHITE"), ("WHITE", "RED"), ("WHITE", "PURPLE")}
    if set(vals) != expected:
        raise SystemExit(f"transition set drift: {sorted(vals)}")

    to_white = vals[("RED", "WHITE")] + vals[("PURPLE", "WHITE")]
    from_white = vals[("WHITE", "RED")] + vals[("WHITE", "PURPLE")]
    total = to_white + from_white
    ratio = to_white / from_white

    summary = {
        "version": "v0.1",
        "source": "published stochastic-mapping means; QC target only",
        "source_doi": "10.3389/fpls.2021.661522",
        "coloured_to_white_mean": round(to_white, 3),
        "white_to_coloured_mean": round(from_white, 3),
        "total_directional_changes_mean": round(total, 3),
        "return_to_white_ratio": round(ratio, 6),
        "fraction_changes_toward_white": round(to_white / total, 6),
        "directional_gain_hypothesis": "FALSIFICATION_TARGET",
        "atlas_reconstruction_complete": False,
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
