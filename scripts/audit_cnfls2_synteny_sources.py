#!/usr/bin/env python3
"""Resolve public GWH assemblies/download routes for the CnFLS2 synteny test.

The source IDs encode GWH assembly stems, but the script does not trust that
inference alone. It queries the official GWH Assembly API, verifies the returned
assembly accession and Camellia taxon, and freezes annotation download URLs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import requests

API = "https://ngdc.cncb.ac.cn/gwh/api/public/assembly"
TARGETS = [
    {
        "role": "cnitidissima_candidate",
        "assembly_candidates": ["GWHFILD00000000.1", "GWHFILD00000000"],
        "target_feature": "GWHTFILD005297.1",
        "target_gene": "GWHGFILD004416.1",
        "source_basis": "public C. nitidissima GWH candidate annotation",
    },
    {
        "role": "tea_dasz_crosswalk",
        "assembly_candidates": ["GWHABKB00000000.1", "GWHABKB00000000"],
        "target_feature": "GWHTABKB031920",
        "target_gene": "",
        "source_basis": "TPIA2 CSA008358 crosswalk to DASZ GWH transcript",
    },
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def resolve(session: requests.Session, target: dict[str, object]) -> tuple[dict[str, object], list[dict[str, object]]]:
    attempts: list[dict[str, object]] = []
    for accession in target["assembly_candidates"]:
        response = session.get(f"{API}/{accession}", timeout=90)
        attempt: dict[str, object] = {
            "requested_accession": accession,
            "url": response.url,
            "status": response.status_code,
            "sha256": sha256(response.content),
            "bytes": len(response.content),
        }
        attempts.append(attempt)
        if response.status_code != 200:
            continue
        try:
            payload = response.json()
        except ValueError:
            attempt["json_error"] = "response was not JSON"
            continue
        returned = str(payload.get("assemblyAccession") or "")
        organism = str(payload.get("organism") or "")
        if not returned.startswith(accession.split(".")[0]):
            attempt["validation_error"] = f"returned assemblyAccession={returned!r}"
            continue
        if "Camellia" not in organism:
            attempt["validation_error"] = f"returned organism={organism!r}"
            continue
        row = {
            "role": target["role"],
            "requested_accession": accession,
            "assembly_accession": returned,
            "assembly_name": payload.get("assemblyName", ""),
            "organism": organism,
            "tax_id": payload.get("taxId", ""),
            "bioproject": payload.get("bioprojectAccession", ""),
            "biosample": payload.get("biosampleAccession", ""),
            "assembly_level": payload.get("assemblyLevel", ""),
            "target_feature": target["target_feature"],
            "target_gene": target["target_gene"],
            "ftp_gff": payload.get("ftpPathGff", ""),
            "ftp_rna": payload.get("ftpPathRna", ""),
            "ftp_cds": payload.get("ftpPathCds", ""),
            "ftp_protein": payload.get("ftpPathProtein", ""),
            "ftp_feature": payload.get("ftpPathFeature", ""),
            "api_response_sha256": attempt["sha256"],
            "source_basis": target["source_basis"],
            "claim_boundary": "official assembly/download provenance only; local collinearity and gene-tree evidence not yet computed",
        }
        if not row["ftp_gff"] or not row["ftp_protein"]:
            attempt["validation_error"] = "assembly lacks public GFF or protein route"
            continue
        return row, attempts
    raise SystemExit(f"Could not resolve official GWH assembly for role={target['role']}: {attempts}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers["User-Agent"] = "chun-cnfls2-synteny-source-audit/0.1"
    rows: list[dict[str, object]] = []
    all_attempts: dict[str, list[dict[str, object]]] = {}
    for target in TARGETS:
        row, attempts = resolve(session, target)
        rows.append(row)
        all_attempts[str(target["role"])] = attempts

    fields = list(rows[0])
    with (args.out_dir / "assembly_sources.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "resolved_sources": len(rows),
        "roles": [row["role"] for row in rows],
        "assemblies": [row["assembly_accession"] for row in rows],
        "target_features": [row["target_feature"] for row in rows],
        "all_annotation_routes_present": all(row["ftp_gff"] and row["ftp_protein"] for row in rows),
        "decision": "proceed to local-neighborhood and FLS-family gene-tree analysis",
        "claim_ceiling": "source-route gate only; no synteny, orthology or functional equivalence inferred",
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (args.out_dir / "request_attempts.json").write_text(json.dumps(all_attempts, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
