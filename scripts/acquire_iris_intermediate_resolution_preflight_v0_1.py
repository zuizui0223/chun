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
from pathlib import Path

PMC_ID = "PMC7588356"
PMC_NUMERIC = "7588356"
XML_URL = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={PMC_NUMERIC}&retmode=xml"
XLINK = "{http://www.w3.org/1999/xlink}href"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "chun-iris-preregistered-analysis/0.1"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def text_content(el: ET.Element) -> str:
    return " ".join("".join(el.itertext()).split())


def candidate_urls(href: str) -> list[str]:
    if href.startswith("http://") or href.startswith("https://"):
        return [href]
    h = href.lstrip("/")
    return [
        f"https://pmc.ncbi.nlm.nih.gov/articles/{PMC_ID}/bin/{h}",
        f"https://pmc.ncbi.nlm.nih.gov/articles/instance/{PMC_NUMERIC}/bin/{h}",
        urllib.parse.urljoin(f"https://pmc.ncbi.nlm.nih.gov/articles/{PMC_ID}/", href),
    ]


def download_href(href: str) -> tuple[str, bytes]:
    errors = []
    for url in candidate_urls(href):
        try:
            b = fetch(url)
            if len(b) > 100:
                return url, b
        except Exception as e:
            errors.append(f"{url}: {e}")
    raise RuntimeError("could not download supplement href %r\n%s" % (href, "\n".join(errors)))


def identify_supplements(root: ET.Element) -> list[dict[str, str]]:
    out = []
    for sm in root.findall(".//supplementary-material"):
        label = text_content(sm.find("label")) if sm.find("label") is not None else ""
        caption = text_content(sm.find("caption")) if sm.find("caption") is not None else ""
        desc = f"{label} {caption}".strip()
        hrefs = []
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
        raise RuntimeError(f"expected one supplement for {pattern!r}, found {len(hits)}: {[x['description'] for x in hits]}")
    return hits[0]


def inspect_table(name: str, filename: str, b: bytes) -> dict[str, object]:
    lower = filename.lower()
    if lower.endswith((".xlsx", ".xls")) or b[:2] == b"PK":
        import pandas as pd
        xls = pd.ExcelFile(io.BytesIO(b))
        sheets = []
        for sheet in xls.sheet_names:
            df = pd.read_excel(io.BytesIO(b), sheet_name=sheet, nrows=0)
            sheets.append({"sheet": str(sheet), "columns": [str(c) for c in df.columns]})
        return {"logical_name": name, "format": "xlsx", "sheets": sheets}
    text = b.decode("utf-8-sig", errors="replace")
    rows = list(csv.reader(io.StringIO(text)))
    return {
        "logical_name": name,
        "format": "csv_or_text",
        "header": rows[0] if rows else [],
        "nonempty_line_count": sum(bool(r) for r in rows),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    xml_bytes = fetch(XML_URL)
    root = ET.fromstring(xml_bytes)
    supplements = identify_supplements(root)

    trait_item = choose(supplements, r"Supplementary\s+Table\s*1|Data table")
    accession_item = choose(supplements, r"Supplementary\s+Material\s*1|Accession numbers")

    outputs = []
    for logical, item in [("traits", trait_item), ("accessions", accession_item)]:
        hrefs = item.get("hrefs") or []
        if not hrefs:
            raise RuntimeError(f"no href for {logical}: {item}")
        href = str(hrefs[0])
        url, b = download_href(href)
        inspection = inspect_table(logical, href, b)
        inspection.update({
            "description": item["description"],
            "href": href,
            "resolved_url": url,
            "bytes": len(b),
            "sha256": sha256_bytes(b),
        })
        outputs.append(inspection)

    receipt = {
        "version": "v0.1",
        "status": "POST_FREEZE_SOURCE_HEADER_PREFLIGHT_ONLY",
        "freeze_contract": "data/intermediate_resolution_rule_prereg_v0_1.json",
        "pmc_id": PMC_ID,
        "xml_url": XML_URL,
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
