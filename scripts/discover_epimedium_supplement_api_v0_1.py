#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from pathlib import Path

PMID = "37915504"
LIST_URL = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/supplmat.cgi/bioc_xml/{PMID}/list"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "chun-epimedium-atlas/0.1 (reproducible supplementary-data audit)"})
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
    names = []
    for name in re.findall(rf"[A-Za-z0-9_.+\-]+\.{extensions}", text, flags=re.I):
        if name not in names:
            names.append(name)

    # Keep a second, looser extraction because the API may emit file names inside
    # XML attributes or text nodes with path prefixes.
    paths = []
    for path in re.findall(rf"[^<>\s\"']+\.{extensions}", text, flags=re.I):
        if path not in paths:
            paths.append(path)

    xlsx = [x for x in names + paths if x.lower().endswith((".xlsx", ".xls"))]
    xlsx = list(dict.fromkeys(xlsx))

    summary = {
        "version": "v0.1",
        "pmid": PMID,
        "list_url": LIST_URL,
        "response_bytes": len(raw),
        "filenames": names,
        "paths": paths,
        "spreadsheet_candidates": xlsx,
        "discovery_status": "PASS" if xlsx else "FAIL_NO_SPREADSHEET_FILENAME",
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if not xlsx:
        raise SystemExit("No spreadsheet filename recovered from NCBI supplementary-material API list response")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
