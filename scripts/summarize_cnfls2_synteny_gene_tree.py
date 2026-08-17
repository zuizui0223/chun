#!/usr/bin/env python3
"""Summarize CnFLS2 target-pair, local-synteny and family-tree evidence."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import mean

from Bio import Phylo

BLAST_FIELDS = ["qseqid", "sseqid", "pident", "length", "qlen", "slen", "qcovs", "evalue", "bitscore"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_blast(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle, fieldnames=BLAST_FIELDS, delimiter="\t")
        for raw in reader:
            if not raw.get("qseqid") or not raw.get("sseqid"):
                continue
            try:
                rows.append(
                    {
                        **raw,
                        "pident_num": float(raw["pident"]),
                        "length_num": int(raw["length"]),
                        "qlen_num": int(raw["qlen"]),
                        "slen_num": int(raw["slen"]),
                        "qcov_num": float(raw["qcovs"]),
                        "evalue_num": float(raw["evalue"]),
                        "bitscore_num": float(raw["bitscore"]),
                    }
                )
            except (TypeError, ValueError):
                continue
    return rows


def best_hits(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    best: dict[str, dict[str, object]] = {}
    for row in rows:
        if row["evalue_num"] > 1e-5 or row["qcov_num"] < 50 or row["pident_num"] < 30:
            continue
        query = str(row["qseqid"])
        current = best.get(query)
        key = (float(row["bitscore_num"]), float(row["qcov_num"]), float(row["pident_num"]), int(row["length_num"]))
        if current is None:
            best[query] = row
        else:
            old = (
                float(current["bitscore_num"]),
                float(current["qcov_num"]),
                float(current["pident_num"]),
                int(current["length_num"]),
            )
            if key > old:
                best[query] = row
    return best


def rankdata(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and values[order[j]] == values[order[i]]:
            j += 1
        rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[order[k]] = rank
        i = j
    return ranks


def pearson(x: list[float], y: list[float]) -> float | None:
    if len(x) < 2 or len(x) != len(y):
        return None
    mx, my = mean(x), mean(y)
    numerator = sum((a - mx) * (b - my) for a, b in zip(x, y))
    dx = math.sqrt(sum((a - mx) ** 2 for a in x))
    dy = math.sqrt(sum((b - my) ** 2 for b in y))
    if dx == 0 or dy == 0:
        return None
    return numerator / (dx * dy)


def spearman(x: list[float], y: list[float]) -> float | None:
    return pearson(rankdata(x), rankdata(y))


def lis_length(values: list[int], increasing: bool = True) -> int:
    if not values:
        return 0
    tails: list[int] = []
    import bisect

    for raw in values:
        value = raw if increasing else -raw
        position = bisect.bisect_left(tails, value)
        if position == len(tails):
            tails.append(value)
        else:
            tails[position] = value
    return len(tails)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preparation-summary", type=Path, required=True)
    parser.add_argument("--neighborhood-metadata", type=Path, required=True)
    parser.add_argument("--family-metadata", type=Path, required=True)
    parser.add_argument("--cn-to-tea", type=Path, required=True)
    parser.add_argument("--tea-to-cn", type=Path, required=True)
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    preparation = json.loads(args.preparation_summary.read_text(encoding="utf-8"))
    neighborhood_rows = read_csv(args.neighborhood_metadata)
    family_rows = read_csv(args.family_metadata)
    metadata = {row["protein_label"]: row for row in neighborhood_rows if row.get("protein_label")}

    cn_rows = read_blast(args.cn_to_tea)
    tea_rows = read_blast(args.tea_to_cn)
    cn_best = best_hits(cn_rows)
    tea_best = best_hits(tea_rows)

    anchors: list[dict[str, object]] = []
    for cn_label, forward in cn_best.items():
        tea_label = str(forward["sseqid"])
        reverse = tea_best.get(tea_label)
        if not reverse or str(reverse["sseqid"]) != cn_label:
            continue
        cn_meta = metadata.get(cn_label)
        tea_meta = metadata.get(tea_label)
        if not cn_meta or not tea_meta:
            continue
        anchors.append(
            {
                "cn_protein_label": cn_label,
                "tea_protein_label": tea_label,
                "cn_gene_id": cn_meta["gene_id"],
                "tea_gene_id": tea_meta["gene_id"],
                "cn_relative_index": int(cn_meta["relative_index"]),
                "tea_relative_index": int(tea_meta["relative_index"]),
                "cn_is_target": cn_meta["is_target"],
                "tea_is_target": tea_meta["is_target"],
                "forward_pident": round(float(forward["pident_num"]), 6),
                "forward_qcov": round(float(forward["qcov_num"]), 6),
                "forward_bitscore": round(float(forward["bitscore_num"]), 6),
                "reverse_pident": round(float(reverse["pident_num"]), 6),
                "reverse_qcov": round(float(reverse["qcov_num"]), 6),
                "reverse_bitscore": round(float(reverse["bitscore_num"]), 6),
                "claim_boundary": "reciprocal-best local protein anchor; orthology still interpreted with gene tree and context",
            }
        )
    anchors.sort(key=lambda row: (int(row["cn_relative_index"]), int(row["tea_relative_index"])))

    anchor_fields = [
        "cn_protein_label",
        "tea_protein_label",
        "cn_gene_id",
        "tea_gene_id",
        "cn_relative_index",
        "tea_relative_index",
        "cn_is_target",
        "tea_is_target",
        "forward_pident",
        "forward_qcov",
        "forward_bitscore",
        "reverse_pident",
        "reverse_qcov",
        "reverse_bitscore",
        "claim_boundary",
    ]
    with (args.out_dir / "reciprocal_best_anchors.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=anchor_fields)
        writer.writeheader()
        writer.writerows(anchors)

    target_anchors = [row for row in anchors if row["cn_is_target"] == "yes" and row["tea_is_target"] == "yes"]
    non_target = [row for row in anchors if row not in target_anchors]
    x = [float(row["cn_relative_index"]) for row in non_target]
    y = [float(row["tea_relative_index"]) for row in non_target]
    rho = spearman(x, y)
    ordered_tea = [int(row["tea_relative_index"]) for row in sorted(non_target, key=lambda row: int(row["cn_relative_index"]))]
    increasing = lis_length(ordered_tea, True)
    decreasing = lis_length(ordered_tea, False)
    monotonic = max(increasing, decreasing)
    orientation = "same" if rho is not None and rho > 0.5 else ("inverted" if rho is not None and rho < -0.5 else "unclear")
    synteny_supported = bool(target_anchors) and len(non_target) >= 3 and rho is not None and abs(rho) >= 0.6 and monotonic >= 3

    cn_target_label = next(row["protein_label"] for row in family_rows if row["species"] == "CN" and row["is_target"] == "yes")
    tea_target_label = next(row["protein_label"] for row in family_rows if row["species"] == "TEA" and row["is_target"] == "yes")

    target_forward = next(
        (
            row
            for row in cn_rows
            if row["qseqid"] == cn_target_label and row["sseqid"] == tea_target_label
        ),
        None,
    )

    tree = Phylo.read(args.tree, "newick")
    terminal_names = {terminal.name for terminal in tree.get_terminals()}
    if cn_target_label not in terminal_names or tea_target_label not in terminal_names:
        raise SystemExit("Target labels are missing from the FLS-family tree")
    mrca = tree.common_ancestor(cn_target_label, tea_target_label)
    target_descendants = sorted(terminal.name for terminal in mrca.get_terminals())
    exclusive_sister_pair = set(target_descendants) == {cn_target_label, tea_target_label}
    pair_distance = tree.distance(cn_target_label, tea_target_label)
    other_names = sorted(terminal_names - {cn_target_label, tea_target_label})
    nearest_other_to_cn = min((tree.distance(cn_target_label, name), name) for name in other_names) if other_names else (None, "")
    nearest_other_to_tea = min((tree.distance(tea_target_label, name), name) for name in other_names) if other_names else (None, "")
    mrca_support = getattr(mrca, "confidence", None)

    identity_supported = bool(
        target_forward
        and float(target_forward["pident_num"]) >= 95
        and float(target_forward["qcov_num"]) >= 95
    )
    tree_supported = exclusive_sister_pair
    if identity_supported and tree_supported and synteny_supported:
        decision = "strong sequence-tree-local-synteny support for the CnFLS2-like same-paralog orthology hypothesis"
    elif identity_supported and tree_supported:
        decision = "strong sequence/tree support; local synteny remains inconclusive"
    else:
        decision = "target-pair evidence remains provisional; do not promote strict orthology"

    summary = {
        "cn_target_transcript": preparation["cn_target_transcript"],
        "cn_target_gene": preparation["cn_target_gene"],
        "cn_target_protein": preparation["cn_target_protein"],
        "tea_target_transcript": preparation["tea_target_transcript"],
        "tea_target_gene": preparation["tea_target_gene"],
        "tea_target_protein": preparation["tea_target_protein"],
        "target_pair_pident": float(target_forward["pident_num"]) if target_forward else None,
        "target_pair_qcov": float(target_forward["qcov_num"]) if target_forward else None,
        "target_pair_alignment_aa": int(target_forward["length_num"]) if target_forward else None,
        "target_pair_is_local_RBH": bool(target_anchors),
        "local_RBH_anchors_total": len(anchors),
        "local_RBH_anchors_non_target": len(non_target),
        "local_anchor_spearman_rho": rho,
        "local_anchor_orientation": orientation,
        "local_anchor_LIS_same": increasing,
        "local_anchor_LIS_inverted": decreasing,
        "local_anchor_longest_monotonic": monotonic,
        "local_synteny_supported_under_declared_gate": synteny_supported,
        "family_tree_terminals": len(terminal_names),
        "target_pair_exclusive_sister": exclusive_sister_pair,
        "target_pair_mrca_descendants": target_descendants,
        "target_pair_tree_distance": pair_distance,
        "target_pair_mrca_support": mrca_support,
        "nearest_other_to_cn": {"label": nearest_other_to_cn[1], "distance": nearest_other_to_cn[0]},
        "nearest_other_to_tea": {"label": nearest_other_to_tea[1], "distance": nearest_other_to_tea[0]},
        "identity_gate_passed": identity_supported,
        "tree_gate_passed": tree_supported,
        "decision": decision,
        "new_chun_inference": "developmental FLS sign heterogeneity can reflect lineage-homologous CnFLS2-like versus distinct FLS-paralog deployment rather than reversal of one undifferentiated FLS node",
        "claim_ceiling": "two-species local synteny plus an exploratory top-homolog protein tree; broader taxon sampling and PacBio source-read validation remain required before literal F01.PB8395 naming or macro strict-node reuse",
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
