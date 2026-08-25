#!/usr/bin/env python3
"""Validate candidate-free dataset roles before recurrence synthesis.

This gate prevents unresolved developmental datasets and interspecific macro
validation datasets from silently increasing the number of independent micro
recurrence clusters. Promotion into primary recurrence requires an explicit
registry edit and an exact canonical-bridge match.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ALLOWED_ROLES = {
    "primary_candidate_free_recurrence",
    "within_cluster_replication",
    "unresolved_developmental_candidate",
    "macro_validation_candidate",
}


def yes(value: str) -> bool:
    v = value.strip().lower()
    if v not in {"yes", "no"}:
        raise ValueError(f"expected yes/no, got {value!r}")
    return v == "yes"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--bridge", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    rows = list(csv.DictReader(args.registry.open(encoding="utf-8")))
    bridge = list(csv.DictReader(args.bridge.open(encoding="utf-8")))
    if not rows:
        raise SystemExit("dataset role registry is empty")

    bridge_keys = {
        (r["dependence_cluster"], r["transition_class"])
        for r in bridge
    }
    seen_ids: set[str] = set()
    increment_keys: set[tuple[str, str]] = set()
    errors: list[str] = []
    role_counts: Counter[str] = Counter()
    recurrence_clusters: defaultdict[str, list[str]] = defaultdict(list)

    for row in rows:
        did = row["dataset_id"].strip()
        role = row["dataset_role"].strip()
        transition = row["transition_class"].strip()
        cluster = row["dependence_cluster"].strip()
        mapping = row["run_mapping_status"].strip().lower()
        try:
            primary = yes(row["can_enter_primary_recurrence"])
            increment = yes(row["can_increment_independent_cluster"])
        except ValueError as exc:
            errors.append(f"{did}: {exc}")
            continue

        if not did or did in seen_ids:
            errors.append(f"duplicate or blank dataset_id: {did!r}")
        seen_ids.add(did)
        if role not in ALLOWED_ROLES:
            errors.append(f"{did}: unsupported dataset_role={role!r}")
        role_counts[role] += 1

        if increment and not primary:
            errors.append(f"{did}: independent-cluster increment requires primary recurrence admission")
        if primary and role != "primary_candidate_free_recurrence":
            errors.append(f"{did}: only primary_candidate_free_recurrence may enter primary recurrence")
        if role == "primary_candidate_free_recurrence" and not primary:
            errors.append(f"{did}: primary role must explicitly enter primary recurrence")

        if primary:
            if (cluster, transition) not in bridge_keys:
                errors.append(
                    f"{did}: primary recurrence key {(cluster, transition)!r} is absent from canonical bridge"
                )
            if not mapping.startswith("resolved_"):
                errors.append(f"{did}: primary recurrence requires frozen resolved run mapping")

        if increment:
            key = (transition, cluster)
            if key in increment_keys:
                errors.append(f"{did}: duplicate independent-cluster increment for {key}")
            increment_keys.add(key)
            recurrence_clusters[transition].append(cluster)

        if role in {"unresolved_developmental_candidate", "macro_validation_candidate", "within_cluster_replication"}:
            if primary or increment:
                errors.append(f"{did}: role {role} cannot increment primary recurrence")

        if role == "unresolved_developmental_candidate" and mapping.startswith("resolved_"):
            errors.append(f"{did}: resolved mapping requires explicit promotion/reclassification")

        if row["accession"].strip() == "PRJNA1003846":
            if role != "macro_validation_candidate":
                errors.append("PRJNA1003846 must remain macro_validation_candidate")
            if transition == "yellow_development":
                errors.append("PRJNA1003846 is interspecific full-bloom contrast, not yellow_development")
            if primary or increment:
                errors.append("PRJNA1003846 cannot increment developmental recurrence")

    expected_current = {
        "anthocyanin_gain": 2,
        "yellow_development": 1,
    }
    observed_current = {k: len(set(v)) for k, v in recurrence_clusters.items()}
    for transition, expected in expected_current.items():
        got = observed_current.get(transition, 0)
        if got != expected:
            errors.append(
                f"current independent-cluster contract changed for {transition}: expected {expected}, got {got}; "
                "promotions require an intentional gate update"
            )

    summary = {
        "status": "pass" if not errors else "fail",
        "n_datasets": len(rows),
        "role_counts": dict(sorted(role_counts.items())),
        "independent_primary_clusters": {
            k: sorted(set(v)) for k, v in sorted(recurrence_clusters.items())
        },
        "independent_primary_cluster_counts": dict(sorted(observed_current.items())),
        "guarded_accessions": {
            "PRJNA981682": "unresolved developmental candidate until exact run-to-stage mapping is frozen",
            "PRJNA1003846": "macro interspecific yellow-intensity validation; never a yellow-development recurrence increment",
        },
        "errors": errors,
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if errors:
        raise SystemExit("candidate-free dataset-role contract failed")


if __name__ == "__main__":
    main()
