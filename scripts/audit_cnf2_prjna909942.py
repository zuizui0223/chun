#!/usr/bin/env python3
"""Audit PRJNA909942 before using it to identify the T2T CnFLS2 paralog.

Feng et al. (2024) state that transcriptome sequencing used the same 15 flower
samples as the five-stage metabolome experiment and deposited raw reads under
PRJNA909942. This script checks the live SRA/BioSample result without assuming
that archive labels use the paper's S0-S4 stage names.
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
from collections import Counter, defaultdict


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: pathlib.Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runinfo", required=True, type=pathlib.Path)
    parser.add_argument("--biosample-records", required=True, type=pathlib.Path)
    parser.add_argument("--biosample-attributes", required=True, type=pathlib.Path)
    parser.add_argument("--out-dir", required=True, type=pathlib.Path)
    args = parser.parse_args()

    runinfo = read_csv(args.runinfo)
    records = read_csv(args.biosample_records)
    attrs = read_csv(args.biosample_attributes)
    failures: list[str] = []

    runs = {r.get("Run", "").strip(): r for r in runinfo if r.get("Run", "").strip()}
    if len(runinfo) != 15 or len(runs) != 15:
        failures.append(
            f"PRJNA909942 resolves to {len(runinfo)} rows / {len(runs)} unique runs; "
            "the 2024 paper reports transcriptome sequencing of 15 flower samples"
        )

    samples = {r.get("BioSample", "").strip() for r in runinfo if r.get("BioSample", "").strip()}
    if len(samples) != 15:
        failures.append(f"expected 15 distinct BioSamples, observed {len(samples)}")

    organisms = Counter(r.get("ScientificName", "").strip() for r in runinfo)
    strategies = Counter(r.get("LibraryStrategy", "").strip() for r in runinfo)
    sources = Counter(r.get("LibrarySource", "").strip() for r in runinfo)
    layouts = Counter(r.get("LibraryLayout", "").strip() for r in runinfo)
    models = Counter(r.get("Model", "").strip() for r in runinfo)
    if organisms and set(organisms) != {"Camellia nitidissima"}:
        failures.append(f"unexpected organism labels: {dict(organisms)}")
    if strategies and set(strategies) != {"RNA-Seq"}:
        failures.append(f"unexpected library strategies: {dict(strategies)}")
    if sources and set(sources) != {"TRANSCRIPTOMIC"}:
        failures.append(f"unexpected library sources: {dict(sources)}")

    by_sample: dict[str, dict[str, str]] = {r.get("biosample", "").strip(): r for r in records}
    attr_by_sample: dict[str, dict[str, str]] = defaultdict(dict)
    for row in attrs:
        biosample = row.get("biosample", "").strip()
        name = row.get("attribute_name", "").strip()
        value = row.get("value", "").strip()
        if biosample and name:
            attr_by_sample[biosample][name] = value

    stage_like_names = {
        "dev_stage", "developmental stage", "developmental_stage", "stage",
        "growth stage", "flower stage", "flower_stage",
    }
    compact: list[dict[str, object]] = []
    stage_values: Counter[str] = Counter()
    tissue_values: Counter[str] = Counter()
    for run in sorted(runs):
        r = runs[run]
        biosample = r.get("BioSample", "").strip()
        rec = by_sample.get(biosample, {})
        a = attr_by_sample.get(biosample, {})
        stage_pairs = []
        for key, value in a.items():
            if key.lower() in stage_like_names or "stage" in key.lower():
                stage_pairs.append(f"{key}={value}")
                if value:
                    stage_values[value] += 1
        tissue = a.get("tissue", a.get("tissue_type", ""))
        if tissue:
            tissue_values[tissue] += 1
        compact.append(
            {
                "run": run,
                "biosample": biosample,
                "sra_sample_name": r.get("SampleName", ""),
                "sra_library_name": r.get("LibraryName", ""),
                "scientific_name": r.get("ScientificName", ""),
                "model": r.get("Model", ""),
                "layout": r.get("LibraryLayout", ""),
                "spots": r.get("spots", ""),
                "bases": r.get("bases", ""),
                "biosample_sample_name": rec.get("sample_name", ""),
                "biosample_title": rec.get("title", ""),
                "tissue": tissue,
                "stage_attributes": ";".join(sorted(stage_pairs)),
                "all_attributes_json": json.dumps(a, sort_keys=True, ensure_ascii=False),
            }
        )

    write_csv(
        args.out_dir / "prjna909942_compact_manifest.csv",
        compact,
        [
            "run", "biosample", "sra_sample_name", "sra_library_name",
            "scientific_name", "model", "layout", "spots", "bases",
            "biosample_sample_name", "biosample_title", "tissue",
            "stage_attributes", "all_attributes_json",
        ],
    )

    summary = {
        "run_count": len(runs),
        "biosample_count": len(samples),
        "organisms": dict(organisms),
        "strategies": dict(strategies),
        "sources": dict(sources),
        "layouts": dict(layouts),
        "models": dict(models),
        "stage_attribute_values": dict(stage_values),
        "tissue_values": dict(tissue_values),
        "stage_mapping_status": (
            "archive_stage_attributes_present_needs_S0_S4_reconciliation"
            if stage_values
            else "no_explicit_stage_attribute_recovered_needs_label_or_supplement_reconciliation"
        ),
        "claim_ceiling": "metadata audit only; no T2T CnFLS2 identity yet",
    }
    (args.out_dir / "prjna909942_audit_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if failures:
        print("PRJNA909942 admission gate FAILED:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        "PRJNA909942 run/sample count and RNA-seq identity match the 15-sample study design; "
        "stage mapping remains a separate provenance question until explicitly reconciled."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
