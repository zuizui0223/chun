#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "scripts/preflight_iochrominae_biochemical_profile_source_v0_1.py"
LEGACY_OUT = ROOT / "build/iochrominae_biochemical_profile_source_preflight_v0_1.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    subprocess.run([sys.executable, str(LEGACY)], cwd=ROOT, check=True)
    x = json.loads(LEGACY_OUT.read_text(encoding="utf-8"))

    objects = {}
    for name, rec in x["file_receipts"].items():
        objects[name] = {
            "file_id": rec["file_id"],
            "size": rec["size"],
            "digest_type_api": rec["digest_type_api"],
            "digest_api": rec["digest_api"],
            "recovered": rec["recovered"],
            "recovered_via": rec["recovered_via"],
            "attempts": [
                {
                    "route": q["route"],
                    "http_status": q["http_status"],
                    "downloaded_bytes": q["downloaded_bytes"],
                    "html_payload": q["html_payload"],
                    "digest_match": q["digest_match"],
                    "reason": q["reason"],
                }
                for q in rec["attempts"]
            ],
        }

    all_recovered = all(v["recovered"] for v in objects.values())
    api_statuses = sorted({
        q["http_status"]
        for v in objects.values()
        for q in v["attempts"]
        if q["route"] == "api_file_download" and q["http_status"] is not None
    })
    stream_statuses = sorted({
        q["http_status"]
        for v in objects.values()
        for q in v["attempts"]
        if q["route"] == "public_file_stream" and q["http_status"] is not None
    })

    if all_recovered:
        status = "SOURCE_BYTES_ACQUIRED_SCHEMA_INSPECTION_ALLOWED_PROFILE_UNCOMPUTED"
        interpretation = "The exact Dryad README and DATA.rar bytes are now recoverable; next step is README/member-name inspection only before any profile-state mapping is frozen."
    else:
        status = "HOLD_DRYAD_SOURCE_BYTES_STILL_UNAVAILABLE_PROFILE_UNCOMPUTED"
        interpretation = "Dryad metadata and exact object identity remain public, but the exact file bytes are not recoverable by the admitted anonymous routes in this execution environment. This is a transport/access hold, not a biological negative."

    out = {
        "version": "v0.2",
        "source_doi": x["source_doi"],
        "dataset_version_number": x["dataset_version_number"],
        "status": status,
        "legacy_preflight_status": x["status"],
        "objects": objects,
        "api_file_download_http_statuses": api_statuses,
        "public_file_stream_http_statuses": stream_statuses,
        "all_exact_objects_recovered": all_recovered,
        "archive_data_rows_opened": False,
        "profile_state_mapping_frozen": False,
        "profile_states_computed": False,
        "patristic_distances_computed": False,
        "profile_auc_computed": False,
        "winner_computed": False,
        "interpretation": interpretation,
        "next_gate": "IF_AND_ONLY_IF_BOTH_EXACT_OBJECTS_RECOVERED_LIST_ARCHIVE_MEMBER_NAMES_AND_READ_README_BEFORE_FREEZING_STATE_MAPPING",
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "all_exact_objects_recovered": all_recovered,
        "api_file_download_http_statuses": api_statuses,
        "public_file_stream_http_statuses": stream_statuses,
        "objects": {k: {"file_id": v["file_id"], "recovered": v["recovered"]} for k, v in objects.items()},
        "profile_auc_computed": False,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
