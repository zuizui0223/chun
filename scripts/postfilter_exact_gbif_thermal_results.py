#!/usr/bin/env python3
"""Post-filter Camellia thermal results to independent EXACT GBIF species matches.

The expensive GBIF/CHELSA extraction is kept unchanged.  This admission layer
removes fuzzy/higher-rank taxon matches from the already-extracted species table,
then recomputes pairwise colour tests and coarse section-block sensitivities.
It is therefore auditable separately from occurrence/climate extraction.
"""
from __future__ import annotations
import argparse, csv, json, math, pathlib
from collections import Counter, defaultdict
import numpy as np

METRICS=("bio1_median","bio6_median","bio6_q05","bio1_iqr")
PAIRS=(("A","W"),("A","Y"),("W","Y"))

def read(path):
    with pathlib.Path(path).open(newline='',encoding='utf-8-sig') as f: return list(csv.DictReader(f))

def write(path,rows):
    path=pathlib.Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    if not rows: path.write_text('',encoding='utf-8'); return
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def perm_test(x,y,seed=20260815,nmc=100000):
    import itertools
    x=np.asarray(x,float); y=np.asarray(y,float); vals=np.concatenate([x,y]); nx=len(x); obs=float(x.mean()-y.mean()); ncomb=math.comb(len(vals),nx)
    if ncomb<=200000:
        d=[]
        for idx in itertools.combinations(range(len(vals)),nx):
            mask=np.zeros(len(vals),bool); mask[list(idx)]=True; d.append(float(vals[mask].mean()-vals[~mask].mean()))
        d=np.asarray(d); method='exact'; nperm=ncomb; add=0
    else:
        rng=np.random.default_rng(seed); d=np.empty(nmc)
        for i in range(nmc):
            idx=rng.choice(len(vals),size=nx,replace=False); mask=np.zeros(len(vals),bool); mask[idx]=True; d[i]=vals[mask].mean()-vals[~mask].mean()
        method=f'monte_carlo_seed_{seed}'; nperm=nmc; add=1
    p2=float((np.sum(np.abs(d)>=abs(obs)-1e-12)+add)/(len(d)+add))
    pl=float((np.sum(d<=obs+1e-12)+add)/(len(d)+add))
    return obs,p2,pl,nperm,method,ncomb

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--species',type=pathlib.Path,required=True); ap.add_argument('--matches',type=pathlib.Path,required=True); ap.add_argument('--out-dir',type=pathlib.Path,required=True); a=ap.parse_args(); a.out_dir.mkdir(parents=True,exist_ok=True)
    species=read(a.species); matches=read(a.matches); mm={r['taxon']:r for r in matches}
    admitted=[]; rejected=[]; seen={}
    for r in species:
        m=mm.get(r['taxon'],{})
        if str(m.get('rank','')).upper()!='SPECIES' or str(m.get('matchType','')).upper()!='EXACT' or not m.get('usageKey'):
            rejected.append({'taxon':r['taxon'],'reason':'non_exact_species_match','rank':m.get('rank',''),'matchType':m.get('matchType',''),'usageKey':m.get('usageKey',''),'matched_scientific_name':m.get('scientificName','')}); continue
        key=str(m['usageKey'])
        if key in seen:
            rejected.append({'taxon':r['taxon'],'reason':'duplicate_gbif_usage_key','rank':m.get('rank',''),'matchType':m.get('matchType',''),'usageKey':key,'matched_scientific_name':m.get('scientificName',''),'duplicate_of':seen[key]}); continue
        seen[key]=r['taxon']; admitted.append(r)
    write(a.out_dir/'species_thermal_niches_exact.csv',admitted); write(a.out_dir/'rejected_taxa.csv',rejected)
    tests=[]
    for metric in METRICS:
        for s1,s2 in PAIRS:
            x=[float(r[metric]) for r in admitted if r['colour_state']==s1]; y=[float(r[metric]) for r in admitted if r['colour_state']==s2]
            if len(x)>=2 and len(y)>=2:
                obs,p2,pl,nperm,method,ncomb=perm_test(x,y)
                tests.append({'metric':metric,'state1':s1,'state2':s2,'n_state1':len(x),'n_state2':len(y),'mean_state1':float(np.mean(x)),'mean_state2':float(np.mean(y)),'difference_state1_minus_state2':obs,'two_sided_p':p2,'one_sided_p_state1_lower':pl,'test_method':method,'n_permutations':nperm,'total_label_combinations':str(ncomb)})
    write(a.out_dir/'colour_pairwise_thermal_tests_exact.csv',tests)
    secrows=[]
    for metric in METRICS:
        for s1,s2 in PAIRS:
            by=defaultdict(lambda:defaultdict(list))
            for r in admitted:
                sec=r.get('section','').strip()
                if sec and ';' not in sec: by[sec][r['colour_state']].append(float(r[metric]))
            diffs=[]
            for sec,d in by.items():
                if d[s1] and d[s2]: diffs.append((sec,float(np.mean(d[s1])-np.mean(d[s2])),len(d[s1]),len(d[s2])))
            if diffs:
                nz=[d for _,d,_,_ in diffs if abs(d)>1e-12]; n=len(nz); k=sum(d<0 for d in nz)
                if n:
                    probs=[math.comb(n,i)*0.5**n for i in range(n+1)]; pk=probs[k]; p2=min(1.0,sum(p for p in probs if p<=pk+1e-15))
                else: p2=1.0
                secrows.append({'metric':metric,'state1':s1,'state2':s2,'n_shared_sections':len(diffs),'n_nonzero_sections':n,'n_sections_state1_lower':k,'two_sided_exact_sign_p':p2,'mean_section_difference':float(np.mean([d for _,d,_,_ in diffs])),'section_differences_json':json.dumps([{'section':s,'difference':d,'n1':n1,'n2':n2} for s,d,n1,n2 in diffs],ensure_ascii=False)})
    write(a.out_dir/'section_blocked_colour_tests_exact.csv',secrows)
    summary={'n_input_species':len(species),'n_exact_independent_species':len(admitted),'states':dict(Counter(r['colour_state'] for r in admitted)),'n_rejected':len(rejected),'rejected_taxa':rejected,'admission':'GBIF rank=SPECIES and matchType=EXACT and unique usageKey','claim_ceiling':'taxon-exact species-level thermal association; section blocks are not a nuclear phylogenetic correction'}
    (a.out_dir/'exact_match_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
