#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    manuscript = a.bundle / "manuscript" / "PAPER1_AJB_SUBMISSION_V0_3.md"
    if not manuscript.exists():
        raise SystemExit("submission manuscript missing")
    text = manuscript.read_text(encoding="utf-8")
    if text.count("[ARCHIVE DOI TO ADD AT SUBMISSION]") != 1:
        raise SystemExit("archive DOI placeholder count is not exactly one")

    main_png = sorted((a.bundle / "main_figures").glob("Fig*.png"))
    main_svg = sorted((a.bundle / "main_figures").glob("Fig*.svg"))
    supp_csv = sorted((a.bundle / "supplementary_tables").glob("Table_S*.csv"))
    supp_png = sorted((a.bundle / "supplementary_figures").glob("FigS*.png"))
    supp_svg = sorted((a.bundle / "supplementary_figures").glob("FigS*.svg"))
    if (len(main_png), len(main_svg)) != (6, 6):
        raise SystemExit(f"expected 6 Main PNG/SVG figures, got {len(main_png)}/{len(main_svg)}")
    if len(supp_csv) != 6:
        raise SystemExit(f"expected 6 Supplementary Tables, got {len(supp_csv)}")
    if (len(supp_png), len(supp_svg)) != (3, 3):
        raise SystemExit(f"expected 3 Supplementary PNG/SVG figures, got {len(supp_png)}/{len(supp_svg)}")

    required_prov = [
        "paper1_authoritative_results_v0_1.csv",
        "paper1_analysis_disposition_v0_1.csv",
        "paper1_micro_source_provenance_v0_1.csv",
        "wfo55_accepted_species_wild_colour_registry_v0_1.csv",
        "paper1_release_artifact_manifest_v0_2.csv",
    ]
    for name in required_prov:
        if not (a.bundle / "provenance" / name).exists():
            raise SystemExit(f"missing provenance file: {name}")

    files = [p for p in a.bundle.rglob("*") if p.is_file()]
    manifest = [
        {
            "path": str(p.relative_to(a.bundle)),
            "bytes": p.stat().st_size,
            "sha256": sha256(p),
        }
        for p in sorted(files)
    ]
    summary = {
        "bundle_version": "v0.3",
        "manuscript": str(manuscript.relative_to(a.bundle)),
        "main_figures_png": len(main_png),
        "main_figures_svg": len(main_svg),
        "supplementary_tables": len(supp_csv),
        "supplementary_figures_png": len(supp_png),
        "supplementary_figures_svg": len(supp_svg),
        "archive_doi_placeholder_count": 1,
        "file_count": len(files),
        "remaining_human_metadata": [
            "author list/order",
            "affiliations/corresponding author",
            "author contributions",
            "funding/acknowledgments",
            "conflict-of-interest statement if required",
            "versioned archive DOI",
        ],
        "new_scientific_analysis": False,
        "files": manifest,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "files"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
