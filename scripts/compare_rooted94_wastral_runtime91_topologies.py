#!/usr/bin/env python3
"""Compare the rooted94 FastTree/ASTRAL sensitivity topology with the stronger runtime91 IQ-TREE/UFBoot/wASTRAL topology.

This gate is deliberately root-independent on the 91 shared Camellia tips. It
asks whether the core paper claims depend on the approximate gene-tree method.
It also checks whether the two robust W->A relationships that are representable
in runtime91 (B011 and B073) retain their local topology. B083/C. japonica is
not in runtime91 and is therefore explicitly non-testable here.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import deque
from pathlib import Path

from Bio import Phylo


def norm(x):
    return re.sub(r"\s+", " ", (x or "").strip().replace("_", " ")).casefold()


def tip_names(tree):
    return {norm(t.name): t.name for t in tree.get_terminals() if t.name}


def prune_to(tree, keep_norm):
    # Bio.Phylo prune one terminal at a time; operate on a fresh parsed tree.
    for t in list(tree.get_terminals()):
        if t.name and norm(t.name) not in keep_norm:
            tree.prune(t)
    return tree


def split_set(tree):
    tips = sorted(norm(t.name) for t in tree.get_terminals() if t.name)
    U = frozenset(tips)
    out = set()
    for c in tree.find_clades(order="preorder"):
        if c is tree.root:
            continue
        side = frozenset(norm(t.name) for t in c.get_terminals() if t.name)
        if len(side) <= 1 or len(U - side) <= 1:
            continue
        other = U - side
        # canonical representation independent of rooting and orientation
        key = side if (len(side), tuple(sorted(side))) <= (len(other), tuple(sorted(other))) else other
        out.add(key)
    return U, out


def edge_distance(tree, a, b):
    na = next((t for t in tree.get_terminals() if norm(t.name) == norm(a)), None)
    nb = next((t for t in tree.get_terminals() if norm(t.name) == norm(b)), None)
    if na is None or nb is None:
        return None
    adj = {}
    for x in tree.find_clades(order="level"):
        adj.setdefault(x, [])
        for y in x.clades:
            adj.setdefault(y, [])
            adj[x].append(y); adj[y].append(x)
    q = deque([(na, 0)]); seen = {na}
    while q:
        x, d = q.popleft()
        if x is nb:
            return d
        for y in adj[x]:
            if y not in seen:
                seen.add(y); q.append((y, d + 1))
    return None


def read_transitions(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return {r["branch_id"]: r for r in csv.DictReader(f)}


def parse_tip_list(x):
    return {norm(v) for v in (x or "").split(";") if v.strip()}


def split_present(target, universe, splits):
    target = frozenset(target & universe)
    if len(target) <= 1 or len(universe - target) <= 1:
        return None
    other = universe - target
    key = target if (len(target), tuple(sorted(target))) <= (len(other), tuple(sorted(other))) else other
    return key in splits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rooted94", type=Path, required=True)
    ap.add_argument("--wastral91", type=Path, required=True)
    ap.add_argument("--transitions", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    r94 = Phylo.read(str(a.rooted94), "newick")
    w91 = Phylo.read(str(a.wastral91), "newick")
    n94 = tip_names(r94); n91 = tip_names(w91)
    common = set(n94) & set(n91)
    if len(n91) != 91 or len(common) != 91:
        raise SystemExit(f"expected all 91 wASTRAL tips in rooted94: n91={len(n91)} common={len(common)}")

    # Fresh parse before pruning to avoid altering the input tree used elsewhere.
    rp = prune_to(Phylo.read(str(a.rooted94), "newick"), common)
    U1, S1 = split_set(rp)
    U2, S2 = split_set(w91)
    if U1 != U2 or len(U1) != 91:
        raise SystemExit("shared-tip universes differ after pruning")
    shared = len(S1 & S2)
    sym = len(S1 ^ S2)
    denom = max(1, len(S1) + len(S2))
    normalized_rf = sym / denom

    tr = read_transitions(a.transitions)
    b011 = parse_tip_list(tr["B011"].get("descendant_tips"))
    b073 = parse_tip_list(tr["B073"].get("descendant_tips"))
    b083 = parse_tip_list(tr["B083"].get("descendant_tips"))

    # B011 is an internal split. B073 is terminal, so its relevant local topology
    # is the brevistyla-confusa cherry/context. B083 is absent from runtime91.
    b011_rooted = split_present(b011, U1, S1)
    b011_wastral = split_present(b011, U2, S2)
    d_b073_rooted = edge_distance(rp, "Camellia brevistyla", "Camellia confusa")
    d_b073_wastral = edge_distance(w91, "Camellia brevistyla", "Camellia confusa")
    b083_runtime_present = norm("Camellia japonica") in U2

    out = {
        "n_shared_tips": len(U1),
        "rooted94_pruned_nontrivial_splits": len(S1),
        "wastral91_nontrivial_splits": len(S2),
        "shared_nontrivial_splits": shared,
        "symmetric_split_difference": sym,
        "normalized_robinson_foulds": normalized_rf,
        "B011_24tip_split_present_rooted94_pruned": b011_rooted,
        "B011_24tip_split_present_wastral91": b011_wastral,
        "B073_brevistyla_confusa_edge_distance_rooted94_pruned": d_b073_rooted,
        "B073_brevistyla_confusa_edge_distance_wastral91": d_b073_wastral,
        "B073_local_pair_retained": d_b073_rooted == 2 and d_b073_wastral == 2,
        "B083_japonica_present_in_runtime91": b083_runtime_present,
        "B083_sensitivity_status": "not_testable_in_runtime91" if not b083_runtime_present else "testable",
        "claim_boundary": "root-independent shared-tip topology sensitivity; absence of B083 from runtime91 is explicit and not treated as disagreement"
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
