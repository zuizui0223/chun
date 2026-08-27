#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

DOI_RE = re.compile(r"https://doi\.org/([^\s)]+)", re.IGNORECASE)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"empty reference registry: {path}")
    return rows


def norm_doi(value: str) -> str:
    value = value.strip()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value, flags=re.IGNORECASE)
    return value.rstrip(".,; ").lower()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--manuscript", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    rows = read_csv(args.registry)
    if len(rows) != 22:
        raise SystemExit(f"v0.4 reference registry must contain 22 rows, found {len(rows)}")
    ids = [r["reference_id"].strip() for r in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate reference_id in v0.4 registry")
    registry_dois = [norm_doi(r["doi"]) for r in rows]
    if any(not doi for doi in registry_dois):
        raise SystemExit("every v0.4 registry row must carry a DOI")
    if len(registry_dois) != len(set(registry_dois)):
        raise SystemExit("duplicate DOI in v0.4 registry")

    text = args.manuscript.read_text(encoding="utf-8")
    if "# LITERATURE CITED" not in text:
        raise SystemExit("manuscript lacks LITERATURE CITED")
    refs_text = text.split("# LITERATURE CITED", 1)[1]
    manuscript_dois = [norm_doi(x) for x in DOI_RE.findall(refs_text)]
    if len(manuscript_dois) != len(set(manuscript_dois)):
        raise SystemExit("duplicate DOI in manuscript reference list")
    if set(registry_dois) != set(manuscript_dois):
        raise SystemExit(
            f"v0.4 DOI mismatch: missing_from_manuscript={sorted(set(registry_dois)-set(manuscript_dois))} "
            f"missing_from_registry={sorted(set(manuscript_dois)-set(registry_dois))}"
        )

    required = {
        "10.1098/rspb.2012.2146",
        "10.1111/nph.13576",
        "10.1093/molbev/msy117",
        "10.1098/rspb.2023.0275",
        "10.1016/j.scienta.2025.114474",
        "10.1007/s11692-025-09645-y",
        "10.1007/s10722-025-02606-6",
    }
    if not required.issubset(set(registry_dois)):
        raise SystemExit(f"missing required audit references: {sorted(required-set(registry_dois))}")

    semiserrata = [r for r in rows if norm_doi(r["doi"]) == "10.1007/s10722-025-02606-6"]
    if len(semiserrata) != 1 or semiserrata[0]["role"] != "literature_ascertainment_CSEMISERRATA":
        raise SystemExit("CSEMISERRATA reference role drift")

    summary = {
        "status": "paper1_reference_registry_v0_4_valid",
        "registry_rows": len(rows),
        "manuscript_reference_dois": len(manuscript_dois),
        "unique_reference_ids": len(set(ids)),
        "unique_dois": len(set(registry_dois)),
        "required_audit_references": len(required),
        "csemiserrata_present": True,
        "registry_matches_generated_manuscript": True,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
