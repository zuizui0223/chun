#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from pathlib import Path

PMID = "37915504"
PMCID = "PMC10616310"
BASE = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/supplmat.cgi/bioc_xml"
LIST_URL = f"{BASE}/{PMCID}/list"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "chun-epimedium-atlas/0.2 (reproducible supplementary-data audit)"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    raw = fetch(LIST_URL)
    (args.out_dir / "supplement_list_response.xml").write_bytes(raw)
    text = raw.decode("utf-8", errors="replace")

    extensions = r"(?:xlsx|xls|docx|pdf|tiff|tif|csv|txt|zip)"
    names: list[str] = []
    for name in re.findall(rf"[A-Za-z0-9_.+\-]+\.{extensions}", text, flags=re.I):
        if name not in names:
            names.append(name)

    paths: list[str] = []
    for path in re.findall(rf"[^<>\s\"']+\.{extensions}", text, flags=re.I):
        if path not in paths:
            paths.append(path)

    spreadsheets = [x for x in names + paths if x.lower().endswith((".xlsx", ".xls"))]
    spreadsheets = list(dict.fromkeys(spreadsheets))

    # Fail closed against the PMID-routing anomaly observed in run 34023987830,
    # where querying PMID 37915504 unexpectedly returned PMC7641839 material.
    foreign_pmcids = sorted({x for x in re.findall(r"PMC\d+", text) if x != PMCID})
    expected_pmcid_present = PMCID in text

    if foreign_pmcids:
        status = "FAIL_FOREIGN_PMCID"
    elif not spreadsheets:
        status = "FAIL_NO_SPREADSHEET_FILENAME"
    else:
        status = "PASS"

    summary = {
        "version": "v0.2",
        "pmid": PMID,
        "pmcid": PMCID,
        "list_url": LIST_URL,
        "response_bytes": len(raw),
        "expected_pmcid_present": expected_pmcid_present,
        "foreign_pmcids": foreign_pmcids,
        "filenames": names,
        "paths": paths,
        "spreadsheet_candidates": spreadsheets,
        "discovery_status": status,
        "prior_failure": {
            "run_id": 34023987830,
            "cause": "PMID endpoint returned supplementary material for PMC7641839 rather than the Epimedium article",
            "fix": "query the verified PMCID directly and reject foreign PMCIDs",
        },
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))

    if status != "PASS":
        raise SystemExit(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
