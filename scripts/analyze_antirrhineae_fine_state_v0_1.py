#!/usr/bin/env python3
"""Conditional fine-state phylogenetic-organization test for Antirrhineae.

Source-native face_phenotype codes:
0 unpigmented, 1 anthocyanin, 2 yellow, 3 double-pigmented.
The coarse null fixes UNPIGMENTED (0) versus PIGMENTED (1/2/3) for every
exactly joined tip and shuffles the exact fine state only within coarse groups.
Twenty deterministic posterior trees are sampled from each 1,000-tree source
ensemble. Posterior trees are topology sensitivities, not biological replicates.
"""
from __future__ import annotations

import argparse
import collections
import copy
import csv
import json
import math
import re
from io import StringIO
from pathlib import Path

import numpy as np
from Bio import Phylo

SEED = 20260907
PERMUTATIONS = 9999
TREE_TESTS = 20
FINE_LABELS = {0: "UNPIGMENTED", 1: "ANTHOCYANIN", 2: "YELLOW", 3: "DOUBLE_PIGMENTED"}
EXPECTED_INTEGRITY = "CURRENT_ISTA_MIRRORS_IDENTICAL_PUBLISHED_MD5_DRIFT"
EXPECTED_SHA256 = "5f25dc400d91ce913d1057aa9c5d7fac13addaf2a479f3af629f8393a90876dd"
HISTORICAL_MD5 = "950f85b80427d357bfeff09608ba02e9"


def read_states(path: Path) -> dict[str, int]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"empty phenotype table: {path}")
    fields = list(rows[0])
    if len(fields) < 2:
        raise ValueError("phenotype table lacks two columns")
    taxon, phenotype = fields[:2]
    out = {}
    for row in rows:
        code = row[taxon]
        value = int(row[phenotype])
        if value not in FINE_LABELS:
            raise ValueError(f"unsupported source phenotype {value}")
        if code in out:
            raise ValueError(f"duplicate taxon code {code}")
        out[code] = value
    return out


def parse_nexus_ensemble(path: Path):
    text = path.read_text(errors="replace")
    mt = re.search(r"\bTRANSLATE\b(.*?);", text, re.I | re.S)
    if not mt:
        raise ValueError(f"TRANSLATE block missing: {path}")
    translate = {int(i): name for i, name in re.findall(r"(\d+)\s+([A-Za-z0-9_.\-]+)\s*,?", mt.group(1))}
    tree_lines = [line.strip() for line in text.splitlines() if re.match(r"TREE\b", line.strip(), re.I)]
    if len(tree_lines) != 1000:
        raise ValueError(f"expected 1000 posterior trees, found {len(tree_lines)} in {path}")
    return translate, tree_lines


def parse_tree_line(line: str, translate: dict[int, str]):
    rhs = line.split("=", 1)[1].strip()
    rhs = re.sub(r"^\[&R\]\s*", "", rhs)
    tree = Phylo.read(StringIO(rhs), "newick")
    for tip in tree.get_terminals():
        if tip.name and tip.name.isdigit():
            tip.name = translate[int(tip.name)]
    names = [tip.name for tip in tree.get_terminals()]
    if len(names) != len(set(names)):
        raise ValueError("duplicate terminal names after TRANSLATE")
    return tree


def prune_to(tree, keep: set[str]):
    tree = copy.deepcopy(tree)
    for tip in list(tree.get_terminals()):
        if tip.name not in keep:
            tree.prune(tip)
    if {tip.name for tip in tree.get_terminals()} != keep:
        raise ValueError("pruned tree does not match exact joined tip set")
    return tree


def make_permutations(names: list[str], states: dict[str, int]):
    codes = sorted({states[name] for name in names})
    code_index = {code: i for i, code in enumerate(codes)}
    observed = np.array([code_index[states[name]] for name in names], dtype=np.int16)
    coarse = np.array([0 if states[name] == 0 else 1 for name in names], dtype=np.int8)
    if set(coarse.tolist()) != {0, 1}:
        raise ValueError("conditional null requires pigmented and unpigmented tips")
    groups = [np.where(coarse == group)[0] for group in (0, 1)]
    out = np.empty((PERMUTATIONS + 1, len(names)), dtype=np.int16)
    out[0] = observed
    rng = np.random.default_rng(SEED)
    for i in range(1, PERMUTATIONS + 1):
        shuffled = observed.copy()
        for group in groups:
            shuffled[group] = observed[rng.permutation(group)]
        out[i] = shuffled
    return out, codes


def sankoff_scores(tree, names: list[str], permuted: np.ndarray, k: int, batch: int = 500):
    leaves = list(tree.get_terminals())
    leaf_names = [leaf.name for leaf in leaves]
    if set(leaf_names) != set(names):
        raise ValueError("tree/state tip mismatch")
    name_index = {name: i for i, name in enumerate(names)}
    leaf_order = np.array([name_index[name] for name in leaf_names], dtype=int)
    nodes = list(tree.find_clades(order="postorder"))
    node_index = {id(node): i for i, node in enumerate(nodes)}
    leaf_nodes = [node_index[id(leaf)] for leaf in leaves]
    children = [[node_index[id(child)] for child in node.clades] for node in nodes]
    scores = np.empty(permuted.shape[0], dtype=np.int16)
    big = np.int16(30000)
    for start in range(0, len(permuted), batch):
        end = min(len(permuted), start + batch)
        state_batch = permuted[start:end][:, leaf_order]
        b = end - start
        d = np.full((len(nodes), b, k), big, dtype=np.int16)
        rows = np.arange(b)
        for j, node_i in enumerate(leaf_nodes):
            d[node_i, rows, state_batch[:, j]] = 0
        for i in range(len(nodes)):
            if not children[i]:
                continue
            d[i].fill(0)
            for child_i in children[i]:
                child = d[child_i]
                minimum = child.min(axis=1)
                d[i] += np.minimum(child, minimum[:, None] + 1)
        scores[start:end] = d[-1].min(axis=1)
    return scores


def analyze_dataset(tree_path: Path, phenotype_path: Path, role: str):
    translate, tree_lines = parse_nexus_ensemble(tree_path)
    source_states = read_states(phenotype_path)
    tree_tips = set(translate.values())
    states = {tip: source_states[tip] for tip in tree_tips if tip in source_states}
    names = sorted(states)
    if len(names) < 140 and role == "PRIMARY":
        raise ValueError(f"primary exact joins below frozen floor: {len(names)}")
    counts = collections.Counter(states.values())
    permuted, codes = make_permutations(names, states)
    indices = np.linspace(0, len(tree_lines) - 1, TREE_TESTS, dtype=int).tolist()
    tests = []
    for tree_index in indices:
        tree = parse_tree_line(tree_lines[tree_index], translate)
        tree = prune_to(tree, set(names))
        scores = sankoff_scores(tree, names, permuted, len(codes))
        observed = int(scores[0])
        null = scores[1:]
        null_mean = float(null.mean())
        ratio = float(observed / null_mean)
        p = float((1 + int((null <= observed).sum())) / (len(null) + 1))
        tests.append({
            "tree_index": int(tree_index),
            "observed_minimum_changes": observed,
            "null_mean": null_mean,
            "observed_over_null_mean": ratio,
            "lower_tail_p": p,
        })
    passing = sum(test["lower_tail_p"] <= 0.01 and test["observed_over_null_mean"] < 1 for test in tests)
    return {
        "role": role,
        "nexus_posterior_trees": len(tree_lines),
        "exact_joined_tips": len(names),
        "fine_state_counts": {str(code): int(counts.get(code, 0)) for code in sorted(counts)},
        "tree_tips_without_exact_phenotype": sorted(tree_tips - set(source_states)),
        "phenotypes_without_exact_tree_tip": sorted(set(source_states) - tree_tips),
        "selected_tree_indices": indices,
        "tests": tests,
        "passing_tests_p_le_0_01_ratio_lt_1": passing,
        "observed_over_null_range": [min(t["observed_over_null_mean"] for t in tests), max(t["observed_over_null_mean"] for t in tests)],
        "p_range": [min(t["lower_tail_p"] for t in tests), max(t["lower_tail_p"] for t in tests)],
    }


def compare(expected, actual, path="result"):
    if type(expected) is not type(actual):
        raise ValueError(f"{path}: type mismatch")
    if isinstance(expected, dict):
        if set(expected) != set(actual):
            raise ValueError(f"{path}: key mismatch expected={sorted(expected)} actual={sorted(actual)}")
        for key in expected:
            compare(expected[key], actual[key], f"{path}.{key}")
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            raise ValueError(f"{path}: length mismatch")
        for i, (x, y) in enumerate(zip(expected, actual)):
            compare(x, y, f"{path}[{i}]")
    elif isinstance(expected, float):
        if not math.isclose(expected, actual, rel_tol=1e-8, abs_tol=1e-10):
            raise ValueError(f"{path}: numeric drift {expected} != {actual}")
    elif expected != actual:
        raise ValueError(f"{path}: value drift {expected!r} != {actual!r}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-dir", type=Path, required=True)
    p.add_argument("--source-manifest", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--expected", type=Path)
    a = p.parse_args()
    source = json.loads(a.source_manifest.read_text())
    if source["current_source_integrity_status"] != EXPECTED_INTEGRITY:
        raise ValueError("source integrity status changed")
    if source["admitted_download"]["sha256"] != EXPECTED_SHA256:
        raise ValueError("current ISTA source SHA256 changed")
    if source["historical_published_md5"] != HISTORICAL_MD5:
        raise ValueError("historical published MD5 contract changed")
    mono = analyze_dataset(a.source_dir / "monomorphic_snapdragons.tree", a.source_dir / "mm_face_phenotypes.csv", "PRIMARY")
    poly = analyze_dataset(a.source_dir / "polymorphic_snapdragons.tree", a.source_dir / "face_phenotypes.csv", "SENSITIVITY")
    primary_counts = mono["fine_state_counts"]
    gate = (
        mono["exact_joined_tips"] >= 140
        and int(primary_counts.get("1", 0)) >= 20
        and int(primary_counts.get("2", 0)) >= 20
        and mono["passing_tests_p_le_0_01_ratio_lt_1"] >= 18
        and poly["passing_tests_p_le_0_01_ratio_lt_1"] >= 18
        and source["current_source_integrity_status"] == EXPECTED_INTEGRITY
    )
    result = {
        "version": "v0.1",
        "source_doi": "10.15479/AT:ISTA:34",
        "source_integrity_status": source["current_source_integrity_status"],
        "source_current_sha256": source["admitted_download"]["sha256"],
        "historical_published_md5": source["historical_published_md5"],
        "seed": SEED,
        "permutations": PERMUTATIONS,
        "selected_tree_count_per_dataset": TREE_TESTS,
        "coarse_state": {"UNPIGMENTED": [0], "PIGMENTED": [1, 2, 3]},
        "fine_state": {str(k): v for k, v in FINE_LABELS.items()},
        "datasets": {"monomorphic": mono, "polymorphic": poly},
        "pre_frozen_gate": "PASS" if gate else "FAIL",
        "third_independent_replication_admitted": bool(gate),
        "cross_radiation_update": (
            "HIERARCHICAL_FINE_STATE_CANDIDATE_REPLICATED_IN_3_OF_3_TESTABLE_EXTERNAL_RADIATIONS"
            if gate else "NO_THIRD_REPLICATION"
        ),
        "interpretation": (
            "Anthocyanin-versus-yellow pigment state remains phylogenetically organized after conditioning on coarse pigment presence across posterior-tree sensitivities; this is a third independent nested fine-state replication, not a universal transition-direction or causal mechanism result."
            if gate else "Pre-frozen third-replication gate not met."
        ),
        "claim_boundary": "Posterior trees are correlated topology uncertainty within one Antirrhineae radiation and are not biological replications. Exact taxon-code joins only; historical source-MD5 drift is retained explicitly.",
        "paper1_science_changed": False,
    }
    if a.expected:
        compare(json.loads(a.expected.read_text()), result)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
