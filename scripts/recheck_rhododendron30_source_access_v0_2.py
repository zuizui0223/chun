#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "scripts/run_rhododendron30_source_preflight_v0_1.py"
LEGACY_OUT = ROOT / "build/rhododendron30_source_preflight_v0_1.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    subprocess.run([sys.executable, str(LEGACY)], cwd=ROOT, check=True)
    x = json.loads(LEGACY_OUT.read_text(encoding="utf-8"))

    trait_attempts = [
        {
            "url": q["url"],
            "http_status": q["http_status"],
            "is_docx_payload": q["is_docx_payload"],
            "downloaded_bytes": q["downloaded_bytes"],
            "content_type": q["content_type"],
            "reason": q["reason"],
        }
        for q in x["trait_receipt"]["attempts"]
    ]
    tree = x["tree_receipt"]
    pass_now = x["status"] == "PASS_CROSSWALK_PREFLIGHT_OUTCOMES_UNOPENED"

    if pass_now:
        status = "SOURCE_ACCESS_AND_CROSSWALK_PASS_CHEMISTRY_STILL_UNOPENED"
        decision = "OPEN_NEXT_GATE_FREEZE_SOURCE_HASH_AND_CROSSWALK_BEFORE_TABLE_S1_CHEMISTRY"
    else:
        status = "HOLD_SOURCE_ACCESS_STILL_BLOCKED_OUTCOMES_UNOPENED"
        decision = "STOP_HOLD_DO_NOT_OPEN_TABLE_S1_CHEMISTRY"

    out = {
        "version": "v0.2",
        "status": status,
        "legacy_preflight_status": x["status"],
        "trait_source_doi": x["trait_source_doi"],
        "trait_species_supplement": x["trait_species_supplement"],
        "trait_attempts": trait_attempts,
        "trait_species_count": x["crosswalk"]["trait_species_count"],
        "primary_tree": {
            "doi": tree["doi"],
            "file": tree["file"],
            "file_id": tree["file_id"],
            "api_size": tree["api_size"],
            "digest_type_api": tree["digest_type_api"],
            "digest_api": tree["digest_api"],
            "public_route_http_status": tree["public_route_http_status"],
            "public_route_content_type": tree["public_route_content_type"],
            "downloaded_bytes": tree["downloaded_bytes"],
            "digest_match": tree["digest_match"],
            "treeish_payload": tree["treeish_payload"],
        },
        "crosswalk": x["crosswalk"],
        "outcome_firewall": x["outcome_firewall"],
        "chemistry_opened": False,
        "profile_auc_computed": False,
        "decision": decision,
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "legacy_preflight_status": x["status"],
        "trait_species_count": out["trait_species_count"],
        "trait_http": [q["http_status"] for q in trait_attempts],
        "tree_http": out["primary_tree"]["public_route_http_status"],
        "tree_digest_match": out["primary_tree"]["digest_match"],
        "treeish_payload": out["primary_tree"]["treeish_payload"],
        "crosswalk_matches": out["crosswalk"]["exact_normalized_matches"],
        "profile_auc_computed": False,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
