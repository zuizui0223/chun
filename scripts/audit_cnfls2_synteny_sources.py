#!/usr/bin/env python3
"""Resolve public annotation routes for the CnFLS2 gene-tree/synteny test.

The C. nitidissima source uses the validated official static GWH release. The
tea comparison uses the original Longjing43 assembly that is directly linked by
TPIA2 to `CSA008358` through transcript `GWHTACFB016172`; this avoids replacing
an exact crosswalk with a merely sequence-similar locus from another assembly.
Transient API/download endpoint failures are retried and recorded rather than
preventing the declared static fallback from being evaluated.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from pathlib import Path
from typing import Any

import requests

API = "https://ngdc.cncb.ac.cn/gwh/api/public/assembly"
CN_BASE = (
    "https://download.cncb.ac.cn/gwh/Plants/"
    "Camellia_nitidissima_Camellia_nitidissima_GWHFILD00000000.1/"
    "GWHFILD00000000.1"
)
TARGETS: list[dict[str, Any]] = [
    {
        "role": "cnitidissima_candidate",
        "assembly_candidates": ["GWHFILD00000000.1", "GWHFILD00000000"],
        "target_feature": "GWHTFILD005297.1",
        "target_gene": "GWHGFILD004416.1",
        "query_anchor": "GWHTFILD005297.1",
        "source_basis": "public C. nitidissima GWH release used by the admitted full-length recovery workflow",
        "fallback": {
            "assembly_accession": "GWHFILD00000000.1",
            "assembly_name": "Camellia_nitidissima",
            "organism": "Camellia nitidissima",
            "tax_id": "",
            "bioproject": "",
            "biosample": "",
            "assembly_level": "public GWH annotated assembly",
            "ftp_gff": CN_BASE + ".gff.gz",
            "ftp_rna": CN_BASE + ".RNA.fasta.gz",
            "ftp_cds": CN_BASE + ".CDS.fasta.gz",
            "ftp_protein": CN_BASE + ".Protein.faa.gz",
            "ftp_feature": CN_BASE + ".feature.gz",
        },
    },
    {
        "role": "tea_longjing43_crosswalk",
        "assembly_candidates": ["GWHACFB00000000", "GWHACFB00000000.1"],
        "target_feature": "GWHTACFB016172",
        "target_gene": "",
        "query_anchor": "CSA008358/CSS0045924 -> GWHTACFB016172 TPIA2 exact crosswalk",
        "source_basis": "TPIA2 exact CSA008358 Longjing43 crosswalk plus official GWHACFB assembly metadata",
    },
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_url(session: requests.Session, url: str, retries: int = 3) -> dict[str, Any]:
    history: list[dict[str, Any]] = []
    for attempt_no in range(1, retries + 1):
        try:
            response = session.get(
                url,
                headers={"Range": "bytes=0-0"},
                stream=True,
                timeout=(20, 120),
            )
            result = {
                "attempt": attempt_no,
                "url": url,
                "status": response.status_code,
                "content_range": response.headers.get("Content-Range", ""),
                "content_type": response.headers.get("Content-Type", ""),
                "available": response.status_code in {200, 206},
            }
            response.close()
            history.append(result)
            if result["available"]:
                return {**result, "history": history}
        except requests.RequestException as exc:
            history.append({"attempt": attempt_no, "url": url, "available": False, "error": str(exc)})
        if attempt_no < retries:
            time.sleep(2 * attempt_no)
    return {**history[-1], "history": history}


def row_from_payload(target: dict[str, Any], accession: str, payload: dict[str, Any], digest: str) -> dict[str, Any] | None:
    returned = str(payload.get("assemblyAccession") or "")
    organism = str(payload.get("organism") or "")
    if not returned.startswith(accession.split(".")[0]) or "Camellia" not in organism:
        return None
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
        "ftp_gff": payload.get("ftpPathGff", ""),
        "ftp_rna": payload.get("ftpPathRna", ""),
        "ftp_cds": payload.get("ftpPathCds", ""),
        "ftp_protein": payload.get("ftpPathProtein", ""),
        "ftp_feature": payload.get("ftpPathFeature", ""),
        "target_feature": target["target_feature"],
        "target_gene": target["target_gene"],
        "query_anchor": target["query_anchor"],
        "resolution_route": "official_GWH_Assembly_API",
        "api_response_sha256": digest,
        "source_basis": target["source_basis"],
        "claim_boundary": "official assembly/download and crosswalk provenance only; local collinearity and gene-tree evidence not yet computed",
    }
    if not row["ftp_gff"] or not row["ftp_protein"]:
        return None
    return row


def resolve(session: requests.Session, target: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    for accession in target["assembly_candidates"]:
        url = f"{API}/{accession}"
        try:
            response = session.get(url, timeout=(20, 120))
        except requests.RequestException as exc:
            attempts.append(
                {
                    "route": "official_GWH_Assembly_API",
                    "requested_accession": accession,
                    "url": url,
                    "transport_error": str(exc),
                }
            )
            continue
        attempt: dict[str, Any] = {
            "route": "official_GWH_Assembly_API",
            "requested_accession": accession,
            "url": response.url,
            "status": response.status_code,
            "sha256": sha256(response.content),
            "bytes": len(response.content),
            "response_preview": response.text[:1000],
        }
        attempts.append(attempt)
        if response.status_code != 200:
            continue
        try:
            payload = response.json()
        except ValueError:
            attempt["validation_error"] = "response was not JSON"
            continue
        attempt["payload_keys"] = sorted(payload)
        row = row_from_payload(target, accession, payload, str(attempt["sha256"]))
        if row is not None:
            return row, attempts
        attempt["validation_error"] = (
            f"unusable API payload: assemblyAccession={payload.get('assemblyAccession')!r}, "
            f"organism={payload.get('organism')!r}, message={payload.get('message')!r}"
        )

    fallback = target.get("fallback")
    if fallback:
        url_checks = [
            validate_url(session, str(fallback[key]))
            for key in ["ftp_gff", "ftp_rna", "ftp_cds", "ftp_protein"]
        ]
        attempts.append({"route": "validated_static_GWH_release", "url_checks": url_checks})
        if all(check.get("available") for check in url_checks):
            first_digest = next((attempt.get("sha256", "") for attempt in attempts if attempt.get("sha256")), "")
            return {
                "role": target["role"],
                "requested_accession": target["assembly_candidates"][0],
                **fallback,
                "target_feature": target["target_feature"],
                "target_gene": target["target_gene"],
                "query_anchor": target["query_anchor"],
                "resolution_route": "validated_static_GWH_release",
                "api_response_sha256": first_digest,
                "source_basis": target["source_basis"],
                "claim_boundary": "official static release provenance only; local collinearity and gene-tree evidence not yet computed",
            }, attempts
    raise RuntimeError(f"Could not resolve annotation source for role={target['role']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers["User-Agent"] = "chun-cnfls2-synteny-source-audit/0.4"
    rows: list[dict[str, Any]] = []
    all_attempts: dict[str, list[dict[str, Any]]] = {}
    failures: list[dict[str, str]] = []
    for target in TARGETS:
        try:
            row, attempts = resolve(session, target)
            rows.append(row)
            all_attempts[str(target["role"])] = attempts
        except Exception as exc:
            failures.append({"role": str(target["role"]), "error": str(exc)})
            all_attempts.setdefault(str(target["role"]), [])

    (args.out_dir / "request_attempts.json").write_text(
        json.dumps(all_attempts, indent=2) + "\n", encoding="utf-8"
    )
    (args.out_dir / "failures.json").write_text(
        json.dumps(failures, indent=2) + "\n", encoding="utf-8"
    )

    if rows:
        fields = list(rows[0])
        with (args.out_dir / "assembly_sources.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    summary = {
        "resolved_sources": len(rows),
        "expected_sources": len(TARGETS),
        "roles": [row["role"] for row in rows],
        "assemblies": [row["assembly_accession"] for row in rows],
        "target_features": [row["target_feature"] for row in rows],
        "resolution_routes": [row["resolution_route"] for row in rows],
        "failed_roles": [failure["role"] for failure in failures],
        "all_annotation_routes_present": bool(rows) and all(row["ftp_gff"] and row["ftp_protein"] for row in rows),
        "decision": "proceed to exact-crosswalk local neighborhoods and FLS-family gene tree" if len(rows) == len(TARGETS) else "source gate incomplete; do not start synteny analysis",
        "claim_ceiling": "source-route and crosswalk gate only; no synteny, orthology or functional equivalence inferred",
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if failures or len(rows) != len(TARGETS):
        raise SystemExit("Not all synteny annotation sources were resolved")


if __name__ == "__main__":
    main()
