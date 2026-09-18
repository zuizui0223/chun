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
from Bio import Phylo
from scipy.stats import binomtest, wilcoxon

CSV_SHA="a253308785e4cbd0e361b3ca04cdfdae29c523eefa843375cebf8030ee0874af"
TREES_SHA="ae5c82945e5bf9c29bcabc52d6029acd8d4f5be1fe9141fad95918eacb4f674d"
STRESS_COLORS=("pink","red","purple","yellow")
REFERENCE_COLOR="white"


def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()


def norm_tip(x:str)->str:
    return re.sub(r"\s+"," ",str(x).strip().replace("_"," ")).lower()


def focal_partner_baseline(states:np.ndarray,focal:str)->float:
    states=np.asarray(states,dtype=object)
    n=len(states); k=int(np.sum(states==focal))
    if n<2 or k<1:
        return float("nan")
    return (k-1)/(n-1)


def focal_memory_curve(distance_matrix:np.ndarray,states:np.ndarray,focal:str,n_bins:int=10)->dict:
    d=np.asarray(distance_matrix,dtype=float)
    states=np.asarray(states,dtype=object)
    n=len(states)
    if d.shape!=(n,n):
        raise ValueError("distance matrix shape mismatch")
    focal_idx=np.where(states==focal)[0]
    k=len(focal_idx)
    if k<1 or n-k<1:
        raise ValueError("focal and nonfocal states both required")
    xs=[]; ys=[]
    for i in focal_idx:
        for j in range(n):
            if i==j:
                continue
            xs.append(float(d[i,j]))
            ys.append(bool(states[j]==focal))
    x=np.asarray(xs,float); y=np.asarray(ys,bool)
    baseline=focal_partner_baseline(states,focal)
    denom=1-baseline
    order=np.argsort(x,kind="stable")
    groups=np.array_split(order,min(n_bins,len(order)))
    bins=[]
    for bi,idx in enumerate(groups,1):
        if not len(idx):
            continue
        p=float(y[idx].mean())
        excess=float((p-baseline)/denom)
        bins.append({
            "bin":bi,
            "n_directed_pairs":int(len(idx)),
            "mean_relative_divergence":float(x[idx].mean()),
            "p_partner_same_color":p,
            "excess_retention":excess,
        })
    bx=np.array([b["mean_relative_divergence"] for b in bins],float)
    by=np.array([b["excess_retention"] for b in bins],float)
    area=float(np.trapezoid(by,bx))
    slope=float(np.polyfit(bx,by,1)[0]) if len(bx)>=2 else float("nan")
    return {"focal_tips":k,"baseline":baseline,"area":area,"slope":slope,"bins":bins}


def stress_minus_white(scores:dict[str,float],stress_colors=STRESS_COLORS)->float:
    if REFERENCE_COLOR not in scores:
        raise ValueError("white score required")
    vals=[scores[c] for c in stress_colors if c in scores and np.isfinite(scores[c])]
    if not vals:
        raise ValueError("at least one stress color score required")
    return float(np.mean(vals)-scores[REFERENCE_COLOR])


def root_to_tip_cv(tree)->float:
    vals=np.array([tree.distance(tree.root,t) for t in tree.get_terminals()],float)
    m=float(vals.mean())
    return float(vals.std(ddof=0)/m) if m>0 else float("nan")


def relative_distance_matrix(tree,tips)->np.ndarray:
    cv=root_to_tip_cv(tree)
    if not np.isfinite(cv) or cv>1e-8:
        raise ValueError(f"source tree not ultrametric enough: CV={cv}")
    crown=float(np.mean([tree.distance(tree.root,t) for t in tree.get_terminals()]))
    n=len(tips)
    out=np.zeros((n,n),float)
    for i in range(n):
        for j in range(i+1,n):
            x=float(tree.distance(tips[i],tips[j])/(2*crown))
            out[i,j]=out[j,i]=x
    if out.max()>1+1e-8:
        raise ValueError("relative divergence exceeds 1")
    return out


def paired_test(contrasts:list[float])->dict:
    x=np.asarray(contrasts,float)
    x=x[np.isfinite(x)]
    median=float(np.median(x)) if len(x) else float("nan")
    if len(x):
        try:
            p=float(wilcoxon(x,alternative="less",zero_method="wilcox").pvalue)
        except ValueError:
            p=1.0
    else:
        p=float("nan")
    nonzero=x[~np.isclose(x,0,atol=1e-15)]
    negative=int(np.sum(nonzero<0))
    sign_p=float(binomtest(negative,len(nonzero),0.5,alternative="greater").pvalue) if len(nonzero) else 1.0
    return {
        "n":int(len(x)),
        "median_contrast":median,
        "negative_count":negative,
        "positive_count":int(np.sum(nonzero>0)),
        "zero_count":int(len(x)-len(nonzero)),
        "wilcoxon_p_one_sided":p,
        "sign_p_one_sided":sign_p,
    }


def analyse(csv_path:Path,trees_path:Path)->dict:
    if sha256_file(csv_path)!=CSV_SHA or sha256_file(trees_path)!=TREES_SHA:
        raise SystemExit("source hash mismatch")

    rows=collections.defaultdict(list)
    with csv_path.open(newline="",encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rows[r["clade"].strip()].append((r["species"].strip(),r["flower_color"].strip()))

    z=zipfile.ZipFile(trees_path)
    members={Path(m).stem.lower():m for m in z.namelist() if not m.endswith("/") and not m.startswith("__MACOSX/") and not m.endswith(".DS_Store")}
    details={}
    paired=[]
    individual=collections.defaultdict(list)

    for clade in sorted(rows):
        vals=rows[clade]
        counts=collections.Counter(c for _,c in vals)
        rare={c for c,n in counts.items() if n<5}
        retained=[(s,c) for s,c in vals if c not in rare]
        if len(retained)<20:
            details[clade]={"status":"HOLD_TIPS_LT_20","eligible_tips":len(retained)}
            continue

        rb={norm_tip(s):c for s,c in retained}
        tree=Phylo.read(io.StringIO(z.read(members[clade.lower()]).decode("utf-8-sig")),"newick")
        tips=[t for t in tree.get_terminals() if norm_tip(t.name) in rb]
        states=np.array([rb[norm_tip(t.name)] for t in tips],dtype=object)
        n=len(tips)
        color_counts=collections.Counter(states.tolist())
        eligible=[c for c,k in color_counts.items() if k>=5 and n-k>=5]
        stress=[c for c in STRESS_COLORS if c in eligible]
        if REFERENCE_COLOR not in eligible or not stress:
            details[clade]={
                "status":"HOLD_NO_PAIRED_WHITE_STRESS_COLOR",
                "eligible_tips":n,
                "eligible_colors":sorted(eligible),
                "eligible_stress_colors":stress,
            }
            continue

        d=relative_distance_matrix(tree,tips)
        curves={}
        scores={}
        for color in [REFERENCE_COLOR]+stress:
            curve=focal_memory_curve(d,states,color,n_bins=10)
            curves[color]=curve
            scores[color]=curve["area"]
        contrast=stress_minus_white(scores,STRESS_COLORS)
        paired.append(contrast)
        for color in stress:
            individual[color].append(scores[color]-scores[REFERENCE_COLOR])
        details[clade]={
            "status":"PAIRED_STRESS_WHITE_MEMORY_COMPLETE",
            "eligible_tips":n,
            "root_to_tip_cv":root_to_tip_cv(tree),
            "color_counts":dict(sorted(color_counts.items())),
            "eligible_stress_colors":stress,
            "areas":scores,
            "stress_mean_area":float(np.mean([scores[c] for c in stress])),
            "white_area":scores[REFERENCE_COLOR],
            "stress_minus_white":contrast,
            "curves":curves,
        }
    z.close()

    primary=paired_test(paired)
    if primary["n"]<10:
        status="HOLD_INSUFFICIENT_PAIRED_CLADES"
        decision="HOLD"
    else:
        passed=primary["median_contrast"]<0 and primary["wilcoxon_p_one_sided"]<=0.05
        status="STRESS_COLOR_MEMORY_PASS" if passed else "STRESS_COLOR_MEMORY_FAIL"
        decision="PASS" if passed else "FAIL"

    secondary={}
    for color in STRESS_COLORS:
        if individual[color]:
            secondary[color]=paired_test(individual[color])

    complete=[k for k,v in details.items() if v["status"]=="PAIRED_STRESS_WHITE_MEMORY_COMPLETE"]
    loo=[]
    if len(paired)>2:
        arr=np.asarray(paired,float)
        for i,clade in enumerate(complete):
            x=np.delete(arr,i)
            loo.append({"held_out":clade,"median_contrast":float(np.median(x)),"negative_median":bool(np.median(x)<0)})

    return {
        "version":"v0.1",
        "status":status,
        "decision":decision,
        "source_sha256":{"final_dataset.csv":CSV_SHA,"trees.zip":TREES_SHA},
        "stress_colors":list(STRESS_COLORS),
        "reference_color":REFERENCE_COLOR,
        "paired_clades":len(paired),
        "primary_test":primary,
        "secondary_individual_colors":secondary,
        "leave_one_clade_out":{
            "negative_median_count":int(sum(x["negative_median"] for x in loo)),
            "total":len(loo),
            "details":loo,
        },
        "results":details,
        "claim_boundary":[
            "retrospective derived analysis on already-opened color outcomes",
            "published environment-color associations are not re-estimated here",
            "a PASS is consistent with repeated ecological convergence but is not causal evidence for abiotic selection",
            "clade is the inferential replication unit"
        ],
        "paper1_science_changed":False,
        "el_v0_2_science_changed":False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--csv",type=Path,required=True)
    ap.add_argument("--trees",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    out=analyse(args.csv,args.trees)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":out["status"],
        "paired_clades":out["paired_clades"],
        "primary_test":out["primary_test"],
        "secondary_individual_colors":out["secondary_individual_colors"],
        "loo":out["leave_one_clade_out"],
    },indent=2))


if __name__=="__main__":
    main()
