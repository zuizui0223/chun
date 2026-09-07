#!/usr/bin/env python3
"""Retrieve real Antirrhineae flower-colour source material.

The script verifies the Ellis & Field (2016) article through Europe PMC, then
retrieves supplementary files through two official routes: Europe PMC's
`supplementaryFiles` endpoint when it is a ZIP, otherwise NCBI's OA package
index and the linked OA tarball. Legacy XLS sheets are exported positionally.
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
import zipfile
from pathlib import Path

import xlrd

ARTICLE_DOI = "10.1093/aob/mcw043"
DATA_DOI = "10.15479/AT:ISTA:34"
PMCID = "PMC4904171"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
NCBI_OA = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={PMCID}"
ISTA_FILENAME = "IST-2016-34-v1+1_tellis_flower_colour_data.zip"
ISTA_MD5 = "950f85b80427d357bfeff09608ba02e9"
MAX_BYTES = 100_000_000


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def retrieve(url: str) -> tuple[bytes, str, dict]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "CHUN-Antirrhineae-open-data-audit/0.3 (+https://github.com/zuizui0223/chun)"},
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
                {
                    "source_row": r + 1,
                    "cells": {str(c): cell_text(sheet.cell_value(r, c)) for c in range(sheet.ncols)},
                }
                for r in range(min(sheet.nrows, 10))
            ],
        })
    return sheets


def collect_member(name: str, raw: bytes, out: Path, members: list[dict], workbooks: list[dict]) -> None:
    basename = Path(name).name
    if not basename:
        return
    lower = basename.lower()
    members.append({"name": name, "bytes": len(raw), "sha256": sha256(raw)})
    if lower.endswith((".xls", ".xlsx", ".csv", ".tsv", ".nex", ".nexus", ".tre", ".tree", ".txt")):
        (out / basename).write_bytes(raw)
    if lower.endswith(".xls"):
        workbooks.append({
            "source_filename": name,
            "basename": basename,
            "sha256": sha256(raw),
            "bytes": len(raw),
            "sheets": export_xls(raw, out, basename),
        })


def extract_epmc_zip(payload: bytes, out: Path, members: list[dict], workbooks: list[dict]) -> bool:
    if not zipfile.is_zipfile(io.BytesIO(payload)):
        return False
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        if sum(x.file_size for x in archive.infolist()) > MAX_BYTES:
            raise ValueError("uncompressed Europe PMC supplement exceeds size limit")
        for entry in archive.infolist():
            if not entry.is_dir():
                collect_member(entry.filename, archive.read(entry), out, members, workbooks)
    return True


def extract_ncbi_oa(out: Path, members: list[dict], workbooks: list[dict]) -> dict:
    oa_xml, oa_resolved, _ = retrieve(NCBI_OA)
    root = ET.fromstring(oa_xml)
    links = root.findall(".//link")
    tgz = next((x.attrib.get("href", "") for x in links if x.attrib.get("format") == "tgz"), "")
    if not tgz:
        raise ValueError("NCBI OA index contains no tgz link")
    if tgz.startswith("ftp://"):
        tgz = "https://" + tgz[len("ftp://"):]
    payload, resolved, headers = retrieve(tgz)
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
        safe_files = [m for m in archive.getmembers() if m.isfile() and not Path(m.name).is_absolute() and ".." not in Path(m.name).parts]
        if sum(m.size for m in safe_files) > MAX_BYTES:
            raise ValueError("uncompressed NCBI OA package exceeds size limit")
        for member in safe_files:
            fh = archive.extractfile(member)
            if fh is not None:
                collect_member(member.name, fh.read(), out, members, workbooks)
    return {
        "oa_index_url": NCBI_OA,
        "oa_index_resolved_url": oa_resolved,
        "oa_index_sha256": sha256(oa_xml),
        "tgz_url": tgz,
        "tgz_resolved_url": resolved,
        "tgz_sha256": sha256(payload),
        "tgz_bytes": len(payload),
        "tgz_content_type": headers.get("content-type", ""),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    xml_url = f"{EPMC}/{PMCID}/fullTextXML"
    xml, xml_resolved, _ = retrieve(xml_url)
    article = ET.fromstring(xml)
    dois = [n.text for n in article.findall(".//article-id") if n.attrib.get("pub-id-type") == "doi"]
    if ARTICLE_DOI not in dois:
        raise ValueError(f"article DOI mismatch: {dois}")
    licenses = [" ".join(n.itertext()).strip() for n in article.findall(".//license")]
    if not licenses:
        raise ValueError("article license not found")

    members: list[dict] = []
    workbooks: list[dict] = []
    supplement_url = f"{EPMC}/{PMCID}/supplementaryFiles"
    supplement_payload, supplement_resolved, supplement_headers = retrieve(supplement_url)
    epmc_zip = extract_epmc_zip(supplement_payload, out, members, workbooks)
    ncbi_meta = None
    if not workbooks:
        ncbi_meta = extract_ncbi_oa(out, members, workbooks)
    if not workbooks:
        diagnostic = {
            "epmc_supplement_bytes": len(supplement_payload),
            "epmc_supplement_sha256": sha256(supplement_payload),
            "epmc_content_type": supplement_headers.get("content-type", ""),
            "epmc_was_zip": epmc_zip,
            "members_seen": members,
        }
        (out / "diagnostic.json").write_text(json.dumps(diagnostic, indent=2) + "\n", encoding="utf-8")
        raise ValueError("no legacy XLS workbook found through Europe PMC or NCBI OA package")

    manifest = {
        "version": "v0.3",
        "article_doi": ARTICLE_DOI,
        "article_pmcid": PMCID,
        "article_license_statements": licenses,
        "article_xml_url": xml_url,
        "article_xml_resolved_url": xml_resolved,
        "article_xml_sha256": sha256(xml),
        "epmc_supplement_url": supplement_url,
        "epmc_supplement_resolved_url": supplement_resolved,
        "epmc_supplement_sha256": sha256(supplement_payload),
        "epmc_supplement_bytes": len(supplement_payload),
        "epmc_supplement_was_zip": epmc_zip,
        "ncbi_oa_fallback": ncbi_meta,
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
