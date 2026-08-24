#!/usr/bin/env python3
"""Aggregate Salmon transcript TPM to preregistered pigment gene-family expression.

All annotated transcripts assigned to a family are summed. No transcript is selected
based on differential expression. The emitted `expression` column is log2(sumTPM+1)
and conforms to the candidate-free module scorer contract.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError(f"empty input: {path}")
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quant-root", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--family-map", type=Path, required=True)
    ap.add_argument("--dataset-id", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--min-percent-mapped", type=float, default=15.0)
    args = ap.parse_args()

    manifest = read_csv(args.manifest)
    fmap = read_csv(args.family_map)
    tx_to_family: dict[str, str] = {}
    families: set[str] = set()
    for row in fmap:
        tx = row["transcript_id"]
        fam = row["gene_family"]
        if tx in tx_to_family and tx_to_family[tx] != fam:
            raise ValueError(f"transcript assigned to multiple families: {tx}")
        tx_to_family[tx] = fam
        families.add(fam)
    if not tx_to_family:
        raise ValueError("family map contains no transcripts")

    rows_out: list[dict[str, object]] = []
    qc = []
    for sample in manifest:
        run = sample["run"]
        qdir = args.quant_root / run
        quant = qdir / "quant.sf"
        meta = qdir / "aux_info" / "meta_info.json"
        if not quant.exists() or not meta.exists():
            raise FileNotFoundError(f"missing Salmon output for {run}: {qdir}")
        meta_obj = json.loads(meta.read_text(encoding="utf-8"))
        pct = float(meta_obj.get("percent_mapped", 0.0))
        qc.append({"run": run, "percent_mapped": pct})
        if pct < args.min_percent_mapped:
            raise ValueError(
                f"{run}: Salmon mapping rate {pct:.2f}% < gate {args.min_percent_mapped:.2f}%"
            )

        fam_tpm = defaultdict(float)
        with quant.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                tx = row["Name"]
                fam = tx_to_family.get(tx)
                if fam is not None:
                    fam_tpm[fam] += float(row["TPM"])

        for fam in sorted(families):
            tpm = fam_tpm.get(fam, 0.0)
            rows_out.append(
                {
                    "dataset_id": args.dataset_id,
                    "dependence_cluster": sample["dependence_cluster"],
                    "sample_id": run,
                    "condition_id": sample["condition_id"],
                    "gene_family": fam,
                    "expression": math.log2(tpm + 1.0),
                    "family_tpm": tpm,
                    "run": run,
                    "archive_sample_name": sample.get("archive_sample_name", ""),
                    "replicate": sample.get("replicate", ""),
                    "salmon_percent_mapped": pct,
                }
            )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows_out[0].keys())
    with args.out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader(); w.writerows(rows_out)

    qc_summary = {
        "status": "family_expression_aggregated",
        "dataset_id": args.dataset_id,
        "n_runs": len(manifest),
        "n_annotation_resolved_families": len(families),
        "families": sorted(families),
        "min_percent_mapped_gate": args.min_percent_mapped,
        "mapping_rate_min": min(x["percent_mapped"] for x in qc),
        "mapping_rate_mean": sum(x["percent_mapped"] for x in qc) / len(qc),
        "mapping_rate_max": max(x["percent_mapped"] for x in qc),
        "runs": qc,
        "aggregation_rule": "sum TPM across all annotation-matched transcripts within family; log2(TPM+1)",
    }
    args.out.with_suffix(".summary.json").write_text(
        json.dumps(qc_summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(qc_summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
