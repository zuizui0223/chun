#!/usr/bin/env python3
"""Validate the focal Camellia SRA manifest before scientific admission.

Archive consistency is kept separate from biological meaning. Known Camellia
metadata conflicts remain frozen in
``data/public_sequence_metadata_conflicts_v0_1.csv`` and cannot be silently
resolved by downstream code.
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import re


EXPECTED = {
    # Zhou et al. 2017: five flower stages x three biological replicates.
    "SEQ002": {"min_runs": 15, "expected_runs": 15},
}

EXPECTED_ARCHIVE_MODELS = {
    "SEQ002": {"Illumina HiSeq 2500"},
}


def read_rows(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_archive_model_snapshot(
    seed_id: str, manifest_rows: list[dict[str, str]]
) -> list[str]:
    observed = {
        row.get("Model", "").strip()
        for row in manifest_rows
        if row.get("Model", "").strip()
    }
    expected = EXPECTED_ARCHIVE_MODELS[seed_id]
    if observed != expected:
        return [
            f"{seed_id}: SRA Model metadata changed: observed={sorted(observed)}, "
            f"frozen={sorted(expected)}; re-audit publication/archive provenance"
        ]
    print(f"{seed_id}: current SRA Model snapshot frozen as {sorted(observed)}")
    return []


def validate_camellia_stage_structure(
    manifest_rows: list[dict[str, str]],
) -> list[str]:
    """Validate five archive groups x three replicates in RunInfo.

    RunInfo does not define biological stage meaning. The subsequent BioSample
    gate independently verifies that groups 10/6/7/8/9 map to S1/S2/S3/S4/S5.
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
            "not inferred from numeric RunInfo labels."
        )
    return failures


def validate_conflict_registry(path: pathlib.Path) -> list[str]:
    rows = read_rows(path)
    if not rows:
        return [f"metadata conflict registry missing or empty: {path}"]
    ids = {row.get("conflict_id", "").strip() for row in rows}
    required = {"META003", "META004", "META005", "META007"}
    missing = sorted(required - ids)
    if missing:
        return [f"metadata conflict registry lacks required Camellia entries: {missing}"]
    non_camellia = sorted(
        row.get("conflict_id", "").strip()
        for row in rows
        if row.get("system", "").strip() != "Camellia"
    )
    if non_camellia:
        return [f"metadata conflict registry contains out-of-scope systems: {non_camellia}"]
    print(f"Camellia metadata conflict registry loaded: {len(rows)} entries")
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-dir", required=True, type=pathlib.Path)
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
        missing_biosample = sum(
            1 for row in rows if not row.get("BioSample", "").strip()
        )
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
    if "SEQ002" in manifests:
        failures.extend(validate_camellia_stage_structure(manifests["SEQ002"]))

    if failures:
        print("\nCamellia manifest admission gate FAILED:")
        for item in failures:
            print(f"- {item}")
        return 1

    print(
        "Camellia manifest admission gate passed for run counts, frozen archive "
        "metadata, and developmental replicate structure."
    )
    print(
        "Known biological/provenance conflicts remain explicit and must be resolved "
        "before the corresponding downstream claim is admitted."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
