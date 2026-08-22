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

    manuscript = a.bundle / "manuscript" / "PAPER1_AJB_UPLOAD_V0_4.md"
    if not manuscript.exists():
        raise SystemExit("AJB upload manuscript v0.4 missing")
    text = manuscript.read_text(encoding="utf-8")
    if text.count("[ARCHIVE DOI TO ADD AT SUBMISSION]") != 1:
        raise SystemExit("expected one archive DOI placeholder")
    if "Additional supporting information may be found online in the Supporting Information section at the end of the article." not in text:
        raise SystemExit("AJB Supporting Information statement missing")
    for i in range(1, 10):
        if f"Appendix S{i}" not in text:
            raise SystemExit(f"manuscript missing Appendix S{i}")

    main_png = sorted((a.bundle / "main_figures").glob("Fig*.png"))
    main_svg = sorted((a.bundle / "main_figures").glob("Fig*.svg"))
    appendices = sorted((a.bundle / "appendices").glob("Appendix_S[1-9].*"))
    upload_appendices = sorted(p for p in appendices if p.name != "Appendix_index.csv")
    expected_names = [f"Appendix_S{i}.csv" for i in range(1,7)] + [f"Appendix_S{i}.png" for i in range(7,10)]
    observed_names = sorted(p.name for p in upload_appendices)
    if sorted(expected_names) != observed_names:
        raise SystemExit(f"AJB Appendix upload set mismatch: {observed_names}")
    if len(main_png) != 6 or len(main_svg) != 6:
        raise SystemExit("Main figure set incomplete")

    required_prov = [
        "paper1_authoritative_results_v0_1.csv",
        "paper1_analysis_disposition_v0_1.csv",
        "paper1_micro_source_provenance_v0_1.csv",
        "paper1_bibliographic_corrections_v0_1.csv",
        "paper1_ajb_appendix_mapping_v0_1.csv",
        "paper1_release_artifact_manifest_v0_2.csv",
    ]
    for name in required_prov:
        if not (a.bundle / "provenance" / name).exists():
            raise SystemExit(f"missing final provenance file: {name}")

    files = [p for p in a.bundle.rglob("*") if p.is_file()]
    frozen = [{
        "path": str(p.relative_to(a.bundle)),
        "bytes": p.stat().st_size,
        "sha256": sha256(p),
    } for p in sorted(files)]
    summary = {
        "bundle_version": "v0.4-ajb-upload",
        "manuscript": str(manuscript.relative_to(a.bundle)),
        "main_figures": 6,
        "appendices": 9,
        "archive_doi_placeholder_count": 1,
        "file_count": len(files),
        "remaining_human_metadata": [
            "author list and order",
            "affiliations and corresponding-author details",
            "author contributions",
            "funding and acknowledgments",
            "conflict-of-interest statement if required",
            "versioned archive DOI",
        ],
        "new_scientific_analysis": False,
        "files": frozen,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k != "files"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
