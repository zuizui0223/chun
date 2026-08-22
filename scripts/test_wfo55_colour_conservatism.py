#!/usr/bin/env python3
"""Root-independent accepted-species visible-colour conservatism under audited trait scenarios."""
from __future__ import annotations
import argparse,csv,json,re
from collections import Counter,deque
from pathlib import Path
import numpy as np
from Bio import Phylo

STATES=("A","W","Y")
def key(x): return re.sub(r"\s+"," ",(x or "").strip().replace("_"," ")).casefold()
def read_seed(path):
    out={}
    with open(path,newline="",encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            k=key(r.get("accepted_species") or r.get("taxon")); s=(r.get("colour_state") or "").strip()
            if k and s in STATES:
                if k in out and out[k]!=s: raise SystemExit(f"conflicting colour state for {k}")
                out[k]=s
    return out

def topology_matrix(path):
    t=Phylo.read(str(path),"newick");adj={}
    for a in t.find_clades(order="level"):
        adj.setdefault(a,[])
        for b in a.clades: adj.setdefault(b,[]);adj[a].append(b);adj[b].append(a)
    tips=[x for x in t.get_terminals() if x.name];names=[key(x.name) for x in tips]
    if len(set(names))!=len(names): raise SystemExit("duplicate normalized tips")
    D=np.zeros((len(tips),len(tips)),dtype=np.int16)
    for i,s in enumerate(tips):
        q=deque([(s,0)]);seen={s};dm={s:0}
        while q:
            u,d=q.popleft()
            for v in adj[u]:
                if v not in seen: seen.add(v);dm[v]=d+1;q.append((v,d+1))
        for j,v in enumerate(tips): D[i,j]=dm[v]
    return names,D

def pair_mpd(D):
    if len(D)<2:return None
    return float(np.mean(D[np.triu_indices(len(D),1)]))

def state_test(state,idx,D,nperm,rng):
    n=len(idx);rec={"state":state,"n_state":n}
    if n<2:
        rec.update({k:None for k in ["observed_mpd_edges","expected_mpd_edges","mpd_z","mpd_cluster_p","observed_mntd_edges","expected_mntd_edges","mntd_z","mntd_cluster_p"]});return rec
    M=D[np.ix_(idx,idx)];om=pair_mpd(M);X=M.astype(float).copy();np.fill_diagonal(X,np.inf);on=float(np.min(X,axis=1).mean())
    N=len(D);nm=np.empty(nperm);nn=np.empty(nperm)
    for z in range(nperm):
        x=rng.choice(N,n,replace=False);R=D[np.ix_(x,x)];nm[z]=pair_mpd(R);Y=R.astype(float).copy();np.fill_diagonal(Y,np.inf);nn[z]=np.min(Y,axis=1).mean()
    sm=float(nm.std(ddof=1));sn=float(nn.std(ddof=1))
    rec.update({"observed_mpd_edges":om,"expected_mpd_edges":float(nm.mean()),"mpd_z":float((om-nm.mean())/sm) if sm else None,"mpd_cluster_p":float((np.sum(nm<=om)+1)/(nperm+1)),"observed_mntd_edges":on,"expected_mntd_edges":float(nn.mean()),"mntd_z":float((on-nn.mean())/sn) if sn else None,"mntd_cluster_p":float((np.sum(nn<=on)+1)/(nperm+1))});return rec

def global_metrics(labels,D):
    labels=np.asarray(labels,dtype=object);iu=np.triu_indices(len(labels),1);same=labels[iu[0]]==labels[iu[1]]
    if not np.any(same): raise SystemExit("no same-state pairs")
    mpd=float(np.mean(D[iu][same]));counts=Counter(labels.tolist());X=D.astype(float).copy();np.fill_diagonal(X,np.inf);near=[]
    for i,s in enumerate(labels):
        if counts[s]<2:continue
        mask=labels==s;mask[i]=False;near.append(float(np.min(X[i,mask])))
    return mpd,float(np.mean(near)),len(near)

def global_test(labels,D,nperm,rng):
    om,on,eligible=global_metrics(labels,D);labels=np.asarray(labels,dtype=object);nm=np.empty(nperm);nn=np.empty(nperm)
    for z in range(nperm):
        p=rng.permutation(labels);nm[z],nn[z],_=global_metrics(p,D)
    sm=float(nm.std(ddof=1));sn=float(nn.std(ddof=1))
    return {"n_nearest_same_state_eligible_tips":eligible,"observed_same_state_mpd_edges":om,"expected_same_state_mpd_edges":float(nm.mean()),"same_state_mpd_z":float((om-nm.mean())/sm) if sm else None,"same_state_mpd_cluster_p":float((np.sum(nm<=om)+1)/(nperm+1)),"observed_nearest_same_state_edges":on,"expected_nearest_same_state_edges":float(nn.mean()),"nearest_same_state_z":float((on-nn.mean())/sn) if sn else None,"nearest_same_state_cluster_p":float((np.sum(nn<=on)+1)/(nperm+1))}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--tree",type=Path,required=True);ap.add_argument("--colour",type=Path,required=True);ap.add_argument("--scenario",required=True);ap.add_argument("--out-dir",type=Path,required=True);ap.add_argument("--permutations",type=int,default=100000);ap.add_argument("--seed",type=int,default=20260822);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    names,D=topology_matrix(a.tree);col=read_seed(a.colour);idx=[i for i,n in enumerate(names) if n in col];labels=[col[names[i]] for i in idx];PD=D[np.ix_(idx,idx)]
    if len(idx)!=len(col): raise SystemExit(f"seed/tree mismatch absent={sorted(set(col)-set(names))}")
    rng=np.random.default_rng(a.seed);state_rows=[state_test(s,[i for i,x in enumerate(labels) if x==s],PD,a.permutations,rng) for s in STATES];g=global_test(labels,PD,a.permutations,rng)
    fields=["state","n_state","observed_mpd_edges","expected_mpd_edges","mpd_z","mpd_cluster_p","observed_mntd_edges","expected_mntd_edges","mntd_z","mntd_cluster_p"]
    with (a.out_dir/"state_clustering.csv").open("w",newline="",encoding="utf-8") as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(state_rows)
    summary={"scenario":a.scenario,"tree_tips_total":len(names),"colour_overlap":len(labels),"state_counts":dict(Counter(labels)),"distance_metric":"unrooted topology edge count","permutations":a.permutations,"state_results":{r["state"]:r for r in state_rows},"global_colour_conservatism":g,"global_colour_conservatism_status":"supported" if g["same_state_mpd_cluster_p"]<.05 and g["nearest_same_state_cluster_p"]<.05 else "partial_or_not_supported","singleton_rule":"states represented by one tip contribute no same-state pair and are excluded from nearest-same-state averaging in observed and count-preserving null permutations","claim_ceiling":"accepted-species root-independent topology pattern only; no transition direction or ecological causation"}
    (a.out_dir/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8");print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
