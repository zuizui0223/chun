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
    x = value.strip()
    x = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", x, flags=re.IGNORECASE)
    return x.rstrip(".,; ").lower()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--manuscript", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    rows = read_csv(args.registry)
    if len(rows) != 21:
        raise SystemExit(f"v0.3 reference registry must contain 21 rows, found {len(rows)}")

    ids = [r["reference_id"].strip() for r in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate reference_id in v0.3 registry")

    registry_dois = [norm_doi(r["doi"]) for r in rows]
    if any(not d for d in registry_dois):
        raise SystemExit("every v0.3 registry row must carry a DOI/stable DOI identifier")
    if len(registry_dois) != len(set(registry_dois)):
        raise SystemExit("duplicate DOI in v0.3 registry")

    text = args.manuscript.read_text(encoding="utf-8")
    if "# LITERATURE CITED" not in text:
        raise SystemExit("generated v0.3 manuscript lacks LITERATURE CITED")
    refs_text = text.split("# LITERATURE CITED", 1)[1]
    manuscript_dois = [norm_doi(x) for x in DOI_RE.findall(refs_text)]
    if len(manuscript_dois) != len(set(manuscript_dois)):
        raise SystemExit("duplicate DOI in generated v0.3 manuscript reference list")

    rset = set(registry_dois)
    mset = set(manuscript_dois)
    if rset != mset:
        raise SystemExit(
            "v0.3 registry/manuscript DOI mismatch: "
            f"missing_from_manuscript={sorted(rset-mset)} "
            f"missing_from_registry={sorted(mset-rset)}"
        )

    required_new = {
        "10.1098/rspb.2012.2146",
        "10.1111/nph.13576",
        "10.1093/molbev/msy117",
        "10.1098/rspb.2023.0275",
        "10.1016/j.scienta.2025.114474",
        "10.1007/s11692-025-09645-y",
    }
    if not required_new.issubset(rset):
        raise SystemExit(f"missing required novelty-audit references: {sorted(required_new-rset)}")

    roles = {r["role"].strip() for r in rows}
    if not any(role.startswith("novelty_") for role in roles):
        raise SystemExit("v0.3 registry lacks explicit novelty prior-art roles")

    summary = {
        "status": "paper1_reference_registry_v0_3_valid",
        "registry_rows": len(rows),
        "manuscript_reference_dois": len(manuscript_dois),
        "unique_reference_ids": len(set(ids)),
        "unique_dois": len(rset),
        "required_novelty_references": len(required_new),
        "registry_matches_generated_manuscript": True,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
