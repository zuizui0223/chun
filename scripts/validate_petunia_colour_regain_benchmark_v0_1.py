#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", type=Path, required=True)
    ap.add_argument("--sources", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.events.open(newline="", encoding="utf-8") as fh:
        events = list(csv.DictReader(fh))
    if len(events) != 2:
        raise SystemExit(f"expected exactly two frozen regain events, found {len(events)}")
    if {r["target_taxon"] for r in events} != {"Petunia secreta", "Petunia exserta"}:
        raise SystemExit("expected P. secreta and P. exserta regain events")
    if any(r["event_independence"] != "INDEPENDENT_REGAIN" for r in events):
        raise SystemExit("both events must be frozen as independent regains")
    if any(r["source_visible_state"] != "colorless/white" for r in events):
        raise SystemExit("both events must originate from the frozen colorless/white context")
    if any(r["molecular_target_class"] != "PATHWAY_SPECIFIC_REGULATOR" for r in events):
        raise SystemExit("high-level shared regulator class must be explicit")

    sec = next(r for r in events if r["target_taxon"] == "Petunia secreta")
    exs = next(r for r in events if r["target_taxon"] == "Petunia exserta")
    if sec["primary_gene_or_module"] != "AN2":
        raise SystemExit("P. secreta AN2 resurrection missing")
    if exs["primary_gene_or_module"] != "DPL":
        raise SystemExit("P. exserta DPL redeployment missing")
    required_exs = ["COPIGMENT/FLUX", "BRANCH", "PIGMENT_MODIFICATION"]
    if not all(x in exs["additional_modules"] for x in required_exs):
        raise SystemExit("P. exserta complex additional modules incomplete")

    with a.sources.open(newline="", encoding="utf-8") as fh:
        sources = list(csv.DictReader(fh))
    if {r["source_id"] for r in sources} != {"PETUNIA_SECRETA_2018", "PETUNIA_EXSERTA_2021"}:
        raise SystemExit("source contract incomplete")
    ex_source = next(r for r in sources if r["source_id"] == "PETUNIA_EXSERTA_2021")
    if ex_source["data_doi"] != "10.5061/dryad.jsxksn083":
        raise SystemExit("P. exserta Dryad identity mismatch")

    summary = {
        "version": "v0.1",
        "independent_regain_events": 2,
        "standalone_minimum_for_recurrence_estimator": 3,
        "standalone_recurrence_gate": "FAIL_EVENT_COUNT",
        "shared_high_level_class": "PATHWAY_SPECIFIC_REGULATOR",
        "complete_programme_identity": "NOT_SUPPORTED_AND_NOT_FULLY_OBSERVED",
        "atlas_role": "WHITE_BASELINE_REGAIN_MECHANISTIC_BENCHMARK",
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
