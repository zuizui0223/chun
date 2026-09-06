#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REQUIRED = {"evidence_layer", "source_id", "observed_value", "status", "notes"}
REQUIRED_LAYERS = {
    "PHYLOGENY", "RNA_SAMPLING", "PROCESSED_DATA", "PIGMENT_CHEMISTRY",
    "EXPRESSION_MODULES", "ANCESTRAL_BASELINE", "REPEATED_TRANSITIONS",
    "VISIBLE_STATES", "SOURCE_CROSSWALK", "HISTORICAL_EVENT_IDENTITY",
    "ANCHOR_DECISION",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.registry.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise SystemExit("missing header")
        missing = REQUIRED.difference(reader.fieldnames)
        if missing:
            raise SystemExit(f"missing columns: {sorted(missing)}")
        rows = list(reader)

    by = {r["evidence_layer"]: r for r in rows}
    if set(by) != REQUIRED_LAYERS:
        raise SystemExit(f"evidence-layer drift: {sorted(set(by) ^ REQUIRED_LAYERS)}")

    if "59 Petunieae species" not in by["PHYLOGENY"]["observed_value"]:
        raise SystemExit("phylogeny taxon contract drift")
    if "3672 gene trees" not in by["PHYLOGENY"]["observed_value"]:
        raise SystemExit("phylogeny gene-tree contract drift")
    if by["RNA_SAMPLING"]["source_id"] != "PRJNA746328":
        raise SystemExit("raw RNA-seq BioProject drift")
    if "3 biological replicates per species" not in by["RNA_SAMPLING"]["observed_value"]:
        raise SystemExit("replication contract drift")
    if by["PROCESSED_DATA"]["source_id"] != "https://osf.io/zg9cu/":
        raise SystemExit("OSF processed-data source drift")
    if "6 anthocyanidins" not in by["PIGMENT_CHEMISTRY"]["observed_value"]:
        raise SystemExit("anthocyanidin chemistry contract drift")
    if "kaempferol/quercetin/myricetin" not in by["PIGMENT_CHEMISTRY"]["observed_value"]:
        raise SystemExit("flavonol chemistry contract drift")
    baseline = by["ANCESTRAL_BASELINE"]["observed_value"]
    if "pale-flowered" not in baseline or "high-flavonol" not in baseline:
        raise SystemExit("ancestral baseline must remain pale/high-flavonol, not be simplified to white")
    if "4-5 transitions" not in by["REPEATED_TRANSITIONS"]["observed_value"]:
        raise SystemExit("source recurrence admission drift")
    if by["HISTORICAL_EVENT_IDENTITY"]["status"] != "PENDING":
        raise SystemExit("historical event identity must remain pending until atlas remapping")
    if by["ANCHOR_DECISION"]["status"] != "PASS_TO_EVENT_MAPPING":
        raise SystemExit("Petunieae source admission decision drift")

    summary = {
        "screen_version": "v0.1",
        "evidence_layers": len(rows),
        "source_data_admission": "PASS",
        "raw_sra": "PRJNA746328",
        "processed_repo": "https://osf.io/zg9cu/",
        "ancestral_baseline": "PALE_LOW_VISIBLE_PIGMENT",
        "source_repeated_transition_signal": "4_TO_5_INTENSE_PURPLE_TRANSITIONS",
        "atlas_event_identity": "PENDING_REANALYSIS",
        "mechanistic_anchor_status": "ADMITTED_PENDING_EVENT_MAPPING",
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
