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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-dir", required=True, type=pathlib.Path)
    args = parser.parse_args()

    failures: list[str] = []
    for seed_id, rule in EXPECTED.items():
        matches = sorted(args.manifest_dir.glob(f"{seed_id}_*_runinfo.csv"))
        if len(matches) != 1:
            failures.append(f"{seed_id}: expected exactly one manifest, found {len(matches)}")
            continue
        rows = read_rows(matches[0])
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

    if failures:
        print("\nManifest admission gate FAILED:")
        for item in failures:
            print(f"- {item}")
        return 1

    print("Manifest admission gate passed for all focal datasets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
