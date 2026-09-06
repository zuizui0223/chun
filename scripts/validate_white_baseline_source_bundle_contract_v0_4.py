#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

REQUIRED = {
    "clade_id", "source_doi", "expected_filename_or_attachment",
    "reported_display_size", "checksum_type", "expected_checksum", "license",
    "required_content", "bundle_status",
}
MD5_RE = re.compile(r"^[0-9a-f]{32}$")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    with a.contract.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise SystemExit("missing header")
        missing = REQUIRED.difference(reader.fieldnames)
        if missing:
            raise SystemExit(f"missing columns: {sorted(missing)}")
        rows = list(reader)

    if not rows:
        raise SystemExit("empty contract")

    for i, r in enumerate(rows, start=2):
        if r["bundle_status"] not in {"REMOTE_VERIFIED_NOT_INGESTED", "INGESTED_VERIFIED"}:
            raise SystemExit(f"row {i}: invalid bundle_status")
        ctype = r["checksum_type"]
        chk = r["expected_checksum"]
        if ctype == "MD5" and not MD5_RE.fullmatch(chk):
            raise SystemExit(f"row {i}: invalid MD5")
        if ctype == "NA" and chk != "NA":
            raise SystemExit(f"row {i}: checksum must be NA when checksum_type is NA")
        if not r["required_content"].strip():
            raise SystemExit(f"row {i}: required_content is empty")

    anti = [r for r in rows if r["clade_id"] == "ANTIRRHINEAE"]
    if len(anti) != 1 or anti[0]["expected_checksum"] != "950f85b80427d357bfeff09608ba02e9":
        raise SystemExit("Antirrhineae verified source checksum drift")

    summary = {
        "version": "v0.4",
        "contracts": len(rows),
        "remote_verified_not_ingested": sum(r["bundle_status"] == "REMOTE_VERIFIED_NOT_INGESTED" for r in rows),
        "ingested_verified": sum(r["bundle_status"] == "INGESTED_VERIFIED" for r in rows),
        "source_identity_gate": "PASS",
        "raw_bundle_ingestion_gate": "BLOCKED_UNTIL_BINARY_AVAILABLE",
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
