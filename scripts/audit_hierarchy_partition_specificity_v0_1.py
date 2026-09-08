#!/usr/bin/env python3
"""Exhaustive alternative-partition control for the hierarchical flower-colour rule.

This script was added after docs/HIERARCHY_SPECIFICITY_PRE_RESULT_GATE_V0_1.md
was frozen.  It does not ask whether the already-established fine state has
phylogenetic signal.  Instead it asks whether the biologically selected coarse
boundary captures an unusually large share of that fine-state organization
relative to every non-trivial two-way partition of the same fine alphabet.

Sensitivity trees/source codings are correlated settings within a radiation and
are never counted as independent biological replications.
"""
from __future__ import annotations

import argparse
import collections
import copy
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from Bio import Phylo

from analyze_linoideae_mk_v0_2 import SEED, COLORS, load_snapshot, rooted_ingroup, subset
from analyze_angraecinae_mk_v0_1 import extract_ingroup_and_prune
from analyze_antirrhineae_fine_state_v0_1 import (
    EXPECTED_INTEGRITY,
    EXPECTED_SHA256,
    HISTORICAL_MD5,
    parse_nexus_ensemble,
    parse_tree_line,
    prune_to,
    read_states,
)

CONTROL_PERMUTATIONS = 999
LINO_CROP_TIP = "LINO113"
ANG_ORGANS = ("sepal_binary", "petal_binary", "labellum_binary", "spur_binary")
ANG_BINARY = {"WHITE", "GREEN"}


def canonical_partitions(labels):
    """Return each non-trivial bipartition once, fixing labels[0] on side A."""
    labels = tuple(labels)
    first = labels[0]
    rest = labels[1:]
    out = []
    # Every subset containing first except the full set: 2^(k-1)-1 partitions.
    for mask in range(1 << len(rest)):
        side = {first}
        for i, label in enumerate(rest):
            if mask & (1 << i):
                side.add(label)
        if len(side) == len(labels):
            continue
        other = set(labels) - side
        out.append((frozenset(side), frozenset(other)))
    return out


def canonicalize_biological(side, labels):
    labels = tuple(labels)
    side = set(side)
    if labels[0] in side:
        return frozenset(side)
    return frozenset(set(labels) - side)


def partition_id(side_a, labels):
    return "A=" + "+".join(str(x) for x in labels if x in side_a)


class SankoffEngine:
    def __init__(self, tree, allowed_states: dict[str, frozenset], labels):
        self.labels = tuple(labels)
        label_index = {label: i for i, label in enumerate(self.labels)}
        self.tree = tree
        self.nodes = list(tree.find_clades(order="postorder"))
        self.index = {id(n): i for i, n in enumerate(self.nodes)}
        self.children = [[self.index[id(c)] for c in n.clades] for n in self.nodes]
        leaves = list(tree.get_terminals())
        leaf_names = [x.name for x in leaves]
        if len(leaf_names) != len(set(leaf_names)) or set(leaf_names) != set(allowed_states):
            raise ValueError("tree/fine-state tips must match exactly")
        self.names = leaf_names
        self.leaf_nodes = [self.index[id(x)] for x in leaves]
        self.allowed_labels = []
        k = len(self.labels)
        base = np.full((len(leaves), k), 30000, dtype=np.int16)
        for i, name in enumerate(self.names):
            allowed = frozenset(allowed_states[name])
            if not allowed or not set(allowed) <= set(self.labels):
                raise ValueError("invalid fine-state allowed set")
            self.allowed_labels.append(allowed)
            for label in allowed:
                base[i, label_index[label]] = 0
        self.base = base
        self.k = k

    def _scores(self, indices: np.ndarray, batch_size=250):
        nperm = len(indices)
        out = np.empty(nperm, dtype=np.int16)
        for start in range(0, nperm, batch_size):
            end = min(nperm, start + batch_size)
            idx = indices[start:end]
            b = end - start
            d = np.zeros((len(self.nodes), b, self.k), dtype=np.int16)
            for pos, node_i in enumerate(self.leaf_nodes):
                d[node_i] = self.base[idx[:, pos]]
            for i in range(len(self.nodes)):
                for child in self.children[i]:
                    child_d = d[child]
                    d[i] += np.minimum(child_d, child_d.min(axis=1)[:, None] + 1)
            out[start:end] = d[-1].min(axis=1)
        return out

    def observed(self):
        return int(self._scores(np.arange(len(self.names), dtype=int)[None, :])[0])

    def null_mean(self, groups=None, permutations=CONTROL_PERMUTATIONS, seed=SEED):
        nt = len(self.names)
        rng = np.random.default_rng(seed)
        indices = np.empty((permutations, nt), dtype=np.int32)
        if groups is None:
            for i in range(permutations):
                indices[i] = rng.permutation(nt)
        else:
            groups = [np.asarray(g, dtype=int) for g in groups if len(g)]
            covered = sorted(np.concatenate(groups).tolist()) if groups else []
            if covered != list(range(nt)):
                raise ValueError("conditional groups do not partition all tips")
            for i in range(permutations):
                row = np.arange(nt, dtype=np.int32)
                for group in groups:
                    row[group] = rng.permutation(group)
                indices[i] = row
        return float(self._scores(indices).mean())

    def groups_for_partition(self, side_a):
        side_a = set(side_a)
        side_b = set(self.labels) - side_a
        grouped = collections.defaultdict(list)
        for i, allowed in enumerate(self.allowed_labels):
            # Exact generalisation of the previous WHITE/NONWHITE/ambiguous mask:
            # only-A, only-B, or crossing both sides.
            key = (bool(set(allowed) & side_a), bool(set(allowed) & side_b))
            if key == (False, False):
                raise ValueError("fine observation intersects neither partition side")
            grouped[key].append(i)
        return list(grouped.values()), {str(k): len(v) for k, v in grouped.items()}


def evaluate_setting(tree, allowed_states, labels, biological_side, setting_id):
    labels = tuple(labels)
    engine = SankoffEngine(tree, allowed_states, labels)
    observed = engine.observed()
    unconditional = engine.null_mean(groups=None)
    denominator = unconditional - observed
    if denominator <= 0:
        raise ValueError(f"{setting_id}: fine state lacks positive unconditional organization; denominator={denominator}")
    partitions = canonical_partitions(labels)
    bio = canonicalize_biological(biological_side, labels)
    records = []
    for side_a, side_b in partitions:
        groups, group_sizes = engine.groups_for_partition(side_a)
        conditional = engine.null_mean(groups=groups)
        capture = (unconditional - conditional) / denominator
        records.append({
            "partition": partition_id(side_a, labels),
            "side_a": [str(x) for x in labels if x in side_a],
            "side_b": [str(x) for x in labels if x in side_b],
            "group_sizes": group_sizes,
            "conditional_null_mean": conditional,
            "capture_fraction": float(capture),
            "is_biological": side_a == bio,
        })
    if sum(r["is_biological"] for r in records) != 1:
        raise ValueError(f"{setting_id}: biological partition not uniquely represented")
    bio_record = next(r for r in records if r["is_biological"])
    tol = 1e-12
    rank = 1 + sum(r["capture_fraction"] > bio_record["capture_fraction"] + tol for r in records)
    percentile = (rank - 1) / (len(records) - 1) if len(records) > 1 else 0.0
    return {
        "setting_id": setting_id,
        "n_tips": len(engine.names),
        "n_fine_states": len(labels),
        "n_partitions": len(records),
        "observed_minimum_changes": observed,
        "unconditional_null_mean": unconditional,
        "fine_organization_gap": denominator,
        "biological_partition": bio_record["partition"],
        "biological_capture_fraction": bio_record["capture_fraction"],
        "biological_rank": rank,
        "biological_percentile": percentile,
        "partitions": records,
    }


def summarize_radiation(radiation, settings):
    percentiles = np.asarray([x["biological_percentile"] for x in settings], dtype=float)
    captures = np.asarray([x["biological_capture_fraction"] for x in settings], dtype=float)
    med_p = float(np.median(percentiles))
    med_c = float(np.median(captures))
    if med_p <= 0.25 and med_c > 0:
        classification = "BIOLOGICAL_PARTITION_ENRICHED"
    elif med_p >= 0.50 or med_c <= 0:
        classification = "BIOLOGICAL_PARTITION_NOT_ENRICHED"
    else:
        classification = "INTERMEDIATE_PARTITION_SPECIFICITY"
    return {
        "radiation": radiation,
        "settings": len(settings),
        "biological_percentile_min_median_max": [float(percentiles.min()), med_p, float(percentiles.max())],
        "biological_capture_min_median_max": [float(captures.min()), med_c, float(captures.max())],
        "top_quartile_settings": int((percentiles <= 0.25).sum()),
        "positive_capture_settings": int((captures > 0).sum()),
        "classification": classification,
        "setting_results": settings,
    }


def run_linoideae(snapshot: Path):
    data = load_snapshot(snapshot)
    rows = {r["tip_id"]: r for r in data["rows"]}
    results = []
    labels = tuple(COLORS)
    biological = {"WHITE"}
    for tag, text in data["trees"].items():
        tree = rooted_ingroup(text)
        names = {tip.name for tip in tree.get_terminals()}
        groups = collections.defaultdict(list)
        for name in sorted(names):
            groups[" ".join(rows[name]["source_taxon"].split()[:2])].append(name)
        rng = np.random.default_rng(SEED)
        draws = [sorted(str(rng.choice(groups[g])) for g in sorted(groups)) for _ in range(3)]
        for policy in ("FIGURE2", "FIGURES5", "UNION"):
            mult = {}
            for name in names:
                if policy == "FIGURE2":
                    values = rows[name]["figure2_states"]
                elif policy == "FIGURES5":
                    values = rows[name]["figureS5_states"]
                else:
                    values = rows[name]["figure2_states"] + rows[name]["figureS5_states"]
                mult[name] = frozenset(values)
            for draw, chosen in enumerate(draws):
                for exclusion in ("NONE", "EXCLUDE_L_USITATISSIMUM"):
                    sample = [n for n in chosen if exclusion == "NONE" or n != LINO_CROP_TIP]
                    t = subset(tree, set(sample))
                    states = {n: mult[n] for n in sample}
                    sid = f"LINOIDEAE|{tag}|{policy}|draw{draw}|{exclusion}"
                    results.append(evaluate_setting(t, states, labels, biological, sid))
    if len(results) != 54:
        raise ValueError(f"expected 54 Linoideae settings, got {len(results)}")
    return summarize_radiation("LINOIDEAE", results)


def run_angraecinae(data_dir: Path):
    samples = list(csv.DictReader((data_dir / "source_sample_manifest.csv").open()))
    traitrows = list(csv.DictReader((data_dir / "terminal_organ_states.csv").open()))
    traits = {r["source_taxon"]: r for r in traitrows}
    full_ingroup = {r["tip_id"] for r in samples if r["source_group"] == "ANGRAECINAE"}
    mapped = {
        r["tip_id"]: traits[r["source_taxon"]]
        for r in samples
        if r["source_group"] == "ANGRAECINAE"
        and r["trait_join_status"] == "EXACT_UNIQUE"
        and r["source_taxon"] in traits
    }
    pattern_by_tip = {
        tip: tuple(row[o] for o in ANG_ORGANS)
        for tip, row in mapped.items()
        if all(row[o] in ANG_BINARY for o in ANG_ORGANS)
    }
    patterns = tuple(sorted(set(pattern_by_tip.values())))
    if len(patterns) != 5:
        raise ValueError(f"expected 5 Angraecinae joint patterns, got {patterns}")
    biological = {p for p in patterns if p[0] == "GREEN"}
    results = []
    for reconstruction in ("checkpoint_resume", "fresh_repeat"):
        for tag in ("plastid_full", "plastid50", "all4_full"):
            tree = Phylo.read(data_dir / "trees" / reconstruction / f"{tag}.treefile", "newick")
            t = extract_ingroup_and_prune(tree, full_ingroup, set(pattern_by_tip))
            states = {tip: frozenset({pattern_by_tip[tip]}) for tip in pattern_by_tip}
            sid = f"ANGRAECINAE|{reconstruction}|{tag}"
            results.append(evaluate_setting(t, states, patterns, biological, sid))
    if len(results) != 6:
        raise ValueError("expected 6 Angraecinae settings")
    return summarize_radiation("ANGRAECINAE", results)


def run_antirrhineae(source_dir: Path, source_manifest: Path):
    manifest = json.loads(source_manifest.read_text())
    if manifest["current_source_integrity_status"] != EXPECTED_INTEGRITY:
        raise ValueError("Antirrhineae source integrity status changed")
    if manifest["admitted_download"]["sha256"] != EXPECTED_SHA256:
        raise ValueError("Antirrhineae current source SHA256 changed")
    if manifest["historical_published_md5"] != HISTORICAL_MD5:
        raise ValueError("Antirrhineae historical MD5 contract changed")
    results = []
    for role, tree_name, phenotype_name in (
        ("MONOMORPHIC_PRIMARY", "monomorphic_snapdragons.tree", "mm_face_phenotypes.csv"),
        ("POLYMORPHIC_SENSITIVITY", "polymorphic_snapdragons.tree", "face_phenotypes.csv"),
    ):
        translate, tree_lines = parse_nexus_ensemble(source_dir / tree_name)
        source_states = read_states(source_dir / phenotype_name)
        tree_tips = set(translate.values())
        states = {tip: source_states[tip] for tip in tree_tips if tip in source_states}
        labels = tuple(sorted(set(states.values())))
        if labels != (0, 1, 2):
            raise ValueError(f"unexpected Antirrhineae fine alphabet {labels}")
        biological = {0}
        indices = np.linspace(0, len(tree_lines) - 1, 20, dtype=int).tolist()
        for tree_index in indices:
            tree = parse_tree_line(tree_lines[tree_index], translate)
            tree = prune_to(tree, set(states))
            allowed = {tip: frozenset({state}) for tip, state in states.items()}
            sid = f"ANTIRRHINEAE|{role}|tree{tree_index}"
            results.append(evaluate_setting(tree, allowed, labels, biological, sid))
    if len(results) != 40:
        raise ValueError("expected 40 Antirrhineae settings")
    return summarize_radiation("ANTIRRHINEAE", results)


def cross_classification(summaries):
    enriched = [x for x in summaries if x["classification"] == "BIOLOGICAL_PARTITION_ENRICHED"]
    not_enriched = [x for x in summaries if x["classification"] == "BIOLOGICAL_PARTITION_NOT_ENRICHED"]
    if len(enriched) >= 2 and len(not_enriched) == 0:
        status = "BOUNDARY_SPECIFICITY_SUPPORTED_ACROSS_SYSTEMS"
        consequence = "Retain and strengthen the coarse-state constraint wording; the biological boundaries capture unusually large shares of fine-state phylogenetic organization across systems."
    elif len(not_enriched) >= 2:
        status = "GENERIC_FINE_STATE_ORGANIZATION_MORE_LIKELY"
        consequence = "Drop the cross-system claim that the selected coarse boundaries are the shared constraining layer; retain only the 3/3 fine-state organization result."
    else:
        status = "MIXED_BOUNDARY_SPECIFICITY"
        consequence = "Retain the 3/3 residual fine-state result but soften the cross-system coarse-constraint interpretation because partition specificity is mixed."
    return {
        "status": status,
        "enriched_radiations": [x["radiation"] for x in enriched],
        "not_enriched_radiations": [x["radiation"] for x in not_enriched],
        "intermediate_radiations": [x["radiation"] for x in summaries if x["classification"] == "INTERMEDIATE_PARTITION_SPECIFICITY"],
        "claim_consequence": consequence,
    }


def compare(expected, actual, path="result"):
    if type(expected) is not type(actual):
        raise ValueError(f"{path}: type mismatch")
    if isinstance(expected, dict):
        if set(expected) != set(actual):
            raise ValueError(f"{path}: key mismatch")
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
    p.add_argument("--linoideae-snapshot", type=Path, default=Path("data/linoideae_source_reanalysis_v0_2/source_manifest.json"))
    p.add_argument("--angraecinae-data", type=Path, default=Path("data/angraecinae_source_reanalysis_v0_1"))
    p.add_argument("--antirrhineae-source", type=Path, required=True)
    p.add_argument("--antirrhineae-manifest", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--expected", type=Path)
    a = p.parse_args()
    summaries = [
        run_linoideae(a.linoideae_snapshot),
        run_angraecinae(a.angraecinae_data),
        run_antirrhineae(a.antirrhineae_source, a.antirrhineae_manifest),
    ]
    result = {
        "version": "v0.1",
        "status": "EXHAUSTIVE_ALTERNATIVE_PARTITION_CONTROL",
        "control_permutations_per_partition": CONTROL_PERMUTATIONS,
        "seed": SEED,
        "radiations": summaries,
        "cross_radiation": cross_classification(summaries),
        "existing_three_of_three_fine_state_replication_changed": False,
        "claim_boundary": "This control tests whether the biologically selected coarse partitions capture fine-state organization unusually strongly relative to exhaustive alternative bipartitions. It does not create additional biological replications or re-estimate transition directions, ecology, molecular mechanisms, or dated rates.",
        "paper1_science_changed": False,
    }
    if a.expected:
        compare(json.loads(a.expected.read_text()), result)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n")
    compact = {
        "cross_radiation": result["cross_radiation"],
        "radiations": [
            {
                "radiation": x["radiation"],
                "settings": x["settings"],
                "classification": x["classification"],
                "biological_percentile_min_median_max": x["biological_percentile_min_median_max"],
                "biological_capture_min_median_max": x["biological_capture_min_median_max"],
                "top_quartile_settings": x["top_quartile_settings"],
            }
            for x in summaries
        ],
    }
    print(json.dumps(compact, indent=2))


if __name__ == "__main__":
    main()
