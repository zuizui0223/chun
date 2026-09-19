#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

EXPECTED = {
    "Eriolarynx fasciculata": ("purple", "white", 3, 3, 1.8, 225),
    "Iochroma calycinum": ("purple", "white", 3, 1, 0.9, 225),
    "Iochroma cyaneum": ("purple", "white", 3, 2, 1.3, 150),
    "Iochroma parvifolium": ("purple", "yellow", 3, 1, 1.3, 75),
    "Iochroma umbellatum": ("purple", "white", 3, 3, 57.0, 200),
    "Saracha punctata": ("purple", "white", 3, 2, 33.0, 150),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=Path, required=True)
    ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.seed.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 6:
        raise SystemExit(f"expected six polymorphic species, found {len(rows)}")
    names = {r["taxon"] for r in rows}
    if names != set(EXPECTED):
        raise SystemExit(f"unexpected taxa: {sorted(names ^ set(EXPECTED))}")

    freqs = []
    for r in rows:
        e = EXPECTED[r["taxon"]]
        observed = (
            r["pigmented_morph"], r["acyanic_morph"],
            int(r["pigmented_n_sampled"]), int(r["acyanic_n_sampled"]),
            float(r["estimated_acyanic_frequency_pct"]), int(r["frequency_survey_n"]),
        )
        if observed != e:
            raise SystemExit(f"published seed mismatch for {r['taxon']}: {observed} != {e}")
        freqs.append(observed[4])
    if not any(r["acyanic_morph"] == "yellow" for r in rows):
        raise SystemExit("yellow acyanic morph must not be collapsed to white")

    with a.bundle.open(newline="", encoding="utf-8") as fh:
        b = list(csv.DictReader(fh))
    required_ids = {"IOCHROMINAE_DVDY_2019", "IOCHROMINAE_DVDY_README"}
    if not required_ids.issubset({r["source_id"] for r in b}):
        raise SystemExit("Dryad archive/README contract incomplete")
    for r in b:
        if r["status"].startswith("REMOTE_VERIFIED") and r["checksum_type"] == "NA" and r["expected_checksum"] != "NA":
            raise SystemExit("checksum must remain NA when not published")

    summary = {
        "version": "v0.1",
        "published_polymorphic_species": len(rows),
        "acyanic_frequency_min_pct": min(freqs),
        "acyanic_frequency_max_pct": max(freqs),
        "dryad_bundle_identity_gate": "PASS_REMOTE_ONLY",
        "row_level_raw_ingestion_gate": "BLOCKED_PENDING_BINARY_INGESTION",
        "published_seed_gate": "PASS",
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
