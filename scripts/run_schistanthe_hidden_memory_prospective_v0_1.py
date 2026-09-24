#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from Bio import Phylo
from scipy.stats import rankdata

COLOR_SHA="266045976d6d0b78a74bcf43c90a30a9e52848d0f25cc4a3b96997b080581e4e"
TREE_SHA="41bc04cdc63032086485c1ce6daf6dedc72fe582e142f7970b72d3143056390b"
PERMUTATIONS=9999
SEED=20260920
FINE_MIN=5
MIN_TIPS=20


def sha256_file(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_color(x:str)->str:
    return " ".join(str(x or "").strip().lower().split())


def coarse_color(x:str)->str:
    return "WHITE" if x=="white" else "NONWHITE"


def same_coarse_pair_indices(coarse:np.ndarray)->tuple[np.ndarray,np.ndarray]:
    ii,jj=np.triu_indices(len(coarse),1)
    m=coarse[ii]==coarse[jj]
    return ii[m],jj[m]


def auc_from_y_ranks(y:np.ndarray,ranks:np.ndarray)->float:
    y=np.asarray(y,dtype=bool)
    ranks=np.asarray(ranks,dtype=float)
    n1=int(y.sum()); n0=len(y)-n1
    if n1==0 or n0==0:
        raise ValueError("conditional AUC requires both same-fine and different-fine pairs")
    return float((ranks[y].sum()-n1*(n1+1)/2)/(n1*n0))


def permute_fine_within_coarse(fine:np.ndarray,coarse:np.ndarray,rng:np.random.Generator)->np.ndarray:
    out=np.asarray(fine).copy()
    fine=np.asarray(fine)
    coarse=np.asarray(coarse)
    for g in np.unique(coarse):
        idx=np.where(coarse==g)[0]
        out[idx]=rng.permutation(fine[idx])
    return out


def decision_label(centered:float,p:float)->str:
    return ("PROSPECTIVE_SCHISTANTHE_HIDDEN_MEMORY_PASS"
            if centered>0 and p<=0.05
            else "PROSPECTIVE_SCHISTANTHE_HIDDEN_MEMORY_FAIL")


def batch_null(fine:np.ndarray,coarse:np.ndarray,ii:np.ndarray,jj:np.ndarray,
               ranks:np.ndarray,n1:int,n0:int,permutations:int,seed:int,batch:int=128)->np.ndarray:
    rng=np.random.default_rng(seed)
    groups=[np.where(coarse==g)[0] for g in np.unique(coarse)]
    const=n1*(n1+1)/2
    denom=n1*n0
    out=np.empty(permutations,dtype=float)
    pos=0
    while pos<permutations:
        b=min(batch,permutations-pos)
        perm=np.tile(fine,(b,1))
        for idx in groups:
            vals=fine[idx]
            order=np.argsort(rng.random((b,len(idx))),axis=1)
            perm[:,idx]=vals[order]
        y=perm[:,ii]==perm[:,jj]
        rank_sums=(y*ranks[None,:]).sum(axis=1)
        out[pos:pos+b]=(rank_sums-const)/denom
        pos+=b
    return out


def analyse(color_path:Path,tree_path:Path,permutations:int=PERMUTATIONS,seed:int=SEED)->dict:
    if sha256_file(color_path)!=COLOR_SHA:
        raise ValueError("color source SHA mismatch")
    if sha256_file(tree_path)!=TREE_SHA:
        raise ValueError("tree source SHA mismatch")

    tree=Phylo.read(str(tree_path),"newick")
    tree_tips={str(t.name).strip():t for t in tree.get_terminals()}

    rows=[]
    with color_path.open(encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f)
        if r.fieldnames!=["Tip_Label","Clade_No","Flower_Color","Clade"]:
            raise ValueError(f"unexpected color schema {r.fieldnames}")
        for row in r:
            tip=str(row["Tip_Label"]).strip()
            if tip in tree_tips:
                fine=normalize_color(row["Flower_Color"])
                if not fine:
                    raise ValueError(f"missing Flower_Color for retained tip {tip}")
                rows.append((tip,fine))

    if len(rows)!=129 or len({x[0] for x in rows})!=129:
        raise ValueError(f"expected 129 unique exact-match tips, got {len(rows)}")

    raw_counts=collections.Counter(x[1] for x in rows)
    rare={k for k,v in raw_counts.items() if v<FINE_MIN}
    retained=[x for x in rows if x[1] not in rare]
    if len(retained)<MIN_TIPS:
        raise ValueError("common frame below minimum")

    names=[x[0] for x in retained]
    fine_labels=np.array([x[1] for x in retained],dtype=object)
    coarse_labels=np.array([coarse_color(x) for x in fine_labels],dtype=object)
    fine_counts=collections.Counter(fine_labels.tolist())
    coarse_counts=collections.Counter(coarse_labels.tolist())

    if len(fine_counts)<2 or len(coarse_counts)<2:
        raise ValueError("insufficient state variation")
    if len(fine_counts)<=len(coarse_counts):
        raise ValueError("no fine-to-coarse compression opportunity")

    fcode={x:i for i,x in enumerate(sorted(fine_counts))}
    ccode={x:i for i,x in enumerate(sorted(coarse_counts))}
    fine=np.array([fcode[x] for x in fine_labels],dtype=np.int16)
    coarse=np.array([ccode[x] for x in coarse_labels],dtype=np.int8)
    tips=[tree_tips[x] for x in names]

    ii,jj=same_coarse_pair_indices(coarse)
    dist=np.array([tree.distance(tips[int(a)],tips[int(b)]) for a,b in zip(ii,jj)],dtype=float)
    ranks=rankdata(-dist,method="average").astype(float)
    y=fine[ii]==fine[jj]
    n1=int(y.sum()); n0=len(y)-n1
    observed=auc_from_y_ranks(y,ranks)
    null=batch_null(fine,coarse,ii.astype(np.int32),jj.astype(np.int32),ranks,n1,n0,permutations,seed)
    null_mean=float(null.mean())
    centered=float(observed-null_mean)
    p=float((1+int(np.sum(null>=observed)))/(permutations+1))
    status=decision_label(centered,p)

    return {
        "version":"v0.1",
        "status":status,
        "analysis_role":"INDEPENDENT_PROSPECTIVE_VISIBLE_RADIATION_VALIDATION",
        "candidate":"RHODODENDRON_SECT_SCHISTANTHE",
        "source_doi":"10.5061/dryad.47d7wm3f4",
        "source_sha256":{"color":COLOR_SHA,"chronogram":TREE_SHA},
        "crosswalk_rule":"exact Tip_Label intersection only; unmatched trait row excluded before phenotype opening; no alias/fuzzy repair",
        "retained_tips":len(retained),
        "fine_state_counts":dict(sorted(fine_counts.items())),
        "coarse_state_counts":dict(sorted(coarse_counts.items())),
        "fine_state_minimum_support":FINE_MIN,
        "compression_opportunity":True,
        "same_coarse_pairs":int(len(ii)),
        "same_fine_pairs_within_coarse":n1,
        "different_fine_pairs_within_coarse":n0,
        "conditional_auc":observed,
        "null_mean_auc":null_mean,
        "null_q025":float(np.quantile(null,0.025)),
        "null_median":float(np.quantile(null,0.5)),
        "null_q975":float(np.quantile(null,0.975)),
        "centered_auc_effect":centered,
        "p_one_sided":p,
        "permutations":permutations,
        "seed":seed,
        "prospective_contract":{
            "candidate_admission_frozen_before_row_level_color_opening":True,
            "crosswalk_frozen_before_color_state_support":True,
            "state_support_and_opportunity_frozen_before_auc":True,
            "pass_rule":"observed conditional AUC > permutation mean and one-sided P <= 0.05"
        },
        "claim_if_pass":"In an independent held-out visible-color radiation, exact fine flower-color identity retains additional phylogenetic organization after coarse WHITE/NONWHITE membership is fixed.",
        "v0_7_promotion_state_changed":False,
        "el_v0_3_science_changed":False,
        "paper1_science_changed":False
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--color",type=Path,required=True)
    ap.add_argument("--tree",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    x=analyse(args.color,args.tree)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print(json.dumps(x,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
