#!/usr/bin/env python3
"""Retrieve real Antirrhineae flower-colour source material.

Primary execution path uses the documented Europe PMC supplementaryFiles API
for the Ellis & Field (2016) article and exports legacy XLS sheets positionally.
The separate ISTA data-object identity remains frozen in project provenance;
this script does not pretend an inaccessible repository endpoint was verified.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import xlrd

ARTICLE_DOI = "10.1093/aob/mcw043"
DATA_DOI = "10.15479/AT:ISTA:34"
PMCID = "PMC4904171"
API = "https://www.ebi.ac.uk/europepmc/webservices/rest"
ISTA_FILENAME = "IST-2016-34-v1+1_tellis_flower_colour_data.zip"
ISTA_MD5 = "950f85b80427d357bfeff09608ba02e9"
MAX_BYTES = 80_000_000


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def retrieve(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "CHUN-Antirrhineae-open-data-audit/0.2 (+https://github.com/zuizui0223/chun)"},
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        payload = response.read(MAX_BYTES + 1)
        resolved = response.url
    if len(payload) > MAX_BYTES:
        raise ValueError("source exceeds download size limit")
    return payload, resolved


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
        preview = []
        for r in range(min(sheet.nrows, 10)):
            preview.append({
                "source_row": r + 1,
                "cells": {str(c): cell_text(sheet.cell_value(r, c)) for c in range(sheet.ncols)},
            })
        sheets.append({
            "name": sheet.name,
            "csv": csv_name,
            "rows": sheet.nrows,
            "columns": sheet.ncols,
            "preview": preview,
        })
    return sheets


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    xml_url = f"{API}/{PMCID}/fullTextXML"
    supplement_url = f"{API}/{PMCID}/supplementaryFiles"
    xml, xml_resolved = retrieve(xml_url)
    article = ET.fromstring(xml)
    dois = [n.text for n in article.findall(".//article-id") if n.attrib.get("pub-id-type") == "doi"]
    if ARTICLE_DOI not in dois:
        raise ValueError(f"article DOI mismatch: {dois}")
    licenses = [" ".join(n.itertext()).strip() for n in article.findall(".//license")]
    if not licenses:
        raise ValueError("article license not found")

    payload, supplement_resolved = retrieve(supplement_url)
    archive_members: list[dict] = []
    workbooks: list[dict] = []
    preserved_files: list[dict] = []
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        total_uncompressed = sum(x.file_size for x in archive.infolist())
        if total_uncompressed > MAX_BYTES:
            raise ValueError("uncompressed supplement exceeds size limit")
        for entry in archive.infolist():
            if entry.is_dir():
                continue
            name = Path(entry.filename).name
            raw = archive.read(entry)
            archive_members.append({"name": entry.filename, "bytes": len(raw), "sha256": sha256(raw)})
            lower = name.lower()
            if lower.endswith((".xls", ".xlsx", ".csv", ".tsv", ".nex", ".nexus", ".tre", ".tree", ".txt")):
                (out / name).write_bytes(raw)
                preserved_files.append({"name": name, "bytes": len(raw), "sha256": sha256(raw)})
            if lower.endswith(".xls"):
                workbooks.append({
                    "source_filename": entry.filename,
                    "basename": name,
                    "sha256": sha256(raw),
                    "bytes": len(raw),
                    "sheets": export_xls(raw, out, name),
                })

    if not workbooks:
        raise ValueError("no legacy XLS workbook found in real article supplement")

    manifest = {
        "version": "v0.2",
        "article_doi": ARTICLE_DOI,
        "article_pmcid": PMCID,
        "article_license_statements": licenses,
        "article_xml_url": xml_url,
        "article_xml_resolved_url": xml_resolved,
        "article_xml_sha256": sha256(xml),
        "supplement_url": supplement_url,
        "supplement_resolved_url": supplement_resolved,
        "supplement_sha256": sha256(payload),
        "supplement_bytes": len(payload),
        "archive_members": archive_members,
        "preserved_files": preserved_files,
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
    (out / "source_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
