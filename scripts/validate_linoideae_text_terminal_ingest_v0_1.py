#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

EXPECTED = {
    "Linum decumbens": "RED",
    "Linum grandiflorum": "RED",
    "Linum viscosum": "PINK",
    "Linum pubescens": "PINK",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--states", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.states.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    got = {r["accepted_taxon"]: r["visible_state"] for r in rows}
    if got != EXPECTED or len(rows) != len(EXPECTED):
        raise SystemExit(f"explicit terminal set drifted: {got}")
    if any(r["display_organ"] != "COROLLA" for r in rows):
        raise SystemExit("Linoideae source study codes corolla flower colour")
    if any(r["source_doi"] != "10.3390/plants11121579" for r in rows):
        raise SystemExit("source DOI drift")
    if any(r["agreement_status"] != "SOURCE_TEXT_EXPLICIT" for r in rows):
        raise SystemExit("all admitted rows must remain explicit primary-text assertions")
    if any(r["phylogeny_tip"] != "UNRESOLVED_TO_EXACT_TREE_TIP" for r in rows):
        raise SystemExit("exact tree-tip mapping must not be invented")
    if any(r["include_macro"] != "0" for r in rows):
        raise SystemExit("partial text recovery cannot enter atlas ASR")

    counts = Counter(r["visible_state"] for r in rows)
    summary = {
        "version": "v0.1",
        "source_backed_terminal_taxa": len(rows),
        "visible_states": dict(sorted(counts.items())),
        "published_terminal_matrix_size": 112,
        "source_text_coverage_fraction": len(rows) / 112,
        "exact_tip_mapping_status": "PENDING",
        "terminal_matrix_status": "PARTIAL_SOURCE_RECOVERY",
        "macro_rows_ready": 0,
        "atlas_asr_status": "NOT_RUN",
        "minimum_provenance_coverage": 0.80,
        "full_matrix_needed_for_common_model": True,
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
