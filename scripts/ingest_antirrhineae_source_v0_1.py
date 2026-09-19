#!/usr/bin/env python3
"""Retrieve real Antirrhineae flower-colour source material.

For this 2016 article the Europe PMC fullTextXML route currently returns 404 in
hosted CI.  The script therefore uses NCBI's official OA-package index, verifies
the article DOI from the package NXML, and positionally exports the legacy XLS
supplement.  The separate ISTA data-object identity remains frozen provenance.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import tarfile
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import xlrd

ARTICLE_DOI = "10.1093/aob/mcw043"
DATA_DOI = "10.15479/AT:ISTA:34"
PMCID = "PMC4904171"
NCBI_OA = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={PMCID}"
ISTA_FILENAME = "IST-2016-34-v1+1_tellis_flower_colour_data.zip"
ISTA_MD5 = "950f85b80427d357bfeff09608ba02e9"
MAX_BYTES = 100_000_000


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def retrieve(url: str) -> tuple[bytes, str, dict]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "CHUN-Antirrhineae-open-data-audit/0.4 (+https://github.com/zuizui0223/chun)"},
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        payload = response.read(MAX_BYTES + 1)
        resolved = response.url
        headers = {k.lower(): v for k, v in response.headers.items()}
    if len(payload) > MAX_BYTES:
        raise ValueError("source exceeds download size limit")
    return payload, resolved, headers


def cell_text(value) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return "" if value is None else str(value)


def export_xls(raw: bytes, out_dir: Path, basename: str) -> list[dict]:
    book = xlrd.open_workbook(file_contents=raw, formatting_info=False)
    sheets: list[dict] = []
    stem = Path(basename).stem
    for index in range(book.nsheets):
        sheet = book.sheet_by_index(index)
        csv_name = f"{stem}_sheet{index + 1}.csv"
        with (out_dir / csv_name).open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["source_row"] + [f"col_{i + 1}" for i in range(sheet.ncols)])
            for r in range(sheet.nrows):
                writer.writerow([r + 1] + [cell_text(sheet.cell_value(r, c)) for c in range(sheet.ncols)])
        sheets.append({
            "name": sheet.name,
            "csv": csv_name,
            "rows": sheet.nrows,
            "columns": sheet.ncols,
            "preview": [
                {"source_row": r + 1,
                 "cells": {str(c): cell_text(sheet.cell_value(r, c)) for c in range(sheet.ncols)}}
                for r in range(min(sheet.nrows, 10))
            ],
        })
    return sheets


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    oa_xml, oa_resolved, _ = retrieve(NCBI_OA)
    oa_root = ET.fromstring(oa_xml)
    tgz_url = next((x.attrib.get("href", "") for x in oa_root.findall(".//link") if x.attrib.get("format") == "tgz"), "")
    if not tgz_url:
        raise ValueError("NCBI OA index contains no tgz link")
    if tgz_url.startswith("ftp://"):
        tgz_url = "https://" + tgz_url[len("ftp://"):]
    tgz, tgz_resolved, tgz_headers = retrieve(tgz_url)

    members: list[dict] = []
    workbooks: list[dict] = []
    nxml_docs: list[dict] = []
    article_dois: set[str] = set()
    licenses: list[str] = []

    with tarfile.open(fileobj=io.BytesIO(tgz), mode="r:gz") as archive:
        files = [m for m in archive.getmembers() if m.isfile()]
        if any(Path(m.name).is_absolute() or ".." in Path(m.name).parts for m in files):
            raise ValueError("unsafe OA archive member")
        if sum(m.size for m in files) > MAX_BYTES:
            raise ValueError("uncompressed NCBI OA package exceeds size limit")
        for member in files:
            fh = archive.extractfile(member)
            if fh is None:
                continue
            raw = fh.read()
            basename = Path(member.name).name
            lower = basename.lower()
            members.append({"name": member.name, "bytes": len(raw), "sha256": sha256(raw)})
            if lower.endswith(".nxml"):
                root = ET.fromstring(raw)
                dois = [n.text for n in root.findall(".//article-id") if n.attrib.get("pub-id-type") == "doi" and n.text]
                article_dois.update(dois)
                licenses.extend(" ".join(n.itertext()).strip() for n in root.findall(".//license"))
                nxml_docs.append({"name": member.name, "sha256": sha256(raw), "dois": dois})
            if lower.endswith((".xls", ".xlsx", ".csv", ".tsv", ".nex", ".nexus", ".tre", ".tree", ".txt")):
                (out / basename).write_bytes(raw)
            if lower.endswith(".xls"):
                workbooks.append({
                    "source_filename": member.name,
                    "basename": basename,
                    "sha256": sha256(raw),
                    "bytes": len(raw),
                    "sheets": export_xls(raw, out, basename),
                })

    if ARTICLE_DOI not in article_dois:
        raise ValueError(f"OA package DOI mismatch: {sorted(article_dois)}")
    if not workbooks:
        raise ValueError("no legacy XLS workbook found in NCBI OA package")

    manifest = {
        "version": "v0.4",
        "article_doi": ARTICLE_DOI,
        "article_pmcid": PMCID,
        "article_dois_in_nxml": sorted(article_dois),
        "article_license_statements": licenses,
        "ncbi_oa_index_url": NCBI_OA,
        "ncbi_oa_index_resolved_url": oa_resolved,
        "ncbi_oa_index_sha256": sha256(oa_xml),
        "oa_tgz_url": tgz_url,
        "oa_tgz_resolved_url": tgz_resolved,
        "oa_tgz_sha256": sha256(tgz),
        "oa_tgz_bytes": len(tgz),
        "oa_tgz_content_type": tgz_headers.get("content-type", ""),
        "nxml_documents": nxml_docs,
        "archive_members": members,
        "workbooks": workbooks,
        "independent_data_object": {
            "doi": DATA_DOI,
            "expected_filename": ISTA_FILENAME,
            "published_md5": ISTA_MD5,
            "status": "REMOTE_IDENTITY_VERIFIED_BINARY_NOT_USED_IN_THIS_RUN",
        },
        "admission_status": "ARTICLE_SUPPLEMENT_INGESTED_REAL_ROWS",
        "phylogeny_status": "NOT_YET_MAPPED_FROM_ISTA_BUNDLE",
        "historical_transition_analysis": "NOT_RUN",
        "paper1_science_changed": False,
    }
    (out / "source_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
