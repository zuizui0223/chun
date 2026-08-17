#!/usr/bin/env python3
"""Separate family recurrence, same-node recurrence, and resolved node contrasts.

The input is a provenance crosswalk built without macro-transition results.
A feature may recur at module level while independent systems use either the
same resolved paralog lineage or different resolved paralog lineages. Keeping
those outcomes separate is the pre-macro claim gate for H_MICRO_MACRO_REUSE
and H_PARALOG_SUBSTITUTION.
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

ANCHOR_STATUSES = {
    "exact_named_sequence_anchor",
    "named_paralogs_resolved_within_species",
    "subclass_sequence_anchor_exact",
    "functional_class_sequence_anchor_exact",
    "source_transcript_groups_with_local_amplicon_anchor",
    "same_paralog_sequence_tree_synteny_source_read_resolved",
}


def yes(value: str) -> bool:
    return value.strip().lower() == "yes"


def rank_class(family_n: int, anchored_n: int, exact_recurrent_n: int) -> str:
    if exact_recurrent_n >= 2:
        return "A_strict_crossspecies_node_recurrent"
    if family_n >= 2 and anchored_n == family_n:
        return "B_resolved_distinct_nodes"
    if family_n >= 2:
        return "B_family_recurrent_orthology_unresolved"
    if family_n == 1 and anchored_n >= 1:
        return "C_strict_node_single_cluster_only"
    return "D_single_cluster_family_only"


def macro_level(family_n: int, anchored_n: int, exact_recurrent_n: int) -> str:
    if exact_recurrent_n >= 2:
        return "ready_strict_node_level"
    if family_n >= 2 and anchored_n == family_n:
        return "ready_family_level_with_resolved_node_contrast"
    if family_n >= 2:
        return "ready_family_or_module_level_only"
    return "not_recurrent_for_enrichment"


def resolution_conclusion(
    family_n: int, anchored_n: int, exact_recurrent_n: int
) -> str:
    if exact_recurrent_n >= 2:
        return (
            "strict cross-species node recurrence demonstrated in independent "
            "micro evidence clusters; macro-branch reuse remains untested"
        )
    if family_n >= 2 and anchored_n == family_n:
        return (
            "family recurrence demonstrated; all recurrent clusters are "
            "anchored to different strict node labels"
        )
    if family_n >= 2:
        return "family recurrence demonstrated; exact ortholog/paralog recurrence not yet demonstrated"
    return "single-cluster evidence only"


def resolution_boundary(
    family_n: int, anchored_n: int, exact_recurrent_n: int
) -> str:
    if exact_recurrent_n >= 2:
        return (
            "the same sequence/context-resolved lineage recurs in at least two "
            "independent micro clusters and can enter a held-out macro test; "
            "this is not evidence that it already recurs on independent macro branches"
        )
    if family_n >= 2 and anchored_n == family_n:
        return (
            "all recurrent micro clusters are sequence anchored but their strict "
            "labels differ; test module convergence and paralog substitution, "
            "not same-node reuse"
        )
    return (
        "gene-symbol/family recurrence is an upper bound on exact ortholog reuse; "
        "sequence-resolved cross-species mapping is required before node-level macro enrichment"
    )


def score_boundary(
    family_n: int, anchored_n: int, exact_recurrent_n: int
) -> str:
    if exact_recurrent_n >= 2:
        return (
            "a recurrent strict micro lineage is available as a held-out macro predictor; "
            "macro transition enrichment and ecological selection remain untested"
        )
    if family_n >= 2 and anchored_n == family_n:
        return (
            "use the family/module predictor together with the resolved different-node "
            "contrast; strict same-node predictor remains zero"
        )
    return (
        "use family/module predictor for the first held-out macro test; strict-node "
        "predictor stays zero/not-ready unless the same sequence-resolved lineage "
        "recurs in at least two independent micro clusters"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("crosswalk", type=Path)
    parser.add_argument("--resolution-output", type=Path, required=True)
    parser.add_argument("--score-output", type=Path, required=True)
    args = parser.parse_args()

    with args.crosswalk.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    by_feature: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if yes(row["family_recurrence_counted"]):
            by_feature[(row["feature"], row["module"])].append(row)

    resolution: list[dict[str, object]] = []
    score: list[dict[str, object]] = []

    for (feature, module), feature_rows in sorted(by_feature.items()):
        family_clusters = sorted(
            {row["independence_cluster"] for row in feature_rows}
        )
        anchored_clusters = sorted(
            {
                row["independence_cluster"]
                for row in feature_rows
                if row["orthology_status"] in ANCHOR_STATUSES
            }
        )
        unresolved_clusters = sorted(
            {
                row["independence_cluster"]
                for row in feature_rows
                if row["orthology_status"] not in ANCHOR_STATUSES
            }
        )

        labels: dict[str, set[str]] = defaultdict(set)
        for row in feature_rows:
            label = row["strict_node_label"].strip()
            if label and row["orthology_status"] in ANCHOR_STATUSES:
                labels[label].add(row["independence_cluster"])

        recurrent_labels = sorted(
            label for label, clusters in labels.items() if len(clusters) >= 2
        )
        exact_clusters = (
            sorted(set().union(*(labels[label] for label in recurrent_labels)))
            if recurrent_labels
            else []
        )
        resolved_labels = ";".join(
            f"{label}@{','.join(sorted(clusters))}"
            for label, clusters in sorted(labels.items())
        )
        statuses = sorted({row["orthology_status"] for row in feature_rows})
        source_ids = sorted(
            {row["source_ids"] for row in feature_rows if row["source_ids"]}
        )

        family_n = len(family_clusters)
        anchored_n = len(anchored_clusters)
        exact_n = len(exact_clusters)

        resolution.append(
            {
                "feature": feature,
                "module": module,
                "family_recurrence_clusters": family_n,
                "named_or_sequence_anchored_clusters": anchored_n,
                "strict_crossspecies_exact_recurrence_clusters": exact_n,
                "unresolved_or_family_only_clusters": len(unresolved_clusters),
                "resolved_strict_node_labels": resolved_labels,
                "recurrent_strict_node_labels": ";".join(recurrent_labels),
                "independence_clusters": ";".join(family_clusters),
                "orthology_statuses": ";".join(statuses),
                "source_id_sets": " | ".join(source_ids),
                "resolution_conclusion": resolution_conclusion(
                    family_n, anchored_n, exact_n
                ),
                "claim_boundary": resolution_boundary(
                    family_n, anchored_n, exact_n
                ),
            }
        )
        score.append(
            {
                "feature": feature,
                "module": module,
                "family_recurrence_clusters": family_n,
                "anchored_clusters": anchored_n,
                "strict_crossspecies_recurrence_clusters": exact_n,
                "harmonized_rank_class": rank_class(
                    family_n, anchored_n, exact_n
                ),
                "macro_test_level": macro_level(
                    family_n, anchored_n, exact_n
                ),
                "primary_family_predictor": family_n,
                "strict_node_predictor": exact_n,
                "claim_boundary": score_boundary(
                    family_n, anchored_n, exact_n
                ),
            }
        )

    for path, data in [
        (args.resolution_output, resolution),
        (args.score_output, score),
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)


if __name__ == "__main__":
    main()
