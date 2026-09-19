#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from Bio import Phylo
from scipy.stats import rankdata

TABLE_SHA="5843d4cd4eb253046f97349fa6bd285ca77e43e7a9c3aaa0e78fae3e8e391edd"
TREE_SHA="95b4a688d3d71417b712b37a2b04cdc22a9431be3172d6509def4435f5fd8614"
OUTGROUP="BROW"
COMPOUNDS=["Pel_mgg","Cyan_mgg","Peon_mgg","Del_mgg","Pet_mgg","Malv_mgg"]
PERMUTATIONS=9999
SEED=20260920


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()


def source_files(source:Path)->tuple[dict,Path,Path]:
    m=json.loads((source/"source_manifest.json").read_text())
    if m["required_duplicate_identity"]!="PASS_PHYLOCCA_PHYLOPCA_CSV_AND_TREE_OSF_METADATA_IDENTICAL":
        raise ValueError("source duplicate-identity gate not passed")
    if m["authoritative_prefix"]!="phyloCCA":
        raise ValueError("unexpected authoritative source root")
    by={x["name"]:source/"processed"/x["local_name"] for x in m["downloaded"]}
    table=by["tpm10k-mgg-combined-with-flavs.csv"]
    tree=by["11genestre_dated_pruned.tre"]
    if sha256(table)!=TABLE_SHA or sha256(tree)!=TREE_SHA:
        raise ValueError("frozen source hash mismatch")
    return m,table,tree


def state_codes(row)->tuple[str,str]:
    vals=[float(row[c]) for c in COMPOUNDS]
    fine="".join("1" if v>0 else "0" for v in vals)
    coarse="1" if any(v>0 for v in vals) else "0"
    return coarse,fine


def same_coarse_pair_indices(coarse:np.ndarray)->tuple[np.ndarray,np.ndarray]:
    coarse=np.asarray(coarse)
    ii,jj=np.triu_indices(len(coarse),1)
    keep=coarse[ii]==coarse[jj]
    return ii[keep],jj[keep]


def auc_from_y_ranks(y:np.ndarray,ranks:np.ndarray)->float:
    y=np.asarray(y,dtype=bool)
    ranks=np.asarray(ranks,dtype=float)
    n1=int(y.sum()); n0=len(y)-n1
    if n1==0 or n0==0:
        raise ValueError("conditional AUC response has one class")
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


def analyze(source:Path,permutations:int=PERMUTATIONS,seed:int=SEED)->dict:
    manifest,table_path,tree_path=source_files(source)
    df=pd.read_csv(table_path)
    req={"key_0",*COMPOUNDS}
    if not req<=set(df.columns):
        raise ValueError(f"missing source columns {sorted(req-set(df.columns))}")
    if len(df)!=60 or df["key_0"].duplicated().any():
        raise ValueError("expected 60 unique source rows")
    if df[COMPOUNDS].isna().any().any():
        raise ValueError("missing primary compound values")
    if int((df["key_0"]==OUTGROUP).sum())!=1:
        raise ValueError("frozen outgroup absent or duplicated")
    full=df.copy()
    df=df[df["key_0"]!=OUTGROUP].copy()
    if len(df)!=59:
        raise ValueError("outgroup exclusion did not yield 59 taxa")

    tree=Phylo.read(str(tree_path),"newick")
    tips0=[t.name for t in tree.get_terminals()]
    if len(tips0)!=60 or len(set(tips0))!=60 or set(tips0)!=set(full["key_0"]):
        raise ValueError("source table/tree pre-prune join failure")
    tree.prune(OUTGROUP)
    tree.root.branch_length=0
    tips=[t.name for t in tree.get_terminals()]
    if set(tips)!=set(df["key_0"]):
        raise ValueError("table/tree join failure after outgroup prune")

    by=df.set_index("key_0")
    raw={name:state_codes(by.loc[name]) for name in tips}
    fine_counts0=collections.Counter(v[1] for v in raw.values())
    rare=sorted(k for k,v in fine_counts0.items() if v<5)
    rare_set=set(rare)
    retained=[name for name in tips if raw[name][1] not in rare_set]
    if len(retained)!=47:
        raise ValueError(f"expected frozen 47-tip frame, got {len(retained)}")

    coarse_labels=[raw[n][0] for n in retained]
    fine_labels=[raw[n][1] for n in retained]
    coarse_counts=dict(sorted(collections.Counter(coarse_labels).items()))
    fine_counts=dict(sorted(collections.Counter(fine_labels).items()))
    if coarse_counts!={"0":6,"1":41}:
        raise ValueError(f"coarse frame drift: {coarse_counts}")
    if len(fine_counts)!=6:
        raise ValueError(f"expected six retained fine states, got {fine_counts}")

    cmap={x:i for i,x in enumerate(sorted(set(coarse_labels)))}
    fmap={x:i for i,x in enumerate(sorted(set(fine_labels)))}
    coarse=np.array([cmap[x] for x in coarse_labels],dtype=np.int8)
    fine=np.array([fmap[x] for x in fine_labels],dtype=np.int16)

    terminals={t.name:t for t in tree.get_terminals()}
    ii,jj=same_coarse_pair_indices(coarse)
    dist=np.array([tree.distance(terminals[retained[int(a)]],terminals[retained[int(b)]])
                   for a,b in zip(ii,jj)],dtype=float)
    ranks=rankdata(-dist,method="average").astype(float)
    y=fine[ii]==fine[jj]
    observed=auc_from_y_ranks(y,ranks)

    rng=np.random.default_rng(seed)
    null=np.empty(permutations,dtype=float)
    for b in range(permutations):
        p=permute_fine_within_coarse(fine,coarse,rng)
        null[b]=auc_from_y_ranks(p[ii]==p[jj],ranks)

    null_mean=float(null.mean())
    effect=centered_effect(observed,null)
    p_one=(1+int(np.count_nonzero(null>=observed)))/(permutations+1)

    return {
      "version":"v0.1",
      "status":"PETUNIEAE_HIERARCHICAL_HIDDEN_MEMORY_RETROSPECTIVE_RESULT",
      "analysis_role":"RETROSPECTIVE_CROSS_REPRESENTATION_HIDDEN_MEMORY",
      "source_osf_node":manifest["osf_node"],
      "source_table_sha256":TABLE_SHA,
      "source_tree_sha256":TREE_SHA,
      "source_defined_outgroup_key_used":OUTGROUP,
      "eligible_tips":len(retained),
      "rare_fine_states_excluded":rare,
      "coarse_state_counts":coarse_counts,
      "fine_state_counts":fine_counts,
      "same_coarse_pairs":int(len(ii)),
      "same_fine_positive_pairs":int(y.sum()),
      "different_fine_negative_pairs":int(len(y)-y.sum()),
      "conditional_auc":float(observed),
      "null_mean_auc":null_mean,
      "centered_auc_effect":effect,
      "null_q025":float(np.quantile(null,0.025)),
      "null_q975":float(np.quantile(null,0.975)),
      "p_one_sided":float(p_one),
      "permutations":permutations,
      "seed":seed,
      "interpretation":"fine biochemical compound identity retains phylogenetic organization within the frozen coarse anthocyanidin-presence states if the centered effect is positive; this is retrospective same-source evidence",
      "do_not_count_as_new_prospective_replication":True,
      "el_v0_3_science_changed":False,
      "paper1_science_changed":False
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--permutations",type=int,default=PERMUTATIONS)
    ap.add_argument("--seed",type=int,default=SEED)
    a=ap.parse_args()
    out=analyze(a.source,a.permutations,a.seed)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
