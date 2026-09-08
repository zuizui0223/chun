#!/usr/bin/env python3
"""Audit the prefrozen Nicotiana exact-TNRS/OpenTree admission layer; no colour signal is computed."""
from __future__ import annotations

import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import requests
from Bio import Phylo

BASE = Path("analysis/_generated/nicotiana_source_v1")
TRAITS = BASE / "trait_audit.json"
OUT = Path("analysis/_generated/nicotiana_opentree_v1")
OT_API = "https://api.opentreeoflife.org/v3"
UA = "chun-nicotiana-falsification/1.0"


def post(path: str, payload: dict):
    r = requests.post(f"{OT_API}/{path}", json=payload, headers={"User-Agent": UA}, timeout=120)
    r.raise_for_status()
    return r.json()


def tnrs(names: list[str]):
    data = post("tnrs/match_names", {
        "names": names,
        "do_approximate_matching": False,
        "include_suppressed": False,
    })
    results = data.get("results", [])
    if len(results) != len(names):
        raise SystemExit(f"TNRS returned {len(results)} results for {len(names)} queries")
    out = []
    for query, result in zip(names, results):
        matches = result.get("matches", [])
        exact = [
            m for m in matches
            if float(m.get("score", 1.0)) >= 0.999999
            and not bool(m.get("is_approximate_match", False))
        ]
        if len(exact) == 1:
            m = exact[0]
            tx = m.get("taxon", {})
            out.append({
                "query": query,
                "ott_id": tx.get("ott_id"),
                "matched_name": tx.get("name", ""),
                "is_synonym": bool(m.get("is_synonym", False)),
                "score": float(m.get("score", 1.0)),
                "status": "EXACT",
            })
        else:
            out.append({
                "query": query,
                "ott_id": None,
                "matched_name": "",
                "is_synonym": None,
                "score": None,
                "status": f"REJECT_{len(exact)}_EXACT_MATCHES",
                "candidate_exact_matches": [
                    {
                        "matched_name": m.get("taxon", {}).get("name", ""),
                        "ott_id": m.get("taxon", {}).get("ott_id"),
                        "is_synonym": bool(m.get("is_synonym", False)),
                        "score": float(m.get("score", 1.0)),
                    }
                    for m in exact
                ],
            })
    return out


def main():
    if not TRAITS.exists():
        raise SystemExit(f"trait audit missing: {TRAITS}")
    data = json.loads(TRAITS.read_text(encoding="utf-8"))
    summary = data["summary"]
    checks = summary.get("pre_tree_admission_checks", {})
    if not checks or not all(checks.values()):
        raise SystemExit(f"trait pre-tree gate not passed: {checks}")
    taxa = summary.get("eligible_taxa", [])
    names = [x["taxon"] for x in taxa]
    if len(names) != len(set(names)) or len(names) < 20:
        raise SystemExit(f"eligible taxon identity/count failure: n={len(names)} unique={len(set(names))}")

    matches = tnrs(names)
    by_ott = defaultdict(list)
    for row in matches:
        if row["status"] == "EXACT" and row["ott_id"] is not None:
            by_ott[int(row["ott_id"])].append(row)
    collisions = {oid: rs for oid, rs in by_ott.items() if len(rs) > 1}
    collision_queries = {r["query"] for rs in collisions.values() for r in rs}
    for row in matches:
        if row["query"] in collision_queries:
            row["status"] = "REJECT_OTT_COLLISION"

    rejected = [
        {
            "query": r["query"],
            "status": r["status"],
            "candidate_exact_matches": r.get("candidate_exact_matches", []),
        }
        for r in matches if r["status"] != "EXACT"
    ]

    admitted = [r for r in matches if r["status"] == "EXACT" and r["ott_id"] is not None]
    ids = sorted(int(r["ott_id"]) for r in admitted)
    ott_to_query = {int(r["ott_id"]): r["query"] for r in admitted}
    if not ids:
        raise SystemExit("no exact one-to-one OpenTree taxa admitted")

    sub = post("tree_of_life/induced_subtree", {"ott_ids": ids, "label_format": "id"})
    nwk = sub.get("newick", "")
    if not nwk:
        raise SystemExit("OpenTree returned empty induced subtree")
    tree = Phylo.read(io.StringIO(nwk), "newick")
    tree_ott = []
    for tip in tree.get_terminals():
        label = str(tip.name).strip("'")
        m = re.search(r"(?:ott)?(\d+)$", label)
        if m:
            tree_ott.append(int(m.group(1)))
    tree_ott_set = set(tree_ott)
    admitted_set = set(ids)
    overlap_ids = admitted_set & tree_ott_set
    coverage = len(overlap_ids) / len(names)

    for tip in tree.get_terminals():
        label = str(tip.name).strip("'")
        m = re.search(r"(?:ott)?(\d+)$", label)
        if m:
            oid = int(m.group(1))
            if oid in ott_to_query:
                tip.name = ott_to_query[oid]
    labeled_names = [t.name for t in tree.get_terminals()]
    if len(labeled_names) != len(set(labeled_names)):
        raise SystemExit("duplicate terminal labels after source-name restoration")

    OUT.mkdir(parents=True, exist_ok=True)
    Phylo.write(tree, OUT / "opentree_source_taxa.nwk", "newick")
    (OUT / "opentree_induced_raw.nwk").write_text(nwk + "\n", encoding="utf-8")
    (OUT / "tnrs_matches.json").write_text(json.dumps(matches, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    result = {
        "source_doi": "10.1093/aob/mcv048",
        "eligible_trait_taxa": len(names),
        "tnrs_status_counts": dict(Counter(r["status"] for r in matches)),
        "rejected_queries": rejected,
        "n_ott_collision_groups": len(collisions),
        "ott_collision_groups": {
            str(oid): [
                {"query": r["query"], "matched_name": r.get("matched_name", "")}
                for r in rs
            ]
            for oid, rs in collisions.items()
        },
        "n_admitted_unique_ott": len(ids),
        "n_tree_overlap": len(overlap_ids),
        "coverage_fraction_of_eligible": coverage,
        "frozen_coverage_gate_80pct": coverage >= 0.80,
        "frozen_minimum_n_20_gate": len(overlap_ids) >= 20,
        "missing_admitted_ott_ids_from_tree": sorted(admitted_set - tree_ott_set),
        "unexpected_tree_ott_ids": sorted(tree_ott_set - admitted_set),
        "source_machine_readable_tree_status": "NOT_RECOVERED_FROM_SUPPLEMENT; FIG_S6_ONLY_AS_DOCUMENT_FIGURE",
        "synth_id": sub.get("synth_id", ""),
        "endpoint_allowed": coverage >= 0.80 and len(overlap_ids) >= 20,
    }
    (OUT / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("NICOTIANA_OPENTREE_AUDIT=" + json.dumps(result, ensure_ascii=False))
    if not result["endpoint_allowed"]:
        raise SystemExit("OpenTree observation-regime gate failed; endpoint must remain HOLD")


if __name__ == "__main__":
    main()
