#!/usr/bin/env python3
"""Retrieve and inspect the frozen Iris trait source without computing the signal endpoint."""
from __future__ import annotations

import io
import json
import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from openpyxl import load_workbook

ARTICLE_URLS = [
    "https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2020.569811/full",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC7588356/",
]
OUT = Path("analysis/_generated/iris_source_inventory_v1.json")
UA = {"User-Agent": "chun-falsification-audit/1.0 (+https://github.com/zuizui0223/chun)"}


def clean(v):
    if v is None:
        return None
    return re.sub(r"\s+", " ", str(v)).strip()


def candidate_links(url: str, html: str):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for a in soup.find_all("a", href=True):
        href = urljoin(url, a["href"])
        text = clean(a.get_text(" ", strip=True)) or ""
        blob = (href + " " + text).lower()
        if ".xlsx" in blob or "supplementary table 1" in blob or "supplementary-table-1" in blob:
            out.append({"url": href, "anchor": text})
    # Frontiers sometimes exposes attachment URLs only in JSON/script payloads.
    for m in re.finditer(r'https?:[^"\'<>\\ ]+?\.xlsx(?:\?[^"\'<>\\ ]*)?', html, flags=re.I):
        out.append({"url": m.group(0).replace("\\/", "/"), "anchor": "raw-html-xlsx"})
    # Also collect relative xlsx-looking paths from raw markup.
    for m in re.finditer(r'["\']([^"\']+?\.xlsx(?:\?[^"\']*)?)["\']', html, flags=re.I):
        out.append({"url": urljoin(url, m.group(1).replace("\\/", "/")), "anchor": "raw-relative-xlsx"})
    dedup = []
    seen = set()
    for x in out:
        if x["url"] not in seen:
            seen.add(x["url"])
            dedup.append(x)
    return dedup


def inspect_xlsx(url: str):
    r = requests.get(url, headers=UA, timeout=60, allow_redirects=True)
    info = {
        "requested_url": url,
        "resolved_url": r.url,
        "status": r.status_code,
        "content_type": r.headers.get("content-type"),
        "bytes": len(r.content),
        "xlsx_magic": r.content[:2] == b"PK",
    }
    if r.status_code != 200 or not info["xlsx_magic"]:
        return info
    wb = load_workbook(io.BytesIO(r.content), read_only=True, data_only=True)
    sheets = []
    for ws in wb.worksheets:
        preview = []
        for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 5), values_only=True):
            preview.append([clean(v) for v in row])
        sheets.append({
            "title": ws.title,
            "max_row": ws.max_row,
            "max_column": ws.max_column,
            "preview_first_5_rows": preview,
        })
    info["sheets"] = sheets
    return info


def main():
    inventory = {"article_pages": [], "xlsx_candidates": [], "selected_trait_candidate": None}
    candidates = []
    for url in ARTICLE_URLS:
        r = requests.get(url, headers=UA, timeout=60)
        page = {"url": url, "resolved_url": r.url, "status": r.status_code, "bytes": len(r.content)}
        inventory["article_pages"].append(page)
        if r.status_code == 200:
            for c in candidate_links(r.url, r.text):
                c["source_page"] = url
                candidates.append(c)
    seen = set()
    for c in candidates:
        if c["url"] in seen:
            continue
        seen.add(c["url"])
        try:
            info = inspect_xlsx(c["url"])
        except Exception as e:
            info = {"requested_url": c["url"], "error": f"{type(e).__name__}: {e}"}
        info["anchor"] = c.get("anchor")
        info["source_page"] = c.get("source_page")
        inventory["xlsx_candidates"].append(info)

    # Select only by source-schema criteria, never by a phylogenetic result.
    viable = []
    for i, x in enumerate(inventory["xlsx_candidates"]):
        for s in x.get("sheets", []):
            flattened = " ".join(str(v or "") for row in s.get("preview_first_5_rows", []) for v in row).lower()
            if s.get("max_row", 0) >= 200 and ("color" in flattened or "colour" in flattened):
                viable.append((i, s["title"], s["max_row"], s["max_column"]))
    if len(viable) == 1:
        i, sheet, rows, cols = viable[0]
        x = inventory["xlsx_candidates"][i]
        inventory["selected_trait_candidate"] = {
            "candidate_index": i,
            "url": x.get("resolved_url") or x.get("requested_url"),
            "sheet": sheet,
            "rows": rows,
            "columns": cols,
        }
    elif viable:
        inventory["selection_status"] = "AMBIGUOUS_MULTIPLE_SCHEMA_MATCHES"
        inventory["viable_candidates"] = viable
    else:
        inventory["selection_status"] = "NO_SCHEMA_MATCH"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    compact = {
        "pages": inventory["article_pages"],
        "n_candidates": len(inventory["xlsx_candidates"]),
        "selected": inventory.get("selected_trait_candidate"),
        "selection_status": inventory.get("selection_status", "SELECTED" if inventory.get("selected_trait_candidate") else None),
        "candidate_schemas": [
            {
                "url": x.get("resolved_url") or x.get("requested_url"),
                "status": x.get("status"),
                "content_type": x.get("content_type"),
                "bytes": x.get("bytes"),
                "sheets": x.get("sheets"),
                "error": x.get("error"),
            }
            for x in inventory["xlsx_candidates"]
        ],
    }
    print("IRIS_SOURCE_INSPECTION=" + json.dumps(compact, ensure_ascii=False))
    if not inventory.get("selected_trait_candidate"):
        raise SystemExit("No unique Iris trait workbook selected by frozen source-schema criteria")


if __name__ == "__main__":
    main()
