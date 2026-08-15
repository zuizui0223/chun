#!/usr/bin/env python3
"""Topology-only phylogenetic sensitivity for Camellia thermal niches.

Uses the Open Tree of Life synthetic induced subtree for exact A/W taxa and
assigns Grafen-style branch lengths (power=1). Fits simple Gaussian BM, stationary
OU and Early-Burst covariance models by maximum likelihood and a BM-PGLS of
thermal metric on A versus W state.

IMPORTANT: this is a topology sensitivity, NOT a dated/nuclear-tree analysis.
Its role is only to ask whether the strong A≈W species-level result reverses after
coarse phylogenetic covariance is introduced.
"""
from __future__ import annotations
import argparse, csv, io, json, math, pathlib
from collections import Counter

import numpy as np
import requests
from Bio import Phylo
from scipy.optimize import minimize_scalar
from scipy.stats import t as tdist

API='https://api.opentreeoflife.org/v3'
UA='chun-opentree-sensitivity/0.1'
METRICS=('bio1_median','bio6_median','bio6_q05','bio1_iqr')

def post(path,payload):
    r=requests.post(API+'/'+path,json=payload,headers={'User-Agent':UA},timeout=120)
    r.raise_for_status(); return r.json()

def read_csv(p):
    with open(p,newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))

def write_csv(p,rows):
    p=pathlib.Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    if not rows: p.write_text('',encoding='utf-8'); return
    with p.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def tnrs(names):
    data=post('tnrs/match_names',{'names':names,'do_approximate_matching':False,'include_suppressed':False})
    out=[]
    for result in data.get('results',[]):
        query=result.get('id') or result.get('name') or ''
        matches=result.get('matches',[])
        # Accept only an unambiguous exact name match (score 1 where supplied).
        good=[m for m in matches if float(m.get('score',1))>=0.999999 and not m.get('is_approximate_match',False)]
        if len(good)==1:
            m=good[0]; tx=m.get('taxon',{})
            out.append({'query':query,'ott_id':tx.get('ott_id'),'matched_name':tx.get('name',''),'is_synonym':m.get('is_synonym',False),'score':m.get('score',1),'status':'admit'})
        else:
            out.append({'query':query,'ott_id':'','matched_name':'','is_synonym':'','score':'','status':f'reject_{len(good)}_exact_matches'})
    # API may not preserve custom id in all versions; recover by positional order when necessary.
    if len(out)==len(names) and any(r['query']=='' for r in out):
        for r,n in zip(out,names): r['query']=n
    return out

def descendants(clade):
    return len(clade.get_terminals())

def assign_grafen(tree,power=1.0):
    n=len(tree.get_terminals())
    heights={}
    for cl in tree.find_clades(order='postorder'):
        heights[cl]=0.0 if cl.is_terminal() else ((descendants(cl)-1)/(n-1))**power
    root=tree.root
    # root should be height 1 for fully bifurcating/multifurcating tree containing all tips.
    for parent in tree.find_clades(order='preorder'):
        for child in parent.clades:
            bl=heights[parent]-heights[child]
            child.branch_length=max(float(bl),1e-8)
    root.branch_length=0.0
    return heights

def root_distances(tree):
    return {cl:tree.distance(tree.root,cl) for cl in tree.find_clades()}

def mrca_matrix(tree,tips):
    terminals={t.name:t for t in tree.get_terminals()}
    rd=root_distances(tree); n=len(tips)
    shared=np.zeros((n,n)); pat=np.zeros((n,n))
    for i,a in enumerate(tips):
        ca=terminals[a]
        for j,b in enumerate(tips[i:],start=i):
            cb=terminals[b]
            if i==j:
                shared[i,j]=rd[ca]; pat[i,j]=0.0
            else:
                m=tree.common_ancestor(ca,cb); s=rd[m]; shared[i,j]=shared[j,i]=s
                dij=rd[ca]+rd[cb]-2*s; pat[i,j]=pat[j,i]=dij
    return shared,pat

def profile_ll(y,C,k_extra=0):
    n=len(y); C=np.asarray(C,float)
    C=(C+C.T)/2 + np.eye(n)*1e-8
    sign,ld=np.linalg.slogdet(C)
    if sign<=0:return (-np.inf,np.nan,np.nan)
    inv=np.linalg.inv(C); one=np.ones((n,1)); yy=y.reshape(-1,1)
    mu=float(np.linalg.solve(one.T@inv@one,one.T@inv@yy)[0,0])
    r=yy-mu; sse=float((r.T@inv@r)[0,0]); sig=sse/n
    if sig<=0:return (-np.inf,mu,sig)
    ll=-0.5*(n*math.log(2*math.pi)+ld+n*math.log(sig)+n)
    return ll,mu,sig

def aicc(ll,k,n):
    aic=2*k-2*ll
    return aic+(2*k*(k+1))/(n-k-1) if n>k+1 else np.inf

def fit_models(y,shared,pat):
    n=len(y); rows=[]
    ll,mu,sig=profile_ll(y,shared); rows.append({'model':'BM','lnL':ll,'AICc':aicc(ll,2,n),'mu':mu,'sigma2':sig,'alpha':'','eb_rate':''})
    def ou_obj(loga):
        alpha=math.exp(loga); C=np.exp(-alpha*pat); ll,_,_=profile_ll(y,C); return -ll
    ou=minimize_scalar(ou_obj,bounds=(-6,5),method='bounded'); alpha=math.exp(ou.x); C=np.exp(-alpha*pat); ll,mu,sig=profile_ll(y,C); rows.append({'model':'OU_stationary','lnL':ll,'AICc':aicc(ll,3,n),'mu':mu,'sigma2':sig,'alpha':alpha,'eb_rate':''})
    # EB covariance integrates rate exp(a*t) from root time 0 to shared path t.
    def eb_cov(rate):
        if abs(rate)<1e-8:return shared.copy()
        return (np.exp(rate*shared)-1.0)/rate
    def eb_obj(rate):
        ll,_,_=profile_ll(y,eb_cov(rate)); return -ll
    eb=minimize_scalar(eb_obj,bounds=(-5,5),method='bounded'); C=eb_cov(float(eb.x)); ll,mu,sig=profile_ll(y,C); rows.append({'model':'EB','lnL':ll,'AICc':aicc(ll,3,n),'mu':mu,'sigma2':sig,'alpha':'','eb_rate':float(eb.x)})
    best=min(float(r['AICc']) for r in rows)
    for r in rows:r['deltaAICc']=float(r['AICc'])-best
    return sorted(rows,key=lambda r:float(r['AICc']))

def pgls(y,state,C):
    n=len(y); X=np.column_stack([np.ones(n),np.asarray([1.0 if s=='A' else 0.0 for s in state])]); C=(C+C.T)/2+np.eye(n)*1e-8; inv=np.linalg.inv(C)
    xtix=np.linalg.inv(X.T@inv@X); beta=xtix@(X.T@inv@y); resid=y-X@beta; df=n-X.shape[1]; sig=float(resid.T@inv@resid/df); covb=sig*xtix; se=np.sqrt(np.diag(covb)); t=float(beta[1]/se[1]); p=float(2*tdist.sf(abs(t),df))
    return {'estimate_A_minus_W':float(beta[1]),'SE':float(se[1]),'t':t,'df':df,'p':p}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--species',type=pathlib.Path,required=True); ap.add_argument('--out-dir',type=pathlib.Path,required=True); a=ap.parse_args(); a.out_dir.mkdir(parents=True,exist_ok=True)
    rows=[r for r in read_csv(a.species) if r['colour_state'] in {'A','W'} and r['taxon']!='Camellia kissi']
    names=[r['taxon'] for r in rows]; matches=tnrs(names); write_csv(a.out_dir/'tnrs_matches.csv',matches)
    mby={r['query']:r for r in matches}; ids=[]; id_to_name={}
    for n in names:
        m=mby.get(n)
        if m and m['status']=='admit' and m['ott_id'] not in ('',None):
            oid=int(m['ott_id']); ids.append(oid); id_to_name[f'ott{oid}']=n; id_to_name[str(oid)]=n
    if len(ids)<20: raise SystemExit(f'only {len(ids)} exact OpenTree TNRS matches')
    sub=post('tree_of_life/induced_subtree',{'ott_ids':ids,'label_format':'id'})
    nwk=sub.get('newick',''); (a.out_dir/'opentree_induced_raw.nwk').write_text(nwk+'\n',encoding='utf-8')
    tree=Phylo.read(io.StringIO(nwk),'newick')
    for t in tree.get_terminals():
        key=str(t.name).strip("'")
        if key in id_to_name:t.name=id_to_name[key]
    available={t.name for t in tree.get_terminals()}; data={r['taxon']:r for r in rows}; common=sorted(available & set(data))
    # prune unmatched tips from induced tree if needed
    for t in list(tree.get_terminals()):
        if t.name not in common: tree.prune(t)
    assign_grafen(tree,1.0)
    Phylo.write(tree,a.out_dir/'opentree_grafen.nwk','newick')
    tips=[t.name for t in tree.get_terminals()]; shared,pat=mrca_matrix(tree,tips)
    model_rows=[]; pgls_rows=[]
    for metric in METRICS:
        y=np.asarray([float(data[t][metric]) for t in tips]); states=[data[t]['colour_state'] for t in tips]
        for r in fit_models(y,shared,pat):model_rows.append({'metric':metric,'n':len(tips),**r})
        p=pgls(y,states,shared); pgls_rows.append({'metric':metric,'n':len(tips),'n_A':sum(s=='A' for s in states),'n_W':sum(s=='W' for s in states),**p})
    write_csv(a.out_dir/'bm_ou_eb_topology_sensitivity.csv',model_rows); write_csv(a.out_dir/'aw_bm_pgls_topology_sensitivity.csv',pgls_rows)
    summary={'scope':'OpenTree synthetic topology + Grafen power=1 branch lengths; sensitivity only, not dated/nuclear primary analysis','n_input_AW':len(rows),'n_exact_tnrs':len(ids),'n_tree_overlap':len(tips),'states':dict(Counter(data[t]['colour_state'] for t in tips)),'synth_id':sub.get('synth_id',''),'claim_ceiling':'tests whether topology-aware BM-PGLS reverses A≈W; OU/EB are branch-length sensitivity only'}
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8'); print(json.dumps(summary,indent=2)); print(pgls_rows); print(model_rows)
if __name__=='__main__':main()
