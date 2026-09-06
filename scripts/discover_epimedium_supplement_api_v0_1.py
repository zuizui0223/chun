#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

DOI = "10.3389/fpls.2023.1234148"
PMID = "37915504"
PMCID = "PMC10616310"
FRONTIERS_URL = "https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2023.1234148/full"
NCBI_URL = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/supplmat.cgi/bioc_xml/{PMCID}/list"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; chun-epimedium-atlas/0.3; +https://github.com/zuizui0223/chun)",
            "Accept": "text/html,application/xhtml+xml,application/json,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def extract_file_candidates(text: str, base_url: str) -> list[str]:
    text = html.unescape(text).replace("\\u002F", "/").replace("\\/", "/")
    extensions = r"(?:xlsx|xls|docx|pdf|tiff|tif|csv|txt|zip)"
    found: list[str] = []

    # Absolute and relative URLs embedded in HTML/JSON hydration payloads.
    patterns = [
        rf"https?://[^\s\"'<>]+\.{extensions}(?:\?[^\s\"'<>]*)?",
        rf"(?:href|src|url|downloadUrl|fileUrl)[\"'=:\s]+[\"']?([^\"'<>\s]+\.{extensions}(?:\?[^\"'<>\s]*)?)",
        rf"[^\s\"'<>]+\.{extensions}",
    ]
    for pat in patterns:
        for match in re.findall(pat, text, flags=re.I):
            value = match if isinstance(match, str) else match[0]
            value = value.strip("\"'()[]{}.,;")
            if not value:
                continue
            if value.startswith("//"):
                value = "https:" + value
            elif value.startswith("/"):
                value = urllib.parse.urljoin(base_url, value)
            elif not value.startswith(("http://", "https://")) and "/" in value:
                value = urllib.parse.urljoin(base_url, value)
            if value not in found:
                found.append(value)
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    diagnostics: dict[str, object] = {}

    # Primary route: publisher full HTML. The article page is verified to expose
    # seven supplementary files, including one 157.3-KB XLSX corresponding to the
    # reproductive dataset that contains Supplementary Table S4.
    frontiers_raw = fetch(FRONTIERS_URL)
    (args.out_dir / "frontiers_full.html").write_bytes(frontiers_raw)
    frontiers_text = frontiers_raw.decode("utf-8", errors="replace")
    frontiers_candidates = extract_file_candidates(frontiers_text, FRONTIERS_URL)
    frontiers_sheets = [x for x in frontiers_candidates if re.search(r"\.xlsx?(?:\?|$)", x, flags=re.I)]
    diagnostics["frontiers"] = {
        "url": FRONTIERS_URL,
        "response_bytes": len(frontiers_raw),
        "file_candidates": frontiers_candidates,
        "spreadsheet_candidates": frontiers_sheets,
        "contains_doi": DOI in frontiers_text,
        "contains_supplementary_s4": "Supplementary Table S4" in frontiers_text,
    }

    # Diagnostic-only route: NCBI FAIR-SMART supplementary API. This endpoint has
    # reproducibly returned unrelated PMC supplementary material for this article,
    # so it is never allowed to override the publisher route.
    ncbi_raw = fetch(NCBI_URL)
    (args.out_dir / "ncbi_list_response.xml").write_bytes(ncbi_raw)
    ncbi_text = ncbi_raw.decode("utf-8", errors="replace")
    ncbi_pmcids = sorted(set(re.findall(r"PMC\d+", ncbi_text)))
    diagnostics["ncbi"] = {
        "url": NCBI_URL,
        "response_bytes": len(ncbi_raw),
        "pmcids_in_response": ncbi_pmcids,
        "routing_status": "CORRECT" if PMCID in ncbi_pmcids and not [x for x in ncbi_pmcids if x != PMCID] else "ANOMALOUS_DO_NOT_USE",
    }

    # We require a publisher spreadsheet URL/candidate; NCBI cannot rescue a
    # missing publisher candidate because its routing is already known to be wrong.
    status = "PASS" if frontiers_sheets else "FAIL_NO_PUBLISHER_SPREADSHEET_URL"
    summary = {
        "version": "v0.3",
        "doi": DOI,
        "pmid": PMID,
        "pmcid": PMCID,
        "primary_route": "FRONTIERS_PUBLISHER_HTML",
        "diagnostics": diagnostics,
        "spreadsheet_candidates": frontiers_sheets,
        "discovery_status": status,
        "known_source_fact": "Publisher/PMC article metadata report seven supplementary files including one 157.3-KB XLSX; S4 is the 699-individual reproductive dataset.",
        "prior_failures": [
            {"run_id": 34023987830, "cause": "PMID API returned unrelated PMC7641839 material"},
            {"run_id": 34024279875, "cause": "PMCID API still returned unrelated PMC1790863/PMC1790864/PMC7641839 material"},
        ],
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if status != "PASS":
        raise SystemExit(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
