#!/usr/bin/env python3
"""Summarize T2T-anchored FLS transcript expression across S1-S5 flowers."""

from __future__ import annotations

import argparse
import csv
import pathlib
import statistics

TARGETS = {
    "GWHTFILD024733.1": "CnFLS1_anchor",
    "GWHTFILD005297.1": "FLS_family_candidate_2",
    "GWHTFILD024731.1": "FLS_family_candidate_3",
}


def read_csv(path: pathlib.Path, delimiter: str = ",") -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def write_csv(path: pathlib.Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=pathlib.Path)
    parser.add_argument("--quant-dir", required=True, type=pathlib.Path)
    parser.add_argument("--out-dir", required=True, type=pathlib.Path)
    args = parser.parse_args()

    manifest = read_csv(args.manifest)
    by_run = {r["run"].strip(): r for r in manifest}
    if len(by_run) != 15:
        raise SystemExit(f"Expected 15 admitted runs, found {len(by_run)}")

    sample_rows: list[dict[str, object]] = []
    missing_targets: dict[str, list[str]] = {target: [] for target in TARGETS}

    for run, meta in sorted(by_run.items()):
        qpath = args.quant_dir / run / "quant.sf"
        if not qpath.exists():
            raise SystemExit(f"Missing Salmon quant.sf for {run}: {qpath}")
        quant = {r["Name"].strip(): r for r in read_csv(qpath, delimiter="\t")}
        for target, label in TARGETS.items():
            if target not in quant:
                missing_targets[target].append(run)
                continue
            q = quant[target]
            sample_rows.append(
                {
                    "run": run,
                    "biosample": meta["biosample"],
                    "stage": meta["publication_stage"],
                    "replicate": meta["replicate"],
                    "target": target,
                    "target_label": label,
                    "TPM": float(q["TPM"]),
                    "NumReads": float(q["NumReads"]),
                    "EffectiveLength": float(q["EffectiveLength"]),
                }
            )

    missing = {k: v for k, v in missing_targets.items() if v}
    if missing:
        raise SystemExit(f"T2T FLS target transcript(s) absent from Salmon reference/quantification: {missing}")

    stage_rows: list[dict[str, object]] = []
    for target, label in TARGETS.items():
        for stage_num in range(1, 6):
            stage = f"S{stage_num}"
            subset = [
                r for r in sample_rows if r["target"] == target and r["stage"] == stage
            ]
            if len(subset) != 3:
                raise SystemExit(f"{target} {stage}: expected 3 replicates, found {len(subset)}")
            tpms = [float(r["TPM"]) for r in subset]
            reads = [float(r["NumReads"]) for r in subset]
            stage_rows.append(
                {
                    "stage": stage,
                    "target": target,
                    "target_label": label,
                    "n": 3,
                    "mean_TPM": statistics.mean(tpms),
                    "median_TPM": statistics.median(tpms),
                    "sd_TPM": statistics.stdev(tpms),
                    "mean_NumReads": statistics.mean(reads),
                }
            )

    write_csv(
        args.out_dir / "fls_expression_by_sample.csv",
        sample_rows,
        [
            "run",
            "biosample",
            "stage",
            "replicate",
            "target",
            "target_label",
            "TPM",
            "NumReads",
            "EffectiveLength",
        ],
    )
    write_csv(
        args.out_dir / "fls_expression_by_stage.csv",
        stage_rows,
        [
            "stage",
            "target",
            "target_label",
            "n",
            "mean_TPM",
            "median_TPM",
            "sd_TPM",
            "mean_NumReads",
        ],
    )

    anchor = [r for r in stage_rows if r["target"] == "GWHTFILD024733.1"]
    print("CnFLS1 anchored transcript expression (mean TPM):")
    for row in anchor:
        print(f"  {row['stage']}: {float(row['mean_TPM']):.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
