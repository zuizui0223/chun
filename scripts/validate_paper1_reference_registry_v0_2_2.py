#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

DOI_RE = re.compile(r"https://doi\.org/([^\s)]+)", re.IGNORECASE)


def norm(value: str) -> str:
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value.strip(), flags=re.IGNORECASE)
    return value.rstrip(".,; ").lower()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--manuscript", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    with args.registry.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 17:
        raise SystemExit(f"science v0.2.2 reference registry must contain 17 rows, found {len(rows)}")
    ids = [r["reference_id"].strip() for r in rows]
    dois = [norm(r["doi"]) for r in rows]
    if len(ids) != len(set(ids)) or len(dois) != len(set(dois)):
        raise SystemExit("duplicate reference id or DOI")

    text = args.manuscript.read_text(encoding="utf-8")
    if "# LITERATURE CITED" not in text:
        raise SystemExit("generated science manuscript lacks LITERATURE CITED")
    manuscript_dois = [norm(x) for x in DOI_RE.findall(text.split("# LITERATURE CITED", 1)[1])]
    if len(manuscript_dois) != 17 or set(manuscript_dois) != set(dois):
        raise SystemExit(
            f"science reference mismatch: manuscript={len(manuscript_dois)} registry={len(dois)} "
            f"missing_from_manuscript={sorted(set(dois)-set(manuscript_dois))} "
            f"missing_from_registry={sorted(set(manuscript_dois)-set(dois))}"
        )
    for required in ("10.1007/s10722-025-02606-6", "10.3389/fpls.2015.01257"):
        if required not in set(dois):
            raise SystemExit(f"required literature-update DOI missing: {required}")

    summary = {
        "status": "paper1_science_reference_registry_v0_2_2_valid",
        "registry_rows": 17,
        "manuscript_reference_dois": 17,
        "csemiserrata_present": True,
        "luo2016_present": True,
        "registry_matches_generated_manuscript": True,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
