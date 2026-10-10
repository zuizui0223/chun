#!/usr/bin/env python3
"""Source-only Erica Table 2 × qPCR key crosswalk and feasible visible-class coverage.

No phylogeny or biochemical identity claim. Only crosswalk names and count
possible same-visible-colour unordered *lineage* pairs if a matched tree exists.
"""
from __future__ import annotations
import argparse
import collections
import json
from pathlib import Path

from audit_erica_qpcr_source_keys_v0_1 import source_key_audit


def crosswalk(d: dict, q: dict) -> dict:
    rows = d["taxa"]
    if len(rows) != 30:
        raise ValueError("Table2 row gate not 30")
    keys = [r["qpcr_label"] for r in rows]
    if len(set(keys)) != 30:
        raise ValueError("duplicate qPCR crosswalk key")
    expected = set(q["taxa_with_row_counts"])
    if set(keys) != expected:
        raise ValueError("Table2 crosswalk must exactly cover 30 raw qPCR labels")
    if q["status"] != "SOURCE_KEYS_ADMITTED_FOR_SCHEMA_ONLY":
        raise ValueError("qPCR expression identity / numeric coverage not admitted")
    if q["quantitative_pathway_measurements"] != 630 or len(q["quantitative_pathway_genes"]) != 7:
        raise ValueError("incomplete original gene panel")
    if q["taxon_stage_combinations"] != 90:
        raise ValueError("original qPCR stage distribution changed")

    colors = {"red", "pink", "white", "yellow"}
    lines = collections.defaultdict(list)
    raw_count = collections.Counter()
    group_count = collections.Counter()
    for row in rows:
        if row["table2_visible_colour"] not in colors or row["table2_group"] not in "ABCDEFGHIJ":
            raise ValueError("unknown Table2 categorical state/group")
        raw_count[row["table2_visible_colour"]] += 1
        group_count[row["table2_group"]] += 1
        lines[row["collapsed_species_lineage"]].append(row)

    if len(lines) != 28:
        raise ValueError("raw qPCR labels collapse to unexpected lineage count")
    morphs = {s: rs for s, rs in lines.items() if len(rs) > 1}
    if len(morphs) != 1 or set(morphs) != {"Erica_plukenetii_plukenetii"}:
        raise ValueError("multimorph identity not isolated")
    if len(morphs["Erica_plukenetii_plukenetii"]) != 3:
        raise ValueError("unexpected morph count")
    fixed = [rs[0] for rs in lines.values() if len(rs) == 1]
    if len(fixed) != 27 or any(not row["phenotypically_fixed_sample"] for row in fixed):
        raise ValueError("expected 27 distinct single-colour taxon labels")
    fixed_count = collections.Counter(r["table2_visible_colour"] for r in fixed)
    potential_pairs = {c: n * (n - 1) // 2 for c, n in sorted(fixed_count.items())}
    return {
        "status": "PASS_TABLE2_VISIBLE_COLOUR_QPCR_KEYS_ONLY_TREE_AND_CHEMICAL_STATES_HOLD",
        "version": "v0.1",
        "source_article_doi": d["source_article_doi"],
        "source_table": d["source_table"],
        "qPCR_source_doi": d["measurement_source_doi"],
        "raw_qpcr_id_labels": len(rows),
        "lineage_labels_after_collapsing_colour_morphs": len(lines),
        "morph_only_lineage": next(iter(morphs)),
        "morph_observation_count": 3,
        "single_visible_colour_lineages": len(fixed),
        "raw_table2_colour_counts": dict(sorted(raw_count.items())),
        "single_colour_lineage_counts": dict(sorted(fixed_count.items())),
        "theoretical_within_visible_colour_pairs_before_tree_join": potential_pairs,
        "total_theoretical_pairs_before_tree_join": sum(potential_pairs.values()),
        "published_comparison_group_counts": dict(sorted(group_count.items())),
        "no_imputed_or_unsequenced_phylogeny_tips_admitted": True,
        "no_true_phylogenetic_pair_count_computed": True,
        "no_sixbit_or_full_anthocyanidin_pigment_profile_measured": True,
        "no_cross_radiation_regulatory_memory_test": True,
        "original_AJB_and_EL_submissions_unchanged": True,
        "interpretation": "Only maximum possible within-visible-state species-pair coverage, assuming all original 27 single-state lineages are subsequently independently matched to observed tree tips; not 117 observed pair samples or a phylogenetic effect.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-xlsx", type=Path, required=True)
    ap.add_argument("--crosswalk", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    q = source_key_audit(args.source_xlsx.read_bytes())
    d = json.loads(args.crosswalk.read_text(encoding="utf-8"))
    r = crosswalk(d, q)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(r, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("ERICA_TABLE2_SOURCE_CROSSWALK",r["status"])
    print("ERICA_TABLE2_VISIBLE_COLOUR_RAW",r["raw_table2_colour_counts"])
    print("ERICA_TABLE2_LINEAGES",r["lineage_labels_after_collapsing_colour_morphs"])
    print("ERICA_TABLE2_FIXED_ONLY",r["single_colour_lineage_counts"])
    print("ERICA_TABLE2_POTENTIAL_WITHIN_VISIBLE_STATE_PAIRS_NOT_TREE_JOINED",
          r["total_theoretical_pairs_before_tree_join"],r["theoretical_within_visible_colour_pairs_before_tree_join"])
    print("NO_NEW_GENE_MEMORY_TEST_OR_PIGMENT_PROFILE")


if __name__ == "__main__":
    main()
