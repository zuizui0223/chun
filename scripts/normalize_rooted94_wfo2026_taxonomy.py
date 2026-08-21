#!/usr/bin/env python3
"""Normalize frozen rooted94 tip names to the WFO Plant List 2026-06 backbone.

The nuclear tree is read only. Each legacy tip is looked up by the live WFO
Plant List GraphQL service while the normative release is 2026-06, and the
raw response plus resolved mapping are frozen as workflow artifacts.

No fuzzy resolution is silently accepted. A legacy binomial must resolve to
one accepted species-level group across all matched name records or the script
marks it unresolved/ambiguous and the CI gate fails.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import time
from collections import defaultdict
from pathlib import Path

import requests
from Bio import Phylo

API = "https://list.worldfloraonline.org/gql"
RELEASE = "2026-06"
RELEASE_DOI = "10.5281/zenodo.20782718"
QUERY = r'''
query NameSearch($terms: String!){
  taxonNameSuggestion(termsString: $terms, limit: 100) {
    id
    stableUri
    fullNameStringPlain
    currentPreferredUsage {
      id
      stableUri
      hasName { id stableUri fullNameStringPlain }
    }
  }
}
'''


def norm_space(x: str | None) -> str:
    return re.sub(r"\s+", " ", (x or "").strip())


def tip_to_name(x: str) -> str:
    return norm_space(x.replace("_", " "))


def binomial_from_full_name(x: str | None) -> str:
    # WFO fullNameStringPlain starts with genus + specific epithet; author and
    # infraspecific material follow. Our input universe is Camellia/Polyspora.
    toks = norm_space(x).replace("× ", "").split()
    if len(toks) < 2:
        return ""
    return f"{toks[0]} {toks[1]}"


def candidate_matches_legacy(candidate: dict, legacy: str) -> bool:
    return binomial_from_full_name(candidate.get("fullNameStringPlain")) == legacy


def resolve_name(session: requests.Session, legacy: str) -> tuple[dict, dict]:
    response = session.post(
        API,
        json={"query": QUERY, "variables": {"terms": legacy}},
        timeout=60,
        headers={"User-Agent": "chun-camellia-taxonomy-audit/1.0"},
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("errors"):
        raise RuntimeError(f"WFO GraphQL errors for {legacy}: {payload['errors']}")
    suggestions = (payload.get("data") or {}).get("taxonNameSuggestion") or []
    exact = [x for x in suggestions if candidate_matches_legacy(x, legacy)]
    resolved = []
    for x in exact:
        usage = x.get("currentPreferredUsage")
        name = (usage or {}).get("hasName") or {}
        accepted_full = norm_space(name.get("fullNameStringPlain"))
        accepted_species = binomial_from_full_name(accepted_full)
        if usage and accepted_species:
            resolved.append((accepted_species, x, accepted_full))
    groups = sorted({x[0] for x in resolved})
    status = "resolved" if len(groups) == 1 else ("unresolved" if not groups else "ambiguous")
    chosen = None
    if status == "resolved":
        same = [x for x in resolved if x[0] == groups[0]]
        # Prefer an accepted-name record if it is present; otherwise stable ID.
        same.sort(key=lambda z: (
            0 if z[1].get("id") == ((z[1].get("currentPreferredUsage") or {}).get("hasName") or {}).get("id") else 1,
            z[1].get("id") or "",
        ))
        chosen = same[0]
    out = {
        "legacy_name": legacy,
        "match_status": status,
        "n_suggestions": len(suggestions),
        "n_exact_binomial_records": len(exact),
        "n_resolved_exact_records": len(resolved),
        "accepted_species_candidates": ";".join(groups),
        "matched_wfo_id": chosen[1].get("id", "") if chosen else "",
        "matched_name": norm_space(chosen[1].get("fullNameStringPlain")) if chosen else "",
        "accepted_name_full": chosen[2] if chosen else "",
        "accepted_species": chosen[0] if chosen else "",
        "accepted_wfo_id": (((chosen[1].get("currentPreferredUsage") or {}).get("hasName") or {}).get("id", "") if chosen else ""),
        "accepted_stable_uri": (((chosen[1].get("currentPreferredUsage") or {}).get("hasName") or {}).get("stableUri", "") if chosen else ""),
        "input_is_current_accepted_name_record": bool(chosen and chosen[1].get("id") == ((chosen[1].get("currentPreferredUsage") or {}).get("hasName") or {}).get("id")),
    }
    return out, {"legacy_name": legacy, "api_payload": payload}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--sleep", type=float, default=0.05)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    tree = Phylo.read(str(args.tree), "newick")
    tips = sorted(t.name for t in tree.get_terminals() if t.name)
    if len(tips) != 94:
        raise SystemExit(f"expected 94 rooted tips, got {len(tips)}")
    legacy_names = [tip_to_name(x) for x in tips]
    if len(set(legacy_names)) != 94:
        raise SystemExit("duplicate normalized rooted tip names")

    session = requests.Session()
    rows, raw = [], []
    for i, legacy in enumerate(legacy_names, 1):
        row, payload = resolve_name(session, legacy)
        row["tree_tip"] = tips[i - 1]
        row["backbone"] = f"WFO Plant List {RELEASE}"
        row["release_doi"] = RELEASE_DOI
        rows.append(row)
        raw.append(payload)
        print(i, legacy, row["match_status"], "=>", row["accepted_species"])
        time.sleep(args.sleep)

    unresolved = [r for r in rows if r["match_status"] != "resolved"]
    cam = [r for r in rows if r["legacy_name"].startswith("Camellia ")]
    poly = [r for r in rows if r["legacy_name"] == "Polyspora speciosa"]
    if len(cam) != 93 or len(poly) != 1:
        raise SystemExit(f"unexpected genus composition: Camellia={len(cam)} Polyspora={len(poly)}")

    groups = defaultdict(list)
    for r in rows:
        if r["accepted_species"]:
            groups[r["accepted_species"]].append(r["tree_tip"])
    duplicates = {k: sorted(v) for k, v in groups.items() if len(v) > 1}

    fields = list(rows[0].keys())
    with (args.out_dir / "wfo2026_06_taxonomy_registry.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    (args.out_dir / "wfo2026_06_raw_responses.json").write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")

    # ASTRAL multiple-individual mapping: one line per legacy gene-tree tip.
    with (args.out_dir / "astral_species_mapping.tsv").open("w", encoding="utf-8") as f:
        for r in rows:
            accepted_tip = r["accepted_species"].replace(" ", "_")
            f.write(f"{r['tree_tip']} {accepted_tip}\n")

    duplicate_rows = []
    for accepted, members in sorted(duplicates.items()):
        duplicate_rows.append({"accepted_species": accepted, "n_legacy_tips": len(members), "legacy_tips": ";".join(members)})
    with (args.out_dir / "duplicate_accepted_species_groups.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["accepted_species", "n_legacy_tips", "legacy_tips"]); w.writeheader(); w.writerows(duplicate_rows)

    summary = {
        "backbone": f"WFO Plant List {RELEASE}",
        "release_doi": RELEASE_DOI,
        "n_tree_tips": len(rows),
        "n_camellia_legacy_tips": len(cam),
        "n_unresolved_or_ambiguous": len(unresolved),
        "unresolved_or_ambiguous": [r["legacy_name"] for r in unresolved],
        "n_accepted_species_groups_all": len(groups),
        "n_accepted_camellia_species_groups": len({r["accepted_species"] for r in cam if r["accepted_species"]}),
        "n_duplicate_accepted_species_groups": len(duplicates),
        "duplicate_groups": duplicates,
        "claim_ceiling": "taxonomic mapping gate only; no topology collapse, colour-state transfer, or evolutionary interpretation",
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if unresolved:
        raise SystemExit(f"WFO normalization unresolved/ambiguous for {len(unresolved)} names")


if __name__ == "__main__":
    main()
