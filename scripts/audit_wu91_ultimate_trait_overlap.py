#!/usr/bin/env python3
"""Audit which ecological/phenotypic layers can be joined to the frozen Wu runtime91 backbone.

This is an input-coverage gate only. It does not infer ancestral states, fit causal
models, or alter the independently reconstructed nuclear topology. The purpose is
to separate analyses that are already estimable on the runtime91 tree from those
that require targeted taxon expansion.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def by_taxon(rows: list[dict[str, str]], key: str = "taxon") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for r in rows:
        t = (r.get(key) or "").strip()
        if not t:
            continue
        if t in out:
            raise SystemExit(f"duplicate exact taxon in {key} table: {t}")
        out[t] = r
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", type=Path, required=True)
    ap.add_argument("--fan-colour", type=Path, required=True)
    ap.add_argument("--climate", type=Path, required=True)
    ap.add_argument("--pollinator", type=Path, required=True)
    ap.add_argument("--latent", type=Path, required=True)
    ap.add_argument("--macro-priority", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args()

    panel = read_csv(a.panel)
    if len(panel) != 91:
        raise SystemExit(f"expected frozen runtime91 panel, got {len(panel)}")
    tree_taxa = [r["taxon"].strip() for r in panel]
    if len(set(tree_taxa)) != 91:
        raise SystemExit("runtime91 panel contains duplicate taxa")
    tree = set(tree_taxa)

    fan = by_taxon(read_csv(a.fan_colour))
    climate = by_taxon(read_csv(a.climate))
    poll = by_taxon(read_csv(a.pollinator))
    latent = by_taxon(read_csv(a.latent))
    macro = by_taxon(read_csv(a.macro_priority))

    rows: list[dict[str, object]] = []
    for t in sorted(tree):
        f = fan.get(t, {})
        c = climate.get(t, {})
        p = poll.get(t, {})
        l = latent.get(t, {})
        m = macro.get(t, {})
        rows.append({
            "taxon": t,
            "visible_colour_available": bool(f),
            "visible_state": f.get("colour_state", ""),
            "climate_available": bool(c),
            "bio1_median": c.get("bio1_median", ""),
            "bio6_median": c.get("bio6_median", ""),
            "bio1_iqr": c.get("bio1_iqr", ""),
            "pollinator_available": bool(p),
            "pollinator_function_class": p.get("pollinator_function_class", ""),
            "latent_state_available": bool(l),
            "anthocyanin_axis": l.get("anthocyanin_axis", ""),
            "flavonol_axis": l.get("flavonol_axis", ""),
            "uv_fluorescence_signal": l.get("uv_fluorescence_signal", ""),
            "macro_priority_available": bool(m),
        })

    fan_overlap = tree & set(fan)
    climate_overlap = tree & set(climate)
    poll_overlap = tree & set(poll)
    latent_overlap = tree & set(latent)
    macro_overlap = tree & set(macro)
    colour_climate_overlap = tree & set(fan) & set(climate)

    fan_state_counts: dict[str, int] = {}
    for t in fan_overlap:
        s = fan[t].get("colour_state", "")
        fan_state_counts[s] = fan_state_counts.get(s, 0) + 1

    priority_union = set(poll) | set(latent) | set(macro)
    extension = []
    for t in sorted(priority_union - tree):
        extension.append({
            "taxon": t,
            "has_pollinator_evidence": t in poll,
            "has_latent_state": t in latent,
            "has_macro_niche_priority": t in macro,
            "visible_state_from_pollinator": poll.get(t, {}).get("visible_state", ""),
            "visible_state_from_latent": latent.get(t, {}).get("visible_state", ""),
            "priority_reason": ";".join(
                x for x, ok in [
                    ("pollinator", t in poll),
                    ("latent", t in latent),
                    ("macro_niche", t in macro),
                ] if ok
            ),
        })

    a.out_dir.mkdir(parents=True, exist_ok=True)
    overlap_path = a.out_dir / "runtime91_trait_overlap.csv"
    with overlap_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

    ext_path = a.out_dir / "priority_tree_extension.csv"
    ext_fields = [
        "taxon", "has_pollinator_evidence", "has_latent_state",
        "has_macro_niche_priority", "visible_state_from_pollinator",
        "visible_state_from_latent", "priority_reason",
    ]
    with ext_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ext_fields)
        w.writeheader(); w.writerows(extension)

    summary = {
        "n_tree_taxa": len(tree),
        "n_visible_colour_overlap": len(fan_overlap),
        "visible_colour_states_on_tree": dict(sorted(fan_state_counts.items())),
        "n_climate_overlap": len(climate_overlap),
        "n_visible_colour_and_climate_overlap": len(colour_climate_overlap),
        "n_pollinator_overlap": len(poll_overlap),
        "pollinator_overlap_taxa": sorted(poll_overlap),
        "n_latent_state_overlap": len(latent_overlap),
        "latent_state_overlap_taxa": sorted(latent_overlap),
        "n_macro_niche_priority_overlap": len(macro_overlap),
        "macro_niche_priority_overlap_taxa": sorted(macro_overlap),
        "n_priority_taxa_missing_from_tree": len(extension),
        "priority_taxa_missing_from_tree": [r["taxon"] for r in extension],
        "analysis_decision": {
            "visible_colour_history": "eligible_on_current_tree_if_state counts provide repeated transitions",
            "colour_climate_branch_screen": "eligible on exact overlapping taxa; use provenance-clean central climate metrics as primary",
            "pollinator_branch_order": "not estimable as a genus-level causal test from current runtime91 overlap; targeted tree expansion required",
            "latent_selection_target": "not estimable as a genus-level causal test from current runtime91 overlap; targeted tree expansion required",
        },
        "claim_ceiling": "trait-coverage and taxon-overlap gate only; no ancestral-state, adaptation, pollinator-causation, or climate-causation inference",
    }
    (a.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
