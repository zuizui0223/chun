#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REQUIRED_IDS = {
    "CNG001", "CNG002", "CNG003", "CNG004", "CNG005",
    "CNG006", "CNG007", "CNG008", "CNG009", "CNG010",
}
CNITIDISSIMA_IDS = {"CNG002", "CNG003", "CNG004", "CNG005", "CNG006", "CNG007", "CNG009", "CNG010"}
ALLOWED_DECISIONS = {
    "ecology_context",
    "auxiliary_same_cluster_upstream",
    "grey_literature_same_cluster",
    "already_screened_same_cluster",
    "auxiliary_same_cluster_functional",
    "auxiliary_functional_no_colour_contrast",
    "auxiliary_same_cluster_regulator",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit("Chinese/grey literature screen is empty")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--screen", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    rows = read_rows(args.screen)
    ids = [r["screen_id"].strip() for r in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate screen_id")
    if set(ids) != REQUIRED_IDS:
        raise SystemExit(f"required screen set drift: observed={sorted(ids)}")

    by_id = {r["screen_id"]: r for r in rows}
    invalid_decisions = {r["screen_id"]: r["decision"] for r in rows if r["decision"] not in ALLOWED_DECISIONS}
    if invalid_decisions:
        raise SystemExit(f"invalid decisions: {invalid_decisions}")

    new_clusters = [r["screen_id"] for r in rows if r["eligible_new_directional_cluster"].strip().lower() != "no"]
    if new_clusters:
        raise SystemExit(f"unexpected new directional cluster(s): {new_clusters}")
    cf = [r["screen_id"] for r in rows if r["candidate_free_eligible"].strip().lower() != "no"]
    if cf:
        raise SystemExit(f"unexpected candidate-free admission(s): {cf}")

    for sid in CNITIDISSIMA_IDS:
        row = by_id[sid]
        if row["taxon"] != "Camellia nitidissima" or row["independence_cluster"] != "CNITIDISSIMA":
            raise SystemExit(f"{sid}: C. nitidissima dependence-cluster drift")

    if by_id["CNG005"]["afcp_axis_if_any"] != "F":
        raise SystemExit("CnFLS1 must remain direct F-axis feasibility evidence")
    if by_id["CNG008"]["afcp_axis_if_any"] != "P":
        raise SystemExit("CoANR must remain direct P-axis feasibility evidence")
    if by_id["CNG001"]["decision"] != "ecology_context" or by_id["CNG001"]["ecology_role"] != "historical_pollinator_identity":
        raise SystemExit("Wu1977 ecology classification drift")
    if by_id["CNG004"]["source_type"] != "doctoral_thesis":
        raise SystemExit("2012 thesis source-type drift")

    summary = {
        "status": "paper1_chinese_grey_screen_v0_1_valid",
        "records": len(rows),
        "cnitidissima_same_background_records": len(CNITIDISSIMA_IDS),
        "new_independent_directional_afcp_clusters": 0,
        "new_candidate_free_systems": 0,
        "historical_ecology_context_records": 1,
        "science_v0_2_1_changed": False,
        "ajb_v0_8_reopened": False,
        "claim_boundary": "indexed Chinese-language/thesis screen; not a formal exhaustive CNKI/Wanfang export",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
