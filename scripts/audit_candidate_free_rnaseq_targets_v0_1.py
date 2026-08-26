#!/usr/bin/env python3
"""Audit whether candidate-free RNA-seq validation is data-limited or harmonization-limited."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

AXES = ("A_change", "F_change", "C_change", "P_change")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError(f"empty input: {path}")
    return rows


def cluster_unknown_axes(micro: list[dict[str, str]]) -> dict[str, list[str]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in micro:
        groups[row["dependence_cluster"]].append(row)

    out: dict[str, list[str]] = {}
    for cluster, rows in groups.items():
        unknown = []
        for axis in AXES:
            known = [r[axis] for r in rows if r[axis] != "unknown"]
            if not known:
                unknown.append(axis.replace("_change", ""))
        out[cluster] = unknown
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--micro", type=Path, required=True)
    ap.add_argument("--targets", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    micro = read_csv(args.micro)
    targets = read_csv(args.targets)
    unknown = cluster_unknown_axes(micro)
    micro_clusters = set(unknown)

    fitting = [r for r in targets if r["analysis_role"] != "external_holdout_not_micro_model_fit"]
    target_clusters = {r["dependence_cluster"] for r in fitting}
    missing_target_clusters = sorted(micro_clusters - target_clusters)

    frozen_manifest_clusters = {
        r["dependence_cluster"]
        for r in fitting
        if r["current_run_manifest_status"].startswith("resolved_")
    }
    exact_run_identity_clusters = {
        r["dependence_cluster"]
        for r in fitting
        if r["current_run_manifest_status"].startswith("resolved_")
        or r["current_run_manifest_status"].startswith("exact_")
    }
    ncbi_clusters = {
        r["dependence_cluster"]
        for r in fitting
        if r["provider"].startswith("NCBI_SRA")
    }
    external = [r for r in targets if r["analysis_role"] == "external_holdout_not_micro_model_fit"]

    cluster_rows = []
    for cluster in sorted(micro_clusters):
        t = [r for r in fitting if r["dependence_cluster"] == cluster]
        cluster_rows.append(
            {
                "dependence_cluster": cluster,
                "unknown_axes_before_candidate_free": unknown[cluster],
                "n_unknown_axes": len(unknown[cluster]),
                "n_public_targets": len(t),
                "has_frozen_run_manifest": cluster in frozen_manifest_clusters,
                "has_exact_run_identity": cluster in exact_run_identity_clusters,
                "has_NCBI_SRA_route": cluster in ncbi_clusters,
                "accessions": [r["accession"] for r in t],
                "run_statuses": [r["current_run_manifest_status"] for r in t],
                "priorities": [r["priority"] for r in t],
            }
        )

    summary = {
        "n_micro_dependence_clusters": len(micro_clusters),
        "n_clusters_with_public_raw_target": len(target_clusters & micro_clusters),
        "missing_public_target_clusters": missing_target_clusters,
        "n_clusters_with_frozen_run_manifest": len(frozen_manifest_clusters & micro_clusters),
        "clusters_with_frozen_run_manifest": sorted(frozen_manifest_clusters & micro_clusters),
        "n_clusters_with_exact_run_identity": len(exact_run_identity_clusters & micro_clusters),
        "clusters_with_exact_run_identity": sorted(exact_run_identity_clusters & micro_clusters),
        "n_clusters_with_NCBI_SRA_route": len(ncbi_clusters & micro_clusters),
        "clusters_with_NCBI_SRA_route": sorted(ncbi_clusters & micro_clusters),
        "external_holdout_targets": [r["target_id"] for r in external],
        "cluster_audit": cluster_rows,
        "bottleneck": (
            "metadata/reference/ortholog harmonization rather than absence of public raw data"
            if not missing_target_clusters
            else "public raw-data coverage remains incomplete"
        ),
        "execution_order": [
            "validate module quantification on already run-mapped CSIN_WHITE_PINK, CJAPONICA and CNITIDISSIMA datasets",
            "freeze run-to-condition mapping for CPERPETUA PRJNA981682 (five stages x three replicates already confirmed)",
            "freeze run-to-condition mapping for CRETICULATA SRR24413180-SRR24413206 (27 runs and experimental design already confirmed)",
            "freeze candidate-free directions and rerun dependence-aware recurrence null",
            "evaluate frozen state representation on the PRJNA1136134 external between-species holdout",
        ],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
