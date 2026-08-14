#!/usr/bin/env python3
"""Resolve and validate the 20 public golden-Camellia SRR accessions.

The source table freezes three different identities instead of collapsing them:

- the taxon label published in Xie et al. (2025);
- the current NCBI SRA ScientificName/BioSample provenance;
- the later taxonomic-independence assessment used by this project.

This script refuses silent archive drift. A change in SRR, BioProject,
BioSample, or ScientificName must be re-audited before downstream use.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import pathlib
import time
import urllib.parse
import urllib.request

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
USER_AGENT = "chun-flower-colour/0.1 (golden Camellia public backbone audit)"
EXPECTED_PROJECT = "PRJNA1050624"
EXPECTED_MODEL = "Illumina HiSeq 2500"
EXPECTED_LAYOUT = "PAIRED"
EXPECTED_SOURCE = "TRANSCRIPTOMIC"


def request_text(endpoint: str, params: dict[str, str], retries: int = 4) -> str:
    url = f"{EUTILS}/{endpoint}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                return response.read().decode("utf-8")
        except Exception as exc:  # pragma: no cover - network-dependent
            last = exc
            if attempt + 1 < retries:
                time.sleep(2**attempt)
    raise RuntimeError(f"NCBI request failed after {retries} attempts: {url}") from last


def esearch_sra(accession: str) -> list[str]:
    payload = request_text(
        "esearch.fcgi",
        {"db": "sra", "term": accession, "retmode": "json", "retmax": "10"},
    )
    return json.loads(payload).get("esearchresult", {}).get("idlist", [])


def efetch_runinfo(uid: str) -> dict[str, str]:
    payload = request_text(
        "efetch.fcgi",
        {"db": "sra", "id": uid, "rettype": "runinfo", "retmode": "text"},
    ).strip()
    rows = list(csv.DictReader(io.StringIO(payload))) if payload else []
    if len(rows) != 1:
        raise RuntimeError(f"SRA UID {uid}: expected one RunInfo row, found {len(rows)}")
    return {str(k): (v or "").strip() for k, v in rows[0].items() if k is not None}


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: pathlib.Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def frozen_equal(
    failures: list[str], *, code: str, field: str, frozen: str, live: str
) -> None:
    if frozen.strip() != live.strip():
        failures.append(
            f"{code}: live SRA {field} changed from frozen {frozen!r} to {live!r}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--table", required=True, type=pathlib.Path)
    parser.add_argument("--out", required=True, type=pathlib.Path)
    args = parser.parse_args()

    source = read_csv(args.table)
    if len(source) != 20:
        raise SystemExit(f"Expected exactly 20 frozen paper rows, found {len(source)}")
    srrs = [row.get("srr", "").strip() for row in source]
    if len(set(srrs)) != 20 or any(not srr.startswith("SRR") for srr in srrs):
        raise SystemExit("The 20-row source table must contain 20 unique SRR accessions")

    resolved: list[dict[str, str]] = []
    failures: list[str] = []
    for index, paper in enumerate(source):
        srr = paper["srr"].strip()
        ids = esearch_sra(srr)
        if len(ids) != 1:
            failures.append(f"{srr}: expected one SRA UID, found {ids}")
            continue
        live = efetch_runinfo(ids[0])
        if live.get("Run", "") != srr:
            failures.append(f"{srr}: live RunInfo resolved to {live.get('Run', '')!r}")
            continue

        code = paper["code"].strip()
        frozen_equal(
            failures,
            code=code,
            field="BioProject",
            frozen=paper.get("bioproject", ""),
            live=live.get("BioProject", ""),
        )
        frozen_equal(
            failures,
            code=code,
            field="BioSample",
            frozen=paper.get("biosample", ""),
            live=live.get("BioSample", ""),
        )
        frozen_equal(
            failures,
            code=code,
            field="ScientificName",
            frozen=paper.get("sra_scientific_name", ""),
            live=live.get("ScientificName", ""),
        )

        if live.get("BioProject", "") != EXPECTED_PROJECT:
            failures.append(
                f"{code}: expected common BioProject {EXPECTED_PROJECT}, got {live.get('BioProject','')!r}"
            )
        if live.get("Model", "") != EXPECTED_MODEL:
            failures.append(
                f"{code}: expected archive model {EXPECTED_MODEL}, got {live.get('Model','')!r}"
            )
        if live.get("LibraryLayout", "") != EXPECTED_LAYOUT:
            failures.append(
                f"{code}: expected paired libraries, got {live.get('LibraryLayout','')!r}"
            )
        if live.get("LibrarySource", "") != EXPECTED_SOURCE:
            failures.append(
                f"{code}: expected transcriptomic source, got {live.get('LibrarySource','')!r}"
            )

        resolved.append(
            {
                "code": paper["code"],
                "published_taxon": paper["published_taxon"],
                "archive_taxon_status": paper["archive_taxon_status"],
                "taxonomic_independence_status": paper["taxonomic_independence_status"],
                "taxonomic_note": paper["taxonomic_note"],
                "original_habitat": paper["original_habitat"],
                "country_or_region": paper["country_or_region"],
                "soil_type": paper["soil_type"],
                **live,
            }
        )
        print(
            f"{paper['code']}: {paper['published_taxon']} / {srr} -> "
            f"BioProject={live.get('BioProject','')} BioSample={live.get('BioSample','')} "
            f"ScientificName={live.get('ScientificName','')}"
        )
        if index + 1 < len(source):
            time.sleep(0.4)

    if failures:
        for item in failures:
            print(f"ERROR: {item}")
        return 1

    write_csv(args.out, resolved)

    projects = sorted({row.get("BioProject", "") for row in resolved if row.get("BioProject", "")})
    biosamples = {row.get("BioSample", "") for row in resolved if row.get("BioSample", "")}
    models = sorted({row.get("Model", "") for row in resolved if row.get("Model", "")})
    layouts = sorted({row.get("LibraryLayout", "") for row in resolved if row.get("LibraryLayout", "")})
    sources = sorted({row.get("LibrarySource", "") for row in resolved if row.get("LibrarySource", "")})
    exact = sum(1 for row in source if row.get("archive_taxon_status", "") == "exact")
    print(f"Resolved {len(resolved)} runs; BioProjects={projects}")
    print(
        f"Unique BioSamples={len(biosamples)}; models={models}; layouts={layouts}; sources={sources}"
    )
    print(
        f"Archive taxonomy: {exact}/20 exact published-name matches; remaining labels are "
        "preserved as explicit taxonomy/nomenclature conflicts rather than overwritten."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
