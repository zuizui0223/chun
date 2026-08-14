#!/usr/bin/env python3
"""Audit PRJNA909942 and admit the five-stage CnFLS2 petal subset.

PRJNA909942 is a broader C. nitidissima transcriptome project, not a
paper-specific 15-run BioProject. Feng et al. (2024) analysed 15 petal samples
from five developmental stages with three biological replicates per stage.
The archive identifies that focal subset by BioSample tissue labels
Petal-B1, Petal-B2, Petal-B3, Petal-Fh, and Petal-Fc.

This audit therefore keeps the complete project manifest for provenance while
validating and exporting only the paper-specific 15-run stage subset. It does
not infer S0-S4 labels from absent BioSample dev_stage attributes.
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
from collections import Counter, defaultdict

FOCAL_TISSUES = ("Petal-B1", "Petal-B2", "Petal-B3", "Petal-Fh", "Petal-Fc")


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: pathlib.Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


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
    if len(runs) != len(runinfo):
        failures.append(
            f"PRJNA909942 contains duplicate/non-run rows: {len(runinfo)} rows / {len(runs)} unique runs"
        )

    by_sample: dict[str, dict[str, str]] = {
        r.get("biosample", "").strip(): r for r in records if r.get("biosample", "").strip()
    }
    attr_by_sample: dict[str, dict[str, str]] = defaultdict(dict)
    for row in attrs:
        biosample = row.get("biosample", "").strip()
        name = row.get("attribute_name", "").strip()
        value = row.get("value", "").strip()
        if biosample and name:
            attr_by_sample[biosample][name] = value

    compact: list[dict[str, object]] = []
    focal: list[dict[str, object]] = []
    tissue_values: Counter[str] = Counter()
    stage_values: Counter[str] = Counter()

    stage_like_names = {
        "dev_stage", "developmental stage", "developmental_stage", "stage",
        "growth stage", "flower stage", "flower_stage",
    }

    for run in sorted(runs):
        r = runs[run]
        biosample = r.get("BioSample", "").strip()
        rec = by_sample.get(biosample, {})
        a = attr_by_sample.get(biosample, {})
        tissue = a.get("tissue", a.get("tissue_type", "")).strip()
        if tissue:
            tissue_values[tissue] += 1

        stage_pairs: list[str] = []
        for key, value in a.items():
            if key.lower() in stage_like_names or "stage" in key.lower():
                stage_pairs.append(f"{key}={value}")
                if value:
                    stage_values[value] += 1

        row: dict[str, object] = {
            "run": run,
            "biosample": biosample,
            "sra_sample_name": r.get("SampleName", ""),
            "sra_library_name": r.get("LibraryName", ""),
            "scientific_name": r.get("ScientificName", ""),
            "library_strategy": r.get("LibraryStrategy", ""),
            "library_source": r.get("LibrarySource", ""),
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
        compact.append(row)
        if tissue in FOCAL_TISSUES:
            focal.append(row)

    full_fields = [
        "run", "biosample", "sra_sample_name", "sra_library_name",
        "scientific_name", "library_strategy", "library_source", "model",
        "layout", "spots", "bases", "biosample_sample_name", "biosample_title",
        "tissue", "stage_attributes", "all_attributes_json",
    ]
    write_csv(args.out_dir / "prjna909942_compact_manifest.csv", compact, full_fields)
    write_csv(args.out_dir / "prjna909942_cnf2_stage_subset.csv", focal, full_fields)

    focal_runs = {str(r["run"]) for r in focal}
    focal_samples = {str(r["biosample"]) for r in focal}
    focal_tissues = Counter(str(r["tissue"]) for r in focal)
    focal_organisms = Counter(str(r["scientific_name"]) for r in focal)
    focal_strategies = Counter(str(r["library_strategy"]) for r in focal)
    focal_sources = Counter(str(r["library_source"]) for r in focal)
    focal_layouts = Counter(str(r["layout"]) for r in focal)
    focal_models = Counter(str(r["model"]) for r in focal)

    if len(focal) != 15 or len(focal_runs) != 15:
        failures.append(
            f"focal five-stage petal subset has {len(focal)} rows / {len(focal_runs)} unique runs; expected 15"
        )
    if len(focal_samples) != 15:
        failures.append(f"focal subset has {len(focal_samples)} distinct BioSamples; expected 15")

    expected_tissues = {t: 3 for t in FOCAL_TISSUES}
    if dict(focal_tissues) != expected_tissues:
        failures.append(
            f"focal tissue/replicate structure changed: observed={dict(focal_tissues)}, expected={expected_tissues}"
        )
    if focal_organisms and set(focal_organisms) != {"Camellia nitidissima"}:
        failures.append(f"unexpected focal organism labels: {dict(focal_organisms)}")
    if focal_strategies and set(focal_strategies) != {"RNA-Seq"}:
        failures.append(f"unexpected focal library strategies: {dict(focal_strategies)}")
    if focal_sources and set(focal_sources) != {"TRANSCRIPTOMIC"}:
        failures.append(f"unexpected focal library sources: {dict(focal_sources)}")
    if focal_layouts and set(focal_layouts) != {"PAIRED"}:
        failures.append(f"unexpected focal library layouts: {dict(focal_layouts)}")

    full_organisms = Counter(r.get("ScientificName", "").strip() for r in runinfo)
    full_strategies = Counter(r.get("LibraryStrategy", "").strip() for r in runinfo)
    full_sources = Counter(r.get("LibrarySource", "").strip() for r in runinfo)
    full_layouts = Counter(r.get("LibraryLayout", "").strip() for r in runinfo)
    full_models = Counter(r.get("Model", "").strip() for r in runinfo)

    summary = {
        "full_project_run_count": len(runs),
        "full_project_biosample_count": len(
            {r.get("BioSample", "").strip() for r in runinfo if r.get("BioSample", "").strip()}
        ),
        "full_project_organisms": dict(full_organisms),
        "full_project_strategies": dict(full_strategies),
        "full_project_sources": dict(full_sources),
        "full_project_layouts": dict(full_layouts),
        "full_project_models": dict(full_models),
        "full_project_tissue_values": dict(tissue_values),
        "focal_subset_rule": "BioSample tissue in Petal-B1/Petal-B2/Petal-B3/Petal-Fh/Petal-Fc",
        "focal_run_count": len(focal_runs),
        "focal_biosample_count": len(focal_samples),
        "focal_tissue_values": dict(focal_tissues),
        "focal_organisms": dict(focal_organisms),
        "focal_strategies": dict(focal_strategies),
        "focal_sources": dict(focal_sources),
        "focal_layouts": dict(focal_layouts),
        "focal_models": dict(focal_models),
        "explicit_stage_attribute_values": dict(stage_values),
        "stage_mapping_status": (
            "archive focal groups B1/B2/B3/Fh/Fc recovered as 3 replicates each; "
            "no explicit S0-S4 BioSample stage attribute, so paper-label reconciliation remains separate"
        ),
        "excluded_from_focal_subset": (
            "general Petal replicates, non-petal tissues, and the mixed-tissue PacBio run remain in the full project manifest"
        ),
        "claim_ceiling": "paper-specific 15-run petal subset admitted; no T2T CnFLS2 identity yet",
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
        "PRJNA909942 full project audited; the paper-specific five-stage petal subset "
        "contains 15 RNA-seq runs (B1/B2/B3/Fh/Fc x 3)."
    )
    print(
        "S0-S4 paper labels are not invented from missing BioSample stage attributes; "
        "that reconciliation remains a separate provenance step."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
