#!/usr/bin/env python3
"""Test whether visible colour states cluster on a frozen, independently inferred nuclear topology.

The species tree must be inferred without colour information.  This script joins
colour labels only after topology inference and uses count-preserving random sets
of the same labelled tips to test unrooted topological clustering.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import deque
from pathlib import Path

import numpy as np
from Bio import Phylo


def taxon_key(x: str) -> str:
    x = (x or "").strip().replace("_", " ")
    x = re.sub(r"\s+", " ", x)
    return x.casefold()


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def build_edge_distance_matrix(tree_path: Path):
    tree = Phylo.read(str(tree_path), "newick")
    adj = {}
    for parent in tree.find_clades(order="level"):
        adj.setdefault(parent, [])
        for child in parent.clades:
            adj.setdefault(child, [])
            adj[parent].append(child)
            adj[child].append(parent)

    terminals = tree.get_terminals()
    names = []
    nodes = []
    seen = set()
    for tip in terminals:
        if not tip.name:
            continue
        key = taxon_key(tip.name)
        if key in seen:
            raise SystemExit(f"duplicate normalized tree tip: {tip.name}")
        seen.add(key)
        names.append(key)
        nodes.append(tip)

    n = len(nodes)
    dist = np.zeros((n, n), dtype=np.int16)
    for i, src in enumerate(nodes):
        q = deque([(src, 0)])
        visited = {src}
        dmap = {src: 0}
        while q:
            node, d = q.popleft()
            for nxt in adj[node]:
                if nxt in visited:
                    continue
                visited.add(nxt)
                dmap[nxt] = d + 1
                q.append((nxt, d + 1))
        for j, dst in enumerate(nodes):
            dist[i, j] = dmap[dst]
    return names, dist


def metrics(submatrix: np.ndarray):
    n = submatrix.shape[0]
    if n < 2:
        return float("nan"), float("nan")
    tri = submatrix[np.triu_indices(n, 1)]
    mpd = float(np.mean(tri))
    x = submatrix.astype(float).copy()
    np.fill_diagonal(x, np.inf)
    mntd = float(np.mean(np.min(x, axis=1)))
    return mpd, mntd


def state_test(state: str, state_indices, pool_dist, nperm: int, rng):
    idx = np.array(state_indices, dtype=int)
    n = len(idx)
    if n < 2:
        return {
            "state": state,
            "n_state": n,
            "observed_mpd_edges": None,
            "expected_mpd_edges": None,
            "mpd_cluster_p": None,
            "observed_mntd_edges": None,
            "expected_mntd_edges": None,
            "mntd_cluster_p": None,
        }
    obs_mpd, obs_mntd = metrics(pool_dist[np.ix_(idx, idx)])
    null_mpd = np.empty(nperm, dtype=float)
    null_mntd = np.empty(nperm, dtype=float)
    N = pool_dist.shape[0]
    for k in range(nperm):
        take = rng.choice(N, size=n, replace=False)
        null_mpd[k], null_mntd[k] = metrics(pool_dist[np.ix_(take, take)])
    return {
        "state": state,
        "n_state": n,
        "observed_mpd_edges": obs_mpd,
        "expected_mpd_edges": float(np.mean(null_mpd)),
        "mpd_cluster_p": float((np.sum(null_mpd <= obs_mpd) + 1) / (nperm + 1)),
        "observed_mntd_edges": obs_mntd,
        "expected_mntd_edges": float(np.mean(null_mntd)),
        "mntd_cluster_p": float((np.sum(null_mntd <= obs_mntd) + 1) / (nperm + 1)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--fan-colour", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--permutations", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=20260820)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    tree_names, tree_dist = build_edge_distance_matrix(args.tree)
    name_to_tree = {name: i for i, name in enumerate(tree_names)}

    colour = {}
    for row in read_csv(args.fan_colour):
        key = taxon_key(row.get("taxon", ""))
        state = (row.get("colour_state") or "").strip()
        if key and state in {"A", "W", "Y"}:
            if key in colour and colour[key] != state:
                raise SystemExit(f"conflicting colour states for {row.get('taxon')}: {colour[key]} vs {state}")
            colour[key] = state

    labelled_tree_indices = [i for i, name in enumerate(tree_names) if name in colour]
    labelled_names = [tree_names[i] for i in labelled_tree_indices]
    labelled_states = [colour[n] for n in labelled_names]
    pool_dist = tree_dist[np.ix_(labelled_tree_indices, labelled_tree_indices)]

    rng = np.random.default_rng(args.seed)
    rows = []
    for state in ["A", "W", "Y"]:
        idx = [i for i, s in enumerate(labelled_states) if s == state]
        rows.append(state_test(state, idx, pool_dist, args.permutations, rng))

    with (args.out_dir / "nuclear_colour_clustering.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

    counts = {s: labelled_states.count(s) for s in ["A", "W", "Y"]}
    A = next(r for r in rows if r["state"] == "A")
    summary = {
        "tree_tips": len(tree_names),
        "visible_colour_overlap": len(labelled_names),
        "state_counts": counts,
        "distance_metric": "unrooted number of nuclear-topology edges",
        "permutations": args.permutations,
        "seed": args.seed,
        "A_lineage_clustering_status": (
            "supported" if A["mpd_cluster_p"] < 0.05 and A["mntd_cluster_p"] < 0.05
            else "partial_or_not_supported"
        ),
        "A_result": A,
        "claim_ceiling": (
            "root-independent nuclear-topology clustering of extant visible colour labels; "
            "does not infer ancestral states, transition direction, adaptation, or pollinator causation"
        ),
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
