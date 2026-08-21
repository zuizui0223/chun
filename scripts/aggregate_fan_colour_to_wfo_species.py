#!/usr/bin/env python3
"""Aggregate held-out Fan A/W/Y labels onto the frozen WFO 2026-06 species map.

This is a trait-quality gate, not an ancestral-state analysis. Historical tree
individuals that map to one accepted species are combined before any colour
history is refit. If more than one A/W/Y state occurs within an accepted species,
the accepted species is explicitly marked conflicting/polymorphic and receives
no hard state.

Absence of a conflict here does not prove wild colour monomorphism; it only says
the existing Fan/tree legacy labels do not conflict after taxonomic collapse.
"""
from __future__ import annotations
import argparse,csv,json,re
from collections import defaultdict
from pathlib import Path

STATES={"A","W","Y"}

def key(x): return re.sub(r"\s+"," ",(x or "").strip().replace("_"," ")).casefold()
def rows(p):
    with p.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--taxonomy",type=Path,required=True);ap.add_argument("--colour",type=Path,required=True);ap.add_argument("--out-dir",type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    tax=rows(a.taxonomy); colrows=rows(a.colour)
    if len(tax)!=94:raise SystemExit(f"expected 94 taxonomy rows, got {len(tax)}")
    col={}
    for r in colrows:
        n=key(r.get("taxon")); s=(r.get("colour_state") or "").strip()
        if not n or s not in STATES:continue
        if n in col and col[n]!=s:raise SystemExit(f"conflicting input Fan labels for {n}: {col[n]} vs {s}")
        col[n]=s

    groups=defaultdict(list)
    for r in tax:
        accepted=(r.get("accepted_species") or "").strip()
        if not accepted:raise SystemExit(f"taxonomy row missing accepted_species: {r}")
        groups[accepted].append(r)
    if len(groups)!=56:raise SystemExit(f"expected 56 accepted groups including Polyspora, got {len(groups)}")

    out=[]; evidence=[]
    for accepted,members in sorted(groups.items()):
        if accepted=="Polyspora speciosa":continue
        obs=[]
        for r in members:
            legacy=(r.get("legacy_name") or "").strip()
            s=col.get(key(legacy),"")
            evidence.append({
                "accepted_species":accepted,
                "tree_tip":r.get("tree_tip",""),
                "legacy_name":legacy,
                "fan_colour_state":s,
                "taxonomy_resolution_method":r.get("resolution_method",""),
            })
            if s:obs.append((legacy,s))
        unique=sorted({s for _,s in obs})
        if len(unique)==0:
            status="unobserved"; hard=""
        elif len(unique)==1:
            status=f"single_state_{unique[0]}";hard=unique[0]
        else:
            status="conflicting_"+"".join(unique);hard=""
        out.append({
            "accepted_species":accepted,
            "n_legacy_tree_tips":len(members),
            "n_fan_observed_legacy_tips":len(obs),
            "fan_states_observed":";".join(unique),
            "fan_aggregation_status":status,
            "hard_state_for_next_gate":hard,
            "observed_legacy_labels":";".join(f"{n}:{s}" for n,s in sorted(obs)),
            "legacy_tree_tips":";".join(sorted(r.get("tree_tip","") for r in members)),
        })

    counts=defaultdict(int)
    for r in out:counts[r["fan_aggregation_status"]]+=1
    hard=[r for r in out if r["hard_state_for_next_gate"]]
    conflict=[r for r in out if r["fan_aggregation_status"].startswith("conflicting_")]
    summary={
        "taxonomy_backbone":"WFO Plant List 2026-06",
        "n_accepted_camellia_species":len(out),
        "n_with_any_fan_colour":sum(r["n_fan_observed_legacy_tips"]>0 for r in out),
        "n_hard_single_state_after_taxonomy":len(hard),
        "hard_state_counts":{s:sum(r["hard_state_for_next_gate"]==s for r in out) for s in sorted(STATES)},
        "n_taxonomy_induced_conflicts":len(conflict),
        "conflicting_species":[{"accepted_species":r["accepted_species"],"states":r["fan_states_observed"],"evidence":r["observed_legacy_labels"]} for r in conflict],
        "status_counts":dict(sorted(counts.items())),
        "claim_ceiling":"taxonomy-normalized aggregation of existing Fan hard labels only; single-state status does not establish wild monomorphism and no evolutionary inference is made"
    }
    with (a.out_dir/"wfo55_fan_colour_aggregation.csv").open("w",newline="",encoding="utf-8") as f:w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    with (a.out_dir/"legacy_colour_taxonomy_evidence.csv").open("w",newline="",encoding="utf-8") as f:w=csv.DictWriter(f,fieldnames=list(evidence[0]));w.writeheader();w.writerows(evidence)
    (a.out_dir/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
