#!/usr/bin/env python3
"""Resolve admitted SRA/BioProject seeds to NCBI RunInfo manifests.

Uses only the Python standard library and NCBI Entrez E-utilities. The script
never downloads sequence reads; it freezes run/sample metadata so downstream
analyses can be keyed to concrete SRR/ERR/DRR accessions.

Example:
    python scripts/fetch_sra_runinfo.py \
        --seeds data/public_sequence_seeds_v0_1.csv \
        --out-dir data/manifests

NCBI documentation:
- E-utilities: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- SRA metadata / RunInfo: https://www.ncbi.nlm.nih.gov/sra/docs/sradownload/
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import pathlib
import sys
import time
import urllib.parse
import urllib.request

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
DEFAULT_USER_AGENT = "chun-flower-colour/0.1 (NCBI public-metadata audit)"


def request_text(endpoint: str, params: dict[str, str], *, retries: int = 4) -> str:
    query = urllib.parse.urlencode(params)
    url = f"{EUTILS}/{endpoint}?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                return response.read().decode("utf-8")
        except Exception as exc:  # pragma: no cover - network-dependent
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"NCBI request failed after {retries} attempts: {url}") from last_error


def esearch_sra(accession: str) -> list[str]:
    payload = request_text(
        "esearch.fcgi",
        {
            "db": "sra",
            "term": accession,
            "retmax": "10000",
            "retmode": "json",
        },
    )
    parsed = json.loads(payload)
    return parsed.get("esearchresult", {}).get("idlist", [])


def efetch_runinfo(uids: list[str]) -> str:
    if not uids:
        return ""
    # NCBI recommends POST for very large UID lists; the focal projects here are
    # small enough for GET. Guard anyway so silent truncation cannot occur.
    if len(uids) > 200:
        raise RuntimeError(
            f"Resolved {len(uids)} SRA UIDs; batch/POST support is required before proceeding."
        )
    return request_text(
        "efetch.fcgi",
        {
            "db": "sra",
            "id": ",".join(uids),
            "rettype": "runinfo",
            "retmode": "text",
        },
    )


def normalize_runinfo(text: str, seed: dict[str, str]) -> list[dict[str, str]]:
    text = text.strip()
    if not text:
        return []
    reader = csv.DictReader(io.StringIO(text))
    rows: list[dict[str, str]] = []
    for row in reader:
        if not row:
            continue
        clean = {str(k): (v or "").strip() for k, v in row.items() if k is not None}
        clean = {
            "seed_id": seed["seed_id"],
            "seed_accession": seed["accession"],
            "seed_system": seed["system"],
            "seed_taxon": seed["taxon"],
            **clean,
        }
        rows.append(clean)
    return rows


def safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in value)


def write_rows(path: pathlib.Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                fields.append(key)
                seen.add(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", required=True, type=pathlib.Path)
    parser.add_argument("--out-dir", required=True, type=pathlib.Path)
    parser.add_argument(
        "--include-status",
        default="admit,secondary",
        help="Comma-separated admission_status values to resolve (default: admit,secondary)",
    )
    args = parser.parse_args()

    statuses = {x.strip() for x in args.include_status.split(",") if x.strip()}
    with args.seeds.open(newline="", encoding="utf-8") as handle:
        seeds = list(csv.DictReader(handle))

    selected = [s for s in seeds if s.get("admission_status", "").strip() in statuses]
    if not selected:
        raise SystemExit("No seed rows matched the requested admission statuses")

    summary: list[dict[str, str]] = []
    failed = False
    for i, seed in enumerate(selected):
        accession = seed["accession"].strip()
        uids = esearch_sra(accession)
        text = efetch_runinfo(uids)
        rows = normalize_runinfo(text, seed)
        out = args.out_dir / f"{safe_name(seed['seed_id'])}_{safe_name(accession)}_runinfo.csv"
        write_rows(out, rows)

        run_accessions = sorted({r.get("Run", "") for r in rows if r.get("Run", "")})
        status = "ok" if rows else "no_runinfo"
        if not rows:
            failed = True
        summary.append(
            {
                "seed_id": seed["seed_id"],
                "accession": accession,
                "accession_type": seed.get("accession_type", ""),
                "admission_status": seed.get("admission_status", ""),
                "sra_uid_count": str(len(uids)),
                "run_count": str(len(run_accessions)),
                "status": status,
                "output_file": str(out),
            }
        )
        # Respect NCBI request-rate guidance without requiring an API key.
        if i + 1 < len(selected):
            time.sleep(0.4)

    write_rows(args.out_dir / "manifest_fetch_summary.csv", summary)

    for row in summary:
        print(
            f"{row['seed_id']}: {row['accession']} -> {row['run_count']} runs "
            f"({row['status']})"
        )

    if failed:
        print(
            "One or more accessions returned no RunInfo. Inspect the summary before downstream use.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
