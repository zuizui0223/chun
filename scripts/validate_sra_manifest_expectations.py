#!/usr/bin/env python3
"""Validate focal public SRA manifests before they become scientific inputs."""

from __future__ import annotations

import argparse
import csv
import pathlib

EXPECTED = {
    # Chang et al. 2026 report 25 newly sequenced samples; the other 12 samples
    # in the 37-sample phylogenomic analysis were obtained from NCBI/other studies.
    "SEQ001": {"min_runs": 25, "expected_runs": 25},
    # Zhou et al. 2017: five flower stages x three biological replicates.
    "SEQ002": {"min_runs": 15, "expected_runs": 15},
}


def read_rows(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_cirsium_taxon_audit(
    manifest_rows: list[dict[str, str]], audit_path: pathlib.Path
) -> list[str]:
    failures: list[str] = []
    audit_rows = read_rows(audit_path)
    if not audit_rows:
        return [f"Cirsium taxon audit is missing or empty: {audit_path}"]

    by_run = {row.get("Run", "").strip(): row for row in manifest_rows}
    audit_by_run = {row.get("run", "").strip(): row for row in audit_rows}
    if set(by_run) != set(audit_by_run):
        missing = sorted(set(by_run) - set(audit_by_run))
        extra = sorted(set(audit_by_run) - set(by_run))
        failures.append(
            "Cirsium taxon-audit run set differs from live SRA metadata; "
            f"missing_from_audit={missing}, extra_in_audit={extra}"
        )
        return failures

    mismatch_count = 0
    for run, live in by_run.items():
        frozen = audit_by_run[run]
        comparisons = {
            "BioSample": "biosample",
            "SampleName": "sra_sample_name",
            "ScientificName": "sra_scientific_name",
        }
        for live_key, audit_key in comparisons.items():
            if live.get(live_key, "").strip() != frozen.get(audit_key, "").strip():
                failures.append(
                    f"{run}: live {live_key} changed from audited value "
                    f"{frozen.get(audit_key, '')!r} to {live.get(live_key, '')!r}"
                )
        if frozen.get("taxon_label_status", "").strip() != "consistent":
            mismatch_count += 1
        if not frozen.get("paper_sample_taxon_from_sample_name", "").strip():
            failures.append(f"{run}: audited paper/sample taxon is empty")
        if not frozen.get("voucher_or_sample_id", "").strip():
            failures.append(f"{run}: audited voucher/sample identifier is empty")

    print(
        f"Cirsium taxonomy audit: {len(audit_rows)} runs frozen; "
        f"{mismatch_count} SRA ScientificName labels are coarse/mismatched relative to SampleName."
    )
    print(
        "Downstream taxon identity must use the audited paper/sample mapping, "
        "not SRA ScientificName."
    )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-dir", required=True, type=pathlib.Path)
    parser.add_argument(
        "--cirsium-taxon-audit",
        type=pathlib.Path,
        default=pathlib.Path("data/cirsium_run_taxon_audit_v0_1.csv"),
    )
    args = parser.parse_args()

    failures: list[str] = []
    manifests: dict[str, list[dict[str, str]]] = {}
    for seed_id, rule in EXPECTED.items():
        matches = sorted(args.manifest_dir.glob(f"{seed_id}_*_runinfo.csv"))
        if len(matches) != 1:
            failures.append(f"{seed_id}: expected exactly one manifest, found {len(matches)}")
            continue
        rows = read_rows(matches[0])
        manifests[seed_id] = rows
        runs = {row.get("Run", "").strip() for row in rows if row.get("Run", "").strip()}
        if len(runs) < rule["min_runs"]:
            failures.append(
                f"{seed_id}: found {len(runs)} unique runs; expected at least {rule['min_runs']}"
            )
        if len(runs) != rule["expected_runs"]:
            failures.append(
                f"{seed_id}: run count {len(runs)} differs from literature expectation "
                f"{rule['expected_runs']}; audit before admission"
            )
        missing_biosample = sum(1 for row in rows if not row.get("BioSample", "").strip())
        if missing_biosample:
            failures.append(f"{seed_id}: {missing_biosample} rows lack BioSample identifiers")
        duplicate_rows = len(rows) - len(runs)
        if duplicate_rows:
            failures.append(
                f"{seed_id}: {duplicate_rows} duplicate/non-unique run rows; inspect RunInfo"
            )
        print(f"{seed_id}: {len(runs)} unique runs in {matches[0].name}")

    if "SEQ001" in manifests:
        failures.extend(validate_cirsium_taxon_audit(manifests["SEQ001"], args.cirsium_taxon_audit))

    if failures:
        print("\nManifest admission gate FAILED:")
        for item in failures:
            print(f"- {item}")
        return 1

    print("Manifest admission gate passed for all focal datasets and frozen taxon mappings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
