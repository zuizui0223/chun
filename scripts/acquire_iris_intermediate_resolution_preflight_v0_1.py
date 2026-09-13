#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

PMC_ID = "PMC7588356"
PMC_NUMERIC = "7588356"
XML_URL = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={PMC_NUMERIC}&retmode=xml"
XLINK = "{http://www.w3.org/1999/xlink}href"
USER_AGENT = "chun-iris-preregistered-analysis/0.1"


def fetch_with_meta(url: str) -> tuple[str, str, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as r:
        final_url = r.geturl()
        content_type = (r.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
        return final_url, content_type, r.read()


def fetch(url: str) -> bytes:
    return fetch_with_meta(url)[2]


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def text_content(el: ET.Element) -> str:
    return " ".join("".join(el.itertext()).split())


def candidate_urls(href: str) -> list[str]:
    urls: list[str] = []
    if href.startswith("http://") or href.startswith("https://"):
        urls.append(href)
    h = href.lstrip("/")
    urls.extend(
        [
            f"https://pmc.ncbi.nlm.nih.gov/articles/{PMC_ID}/bin/{h}",
            f"https://pmc.ncbi.nlm.nih.gov/articles/instance/{PMC_NUMERIC}/bin/{h}",
            urllib.parse.urljoin(f"https://pmc.ncbi.nlm.nih.gov/articles/{PMC_ID}/", href),
        ]
    )
    # Stable-order de-duplication.
    return list(dict.fromkeys(urls))


def looks_like_html(content_type: str, b: bytes) -> bool:
    prefix = b[:512].lstrip().lower()
    return (
        content_type in {"text/html", "application/xhtml+xml"}
        or prefix.startswith(b"<!doctype html")
        or prefix.startswith(b"<html")
        or b"<html" in prefix[:200]
    )


def download_href(href: str) -> tuple[str, str, bytes, list[dict[str, object]]]:
    attempts: list[dict[str, object]] = []
    for url in candidate_urls(href):
        try:
            final_url, content_type, b = fetch_with_meta(url)
            attempt = {
                "requested_url": url,
                "final_url": final_url,
                "content_type": content_type,
                "bytes": len(b),
                "magic_hex": b[:16].hex(),
                "html_rejected": looks_like_html(content_type, b),
            }
            attempts.append(attempt)
            if len(b) <= 100 or attempt["html_rejected"]:
                continue
            return final_url, content_type, b, attempts
        except Exception as e:
            attempts.append({"requested_url": url, "error": repr(e)})
    raise RuntimeError(
        "could not download a non-HTML supplement for href %r\n%s"
        % (href, json.dumps(attempts, indent=2))
    )


def identify_supplements(root: ET.Element) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for sm in root.findall(".//supplementary-material"):
        label = text_content(sm.find("label")) if sm.find("label") is not None else ""
        caption = text_content(sm.find("caption")) if sm.find("caption") is not None else ""
        desc = f"{label} {caption}".strip()
        hrefs: list[str] = []
        for e in sm.iter():
            href = e.attrib.get(XLINK)
            if href:
                hrefs.append(href)
        out.append({"description": desc, "hrefs": hrefs})
    return out


def choose(items: list[dict[str, object]], pattern: str) -> dict[str, object]:
    rx = re.compile(pattern, re.I)
    hits = [x for x in items if rx.search(str(x["description"]))]
    if len(hits) != 1:
        raise RuntimeError(
            f"expected one supplement for {pattern!r}, found {len(hits)}: "
            f"{[x['description'] for x in hits]}"
        )
    return hits[0]


def inspect_xlsx(name: str, b: bytes, container_member: str | None = None) -> dict[str, object]:
    import pandas as pd

    xls = pd.ExcelFile(io.BytesIO(b), engine="openpyxl")
    sheets: list[dict[str, object]] = []
    for sheet in xls.sheet_names:
        df = pd.read_excel(io.BytesIO(b), sheet_name=sheet, nrows=0, engine="openpyxl")
        sheets.append({"sheet": str(sheet), "columns": [str(c) for c in df.columns]})
    out: dict[str, object] = {"logical_name": name, "format": "xlsx", "sheets": sheets}
    if container_member is not None:
        out["container_member"] = container_member
    return out


def inspect_text_table(name: str, filename: str, b: bytes, container_member: str | None = None) -> dict[str, object]:
    text = b.decode("utf-8-sig", errors="replace")
    sample = text[:8192]
    delimiter = "\t" if filename.lower().endswith((".tsv", ".txt")) or sample.count("\t") > sample.count(",") else ","
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    header = next(reader, [])
    out: dict[str, object] = {
        "logical_name": name,
        "format": "tsv_or_text" if delimiter == "\t" else "csv_or_text",
        "delimiter": "TAB" if delimiter == "\t" else "COMMA",
        "header": header,
    }
    if container_member is not None:
        out["container_member"] = container_member
    return out


def inspect_table(name: str, filename: str, content_type: str, b: bytes) -> dict[str, object]:
    if looks_like_html(content_type, b):
        raise RuntimeError(f"HTML reached table inspector for {filename}")

    lower = filename.lower()
    if zipfile.is_zipfile(io.BytesIO(b)):
        with zipfile.ZipFile(io.BytesIO(b)) as zf:
            members = [m for m in zf.namelist() if not m.endswith("/") and not m.startswith("__MACOSX/")]
            # A native XLSX is itself a ZIP containing the Office package structure.
            if "[Content_Types].xml" in members and any(m.startswith("xl/") for m in members):
                return inspect_xlsx(name, b)
            tabular = [m for m in members if m.lower().endswith((".xlsx", ".csv", ".tsv", ".txt"))]
            if len(tabular) != 1:
                raise RuntimeError(
                    f"generic ZIP for {filename} has {len(tabular)} candidate tabular members; "
                    f"members={members[:50]}"
                )
            member = tabular[0]
            payload = zf.read(member)
            if member.lower().endswith(".xlsx"):
                return inspect_xlsx(name, payload, container_member=member)
            return inspect_text_table(name, member, payload, container_member=member)

    # Legacy Excel OLE container. We do not inspect values; pandas/xlrd is used only for headers.
    if b.startswith(bytes.fromhex("d0cf11e0a1b11ae1")) or lower.endswith(".xls"):
        import pandas as pd

        xls = pd.ExcelFile(io.BytesIO(b), engine="xlrd")
        sheets: list[dict[str, object]] = []
        for sheet in xls.sheet_names:
            df = pd.read_excel(io.BytesIO(b), sheet_name=sheet, nrows=0, engine="xlrd")
            sheets.append({"sheet": str(sheet), "columns": [str(c) for c in df.columns]})
        return {"logical_name": name, "format": "xls", "sheets": sheets}

    if lower.endswith(".xlsx"):
        raise RuntimeError(f"filename suggests XLSX but payload is not a valid ZIP: {filename}")
    return inspect_text_table(name, filename, b)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    xml_final_url, xml_content_type, xml_bytes = fetch_with_meta(XML_URL)
    root = ET.fromstring(xml_bytes)
    supplements = identify_supplements(root)

    trait_item = choose(supplements, r"Supplementary\s+Table\s*1|Data table")
    accession_item = choose(supplements, r"Supplementary\s+Material\s*1|Accession numbers")

    outputs: list[dict[str, object]] = []
    for logical, item in [("traits", trait_item), ("accessions", accession_item)]:
        hrefs = item.get("hrefs") or []
        if not hrefs:
            raise RuntimeError(f"no href for {logical}: {item}")
        href = str(hrefs[0])
        url, content_type, b, attempts = download_href(href)
        inspection = inspect_table(logical, href, content_type, b)
        inspection.update(
            {
                "description": item["description"],
                "href": href,
                "resolved_url": url,
                "content_type": content_type,
                "bytes": len(b),
                "sha256": sha256_bytes(b),
                "magic_hex": b[:16].hex(),
                "download_attempts": attempts,
            }
        )
        outputs.append(inspection)

    receipt = {
        "version": "v0.1",
        "status": "POST_FREEZE_SOURCE_HEADER_PREFLIGHT_ONLY",
        "freeze_contract": "data/intermediate_resolution_rule_prereg_v0_1.json",
        "pmc_id": PMC_ID,
        "xml_url": XML_URL,
        "xml_final_url": xml_final_url,
        "xml_content_type": xml_content_type,
        "xml_sha256": sha256_bytes(xml_bytes),
        "supplement_count_in_xml": len(supplements),
        "files": outputs,
        "row_level_values_emitted": False,
        "auc_computed": False,
        "paper1_science_changed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
