#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from Bio import Phylo
from scipy.stats import rankdata, spearmanr, wilcoxon, binomtest

CSV_SHA="a253308785e4cbd0e361b3ca04cdfdae29c523eefa843375cebf8030ee0874af"
TREES_SHA="ae5c82945e5bf9c29bcabc52d6029acd8d4f5be1fe9141fad95918eacb4f674d"
MAP={"black":"NONWHITE","purple":"NONWHITE","green":"NONWHITE","orange":"NONWHITE",
     "pink":"NONWHITE","red":"NONWHITE","white":"WHITE","yellow":"NONWHITE"}


def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()


def norm_tip(x:str)->str:
    return re.sub(r"\s+"," ",str(x).strip().replace("_"," ")).lower()


def same_coarse_pair_indices(coarse:np.ndarray)->tuple[np.ndarray,np.ndarray]:
    coarse=np.asarray(coarse)
    ii,jj=np.triu_indices(len(coarse),1)
    m=coarse[ii]==coarse[jj]
    return ii[m],jj[m]


def auc_from_y_ranks(y:np.ndarray,ranks:np.ndarray)->float:
    y=np.asarray(y,dtype=bool)
    ranks=np.asarray(ranks,dtype=float)
    n1=int(y.sum()); n0=len(y)-n1
    if n1==0 or n0==0:
        return float("nan")
    return float((ranks[y].sum()-n1*(n1+1)/2)/(n1*n0))


def permute_fine_within_coarse(fine:np.ndarray,coarse:np.ndarray,rng:np.random.Generator)->np.ndarray:
    fine=np.asarray(fine).copy()
    coarse=np.asarray(coarse)
    out=fine.copy()
    for g in np.unique(coarse):
        idx=np.where(coarse==g)[0]
        out[idx]=rng.permutation(fine[idx])
    return out


def centered_effect(observed:float,null:np.ndarray)->float:
    return float(observed-np.mean(np.asarray(null,dtype=float)))


def _rho(x,y)->dict:
    r=spearmanr(np.asarray(x,dtype=float),np.asarray(y,dtype=float))
    return {"rho":float(r.statistic),"p_two_sided":float(r.pvalue)}


def _batch_null(fine,coarse,ii,jj,ranks,n1,n0,permutations,seed,batch):
    fine=np.asarray(fine)
    coarse=np.asarray(coarse)
    rng=np.random.default_rng(seed)
    groups=[np.where(coarse==g)[0] for g in np.unique(coarse)]
    const=n1*(n1+1)/2
    denom=n1*n0
    null=np.empty(permutations,dtype=float)
    pos=0
    while pos<permutations:
        bb=min(batch,permutations-pos)
        perm=np.tile(fine,(bb,1))
        for idx in groups:
            vals=fine[idx]
            order=np.argsort(rng.random((bb,len(idx))),axis=1)
            perm[:,idx]=vals[order]
        same=perm[:,ii]==perm[:,jj]
        rank_sums=(same*ranks[None,:]).sum(axis=1)
        null[pos:pos+bb]=(rank_sums-const)/denom
        pos+=bb
    return null


def analyse(csv_path:Path,trees_path:Path,permutations:int=9999,seed:int=20260920,batch:int=64,
            architecture_path:Path|None=None,bootstrap:int=20000)->dict:
    if sha256_file(csv_path)!=CSV_SHA or sha256_file(trees_path)!=TREES_SHA:
        raise ValueError("exact source hash mismatch")

    rows=collections.defaultdict(list)
    with csv_path.open(newline="",encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rows[r["clade"].strip()].append((r["species"].strip(),r["flower_color"].strip()))

    z=zipfile.ZipFile(trees_path)
    members={Path(m).stem.lower():m for m in z.namelist()
             if not m.endswith("/") and not m.startswith("__MACOSX/") and not m.endswith(".DS_Store")}
    clades=[]
    for clade in sorted(rows):
        vals=rows[clade]
        counts=collections.Counter(c for _,c in vals)
        rare={k for k,v in counts.items() if v<5}
        retained=[(s,c) for s,c in vals if c not in rare]
        fine_raw=[c for _,c in retained]
        coarse_raw=[MAP[c] for c in fine_raw]
        if len(retained)<20 or len(set(fine_raw))<2 or len(set(coarse_raw))<2:
            continue
        if len(set(fine_raw))<=len(set(coarse_raw)):
            continue

        tree=Phylo.read(io.StringIO(z.read(members[clade.lower()]).decode("utf-8-sig")),"newick")
        by={norm_tip(s):c for s,c in retained}
        tips=[t for t in tree.get_terminals() if norm_tip(t.name) in by]
        fine_labels=np.array([by[norm_tip(t.name)] for t in tips],dtype=object)
        coarse_labels=np.array([MAP[x] for x in fine_labels],dtype=object)
        f_map={x:i for i,x in enumerate(sorted(set(fine_labels.tolist())))}
        c_map={x:i for i,x in enumerate(sorted(set(coarse_labels.tolist())))}
        fine=np.array([f_map[x] for x in fine_labels],dtype=np.int16)
        coarse=np.array([c_map[x] for x in coarse_labels],dtype=np.int8)

        ii,jj=same_coarse_pair_indices(coarse)
        dist=np.array([tree.distance(tips[int(a)],tips[int(b)]) for a,b in zip(ii,jj)],dtype=float)
        ranks=rankdata(-dist,method="average").astype(float)
        y=fine[ii]==fine[jj]
        n1=int(y.sum()); n0=len(y)-n1
        if n1==0 or n0==0:
            continue
        observed=auc_from_y_ranks(y,ranks)
        null=_batch_null(fine,coarse,ii.astype(np.int32),jj.astype(np.int32),ranks,n1,n0,
                         permutations,seed+len(clades),batch)
        mean=float(null.mean())
        clades.append({
            "clade":clade,
            "tips":len(tips),
            "fine_states":len(f_map),
            "coarse_states":len(c_map),
            "conditional_auc":observed,
            "null_mean_auc":mean,
            "centered_auc_effect":centered_effect(observed,null),
            "p_one_sided":(1+int(np.sum(null>=observed)))/(permutations+1),
            "null_q025":float(np.quantile(null,0.025)),
            "null_q975":float(np.quantile(null,0.975)),
        })
    z.close()

    effects=np.array([r["centered_auc_effect"] for r in clades],dtype=float)
    positive=int(np.sum(effects>0))
    nonzero=int(np.sum(np.abs(effects)>1e-12))
    rng=np.random.default_rng(seed)
    boot=np.median(effects[rng.integers(0,len(effects),(bootstrap,len(effects)))],axis=1)
    summary={
        "n_clades":len(clades),
        "positive_effect_clades":positive,
        "median_centered_auc_effect":float(np.median(effects)),
        "bootstrap95_median_effect":[float(np.quantile(boot,0.025)),float(np.quantile(boot,0.975))],
        "wilcoxon_effect_gt_zero_p":float(wilcoxon(effects,alternative="greater",zero_method="wilcox").pvalue),
        "sign_effect_gt_zero_p":float(binomtest(positive,nonzero,0.5,alternative="greater").pvalue),
        "per_clade_p_le_0_05":int(sum(r["p_one_sided"]<=0.05 for r in clades)),
    }

    secondary={}
    if architecture_path is not None and architecture_path.exists():
        a=pd.read_csv(architecture_path)
        h=pd.DataFrame(clades)
        j=h.merge(a[["clade","scale_tilt","amplitude"]],on="clade",how="inner",validate="one_to_one")
        secondary={
            "n_joined":int(len(j)),
            "hidden_effect_vs_scale_tilt":_rho(j["centered_auc_effect"],j["scale_tilt"]),
            "hidden_effect_vs_amplitude":_rho(j["centered_auc_effect"],j["amplitude"]),
            "positive_tilt":{"n":int((j["scale_tilt"]>1e-12).sum()),
                             "positive_hidden":int(((j["scale_tilt"]>1e-12)&(j["centered_auc_effect"]>0)).sum()),
                             "median_hidden_effect":float(np.median(j.loc[j["scale_tilt"]>1e-12,"centered_auc_effect"]))},
            "negative_tilt":{"n":int((j["scale_tilt"]<-1e-12).sum()),
                             "positive_hidden":int(((j["scale_tilt"]<-1e-12)&(j["centered_auc_effect"]>0)).sum()),
                             "median_hidden_effect":float(np.median(j.loc[j["scale_tilt"]<-1e-12,"centered_auc_effect"]))},
        }

    return {
        "version":"v0.1",
        "status":"FLOWERCLADES51_HIERARCHICAL_HIDDEN_FINE_MEMORY_EXPLORATORY_RESULT",
        "source_sha256":{"final_dataset.csv":CSV_SHA,"trees.zip":TREES_SHA},
        "permutations":permutations,
        "seed":seed,
        "summary":summary,
        "secondary_relations":secondary,
        "clades":clades,
        "claim_boundary":"post-outcome pilot-exposed exploratory analysis; within-coarse permutation isolates fine-state organization beyond coarse membership; frozen EL v0.3 unchanged",
        "el_v0_3_science_changed":False,
        "paper1_science_changed":False,
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--csv",type=Path,required=True)
    ap.add_argument("--trees",type=Path,required=True)
    ap.add_argument("--out-json",type=Path,required=True)
    ap.add_argument("--out-csv",type=Path,required=True)
    ap.add_argument("--architecture",type=Path)
    ap.add_argument("--permutations",type=int,default=9999)
    ap.add_argument("--seed",type=int,default=20260920)
    ap.add_argument("--batch",type=int,default=64)
    a=ap.parse_args()
    out=analyse(a.csv,a.trees,a.permutations,a.seed,a.batch,a.architecture)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    with a.out_csv.open("w",newline="",encoding="utf-8") as f:
        fields=["clade","tips","fine_states","coarse_states","conditional_auc","null_mean_auc",
                "centered_auc_effect","p_one_sided","null_q025","null_q975"]
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out["clades"])
    print(json.dumps(out["summary"],indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
