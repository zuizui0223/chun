#!/usr/bin/env python3
"""Held-out species expression prediction, conditioned on exact pigment presence.

Retrospective Petunieae analysis; frozen protocol committed before this
new predictor-vs-baseline outcome was calculated. Not external validation.
"""
from __future__ import annotations
import argparse
import collections
import json
from pathlib import Path
import numpy as np
import pandas as pd
from Bio import Phylo
from analyze_petunieae_nested_regulatory_memory_v0_1 import sha256, fine_sixbit


def weights(dist:np.ndarray, fine:list[str], names:list[str], k:int=2) -> tuple[np.ndarray,np.ndarray]:
    n=len(fine)
    if dist.shape!=(n,n) or len(names)!=n:raise ValueError("distance/tip frame mismatch")
    state=np.zeros((n,n),dtype=float)
    local=np.zeros((n,n),dtype=float)
    for i,klass in enumerate(fine):
        candidates=[j for j in range(n) if i!=j and fine[j]==klass]
        if len(candidates)<k:raise ValueError("fine state cannot supply fixed k donors")
        state[i,candidates]=1/len(candidates)
        ordered=sorted(candidates,key=lambda j:(float(dist[i,j]),str(names[j])))
        local[i,ordered[:k]]=1/k
    if not np.allclose(state.sum(axis=1),1) or not np.allclose(local.sum(axis=1),1):
        raise ValueError("invalid predictor weights")
    if np.any(np.diag(state)!=0) or np.any(np.diag(local)!=0):
        raise ValueError("heldout tip used for prediction")
    return state,local


def loss_gain(expr_log:np.ndarray, state_weights:np.ndarray, local_weights:np.ndarray) -> dict:
    x=np.asarray(expr_log,dtype=float)
    n,p=x.shape
    if n<3 or not np.isfinite(x).all():raise ValueError("nonfinite expression matrix or insufficient tips")
    mu=(x.sum(axis=0)[None,:]-x)/(n-1)
    variance=(np.square(x).sum(axis=0)[None,:]-np.square(x))/(n-1)-np.square(mu)
    variance=np.where(variance>1e-12,variance,1.0)
    baseline=state_weights@x
    neighbor=local_weights@x
    l0=np.mean(np.square(baseline-x)/variance,axis=1)
    l1=np.mean(np.square(neighbor-x)/variance,axis=1)
    avg0=float(l0.mean());avg1=float(l1.mean())
    if avg0<=0:raise ValueError("zero baseline loss")
    return {"state_only_mse":avg0,"phylogenetic_neighbor_mse":avg1,
            "relative_gain":float((avg0-avg1)/avg0),
            "per_tip_state_only_mse":l0,"per_tip_neighbor_mse":l1}


def permute_within_fine(expr:np.ndarray,groups:list[np.ndarray],rng:np.random.Generator)->np.ndarray:
    order=np.arange(expr.shape[0])
    for inds in groups:
        order[inds]=rng.permutation(inds)
    return expr[order]


def calculate(dist:np.ndarray,fine:list[str],names:list[str],expr_log:np.ndarray,
              *,k:int=2,permutations:int=9999,seed:int=20261008)->dict:
    w_state,w_neighbor=weights(dist,fine,names,k)
    result=loss_gain(expr_log,w_state,w_neighbor)
    observed=result["relative_gain"]
    groups=[np.array([i for i,s in enumerate(fine) if s==g],dtype=int) for g in sorted(set(fine))]
    rng=np.random.default_rng(seed)
    null=np.empty(permutations,dtype=float)
    for b in range(permutations):
        xp=permute_within_fine(expr_log,groups,rng)
        null[b]=loss_gain(xp,w_state,w_neighbor)["relative_gain"]
    if not np.isfinite(null).all():raise ValueError("nonfinite null gain")
    per_class=[]
    l0=result["per_tip_state_only_mse"];l1=result["per_tip_neighbor_mse"]
    for group,idx in zip(sorted(set(fine)),groups):
        a=float(l0[idx].mean());b=float(l1[idx].mean())
        per_class.append({"fine_code":group,"tips":int(len(idx)),
           "state_only_loss":a,"neighbor_loss":b,
           "relative_gain":float((a-b)/a)})
    loo=[]
    for indices in groups:
        retained=np.ones(len(fine),dtype=bool);retained[indices]=False
        a=float(l0[retained].mean());b=float(l1[retained].mean())
        loo.append(float((a-b)/a))
    return {
        "retained_tips":len(fine),"fine_state_counts":dict(sorted(collections.Counter(fine).items())),
        "expression_genes":int(expr_log.shape[1]),"neighbor_k":k,
        "baseline_loss":result["state_only_mse"],"neighbor_loss":result["phylogenetic_neighbor_mse"],
        "observed_relative_prediction_gain":observed,
        "permutation_null_mean":float(null.mean()),
        "permutation_null_q025":float(np.quantile(null,0.025)),
        "permutation_null_q975":float(np.quantile(null,0.975)),
        "p_one_sided":float((1+np.count_nonzero(null>=observed))/(permutations+1)),
        "decision":"POSITIVE_EXPLORATORY_PREDICTION" if observed>0 and (1+np.count_nonzero(null>=observed))/(permutations+1)<=.05 else "NOT_SUPPORTED",
        "permutations":permutations,"seed":seed,
        "per_class_descriptive":per_class,
        "leave_one_fine_class_out_descriptive":{
            "n":len(loo),"positive":sum(x>0 for x in loo),
            "min":float(min(loo)),"median":float(np.median(loo)),"max":float(max(loo))
        }
    }


def load_source(source:Path,design:dict,original:dict)->tuple[np.ndarray,list[str],list[str],np.ndarray]:
    spec=original["source"]
    for loc,key in [
        (spec["processed_csv_path"],"processed_csv_sha256"),
        (spec["tree_path"],"tree_sha256"),
        ("processed/phyloCCA__phyloCCA_expression_HPLC-with-flavs-final.r","source_script_sha256")
    ]:
        path=source/loc
        if not path.exists() or sha256(path)!=spec[key]:raise ValueError("source SHA256 mismatch "+loc)
    manifest=json.loads((source/"source_manifest.json").read_text(encoding="utf-8"))
    if manifest["authoritative_prefix"]!="phyloCCA" or manifest["required_duplicate_identity"]!="PASS_PHYLOCCA_PHYLOPCA_CSV_AND_TREE_OSF_METADATA_IDENTICAL":
        raise ValueError("source manifest duplicate-identity mismatch")
    df=pd.read_csv(source/spec["processed_csv_path"])
    tree=Phylo.read(str(source/spec["tree_path"]),"newick")
    tips=[t.name for t in tree.get_terminals()]
    if len(tips)!=60 or len(df)!=60 or set(tips)!=set(df["key_0"]) or df["key_0"].duplicated().any():
        raise ValueError("source tree and expression table do not align")
    df=df.set_index("key_0").loc[[t for t in tips if t!="BROW"]]
    fine=fine_sixbit(df,original["frame"]["fine_six_compounds_order"])
    cnt=collections.Counter(fine)
    keep=[i for i,s in enumerate(fine) if cnt[s]>=5]
    df=df.iloc[keep]
    fine=[fine[i] for i in keep]
    names=list(df.index)
    if len(names)!=design["retained_taxa"] or dict(sorted(collections.Counter(fine).items()))!=design["class_counts"]:
        raise ValueError("frozen common phenotype state frame drift")
    expression_genes=original["primary"]["raw_gene_expression_columns"]
    X=np.log1p(df[expression_genes].to_numpy(dtype=float))
    if np.any(~np.isfinite(X)) or np.any(X<0):raise ValueError("invalid expression values")
    n=len(names);terminals={t.name:t for t in tree.get_terminals()}
    dist=np.zeros((n,n),dtype=float)
    for i in range(n):
        for j in range(i+1,n):
            dd=float(tree.distance(terminals[names[i]],terminals[names[j]]))
            dist[i,j]=dist[j,i]=dd
    if np.any(dist[np.triu_indices(n,1)]<=0):raise ValueError("non-positive distances")
    return dist,fine,names,X


def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--design",type=Path,required=True)
    p.add_argument("--original-design",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--permutations",type=int,default=None)
    a=p.parse_args()
    d=json.loads(a.design.read_text(encoding="utf-8"))
    od=json.loads(a.original_design.read_text(encoding="utf-8"))
    dist,fine,names,X=load_source(a.source,d,od)
    n=d["null"]["iterations"] if a.permutations is None else a.permutations
    r=calculate(dist,fine,names,X,k=d["predictor_2"]["k"],permutations=n,seed=d["null"]["seed"])
    r.update({
        "version":"v0.1","status":"RETROSPECTIVE_OUTCOME_OPENED_SOURCE_PREDICTION_STUDY",
        "source_verified":True,"new_prediction_design_status":d["status"],
        "substantive_boundary":d["result_boundary"],
        "not_prospective_independent_validation":True,
        "original_paper1_and_el_science_unchanged":True
    })
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(r,indent=2))


if __name__=="__main__":
    main()
