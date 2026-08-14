#!/usr/bin/env python3
"""Validate frozen scientific sample manifests against current NCBI metadata.

The goal is not to assert that every archive field is biologically correct.
Instead, it guarantees that downstream code sees the exact run/sample identity
that was audited, while known publication/archive conflicts remain explicit.
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import re


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def index(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        value = row.get(key, "").strip()
        if not value:
            raise ValueError(f"blank key {key}")
        if value in out:
            raise ValueError(f"duplicate {key}: {value}")
        out[value] = row
    return out


def bio_attributes(rows: list[dict[str, str]]) -> dict[tuple[str, str], str]:
    out: dict[tuple[str, str], str] = {}
    for row in rows:
        biosample = row.get("biosample", "").strip()
        name = row.get("attribute_name", "").strip()
        value = row.get("value", "").strip()
        key = (biosample, name)
        if key in out and out[key] != value:
            raise ValueError(f"conflicting BioSample attribute {key}: {out[key]!r} vs {value!r}")
        out[key] = value
    return out


def check_equal(
    failures: list[str], label: str, observed: object, expected: object
) -> None:
    if str(observed).strip() != str(expected).strip():
        failures.append(f"{label}: observed={observed!r}, expected={expected!r}")


def validate_cirsium(
    frozen_path: pathlib.Path,
    runinfo_path: pathlib.Path,
    attr_rows: list[dict[str, str]],
) -> list[str]:
    failures: list[str] = []
    frozen = index(read_csv(frozen_path), "run")
    live = index(read_csv(runinfo_path), "Run")
    attrs = bio_attributes(attr_rows)

    if set(frozen) != set(live):
        failures.append(
            f"Cirsium run set changed: frozen_only={sorted(set(frozen)-set(live))}, "
            f"live_only={sorted(set(live)-set(frozen))}"
        )
        return failures

    for run, fr in frozen.items():
        lv = live[run]
        comparisons = {
            "biosample": "BioSample",
            "sra_scientific_name": "ScientificName",
            "sra_sample_name": "SampleName",
            "sra_library_name": "LibraryName",
            "sra_model": "Model",
            "spots": "spots",
            "bases": "bases",
            "avg_length": "avgLength",
            "run_hash": "RunHash",
            "read_hash": "ReadHash",
        }
        for frozen_key, live_key in comparisons.items():
            check_equal(failures, f"{run} {frozen_key}", lv.get(live_key, ""), fr.get(frozen_key, ""))

        biosample = fr["biosample"].strip()
        check_equal(failures, f"{run} isolate", attrs.get((biosample, "isolate"), ""), fr["biosample_isolate"])
        check_equal(failures, f"{run} locality", attrs.get((biosample, "geo_loc_name"), ""), fr["geo_loc_name"])
        check_equal(failures, f"{run} collection_date", attrs.get((biosample, "collection_date"), ""), fr["collection_date"])
        check_equal(failures, f"{run} dev_stage", attrs.get((biosample, "dev_stage"), ""), fr["biosample_dev_stage"])
        check_equal(failures, f"{run} tissue", attrs.get((biosample, "tissue"), ""), fr["tissue"])

        sample_match = re.match(r"^(.*)-(\d+)$", fr["sra_sample_name"].strip())
        if not sample_match:
            failures.append(f"{run}: SRA SampleName no longer parses as taxon-voucher")
        else:
            check_equal(failures, f"{run} paper_taxon", sample_match.group(1), fr["paper_taxon"])
            check_equal(failures, f"{run} voucher", sample_match.group(2), fr["voucher_or_sample_id"])
        if fr["admission_status"].strip() != "admit_for_leaf_coding_screen":
            failures.append(f"{run}: unexpected admission status {fr['admission_status']!r}")
        if fr["tissue"].strip().lower() != "young leaves":
            failures.append(f"{run}: coding-screen manifest unexpectedly contains non-leaf tissue")

    print(f"Cirsium admitted manifest validated: {len(frozen)} runs")
    return failures


def validate_camellia(
    frozen_path: pathlib.Path,
    runinfo_path: pathlib.Path,
    attr_rows: list[dict[str, str]],
) -> list[str]:
    failures: list[str] = []
    frozen = index(read_csv(frozen_path), "run")
    live = index(read_csv(runinfo_path), "Run")
    attrs = bio_attributes(attr_rows)

    if set(frozen) != set(live):
        failures.append(
            f"Camellia run set changed: frozen_only={sorted(set(frozen)-set(live))}, "
            f"live_only={sorted(set(live)-set(frozen))}"
        )
        return failures

    stage_counts: dict[str, int] = {}
    total_spots = 0
    total_bases = 0
    paired = True
    for run, fr in frozen.items():
        lv = live[run]
        comparisons = {
            "biosample": "BioSample",
            "sra_scientific_name": "ScientificName",
            "sra_sample_name": "SampleName",
            "sra_library_name": "LibraryName",
            "sra_model": "Model",
            "spots": "spots",
            "bases": "bases",
            "avg_length": "avgLength",
            "run_hash": "RunHash",
            "read_hash": "ReadHash",
        }
        for frozen_key, live_key in comparisons.items():
            check_equal(failures, f"{run} {frozen_key}", lv.get(live_key, ""), fr.get(frozen_key, ""))

        biosample = fr["biosample"].strip()
        dev_stage = attrs.get((biosample, "dev_stage"), "")
        tissue = attrs.get((biosample, "tissue"), "")
        isolate = attrs.get((biosample, "isolate"), "")
        geo = attrs.get((biosample, "geo_loc_name"), "")
        check_equal(failures, f"{run} dev_stage", dev_stage, fr["biosample_dev_stage"])
        check_equal(failures, f"{run} tissue", tissue, fr["tissue"])
        check_equal(failures, f"{run} biological_replicate", isolate, fr["biological_replicate"])
        check_equal(failures, f"{run} geo_loc_name", geo, fr["geo_loc_name"])

        stage_match = re.fullmatch(r"stage([1-5])", dev_stage)
        if not stage_match:
            failures.append(f"{run}: BioSample dev_stage is not stage1-stage5: {dev_stage!r}")
        else:
            publication_stage = f"S{stage_match.group(1)}"
            check_equal(failures, f"{run} publication_stage", publication_stage, fr["publication_stage"])
            stage_counts[publication_stage] = stage_counts.get(publication_stage, 0) + 1

        lib_match = re.fullmatch(r"(\d+)_rep([123])", fr["sra_library_name"].strip())
        if not lib_match:
            failures.append(f"{run}: unexpected SRA LibraryName {fr['sra_library_name']!r}")
        else:
            check_equal(failures, f"{run} archive_group", lib_match.group(1), fr["archive_group"])
            check_equal(failures, f"{run} replicate", lib_match.group(2), fr["replicate"])

        if fr["tissue"].strip().lower() != "flower":
            failures.append(f"{run}: admitted flower-expression manifest contains non-flower tissue")
        if fr["admission_status"].strip() != "admit":
            failures.append(f"{run}: unexpected admission status {fr['admission_status']!r}")

        total_spots += int(lv["spots"])
        total_bases += int(lv["bases"])
        paired = paired and lv.get("LibraryLayout", "").strip().upper() == "PAIRED"

    expected_stage_counts = {f"S{i}": 3 for i in range(1, 6)}
    if stage_counts != expected_stage_counts:
        failures.append(f"Camellia stage counts changed: {stage_counts}, expected {expected_stage_counts}")

    if not paired:
        failures.append("Camellia SRP112181 no longer resolves as all paired-end libraries")
    total_reads = total_spots * 2 if paired else 0
    if total_spots != 35_844_645:
        failures.append(f"Camellia paired-spot total changed: {total_spots} != 35,844,645")
    if total_reads != 71_689_290:
        failures.append(f"Camellia mate-read total changed: {total_reads} != 71,689,290")
    if total_bases != 10_753_393_500:
        failures.append(f"Camellia base total changed: {total_bases} != 10,753,393,500")

    # Independent publication-level sanity bounds (Zhou et al. 2017 report
    # approximately 71.8 million raw reads / 10.8 Gbp).
    if abs(total_reads - 71_800_000) > 500_000:
        failures.append(f"Camellia total reads {total_reads} no longer match publication rounding (~71.8M)")
    if abs(total_bases - 10_800_000_000) > 200_000_000:
        failures.append(f"Camellia total bases {total_bases} no longer match publication rounding (~10.8Gbp)")

    print(
        "Camellia admitted manifest validated: 15 runs, S1-S5 x 3 replicates, "
        f"{total_reads:,} mate reads, {total_bases/1e9:.3f} Gbp"
    )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-dir", required=True, type=pathlib.Path)
    parser.add_argument("--biosample-dir", required=True, type=pathlib.Path)
    parser.add_argument(
        "--cirsium-frozen",
        default=pathlib.Path("data/cirsium_prjna1311153_admitted_manifest_v0_1.csv"),
        type=pathlib.Path,
    )
    parser.add_argument(
        "--camellia-frozen",
        default=pathlib.Path("data/camellia_srp112181_admitted_manifest_v0_1.csv"),
        type=pathlib.Path,
    )
    args = parser.parse_args()

    attr_rows = read_csv(args.biosample_dir / "biosample_attributes_long.csv")
    cir_attrs = [r for r in attr_rows if r.get("seed_id", "").strip() == "SEQ001"]
    cam_attrs = [r for r in attr_rows if r.get("seed_id", "").strip() == "SEQ002"]

    failures: list[str] = []
    failures.extend(
        validate_cirsium(
            args.cirsium_frozen,
            args.manifest_dir / "SEQ001_PRJNA1311153_runinfo.csv",
            cir_attrs,
        )
    )
    failures.extend(
        validate_camellia(
            args.camellia_frozen,
            args.manifest_dir / "SEQ002_SRP112181_runinfo.csv",
            cam_attrs,
        )
    )

    if failures:
        print("\nFrozen sample-manifest gate FAILED:")
        for item in failures:
            print(f"- {item}")
        return 1

    print("Frozen sample-manifest gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
