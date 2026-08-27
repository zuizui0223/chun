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
    args = ap.parse_args()

    with args.screen.open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 23:
        raise SystemExit(f"expected 23 priority-screen rows, found {len(rows)}")
    ids = [r["candidate_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate citation-chase candidate_id")

    if any(r["new_independent_directional_afcp_cluster"].lower() != "no" for r in rows):
        raise SystemExit("citation chasing unexpectedly added an independent directional A/F/C/P cluster")
    if any(r["candidate_free_addition"].lower() != "no" for r in rows):
        raise SystemExit("citation chasing unexpectedly added a candidate-free system")

    admitted = [r for r in rows if r["decision"] == "admit_same_cluster_literature_update"]
    if len(admitted) != 1:
        raise SystemExit(f"expected one literature-side update, found {len(admitted)}")
    luo = admitted[0]
    if luo["doi_or_resolved_doi"].lower() != "10.3389/fpls.2015.01257" or luo["independence_cluster"] != "CJAPONICA":
        raise SystemExit(f"Luo decision drift: {luo}")

    summary = {
        "status": "paper1_citation_chase_priority_screen_v0_1_valid",
        "screened_priority_rows": len(rows),
        "new_independent_directional_afcp_clusters": 0,
        "new_candidate_free_systems": 0,
        "literature_side_updates": 1,
        "luo2016_cluster": "CJAPONICA",
        "science_consequence": "literature-side CJAPONICA F resolved; handled by versioned science recheck",
        "claim_boundary": "citation retrieval and screen do not auto-admit candidate-free evidence",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
