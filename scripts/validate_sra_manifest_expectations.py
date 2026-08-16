#!/usr/bin/env python3
"""Validate focal public SRA manifests before they become scientific inputs.

This gate intentionally separates archive consistency from biological meaning.
A manifest can be internally stable while still carrying a known conflict with
publication metadata; such conflicts are frozen in
``data/public_sequence_metadata_conflicts_v0_1.csv`` and must not be silently
resolved by downstream code.
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import re

EXPECTED = {
    # Chang et al. 2026 report 25 newly sequenced samples; the other 12 samples
    # in the 37-sample phylogenomic analysis were obtained from NCBI/other studies.
    "SEQ001": {"min_runs": 25, "expected_runs": 25},
    # Zhou et al. 2017: five flower stages x three biological replicates.
    "SEQ002": {"min_runs": 15, "expected_runs": 15},
}

# These are the current SRA RunInfo values, not an assertion that the archive
# value is biologically/methodologically correct. In particular, SEQ001 is a
# known publication-vs-archive conflict: the paper reports NovaSeq whereas the
# current SRA records say MiniSeq. Freezing the live value makes future archive
# edits visible instead of silently changing the analysis provenance.
EXPECTED_ARCHIVE_MODELS = {
    "SEQ001": {"Illumina MiniSeq"},
    "SEQ002": {"Illumina HiSeq 2500"},
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


def validate_archive_model_snapshot(
    seed_id: str, manifest_rows: list[dict[str, str]]
) -> list[str]:
    observed = {row.get("Model", "").strip() for row in manifest_rows if row.get("Model", "").strip()}
    expected = EXPECTED_ARCHIVE_MODELS[seed_id]
    if observed != expected:
        return [
            f"{seed_id}: SRA Model metadata changed: observed={sorted(observed)}, "
            f"frozen={sorted(expected)}; re-audit publication/archive provenance"
        ]
    print(f"{seed_id}: current SRA Model snapshot frozen as {sorted(observed)}")
    if seed_id == "SEQ001":
        print(
            "SEQ001 WARNING: publication reports Illumina NovaSeq, while current SRA "
            "RunInfo reports Illumina MiniSeq. Conflict remains unresolved; neither "
            "value may silently overwrite the other."
        )
    return []


def validate_camellia_stage_structure(manifest_rows: list[dict[str, str]]) -> list[str]:
    """Validate the five archive groups x three replicates in RunInfo.

    RunInfo itself does not explain the biological stage meaning; the subsequent
    BioSample provenance gate independently verifies that groups 10/6/7/8/9 map
    to stage1/stage2/stage3/stage4/stage5.
    """

    failures: list[str] = []
    pattern = re.compile(r"^(?P<group>\d+)_rep(?P<rep>[123])$")
    groups: dict[str, set[str]] = {}
    unparsed: list[str] = []

    for row in manifest_rows:
        label = (row.get("LibraryName") or row.get("SampleName") or "").strip()
        match = pattern.match(label)
        if not match:
            unparsed.append(label)
            continue
        groups.setdefault(match.group("group"), set()).add(match.group("rep"))

    if unparsed:
        failures.append(f"SEQ002: unparsed LibraryName labels: {sorted(unparsed)}")

    expected_groups = {"6", "7", "8", "9", "10"}
    if set(groups) != expected_groups:
        failures.append(
            f"SEQ002: SRA developmental group labels changed: observed={sorted(groups)}, "
            f"frozen={sorted(expected_groups)}"
        )

    for group in sorted(groups):
        if groups[group] != {"1", "2", "3"}:
            failures.append(
                f"SEQ002: archive group {group} has replicate labels {sorted(groups[group])}; "
                "expected rep1, rep2, rep3"
            )

    if not failures:
        print("SEQ002: RunInfo structure is five numeric groups (6-10) x three replicates.")
        print(
            "SEQ002: biological S1-S5 meaning is verified later from BioSample dev_stage, "
            "not inferred from these numeric RunInfo labels."
        )
    return failures


def validate_conflict_registry(path: pathlib.Path) -> list[str]:
    rows = read_rows(path)
    if not rows:
        return [f"metadata conflict registry missing or empty: {path}"]
    ids = {row.get("conflict_id", "").strip() for row in rows}
    required = {"META001", "META002", "META003", "META004", "META005", "META006"}
    missing = sorted(required - ids)
    if missing:
        return [f"metadata conflict registry lacks required entries: {missing}"]
    print(f"Metadata conflict registry loaded: {len(rows)} entries")
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-dir", required=True, type=pathlib.Path)
    parser.add_argument(
        "--cirsium-taxon-audit",
        type=pathlib.Path,
        default=pathlib.Path("data/cirsium_run_taxon_audit_v0_1.csv"),
    )
    parser.add_argument(
        "--metadata-conflicts",
        type=pathlib.Path,
        default=pathlib.Path("data/public_sequence_metadata_conflicts_v0_1.csv"),
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
        failures.extend(validate_archive_model_snapshot(seed_id, rows))

    failures.extend(validate_conflict_registry(args.metadata_conflicts))

    if "SEQ001" in manifests:
        failures.extend(validate_cirsium_taxon_audit(manifests["SEQ001"], args.cirsium_taxon_audit))
    if "SEQ002" in manifests:
        failures.extend(validate_camellia_stage_structure(manifests["SEQ002"]))

    if failures:
        print("\nManifest admission gate FAILED:")
        for item in failures:
            print(f"- {item}")
        return 1

    print(
        "Manifest admission gate passed for run counts, frozen archive metadata, "
        "Cirsium taxon mappings, and Camellia replicate structure."
    )
    print(
        "Known biological/provenance conflicts remain explicit and must be resolved "
        "before the corresponding downstream claim is admitted."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
