#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import re
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

DOI = "10.1002/ajb2.70146"
FILENAME = "ajb270146-sup-0002-AJB_SinnottArmstrong_D_24_00358_AppendixS2_ce.docx"
ARTICLE = "https://bsapubs.onlinelibrary.wiley.com/doi/10.1002/ajb2.70146"
UA = "Mozilla/5.0 CHUN-AppendixS2-source-gate/0.1"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def valid_docx_bytes(data: bytes) -> bool:
    if len(data) < 4 or data[:2] != b"PK":
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            names = set(z.namelist())
            if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                return False
            ct = z.read("[Content_Types].xml")
            return b"wordprocessingml.document.main+xml" in ct
    except Exception:
        return False


def _cell_text(tc: ET.Element) -> str:
    parts = []
    for t in tc.iter(W + "t"):
        if t.text:
            parts.append(t.text)
    return " ".join(" ".join(parts).split())


def extract_tables_from_docx_bytes(data: bytes) -> list[list[list[str]]]:
    if not valid_docx_bytes(data):
        raise ValueError("not a valid Word DOCX")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    out = []
    for tbl in root.iter(W + "tbl"):
        rows = []
        for tr in tbl.findall(W + "tr"):
            cells = [_cell_text(tc) for tc in tr.findall(W + "tc")]
            rows.append(cells)
        out.append(rows)
    return out


def fetch(url: str, referer: str | None = None, timeout: int = 60) -> tuple[bytes | None, dict]:
    headers = {"User-Agent": UA, "Accept": "*/*"}
    if referer:
        headers["Referer"] = referer
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
            return data, {
                "url": url,
                "final_url": r.geturl(),
                "http_status": getattr(r, "status", 200),
                "content_type": r.headers.get("Content-Type"),
                "content_disposition": r.headers.get("Content-Disposition"),
                "bytes": len(data),
                "sha256": sha256_bytes(data),
                "valid_docx": valid_docx_bytes(data),
            }
    except Exception as e:
        return None, {"url": url, "error": f"{type(e).__name__}: {e}"}


def candidate_urls() -> list[str]:
    qdoi = urllib.parse.quote(DOI, safe="")
    qfile = urllib.parse.quote(FILENAME, safe="")
    raw_file = FILENAME
    return [
        f"https://bsapubs.onlinelibrary.wiley.com/action/downloadSupplement?doi={qdoi}&file={qfile}",
        f"https://bsapubs.onlinelibrary.wiley.com/action/downloadSupplement?doi={qdoi}&file={raw_file}",
        f"https://onlinelibrary.wiley.com/action/downloadSupplement?doi={qdoi}&file={qfile}",
        f"https://onlinelibrary.wiley.com/action/downloadSupplement?doi={qdoi}&file={raw_file}",
    ]


def discover_href_from_article() -> tuple[list[str], list[dict]]:
    urls = []
    diags = []
    for article in (
        ARTICLE,
        "https://onlinelibrary.wiley.com/doi/10.1002/ajb2.70146",
        "https://doi.org/10.1002/ajb2.70146",
    ):
        data, diag = fetch(article)
        diags.append(diag)
        if not data:
            continue
        txt = data.decode("utf-8", "replace")
        for m in re.finditer(r'href=["\']([^"\']*' + re.escape(FILENAME) + r'[^"\']*)["\']', txt, flags=re.I):
            href = html.unescape(m.group(1))
            urls.append(urllib.parse.urljoin(article, href))
    return list(dict.fromkeys(urls)), diags


def table_inventory(tables: list[list[list[str]]]) -> list[dict]:
    inv = []
    for idx, rows in enumerate(tables, 1):
        max_cols = max((len(r) for r in rows), default=0)
        flat = " | ".join(" | ".join(r) for r in rows[:3])
        inv.append({
            "table_index": idx,
            "rows": len(rows),
            "max_columns": max_cols,
            "first_rows": rows[:3],
            "contains_clade_token": bool(re.search(r"\bclade\b", flat, flags=re.I)),
            "contains_transition_token": bool(re.search(r"transition", flat, flags=re.I)),
        })
    return inv


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    diagnostics = []
    found: bytes | None = None
    found_url: str | None = None

    discovered, article_diags = discover_href_from_article()
    diagnostics.extend({"stage": "article_discovery", **x} for x in article_diags)
    urls = list(dict.fromkeys(discovered + candidate_urls()))

    for url in urls:
        data, diag = fetch(url, referer=ARTICLE)
        diagnostics.append({"stage": "supplement_probe", **diag})
        if data is not None and valid_docx_bytes(data):
            found = data
            found_url = diag.get("final_url") or url
            break

    if found is None:
        out = {
            "version": "v0.1",
            "status": "HOLD_WILEY_APPENDIX_S2_BYTES_UNAVAILABLE",
            "doi": DOI,
            "expected_filename": FILENAME,
            "diagnostics": diagnostics,
            "outcome_firewall": {
                "clade_transition_values_extracted": False,
                "chun_bridge_fitted": False,
            },
            "paper1_science_changed": False,
            "el_v0_2_science_changed": False,
        }
        (args.outdir / "source_receipt.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"status": out["status"], "probes": len(diagnostics)}, indent=2))
        return

    docx_path = args.outdir / FILENAME
    docx_path.write_bytes(found)
    tables = extract_tables_from_docx_bytes(found)
    inventory = table_inventory(tables)
    tables_path = args.outdir / "appendix_s2_tables_full.json"
    tables_path.write_text(json.dumps(tables, indent=2, ensure_ascii=False) + "\n")

    out = {
        "version": "v0.1",
        "status": "WILEY_APPENDIX_S2_SOURCE_RECOVERED_TABLES_INVENTORIED",
        "doi": DOI,
        "filename": FILENAME,
        "recovered_url": found_url,
        "bytes": len(found),
        "sha256": sha256_bytes(found),
        "table_count": len(tables),
        "table_inventory": inventory,
        "diagnostics": diagnostics,
        "outcome_firewall": {
            "tables_serialized_verbatim_cell_text": True,
            "clade_transition_predictor_selected_or_transformed": False,
            "chun_bridge_fitted": False,
        },
        "paper1_science_changed": False,
        "el_v0_2_science_changed": False,
    }
    (args.outdir / "source_receipt.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": out["status"],
        "bytes": out["bytes"],
        "sha256": out["sha256"],
        "table_count": out["table_count"],
        "table_inventory": inventory,
    }, indent=2))


if __name__ == "__main__":
    main()
