#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.source.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 20:
        raise SystemExit(f"expected frozen 20-cell candidate-free table, got {len(rows)}")

    out = []
    for r in rows:
        out.append({
            "measurement_id": f"{r['transition_class']}::{r['dependence_cluster']}::{r['axis']}",
            "dependence_cluster": r["dependence_cluster"],
            "transition_class": r["transition_class"],
            "axis": r["axis"],
            "direction": r["direction"],
            "status": r["status"],
            "source": f"paper1_fig2_candidate_free_signature_v0_2.csv;run={r['source_run']}",
        })

    expected = {
        ("anthocyanin_gain", "CJAPONICA"),
        ("anthocyanin_gain", "CRETICULATA"),
        ("anthocyanin_gain", "CSIN_WHITE_PINK"),
        ("yellow_development", "CNITIDISSIMA"),
        ("yellow_development", "CPERPETUA"),
    }
    if {(r["transition_class"], r["dependence_cluster"]) for r in out} != expected:
        raise SystemExit("candidate-free common-set drift")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(f"wrote {len(out)} frozen candidate-free measurements to {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
