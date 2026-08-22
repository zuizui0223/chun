#!/usr/bin/env python3
"""Audit whether current public micro-mechanistic evidence can test hierarchical reuse on robust macro W->A branches.

The macro branches are frozen before this join. Micro evidence is kept at three
levels: exact/strict node, resolved paralog subclass, and family/module. Extant
mechanism data inside a multi-tip descendant clade are reported but are not
promoted to the ancestral transition branch.
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


def species_from_scope(x: str):
    # Return all Camellia binomials found in a taxon_scope field.
    out=[]
    for part in re.split(r"[|;]", x or ""):
        p=part.strip().replace("C. ","Camellia ")
        tok=p.split()
        if len(tok)>=2 and tok[0]=="Camellia": out.append(" ".join(tok[:2]))
    return out


def branch_rows(crown):
    out=[];idx=0
    for parent in crown.find_clades(order="preorder"):
        for child in parent.clades:
            idx+=1
            desc=sorted(t.name for t in child.get_terminals() if t.name)
            sis=sorted(t.name for sib in parent.clades if sib is not child for t in sib.get_terminals() if t.name)
            out.append({"branch_id":f"B{idx:03d}","clade_hash":hashlib.sha1("|".join(desc).encode()).hexdigest()[:12],"descendant_tips":desc,"sister_tips":sis})
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--tree",type=Path,required=True)
    ap.add_argument("--transitions",type=Path,required=True)
    ap.add_argument("--mechanism-meta",type=Path,required=True)
    ap.add_argument("--node-crosswalk",type=Path,required=True)
    ap.add_argument("--feature-score",type=Path,required=True)
    ap.add_argument("--out-dir",type=Path,required=True)
    ap.add_argument("--outgroup",default="Polyspora speciosa")
    a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)

    tree=Phylo.read(str(a.tree),"newick"); crown=extract_camellia_crown(tree,a.outgroup)
    br={r["branch_id"]:r for r in branch_rows(crown)}
    tr={r["branch_id"]:r for r in rows(a.transitions)}
    if len(br)!=184 or len(tr)!=184: raise SystemExit("unexpected branch universe")
    strong=sorted(bid for bid,r in tr.items() if str(r.get("strong_robust_endpoint_transition","")).lower()=="true" and r.get("top_direction_by_mean")=="W_to_A")
    if strong!=["B011","B073","B083"]: raise SystemExit(f"unexpected robust set {strong}")

    meta=rows(a.mechanism_meta); cross=rows(a.node_crosswalk); score=rows(a.feature_score)
    cluster_taxa={}
    cluster_studies={}
    for r in meta:
        cl=r.get("independence_cluster","")
        if not cl: continue
        cluster_taxa.setdefault(cl,set()).update(species_from_scope(r.get("taxon_scope","")))
        cluster_studies.setdefault(cl,[]).append(r)
    cross_by_cluster={}
    for r in cross: cross_by_cluster.setdefault(r.get("independence_cluster",""),[]).append(r)

    detail=[]
    for bid in strong:
        b=br[bid]
        if tr[bid].get("clade_hash")!=b["clade_hash"]: raise SystemExit(f"branch identity mismatch {bid}")
        desc={norm_name(x) for x in b["descendant_tips"]}; sis={norm_name(x) for x in b["sister_tips"]}
        desc_clusters=[];sis_clusters=[]
        for cl,taxa in cluster_taxa.items():
            nt={norm_name(x) for x in taxa}
            if desc & nt: desc_clusters.append(cl)
            if sis & nt: sis_clusters.append(cl)
        terminal_assignable=len(b["descendant_tips"])==1 and bool(desc_clusters)
        feature_rows=[]
        for cl in desc_clusters:
            for r in cross_by_cluster.get(cl,[]):
                feature_rows.append({
                    "cluster":cl,"feature":r.get("feature"),"module":r.get("module"),
                    "strict_node_label":r.get("strict_node_label"),"orthology_status":r.get("orthology_status"),
                    "strict_crossspecies_recurrence_counted":r.get("strict_crossspecies_recurrence_counted"),
                })
        detail.append({
            "branch_id":bid,"n_descendant_tips":len(b["descendant_tips"]),
            "descendant_tips":";".join(b["descendant_tips"]),"sister_tips":";".join(b["sister_tips"]),
            "descendant_mechanism_clusters":";".join(sorted(desc_clusters)),
            "sister_mechanism_clusters":";".join(sorted(sis_clusters)),
            "terminal_transition_with_descendant_mechanism":terminal_assignable,
            "descendant_feature_evidence":json.dumps(feature_rows,sort_keys=True),
            "macro_mechanism_identifiability":"branch_assignable_extant_mechanism" if terminal_assignable else "public_data_unidentifiable",
            "gap_reason":(
                "mechanism studies exist only in one or more extant descendants of a multi-tip clade; they cannot identify the ancestral transition mechanism" if desc_clusters and len(b["descendant_tips"])>1
                else "no current public micro-mechanism independence cluster maps to the descendant transition taxon" if not desc_clusters
                else "terminal descendant mechanism exists, but independent macro transitions with comparable node-resolved evidence are still required for reuse enrichment"
            )
        })

    fields=list(detail[0])
    with (a.out_dir/"robust_W_to_A_micro_macro_coverage.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(detail)

    # Evaluate whether each molecular resolution level has >=2 independent,
    # branch-assignable macro transitions. This is the minimum needed even for
    # a descriptive recurrence/enrichment comparison.
    branch_assignable=[r for r in detail if r["terminal_transition_with_descendant_mechanism"]]
    assignable_features={}
    for r in branch_assignable:
        for x in json.loads(r["descendant_feature_evidence"]):
            assignable_features.setdefault(x["feature"],set()).add(r["branch_id"])

    strict_recurrent_features=[r for r in score if r.get("macro_test_level")=="ready_strict_node_level" and int(float(r.get("strict_node_predictor") or 0))>0]
    strict_macro={r["feature"]:sorted(assignable_features.get(r["feature"],set())) for r in strict_recurrent_features}
    resolved_contrast_features=[r for r in score if r.get("harmonized_rank_class")=="B_resolved_distinct_nodes"]
    resolved_macro={r["feature"]:sorted(assignable_features.get(r["feature"],set())) for r in resolved_contrast_features}
    module_ready=[r for r in score if str(r.get("macro_test_level","")).startswith("ready_")]
    module_macro={r["feature"]:sorted(assignable_features.get(r["feature"],set())) for r in module_ready}

    n_branch_assignable=len(branch_assignable)
    hierarchy_testable=(
        any(len(v)>=2 for v in strict_macro.values()) and
        any(len(v)>=2 for v in resolved_macro.values()) and
        n_branch_assignable>=2
    )
    status="testable_with_current_public_data" if hierarchy_testable else "public_data_unidentifiable"
    summary={
        "robust_W_to_A_branches":strong,
        "n_robust_branches":3,
        "n_branch_assignable_extant_mechanism":n_branch_assignable,
        "branch_assignable_ids":[r["branch_id"] for r in branch_assignable],
        "strict_same_node_macro_coverage":strict_macro,
        "resolved_different_node_macro_coverage":resolved_macro,
        "family_module_macro_coverage":module_macro,
        "H_hierarchical_reuse_macro_status":status,
        "H_hierarchical_reuse_macro_reason":(
            "multiple independent branch-assignable macro transitions are available at both strict-node and resolved-different-node levels" if hierarchy_testable
            else "current public micro evidence does not provide >=2 independent robust W->A branches with branch-assignable, paralog-resolved mechanisms; strict FLS recurrence is confined to micro systems outside the robust W->A branch set"
        ),
        "important_positive_link":"B083 is a robust terminal W->A transition to C. japonica and has a public C. japonica mechanism cluster with CsDFRa-like DFR plus CjMYB114/CjbHLH1 anchors. This is a branch-linked mechanistic case, not recurrence enrichment.",
        "B011_boundary":"C. reticulata ANS/ANR/UFGT evidence occurs inside the 24-tip descendant clade, but cannot be assigned to the basal B011 W->A event.",
        "B073_boundary":"no current public paralog-resolved colour-mechanism cluster maps to C. brevistyla.",
        "public_data_boundary":"the micro hierarchy is supported as molecular accessibility evidence, while its enrichment/reuse across independent macro transitions remains unidentifiable without matched branch-targeted molecular data",
        "empirical_or_new_data_needed":[
            "paralog-specific expression and pigment chemistry in C. brevistyla and its sister C. confusa",
            "paralog-specific expression/chemistry across C. albogigas(granthamiana) and phylogenetically informative B011 descendant representatives near the transition",
            "matched C. japonica vs C. szechuanensis expression/chemistry to turn B083 into a paired branch contrast",
            "sequence-resolved FLS/DFR/ANS/ANR copy identities under the same assay framework"
        ],
        "claim_ceiling":"do not claim macro hierarchical reuse enrichment; current evidence establishes micro accessibility plus one direct macro-linked C. japonica mechanism case"
    }
    (a.out_dir/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=="__main__": main()
