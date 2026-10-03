#!/usr/bin/env python3
"""Fetch PMC supplementary/media files through the current PMC Cloud Service.

The legacy PMC OA Web Service / tar-package route was retired in August 2026.
This compatibility wrapper preserves CHUN's existing supplement-manifest outputs
while using the supported pmc-oa-opendata object store underneath.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from fetch_pmc_cloud_media_v0_1 import fetch_pmc_media


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pmcid", required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    out = args.out_dir
    pkg_dir = out / "package"
    article_dir = pkg_dir / args.pmcid
    nested_dir = out / "nested"
    article_dir.mkdir(parents=True, exist_ok=True)
    nested_dir.mkdir(parents=True, exist_ok=True)

    # Preserve the historical extracted-package layout expected by frozen
    # downstream extractors: package/<PMCID>/<media filename>.
    cloud = fetch_pmc_media(args.pmcid, article_dir)

    # Keep transport receipts outside the biological package inventory.
    for name in (
        "pmc_cloud_metadata.json",
        "pmc_cloud_media_manifest.csv",
        "pmc_cloud_summary.json",
    ):
        src = article_dir / name
        if src.exists():
            shutil.move(str(src), str(out / name))

    # Unpack nested ZIP supplements without deleting originals.
    for zpath in sorted(pkg_dir.rglob("*.zip")):
        dest = nested_dir / zpath.stem
        dest.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zpath) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                name = Path(info.filename).name
                if not name:
                    continue
                target = dest / name
                with zf.open(info) as src, target.open("wb") as dst:
                    dst.write(src.read())

    rows = []
    for scope, base in [("package", pkg_dir), ("nested", nested_dir)]:
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            rows.append({
                "scope": scope,
                "relative_path": str(path.relative_to(base)),
                "suffix": path.suffix.lower(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            })

    fields = ["scope", "relative_path", "suffix", "bytes", "sha256"]
    with (out / "supplement_manifest.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    summary = {
        "pmcid": args.pmcid,
        "citation": cloud.get("citation"),
        "license": cloud.get("license_code"),
        "transport": "PMC_CLOUD_PMC_OA_OPENDATA",
        "selected_prefix": cloud.get("selected_prefix"),
        "oa_package_original_href": None,
        "oa_package_api_url": None,
        "oa_package_download_url": None,
        "download_attempts": [],
        "package_sha256": None,
        "package_bytes": None,
        "inventory_files": len(rows),
        "tabular_candidates": sum(
            r["suffix"] in {".xlsx", ".xls", ".csv", ".tsv"} for r in rows
        ),
        "claim_ceiling": "public supplementary-file provenance only; no biological effect extracted yet",
    }
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
