#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v02", type=Path, required=True)
    ap.add_argument("--cleanup", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    a = ap.parse_args()

    text = a.v02.read_text(encoding="utf-8")
    spec = json.loads(a.cleanup.read_text(encoding="utf-8"))
    applied = []
    for row in spec["replacements"]:
        old = row["old"]
        new = row["new"]
        n = text.count(old)
        if n != 1:
            raise SystemExit(f"{row['id']}: expected exactly one match, found {n}")
        text = text.replace(old, new, 1)
        applied.append(row["id"])

    open_marker = "# OPEN ITEMS FOR v0.3"
    if open_marker not in text:
        raise SystemExit("submission cleanup could not locate OPEN ITEMS marker")
    text = text.split(open_marker, 1)[0].rstrip() + "\n"
    text = text.replace("# REFERENCES — v0.2 verified core set", "# LITERATURE CITED", 1)

    forbidden = [
        "Draft v0.2",
        "# OPEN ITEMS",
        "`data/",
        "`docs/",
        "`scripts/",
        "GitHub Actions",
        "final manuscript should provide",
        "PR #",
        "PR#",
    ]
    for token in forbidden:
        if token in text:
            raise SystemExit(f"submission-clean output retains internal token: {token}")

    required = [
        "Supplementary Table S1",
        "Supplementary Table S2",
        "Supplementary Table S3",
        "Supplementary Tables S2–S4",
        "Supplementary Tables S5–S6",
        "Supplementary Figures S1–S3",
        "[ARCHIVE DOI TO ADD AT SUBMISSION]",
        "# LITERATURE CITED",
    ]
    for token in required:
        if token not in text:
            raise SystemExit(f"submission-clean output missing required token: {token}")

    if text.count("[ARCHIVE DOI TO ADD AT SUBMISSION]") != 1:
        raise SystemExit("expected exactly one archive DOI placeholder")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(text, encoding="utf-8")
    summary = {
        "submission_version": "v0.3",
        "source": str(a.v02),
        "cleanup_spec": str(a.cleanup),
        "applied_cleanup_rules": applied,
        "internal_tokens_absent": True,
        "supplementary_references_present": True,
        "archive_doi_placeholders": 1,
        "scientific_results_changed": False,
        "status": "submission-clean build passed",
    }
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
