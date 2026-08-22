#!/usr/bin/env python3
"""Audit whether public pollination-service evidence can identify causes of robust W->A branches.

This is an identifiability gate, not a null-hypothesis test. It distinguishes:
- direct reproductive-service evidence (exclusion, controlled pollination,
  pollen-flow/effectiveness linked to reproductive output),
- environmental/seasonal modulation of service,
- indirect floral sensory/reward traits,
- no directly comparable service evidence recovered.

A rooted branch is considered publicly service-comparable only when direct
service-quality evidence exists on both the descendant and local-sister sides.
For a multi-tip descendant clade, evidence in one extant descendant is reported
but is not treated as proof of the ancestral branch state.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

from Bio import Phylo

from analyze_rooted_camellia_colour_history import extract_camellia_crown, norm_name


def rows(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def truth(x):
    return str(x or "").strip().lower() in {"yes", "true", "1", "direct"}


def direct_from_meta(r):
    t=(r.get("primary_evidence_type") or "").lower()
    # Keep this conservative: pure behavioural/spectral evidence is not enough.
    return any(k in t for k in ("exclusion", "pollen_flow", "field_pollination", "insect_efficiency"))


def build_evidence(meta_path: Path, supplement_path: Path):
    ev={}
    for r in rows(meta_path):
        k=norm_name(r.get("taxon"))
        if not k: continue
        ev.setdefault(k,[]).append({
            "taxon":r.get("taxon",""),
            "direct_service":direct_from_meta(r),
            "environment_modulation":(r.get("environmental_or_seasonal_modulation") or "").strip() not in {"", "not_tested", "none"},
            "sensory_reward":(r.get("spectral_or_sensory_evidence") or "").strip() not in {"", "none_in_this_source", "none"},
            "evidence_type":r.get("primary_evidence_type",""),
            "key_result":r.get("key_result",""),
            "source":r.get("source_doi_or_citation",""),
            "claim_ceiling":r.get("claim_ceiling",""),
            "source_table":"camellia_pollination_function_meta_v0_3.csv",
        })
    for r in rows(supplement_path):
        k=norm_name(r.get("taxon"))
        if not k: continue
        ev.setdefault(k,[]).append({
            "taxon":r.get("taxon",""),
            "direct_service":truth(r.get("direct_service_quality")),
            "environment_modulation":(r.get("environment_or_season_modulation") or "").strip() not in {"", "not_tested", "none"},
            "sensory_reward":(r.get("reward_or_sensory_trait") or "").strip() not in {"", "none", "not_tested"},
            "evidence_type":r.get("evidence_type",""),
            "key_result":r.get("key_result",""),
            "source":r.get("source",""),
            "claim_ceiling":r.get("claim_ceiling",""),
            "source_table":supplement_path.name,
        })
    return ev


def branch_rows(crown):
    out=[]; idx=0
    for parent in crown.find_clades(order="preorder"):
        for child in parent.clades:
            idx+=1
            desc=sorted(t.name for t in child.get_terminals() if t.name)
            sis=sorted(t.name for sib in parent.clades if sib is not child for t in sib.get_terminals() if t.name)
            out.append({
                "branch_id":f"B{idx:03d}",
                "clade_hash":hashlib.sha1("|".join(desc).encode()).hexdigest()[:12],
                "descendant_tips":desc,
                "sister_tips":sis,
            })
    return out


def summarize_side(tips, evidence):
    records=[]
    for tip in tips:
        records.extend(evidence.get(norm_name(tip),[]))
    direct=sorted({r["taxon"] for r in records if r["direct_service"]})
    mod=sorted({r["taxon"] for r in records if r["environment_modulation"]})
    traits=sorted({r["taxon"] for r in records if r["sensory_reward"]})
    anytax=sorted({r["taxon"] for r in records})
    return {
        "n_tips":len(tips),
        "n_tips_with_any_recovered_evidence":len(anytax),
        "taxa_with_any_recovered_evidence":";".join(anytax),
        "direct_service_taxa":";".join(direct),
        "environment_modulation_taxa":";".join(mod),
        "sensory_reward_taxa":";".join(traits),
        "has_direct_service":bool(direct),
        "has_environment_modulation":bool(mod),
        "has_sensory_reward":bool(traits),
        "evidence_records":records,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--tree",type=Path,required=True)
    ap.add_argument("--transitions",type=Path,required=True)
    ap.add_argument("--meta",type=Path,required=True)
    ap.add_argument("--supplement",type=Path,required=True)
    ap.add_argument("--out-dir",type=Path,required=True)
    ap.add_argument("--outgroup",default="Polyspora speciosa")
    a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)

    tree=Phylo.read(str(a.tree),"newick")
    crown=extract_camellia_crown(tree,a.outgroup)
    br={r["branch_id"]:r for r in branch_rows(crown)}
    tr={r["branch_id"]:r for r in rows(a.transitions)}
    ev=build_evidence(a.meta,a.supplement)
    if len(br)!=184 or len(tr)!=184: raise SystemExit(f"unexpected branch counts tree={len(br)} transitions={len(tr)}")

    strong=[]
    for bid,r in tr.items():
        if str(r.get("strong_robust_endpoint_transition","")).lower()=="true" and r.get("top_direction_by_mean")=="W_to_A":
            strong.append(bid)
    if sorted(strong)!=["B011","B073","B083"]:
        raise SystemExit(f"unexpected robust W->A set {strong}")

    out=[]
    for bid in sorted(strong):
        b=br[bid]
        if tr[bid].get("clade_hash")!=b["clade_hash"]: raise SystemExit(f"branch identity mismatch {bid}")
        d=summarize_side(b["descendant_tips"],ev);s=summarize_side(b["sister_tips"],ev)
        paired=d["has_direct_service"] and s["has_direct_service"]
        # Evidence in a multi-tip descendant clade is useful for taxon targeting,
        # but cannot by itself be promoted to the ancestral branch state.
        ancestral_descendant_assignable=d["has_direct_service"] and len(b["descendant_tips"])==1
        row={
            "branch_id":bid,
            "n_descendant_tips":len(b["descendant_tips"]),
            "descendant_tips":";".join(b["descendant_tips"]),
            "sister_tips":";".join(b["sister_tips"]),
            "descendant_direct_service_taxa":d["direct_service_taxa"],
            "sister_direct_service_taxa":s["direct_service_taxa"],
            "descendant_environment_modulation_taxa":d["environment_modulation_taxa"],
            "sister_environment_modulation_taxa":s["environment_modulation_taxa"],
            "descendant_sensory_reward_taxa":d["sensory_reward_taxa"],
            "sister_sensory_reward_taxa":s["sensory_reward_taxa"],
            "direct_service_on_both_sides":paired,
            "descendant_direct_service_assignable_to_terminal_transition":ancestral_descendant_assignable,
            "branch_service_identifiability":"paired_public_service_comparison" if paired and ancestral_descendant_assignable else "public_data_unidentifiable",
            "gap_reason":(
                "direct service evidence missing on local sister side" if d["has_direct_service"] and not s["has_direct_service"]
                else "direct service evidence missing on descendant transition side" if s["has_direct_service"] and not d["has_direct_service"]
                else "direct service evidence absent on both branch sides" if not d["has_direct_service"] and not s["has_direct_service"]
                else "descendant direct service exists only within a multi-tip clade and cannot be assigned to the ancestral transition branch"
            ),
        }
        out.append(row)

    fields=list(out[0])
    with (a.out_dir/"robust_W_to_A_pollination_service_coverage.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    with (a.out_dir/"evidence_records.json").open("w",encoding="utf-8") as f:
        json.dump(ev,f,indent=2,ensure_ascii=False)

    npaired=sum(r["branch_service_identifiability"]=="paired_public_service_comparison" for r in out)
    if npaired>=2:
        status="testable_with_current_public_data"
        reason="at least two independent robust W->A transitions have paired direct service evidence"
    else:
        status="public_data_unidentifiable"
        reason=f"only {npaired}/3 robust W->A branches have paired, branch-assignable direct pollination-service evidence"
    priorities=[]
    for r in out:
        if r["branch_service_identifiability"]=="public_data_unidentifiable":
            priorities.append({
                "branch_id":r["branch_id"],
                "needed":"matched descendant-vs-sister pollination-service measurements under one protocol",
                "measure":["guild visitation","single-visit stigma pollen deposition","pollen removal","bird/insect exclusion","fruit and seed set","flowering-window weather","nectar volume and sugar composition","UV/visible spectrum"],
                "current_gap":r["gap_reason"],
            })
    summary={
        "robust_W_to_A_branches":sorted(strong),
        "n_robust_branches":3,
        "n_branches_with_paired_branch_assignable_direct_service":npaired,
        "H_pollination_service_branch_status":status,
        "H_pollination_service_branch_reason":reason,
        "important_positive_public_evidence":{
            "B011":"C. reticulata within the descendant clade has controlled evidence for insect-mediated fruit set, but this does not reconstruct the B011 ancestral state and C. albogigas/granthamiana lacks a comparable service experiment",
            "B073":"C. brevistyla has floral scent/pseudopollen evidence but no recovered direct service-quality comparison; C. confusa likewise lacks direct service evidence",
            "B083":"C. japonica has strong bird-function, pollen-flow and sensory evidence; C. szechuanensis lacks a comparable service-quality study",
        },
        "public_data_boundary":"current published studies can motivate pollination-service hypotheses but cannot estimate a phylogenetically independent branch-level causal effect across the three robust W->A events",
        "empirical_priority":priorities,
        "claim_ceiling":"coverage/identifiability audit only; no absence-of-effect inference and no causal rejection of pollination-service filtering",
    }
    (a.out_dir/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=="__main__": main()
