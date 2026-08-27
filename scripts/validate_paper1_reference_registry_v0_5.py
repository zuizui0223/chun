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
    a = ap.parse_args()

    with a.registry.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 25:
        raise SystemExit(f"reference v0.5 must contain 25 rows, found {len(rows)}")
    ids = [r["reference_id"].strip() for r in rows]
    dois = [norm(r["doi"]) for r in rows]
    if len(ids) != len(set(ids)) or len(dois) != len(set(dois)):
        raise SystemExit("duplicate reference id or DOI")

    text = a.manuscript.read_text(encoding="utf-8")
    if "# LITERATURE CITED" not in text:
        raise SystemExit("framed manuscript lacks LITERATURE CITED")
    ref_text = text.split("# LITERATURE CITED", 1)[1]
    if "\n# " in ref_text:
        ref_text = ref_text.split("\n# ", 1)[0]
    manuscript_dois = [norm(x) for x in DOI_RE.findall(ref_text)]
    if len(manuscript_dois) != 25 or set(manuscript_dois) != set(dois):
        raise SystemExit(
            f"reference mismatch: manuscript={len(manuscript_dois)} registry={len(dois)} "
            f"missing_from_manuscript={sorted(set(dois)-set(manuscript_dois))} "
            f"missing_from_registry={sorted(set(manuscript_dois)-set(dois))}"
        )

    required = {
        "10.3389/fpls.2015.01257",
        "10.1016/j.phytochem.2022.113559",
        "10.3732/ajb.1600428",
        "10.1098/rspb.2012.2146",
        "10.1111/nph.13576",
        "10.1093/molbev/msy117",
        "10.1098/rspb.2023.0275",
        "10.1016/j.scienta.2025.114474",
        "10.1007/s11692-025-09645-y",
    }
    if not required <= set(dois):
        raise SystemExit(f"required temporal/prior-art references missing: {sorted(required-set(dois))}")

    summary = {
        "status": "paper1_reference_registry_v0_5_valid",
        "registry_rows": 25,
        "manuscript_reference_dois": 25,
        "luo_present": True,
        "camellia_pollinator_context_present": True,
        "prior_art_present": True,
        "registry_matches_generated_manuscript": True,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
