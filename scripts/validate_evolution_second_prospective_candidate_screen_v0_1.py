#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/evolution_second_prospective_candidate_screen_v0_1.csv"
DOC = ROOT / "docs/EVOLUTION_SECOND_PROSPECTIVE_CANDIDATE_SCREEN_V0_1.md"

EXPECTED = {
    "Ruellia": "HOLD_MATCHED_MOLECULAR_PANEL_TOO_SMALL",
    "Rhododendron": "HOLD_MATCHED_MOLECULAR_PANEL_TOO_SMALL",
    "Gesnerioideae": "HOLD_NO_MATCHED_RADIATION_WIDE_MOLECULAR_PANEL",
    "Antirrhineae": "HOLD_MOLECULAR_EVIDENCE_DEPENDENCE_COLLAPSE",
    "Mimulus": "HOLD_MECHANISTIC_STUDIES_NOT_RADIATION_WIDE_MATCHED_PANEL",
    "Aquilegia": "HOLD_HUE_AXIS_NOT_MATCHED_DIRECTLY",
}


def main() -> None:
    assert LEDGER.is_file(), LEDGER
    assert DOC.is_file(), DOC
    rows = list(csv.DictReader(LEDGER.open(encoding="utf-8")))
    assert len(rows) == 6, len(rows)
    assert {r["candidate"] for r in rows} == set(EXPECTED)
    for row in rows:
        name = row["candidate"]
        assert row["status"] == EXPECTED[name], (name, row["status"])
        assert row["prospective_full_bridge_eligible"] == "FALSE", name
        # A second prospective decisive bridge may not be admitted by lowering
        # the post-Petunieae matched-frame requirement.
        assert row["matched_taxa_ge30"] == "FALSE", name
        assert row["primary_failure"].strip(), name
        assert row["source_evidence"].strip(), name

    text = DOC.read_text(encoding="utf-8")
    required = [
        "No candidate passes the frozen second-prospective admission rule.",
        "NO_SECOND_PROSPECTIVE_FULL_BRIDGE_CANDIDATE_ADMITTED_UNDER_FROZEN_SCREEN",
        "Do not lower the >=30 matched-taxon criterion",
        "Do not convert retrospective Iochrominae/Cape Erica evidence into prospective replication.",
        "Evolution escalation remains HOLD.",
        "This candidate screen is closed after the six named candidates.",
        "Paper 1 remains unchanged.",
    ]
    for token in required:
        assert token in text, token

    forbidden = [
        "Evolution escalation PASS",
        "prospective full-bridge PASS count = 1",
        "AJB is displaced",
    ]
    for token in forbidden:
        assert token not in text, token

    print(
        {
            "candidate_count": len(rows),
            "admitted_count": 0,
            "status": "NO_SECOND_PROSPECTIVE_FULL_BRIDGE_CANDIDATE_ADMITTED_UNDER_FROZEN_SCREEN",
            "paper1_changed": False,
        }
    )


if __name__ == "__main__":
    main()
