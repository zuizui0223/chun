#!/usr/bin/env python3
"""Execution wrapper for the frozen Iris endpoint.

This patches only the tree-pruning implementation used by the predeclared
single-coarse sensitivity. Scientific state definitions, nulls, seed,
permutation count and decision gates remain in the frozen endpoint module.
"""
from __future__ import annotations

import copy

import analyze_iris_fine_state_falsification_v1 as endpoint


def robust_prune_tree(tree, keep):
    """Prune by re-reading current terminals after each collapse.

    Bio.Phylo may collapse a parent when pruning a child. Reusing a stale list of
    Clade objects across those collapses can leave the final terminal set unequal
    to the requested set. This implementation makes the same deterministic
    topology-only exclusion but resolves each next target from the current tree.
    """
    keep = set(keep)
    t = copy.deepcopy(tree)
    while True:
        removable = [tip for tip in t.get_terminals() if tip.name not in keep]
        if not removable:
            break
        # Deterministic and colour-blind: lexical source identifier only.
        removable.sort(key=lambda tip: str(tip.name))
        t.prune(removable[0])
    names = {tip.name for tip in t.get_terminals()}
    if names != keep:
        raise ValueError(
            f"sensitivity pruning failed after dynamic pruning: "
            f"missing={sorted(keep-names)[:10]} extra={sorted(names-keep)[:10]}"
        )
    return t


endpoint.prune_tree = robust_prune_tree
endpoint.main()
