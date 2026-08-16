#!/usr/bin/env python3
"""Fetch a PMC Open Access article package and inventory supplementary files.

The script uses the documented PMC OA Web Service to resolve the package URL,
then inventories the extracted package and nested ZIP files with checksums. It
is intended as a provenance gate before extracting reported quantitative tables.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import tarfile
import zipfile
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

import requests


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def safe_extract_tar(tar: tarfile.TarFile, out: Path) -> None:
    root = out.resolve()
    for member in tar.getmembers():
        target = (out / member.name).resolve()
        if root not in target.parents and target != root:
            raise RuntimeError(f"unsafe tar member: {member.name}")
    tar.extractall(out)


def normalize_download_url(href: str) -> str:
    if href.startswith("ftp://ftp.ncbi.nlm.nih.gov/"):
        return "https://ftp.ncbi.nlm.nih.gov/" + href.split("ftp.ncbi.nlm.nih.gov/", 1)[1]
    return href


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pmcid", required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    out = args.out_dir
    pkg_dir = out / "package"
    nested_dir = out / "nested"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    nested_dir.mkdir(parents=True, exist_ok=True)

    api = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"
    s = requests.Session()
    s.headers["User-Agent"] = "chun-camellia-meta/0.1 (public-data audit)"
    r = s.get(api, params={"id": args.pmcid}, timeout=60)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    rec = root.find(".//record")
    if rec is None:
        raise SystemExit(f"PMC OA record not found for {args.pmcid}: {r.text[:1000]}")
    links = rec.findall("link")
    tgz = next((x.attrib.get("href", "") for x in links if x.attrib.get("format") == "tgz"), "")
    if not tgz:
        raise SystemExit(f"No OA tgz package for {args.pmcid}")
    url = normalize_download_url(tgz)

    package = out / f"{args.pmcid}.tar.gz"
    with s.get(url, stream=True, timeout=(20, 180)) as rr:
        rr.raise_for_status()
        with package.open("wb") as fh:
            for chunk in rr.iter_content(1024 * 1024):
                if chunk:
                    fh.write(chunk)

    with tarfile.open(package, "r:gz") as tar:
        safe_extract_tar(tar, pkg_dir)

    # Unpack nested ZIP supplements without deleting originals.
    for zpath in sorted(pkg_dir.rglob("*.zip")):
        zslug = zpath.stem
        dest = nested_dir / zslug
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

    with (out / "supplement_manifest.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["scope", "relative_path"])
        w.writeheader()
        w.writerows(rows)

    summary = {
        "pmcid": args.pmcid,
        "citation": rec.attrib.get("citation"),
        "license": rec.attrib.get("license"),
        "oa_package_original_href": tgz,
        "oa_package_download_url": url,
        "package_sha256": sha256(package),
        "package_bytes": package.stat().st_size,
        "inventory_files": len(rows),
        "tabular_candidates": sum(r["suffix"] in {".xlsx", ".xls", ".csv", ".tsv"} for r in rows),
        "claim_ceiling": "public supplementary-file provenance only; no biological effect extracted yet",
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
