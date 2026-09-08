#!/usr/bin/env python3
"""Retrieve and inspect the frozen Iris trait source without computing the signal endpoint."""
from __future__ import annotations

import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from openpyxl import load_workbook

ARTICLE_URLS = [
    "https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2020.569811/full",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC7588356/",
]
EUROPE_PMC_SUPPLEMENT = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7588356/supplementaryFiles"
OUT = Path("analysis/_generated/iris_source_inventory_v1.json")
UA = {"User-Agent": "chun-falsification-audit/1.0 (+https://github.com/zuizui0223/chun)"}


def clean(v):
    if v is None:
        return None
    return re.sub(r"\s+", " ", str(v)).strip()


def workbook_schema(blob: bytes):
    info = {"bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest(), "xlsx_magic": blob[:2] == b"PK"}
    if not info["xlsx_magic"]:
        return info
    try:
        wb = load_workbook(io.BytesIO(blob), read_only=True, data_only=True)
    except Exception as e:
        info["workbook_error"] = f"{type(e).__name__}: {e}"
        return info
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


def nearby_snippets(html: str):
    snippets = []
    lower = html.lower()
    for needle in ("supplementary table 1", "table_1.xlsx", "#ts1", 'id="ts1"'):
        start = 0
        while len(snippets) < 16:
            i = lower.find(needle, start)
            if i < 0:
                break
            snippets.append({"needle": needle, "snippet": clean(html[max(0, i-500):min(len(html), i+1000)])})
            start = i + len(needle)
    return snippets


def candidate_links(url: str, html: str):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for a in soup.find_all("a", href=True):
        href = urljoin(url, a["href"])
        text = clean(a.get_text(" ", strip=True)) or ""
        blob = (href + " " + text).lower()
        if ".xlsx" in blob or "supplementary table 1" in blob or "supplementary-table-1" in blob or "table_1" in blob:
            out.append({"url": href, "anchor": text})
    for m in re.finditer(r'https?:[^"\'<>\\ ]+?\.xlsx(?:\?[^"\'<>\\ ]*)?', html, flags=re.I):
        out.append({"url": m.group(0).replace("\\/", "/").replace("&amp;", "&"), "anchor": "raw-html-xlsx"})
    for m in re.finditer(r'["\']([^"\']+?\.xlsx(?:\?[^"\']*)?)["\']', html, flags=re.I):
        out.append({"url": urljoin(url, m.group(1).replace("\\/", "/")), "anchor": "raw-relative-xlsx"})
    dedup, seen = [], set()
    for x in out:
        if x["url"].startswith("http") and x["url"] not in seen:
            seen.add(x["url"])
            dedup.append(x)
    return dedup


def inspect_direct(url: str):
    r = requests.get(url, headers=UA, timeout=60, allow_redirects=True)
    info = {
        "route": "direct",
        "requested_url": url,
        "resolved_url": r.url,
        "status": r.status_code,
        "content_type": r.headers.get("content-type"),
    }
    if r.status_code == 200:
        info.update(workbook_schema(r.content))
    else:
        info["bytes"] = len(r.content)
    return info


def inspect_europe_pmc_package():
    r = requests.get(EUROPE_PMC_SUPPLEMENT, headers=UA, timeout=90, allow_redirects=True)
    package = {
        "route": "europe_pmc_supplementaryFiles",
        "requested_url": EUROPE_PMC_SUPPLEMENT,
        "resolved_url": r.url,
        "status": r.status_code,
        "content_type": r.headers.get("content-type"),
        "bytes": len(r.content),
        "zip_magic": r.content[:2] == b"PK",
        "members": [],
    }
    candidates = []
    if r.status_code != 200 or not package["zip_magic"]:
        return package, candidates
    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        for name in zf.namelist():
            member = {"name": name, "bytes": zf.getinfo(name).file_size}
            package["members"].append(member)
            if name.lower().endswith(".xlsx"):
                blob = zf.read(name)
                info = {"route": "europe_pmc_zip_member", "package_url": r.url, "member": name}
                info.update(workbook_schema(blob))
                candidates.append(info)
    return package, candidates


def is_trait_schema(sheet):
    flattened = " ".join(str(v or "") for row in sheet.get("preview_first_5_rows", []) for v in row).lower()
    return sheet.get("max_row", 0) >= 200 and ("color" in flattened or "colour" in flattened)


def main():
    inventory = {
        "article_pages": [],
        "diagnostic_snippets": [],
        "supplement_packages": [],
        "xlsx_candidates": [],
        "selected_trait_candidate": None,
    }
    direct_candidates = []
    for url in ARTICLE_URLS:
        r = requests.get(url, headers=UA, timeout=60)
        inventory["article_pages"].append({"url": url, "resolved_url": r.url, "status": r.status_code, "bytes": len(r.content)})
        if r.status_code == 200:
            for snip in nearby_snippets(r.text):
                snip["source_page"] = url
                inventory["diagnostic_snippets"].append(snip)
            for c in candidate_links(r.url, r.text):
                c["source_page"] = url
                direct_candidates.append(c)

    seen = set()
    for c in direct_candidates:
        if c["url"] in seen:
            continue
        seen.add(c["url"])
        if not any(k in c["url"].lower() for k in ("xlsx", "supplement", "attachment", "download")):
            continue
        try:
            info = inspect_direct(c["url"])
        except Exception as e:
            info = {"route": "direct", "requested_url": c["url"], "error": f"{type(e).__name__}: {e}"}
        info["anchor"] = c.get("anchor")
        info["source_page"] = c.get("source_page")
        inventory["xlsx_candidates"].append(info)

    try:
        package, epmc_candidates = inspect_europe_pmc_package()
    except Exception as e:
        package, epmc_candidates = ({"route": "europe_pmc_supplementaryFiles", "error": f"{type(e).__name__}: {e}"}, [])
    inventory["supplement_packages"].append(package)
    inventory["xlsx_candidates"].extend(epmc_candidates)

    viable = []
    for i, x in enumerate(inventory["xlsx_candidates"]):
        for s in x.get("sheets", []):
            if is_trait_schema(s):
                viable.append({"candidate_index": i, "sheet": s["title"], "rows": s["max_row"], "columns": s["max_column"], "sha256": x.get("sha256")})

    # Multiple delivery routes to the exact same workbook count as one source object.
    unique_hashes = {v["sha256"] for v in viable if v.get("sha256")}
    if len(unique_hashes) == 1 and viable:
        v = viable[0]
        x = inventory["xlsx_candidates"][v["candidate_index"]]
        inventory["selected_trait_candidate"] = {
            **v,
            "route": x.get("route"),
            "url": x.get("resolved_url") or x.get("package_url") or x.get("requested_url"),
            "member": x.get("member"),
        }
        inventory["selection_status"] = "SELECTED_UNIQUE_WORKBOOK_HASH"
    elif viable:
        inventory["selection_status"] = "AMBIGUOUS_MULTIPLE_WORKBOOK_HASHES"
        inventory["viable_candidates"] = viable
    else:
        inventory["selection_status"] = "NO_SCHEMA_MATCH"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    compact = {
        "pages": inventory["article_pages"],
        "packages": inventory["supplement_packages"],
        "n_candidates": len(inventory["xlsx_candidates"]),
        "selected": inventory.get("selected_trait_candidate"),
        "selection_status": inventory["selection_status"],
        "candidate_schemas": inventory["xlsx_candidates"],
    }
    print("IRIS_SOURCE_INSPECTION=" + json.dumps(compact, ensure_ascii=False))
    if not inventory.get("selected_trait_candidate"):
        raise SystemExit("No unique Iris trait workbook selected by frozen source-schema criteria")


if __name__ == "__main__":
    main()
