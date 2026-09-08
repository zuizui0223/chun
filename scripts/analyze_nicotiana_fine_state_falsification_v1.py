#!/usr/bin/env python3
"""Prospective fifth-radiation Nicotiana fine-state falsification endpoint.

Scientific definitions, nulls, seed, permutation count and decision gates are
frozen in analysis/nicotiana_fine_state_falsification_prefreeze_v1.md. This
script must not be run unless the source/trait/OpenTree admission layers pass.
"""
from __future__ import annotations

import copy
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from Bio import Phylo

SEED = 20260908
PERMUTATIONS = 9999
FINE = ("MAGENTA", "RED", "PINK", "UV_WHITE", "WHITE", "YELLOW", "GREEN", "DARK_GREEN")
FINE_INDEX = {x: i for i, x in enumerate(FINE)}
SOURCE_DIR = Path("analysis/_generated/nicotiana_source_v1")
TREE_DIR = Path("analysis/_generated/nicotiana_opentree_v1")
OUT_DIR = Path("analysis/_generated/nicotiana_falsification_v1")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_inputs():
    trait_path = SOURCE_DIR / "trait_audit.json"
    inventory_path = SOURCE_DIR / "inventory.json"
    tree_summary_path = TREE_DIR / "summary.json"
    tree_path = TREE_DIR / "opentree_source_taxa.nwk"
    for p in (trait_path, inventory_path, tree_summary_path, tree_path):
        if not p.exists():
            raise SystemExit(f"required frozen admission input missing: {p}")
    trait = json.loads(trait_path.read_text(encoding="utf-8"))
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    tree_summary = json.loads(tree_summary_path.read_text(encoding="utf-8"))
    if not all(trait["summary"].get("pre_tree_admission_checks", {}).values()):
        raise SystemExit("trait pre-tree admission gate not passed")
    if not tree_summary.get("endpoint_allowed", False):
        raise SystemExit("OpenTree admission gate not passed")
    tree = Phylo.read(str(tree_path), "newick")
    return trait, inventory, tree_summary, tree, tree_path


def trait_map(trait):
    return {
        row["taxon"]: {
            "fine": frozenset(row["fine_states"]),
            "coarse": frozenset(row["coarse_states"]),
            "source_labels": tuple(row["source_labels"]),
        }
        for row in trait["summary"]["eligible_taxa"]
    }


def prune_tree(tree, keep):
    """Deterministic collapse-safe pruning by current terminal name."""
    keep = set(keep)
    t = copy.deepcopy(tree)
    while True:
        removable = sorted((tip for tip in t.get_terminals() if tip.name not in keep), key=lambda x: str(x.name))
        if not removable:
            break
        t.prune(removable[0])
    names = {tip.name for tip in t.get_terminals()}
    if names != keep:
        raise ValueError(f"tree pruning mismatch: missing={sorted(keep-names)} extra={sorted(names-keep)}")
    return t


def sankoff_scores(tree, names, vector_sets, group_keys, permutations=PERMUTATIONS, seed=SEED, batch=500):
    """Unordered Sankoff score for allowed-state vectors under a conditional permutation null."""
    names = list(names)
    if len(names) != len(set(names)):
        raise ValueError("duplicate analysis names")
    if set(names) != set(vector_sets) or set(names) != set(group_keys):
        raise ValueError("state/group name sets do not match")
    k = len(FINE)
    allowed = [frozenset(vector_sets[n]) for n in names]
    if any(not x for x in allowed):
        raise ValueError("empty fine-state vector")
    if any(not set(x) <= set(FINE) for x in allowed):
        raise ValueError("unknown fine state")

    # Each row is the allowed-state cost vector belonging to one species unit.
    patterns = np.array(
        [[0 if state in states else 20000 for state in FINE] for states in allowed],
        dtype=np.int16,
    )
    by_group = defaultdict(list)
    for i, n in enumerate(names):
        by_group[tuple(sorted(group_keys[n]))].append(i)
    groups = [np.asarray(v, dtype=int) for _, v in sorted(by_group.items(), key=lambda kv: kv[0])]
    if not groups:
        raise ValueError("no conditional groups")

    rng = np.random.default_rng(seed)
    assignment = np.empty((permutations + 1, len(names)), dtype=np.int16)
    assignment[0] = np.arange(len(names), dtype=np.int16)
    for p in range(1, permutations + 1):
        row = np.arange(len(names), dtype=np.int16)
        for g in groups:
            row[g] = rng.permutation(g)
        assignment[p] = row

    terminals = list(tree.get_terminals())
    terminal_names = [tip.name for tip in terminals]
    if set(terminal_names) != set(names):
        raise ValueError("tree/state terminal mismatch")
    name_index = {n: i for i, n in enumerate(names)}
    leaf_source_positions = np.asarray([name_index[n] for n in terminal_names], dtype=int)

    nodes = list(tree.find_clades(order="postorder"))
    node_index = {id(node): i for i, node in enumerate(nodes)}
    children = [[node_index[id(c)] for c in node.clades] for node in nodes]
    leaf_nodes = [node_index[id(t)] for t in terminals]
    scores = np.empty(permutations + 1, dtype=np.int16)
    big = np.int16(20000)

    for start in range(0, permutations + 1, batch):
        end = min(permutations + 1, start + batch)
        b = end - start
        d = np.full((len(nodes), b, k), big, dtype=np.int16)
        batch_assign = assignment[start:end]
        for leaf_pos, node_i in enumerate(leaf_nodes):
            species_position = leaf_source_positions[leaf_pos]
            source_vector_index = batch_assign[:, species_position]
            d[node_i] = patterns[source_vector_index]
        for i, ch in enumerate(children):
            if not ch:
                continue
            d[i].fill(0)
            for c in ch:
                child = d[c]
                mn = child.min(axis=1)
                d[i] += np.minimum(child, mn[:, None] + 1)
        scores[start:end] = d[-1].min(axis=1)

    observed = int(scores[0])
    null = scores[1:]
    mean = float(null.mean())
    p_lower = float((1 + int((null <= observed).sum())) / (len(null) + 1))
    ratio = float(observed / mean) if mean else None
    return {
        "n_tips": len(names),
        "conditional_group_sizes": {
            "|".join(key): len(v)
            for key, v in sorted(((tuple(sorted(group_keys[n])), []) for n in []), key=lambda x: x[0])
        },
        "observed_minimum_changes": observed,
        "null_mean": mean,
        "null_quantiles": [float(x) for x in np.quantile(null, [0, 0.025, 0.5, 0.975, 1])],
        "observed_over_null_mean": ratio,
        "p_lower": p_lower,
        "permutations": len(null),
        "seed": seed,
        "support_gate_p_le_0_01_and_ratio_lt_1": bool(p_lower <= 0.01 and ratio is not None and ratio < 1),
        "_group_sizes_internal": {
            "|".join(k): len(v)
            for k, v in sorted(by_group.items(), key=lambda kv: kv[0])
        },
    }


def clean_result(r):
    r = dict(r)
    r["conditional_group_sizes"] = r.pop("_group_sizes_internal")
    return r


def computationally_admissible(names, vectors, groups):
    if len(names) < 2:
        return False, "FEWER_THAN_2_TIPS"
    observed_states = set().union(*(set(vectors[n]) for n in names))
    if len(observed_states) < 2:
        return False, "FEWER_THAN_2_FINE_STATES"
    key_counts = Counter(tuple(sorted(groups[n])) for n in names)
    if not any(n >= 2 for n in key_counts.values()):
        return False, "NO_CONDITIONAL_GROUP_WITH_AT_LEAST_2_TIPS"
    return True, "ADMITTED"


def run_test(label, tree, names, vectors, groups):
    names = sorted(names)
    ok, why = computationally_admissible(names, vectors, groups)
    if not ok:
        return {"status": "NOT_ADJUDICABLE", "reason": why, "label": label, "n_tips": len(names)}
    sub = prune_tree(tree, set(names))
    r = clean_result(sankoff_scores(sub, names, {n: vectors[n] for n in names}, {n: groups[n] for n in names}))
    r["status"] = "COMPUTED"
    r["label"] = label
    r["fine_state_tip_presence"] = dict(sorted(Counter(s for n in names for s in vectors[n]).items()))
    return r


def main():
    trait, inventory, tree_summary, tree, tree_path = load_inputs()
    traits = trait_map(trait)
    tree_names = {tip.name for tip in tree.get_terminals()}
    admitted = sorted(tree_names & set(traits))
    if len(admitted) != int(tree_summary["n_tree_overlap"]):
        raise SystemExit(f"endpoint tree/trait overlap drift: {len(admitted)} != {tree_summary['n_tree_overlap']}")

    vectors = {n: traits[n]["fine"] for n in admitted}
    primary_groups = {n: traits[n]["coarse"] for n in admitted}

    # Recheck the frozen primary post-tree gates on the actual admitted intersection.
    definite_counts = Counter()
    fine_by_definite = defaultdict(set)
    for n in admitted:
        if len(primary_groups[n]) == 1:
            c = next(iter(primary_groups[n]))
            definite_counts[c] += 1
            fine_by_definite[c].update(vectors[n])
    eligibility_n = int(tree_summary["eligible_trait_taxa"])
    primary_gates = {
        "coverage_ge_80pct": len(admitted) / eligibility_n >= 0.80,
        "admitted_n_ge_20": len(admitted) >= 20,
        "all_admitted_have_fine_and_coarse": all(vectors[n] and primary_groups[n] for n in admitted),
        "both_definite_coarse_classes_ge_5": all(definite_counts[c] >= 5 for c in ("CHLOROPHYLL_PRESENT", "CHLOROPHYLL_ABSENT")),
        "one_definite_coarse_class_ge_10_and_ge_3_fine": any(
            definite_counts[c] >= 10 and len(fine_by_definite[c]) >= 3 for c in definite_counts
        ),
        "no_signal_based_taxon_exclusion": True,
    }
    if not all(primary_gates.values()):
        raise SystemExit(f"HOLD_OBSERVATION_REGIME primary post-tree gate failed: {primary_gates}")

    primary = run_test("PRIMARY_CHLOROPHYLL_LAYER", tree, admitted, vectors, primary_groups)
    if primary.get("status") != "COMPUTED":
        raise SystemExit(f"primary endpoint unexpectedly not adjudicable: {primary}")

    single_fine_names = [n for n in admitted if len(vectors[n]) == 1]
    single_fine = run_test(
        "SENSITIVITY_SINGLE_FINE_STATE_SPECIES",
        tree,
        single_fine_names,
        vectors,
        primary_groups,
    )

    definite_coarse_names = [n for n in admitted if len(primary_groups[n]) == 1]
    definite_coarse = run_test(
        "SENSITIVITY_DEFINITE_CHLOROPHYLL_SPECIES",
        tree,
        definite_coarse_names,
        vectors,
        primary_groups,
    )

    white_like_groups = {}
    for n in admitted:
        g = set()
        if any(s in {"WHITE", "UV_WHITE"} for s in vectors[n]):
            g.add("WHITE_LIKE")
        if any(s not in {"WHITE", "UV_WHITE"} for s in vectors[n]):
            g.add("NONWHITE_LIKE")
        white_like_groups[n] = frozenset(g)
    white_like = run_test(
        "SENSITIVITY_WHITE_UVWHITE_VS_NONWHITE",
        tree,
        admitted,
        vectors,
        white_like_groups,
    )

    trait_sensitivities = [single_fine, definite_coarse, white_like]
    computed = [x for x in trait_sensitivities if x.get("status") == "COMPUTED"]
    support_primary = bool(primary["support_gate_p_le_0_01_and_ratio_lt_1"])
    computed_supports = [bool(x["support_gate_p_le_0_01_and_ratio_lt_1"]) for x in computed]
    unavailable = [x for x in trait_sensitivities if x.get("status") != "COMPUTED"]

    if support_primary:
        classification = "MIXED" if any(not x for x in computed_supports) else "SUPPORTIVE_ALIGNMENT"
    else:
        if any(computed_supports):
            classification = "MIXED"
        elif unavailable:
            classification = "ADVERSE_BUT_NOT_REFUTATION"
        else:
            classification = "REFUTATION"

    selected_doc = inventory.get("selected_doc") or {}
    result = {
        "version": "v1",
        "test_unit": "Nicotiana_nonhybrid_diploids",
        "source_doi": "10.1093/aob/mcv048",
        "source_supplement_member_sha256": selected_doc.get("sha256"),
        "fine_alphabet": list(FINE),
        "primary_coarse_layer": ["CHLOROPHYLL_PRESENT", "CHLOROPHYLL_ABSENT"],
        "permutations": PERMUTATIONS,
        "seed": SEED,
        "tree": {
            **tree_summary,
            "source_labeled_newick_sha256": sha256_file(tree_path),
        },
        "primary_admission_gates": primary_gates,
        "post_tree_definite_coarse_counts": dict(sorted(definite_counts.items())),
        "post_tree_fine_states_within_definite_coarse": {k: sorted(v) for k, v in sorted(fine_by_definite.items())},
        "primary": primary,
        "sensitivities": {
            "single_fine_state_species": single_fine,
            "definite_chlorophyll_species": definite_coarse,
            "white_uvwhite_vs_nonwhite": white_like,
            "source_topology": {
                "status": "NOT_AVAILABLE",
                "reason": "No machine-readable final source tree recovered from the publisher supplement; Fig. S6 is embedded in the legacy document.",
            },
        },
        "classification": classification,
        "interpretation": (
            "Nicotiana supports residual fine-state organization after the frozen chlorophyll coarse layer without material contradictory admitted trait sensitivity."
            if classification == "SUPPORTIVE_ALIGNMENT" else
            "Nicotiana produces materially different outcomes across the frozen primary and/or trait sensitivities; classify as MIXED."
            if classification == "MIXED" else
            "Nicotiana fails the frozen primary and all adjudicable predeclared trait sensitivities; this is a matched fifth-radiation refutation of the surviving recurrence generalization."
            if classification == "REFUTATION" else
            "The Nicotiana primary result is adverse but required robustness cannot be fully adjudicated; do not upgrade to refutation."
        ),
        "claim_boundary": "Prospective matched test of residual spectral fine-state phylogenetic organization after source-defined petal chlorophyll conditioning in non-hybrid diploids. Not a universal transition-direction, pollinator-perception, pigment-pathway or hybrid-network test.",
        "paper1_science_changed": False,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("NICOTIANA_FALSIFICATION_ENDPOINT=" + json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
