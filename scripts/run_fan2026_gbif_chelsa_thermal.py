#!/usr/bin/env python3
"""Species-scale thermal analysis for the Fan et al. 2026 Camellia colour table.

Input is the deterministic species-level seed created from Data S1. GBIF records
are restricted to source-provenance countries, filtered/thinned, and sampled
against local CHELSA BIO1/BIO6 rasters. Species are the replicate units.

Two record modes are supported:
- wildlike: the main filter set (specimens/material plus observations after
  explicit cultivation/non-native/geospatial filtering);
- specimen_only: a stricter sensitivity retaining PRESERVED_SPECIMEN,
  MATERIAL_SAMPLE and MATERIAL_CITATION only.

Pairwise colour-state tests use exact permutations when feasible and a fixed-seed
Monte Carlo permutation otherwise. A section-stratified sensitivity test is also
reported; section is only a coarse taxonomic block, not a substitute for a
nuclear phylogeny.
"""
from __future__ import annotations
import argparse, json, math, pathlib, time
from collections import Counter, defaultdict
import numpy as np
from run_camellia_gbif_worldclim_niche import (
    read_csv, write_csv, gbif_match, fetch_occurrences, keep_occurrence, thin_records,
)
from run_camellia_gbif_chelsa_thermal import sample_one, systematic_cap

SPECIMEN_BASIS={"PRESERVED_SPECIMEN","MATERIAL_SAMPLE","MATERIAL_CITATION"}

def summarize(seed, rows):
    out={k:seed.get(k,"") for k in ("taxon","colour_state","pigment_proxy","section","areas","n_source_accessions","source_color_values")}
    out["n_points"]=len(rows)
    for b in (1,6):
        v=np.asarray([float(r[f"bio{b}"]) for r in rows],dtype=float)
        out[f"bio{b}_mean"]=float(np.mean(v)); out[f"bio{b}_median"]=float(np.median(v)); out[f"bio{b}_q05"]=float(np.quantile(v,.05)); out[f"bio{b}_q95"]=float(np.quantile(v,.95)); out[f"bio{b}_iqr"]=float(np.quantile(v,.75)-np.quantile(v,.25))
    return out

def perm_test(x,y,seed=20260815,nmc=100000):
    x=np.asarray(x,float); y=np.asarray(y,float); vals=np.concatenate([x,y]); nx=len(x); obs=float(x.mean()-y.mean()); ncomb=math.comb(len(vals),nx)
    if ncomb<=200000:
        import itertools
        diffs=[]
        for idx in itertools.combinations(range(len(vals)),nx):
            mask=np.zeros(len(vals),bool); mask[list(idx)]=True; diffs.append(float(vals[mask].mean()-vals[~mask].mean()))
        d=np.asarray(diffs); method="exact"; nperm=ncomb
    else:
        rng=np.random.default_rng(seed); d=np.empty(nmc)
        for i in range(nmc):
            idx=rng.choice(len(vals),size=nx,replace=False); mask=np.zeros(len(vals),bool); mask[idx]=True; d[i]=vals[mask].mean()-vals[~mask].mean()
        method=f"monte_carlo_seed_{seed}"; nperm=nmc
    add=0 if method=="exact" else 1
    p2=float((np.sum(np.abs(d)>=abs(obs)-1e-12)+add)/(len(d)+add))
    pl=float((np.sum(d<=obs+1e-12)+add)/(len(d)+add))
    return obs,p2,pl,nperm,method,ncomb

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--taxa',type=pathlib.Path,required=True)
    ap.add_argument('--bio1',type=pathlib.Path,required=True)
    ap.add_argument('--bio6',type=pathlib.Path,required=True)
    ap.add_argument('--out-dir',type=pathlib.Path,required=True)
    ap.add_argument('--min-points',type=int,default=5)
    ap.add_argument('--cap-points',type=int,default=80)
    ap.add_argument('--gbif-cap-per-country',type=int,default=1000)
    ap.add_argument('--record-mode',choices=('wildlike','specimen_only'),default='wildlike')
    a=ap.parse_args(); a.out_dir.mkdir(parents=True,exist_ok=True)
    taxa=read_csv(a.taxa); species=[]; audit=[]; matches=[]; point_rows=[]; raster_meta={}
    for seed in taxa:
        taxon=seed['taxon']; m=gbif_match(taxon); matches.append({**seed,**m})
        if not m.get('usageKey') or str(m.get('rank','')).upper()!='SPECIES':
            audit.append({'taxon':taxon,'matched_name':m.get('scientificName',''),'matched_rank':m.get('rank',''),'match_type':m.get('matchType',''),'status':'reject_non_species_match'}); continue
        raw=[]; total=0
        for country in [z.strip() for z in seed['native_country_codes'].split(';') if z.strip()]:
            rr,n=fetch_occurrences(int(m['usageKey']),country,a.gbif_cap_per_country); raw.extend(rr); total+=n
        raw=list({str(r.get('key',i)):r for i,r in enumerate(raw)}.values()); reasons=Counter(); clean=[]
        for r in raw:
            ok,reason=keep_occurrence(r)
            if ok and a.record_mode=='specimen_only' and str(r.get('basisOfRecord','')).upper() not in SPECIMEN_BASIS:
                ok=False; reason='non_specimen_basis_sensitivity'
            reasons[reason]+=1
            if ok: clean.append(r)
        pts=systematic_cap(thin_records(clean),a.cap_points)
        if len(pts)<a.min_points:
            audit.append({'taxon':taxon,'gbif_total':total,'n_fetched':len(raw),'n_clean':len(clean),'n_thinned_capped':len(pts),'filter_reasons_json':json.dumps(dict(reasons),sort_keys=True),'status':'insufficient_points'}); continue
        b1,m1=sample_one(a.bio1,pts); b6,m6=sample_one(a.bio6,pts); raster_meta={'bio1':m1,'bio6':m6}; clim=[]
        for i,r in enumerate(pts):
            if b1[i] is None or b6[i] is None: continue
            q={'taxon':taxon,'colour_state':seed['colour_state'],'section':seed.get('section',''),'gbif_key':r.get('key',''),'basisOfRecord':r.get('basisOfRecord',''),'latitude':r['decimalLatitude'],'longitude':r['decimalLongitude'],'bio1':b1[i],'bio6':b6[i]}; clim.append(q); point_rows.append(q)
        if len(clim)>=a.min_points: species.append(summarize(seed,clim)); status='admit'
        else: status='insufficient_climate_points'
        audit.append({'taxon':taxon,'gbif_total':total,'n_fetched':len(raw),'n_clean':len(clean),'n_thinned_capped':len(pts),'n_climate':len(clim),'filter_reasons_json':json.dumps(dict(reasons),sort_keys=True),'status':status})
        print(f"{taxon}: {status} total={total} clean={len(clean)} thin={len(pts)} mode={a.record_mode}",flush=True); time.sleep(.05)
    write_csv(a.out_dir/'gbif_taxon_matches.csv',matches); write_csv(a.out_dir/'occurrence_filter_audit.csv',audit); write_csv(a.out_dir/'thermal_points.csv',point_rows); write_csv(a.out_dir/'species_thermal_niches.csv',species); (a.out_dir/'chelsa_metadata.json').write_text(json.dumps(raster_meta,indent=2)+'\n')
    tests=[]; metrics=('bio1_median','bio6_median','bio6_q05','bio1_iqr'); pairs=(('A','W'),('A','Y'),('W','Y'))
    for metric in metrics:
        for s1,s2 in pairs:
            x=[float(r[metric]) for r in species if r['colour_state']==s1]; y=[float(r[metric]) for r in species if r['colour_state']==s2]
            if len(x)>=2 and len(y)>=2:
                obs,p2,pl,nperm,method,ncomb=perm_test(x,y)
                tests.append({'metric':metric,'state1':s1,'state2':s2,'n_state1':len(x),'n_state2':len(y),'mean_state1':float(np.mean(x)),'mean_state2':float(np.mean(y)),'difference_state1_minus_state2':obs,'two_sided_p':p2,'one_sided_p_state1_lower':pl,'test_method':method,'n_permutations':nperm,'total_label_combinations':str(ncomb)})
    write_csv(a.out_dir/'colour_pairwise_thermal_tests.csv',tests)
    section_rows=[]
    for metric in metrics:
        for s1,s2 in pairs:
            by=defaultdict(lambda:defaultdict(list))
            for r in species:
                sec=r.get('section','').strip()
                if sec and ';' not in sec: by[sec][r['colour_state']].append(float(r[metric]))
            diffs=[]
            for sec,d in by.items():
                if d[s1] and d[s2]: diffs.append((sec,float(np.mean(d[s1])-np.mean(d[s2])),len(d[s1]),len(d[s2])))
            if diffs:
                nonzero=[d for _,d,_,_ in diffs if abs(d)>1e-12]; n=len(nonzero); k=sum(d<0 for d in nonzero)
                if n:
                    probs=[math.comb(n,i)*0.5**n for i in range(n+1)]; pk=probs[k]; p2=min(1.0,sum(p for p in probs if p<=pk+1e-15))
                else: p2=1.0
                section_rows.append({'metric':metric,'state1':s1,'state2':s2,'n_shared_sections':len(diffs),'n_nonzero_sections':n,'n_sections_state1_lower':k,'two_sided_exact_sign_p':p2,'mean_section_difference':float(np.mean([d for _,d,_,_ in diffs])),'section_differences_json':json.dumps([{'section':s,'difference':d,'n1':n1,'n2':n2} for s,d,n1,n2 in diffs],ensure_ascii=False)})
    write_csv(a.out_dir/'section_blocked_colour_tests.csv',section_rows)
    summary={'n_seed_species':len(taxa),'n_admitted_species':len(species),'admitted_states':dict(Counter(r['colour_state'] for r in species)),'record_mode':a.record_mode,'climate':'CHELSA v2.1 BIO1/BIO6','gbif':'source-country constrained; cultivation/non-native/high-uncertainty filtering; 0.1-degree thinning; max points capped','claim_ceiling':'species-scale thermal association; section-block is a coarse sensitivity, not nuclear phylogenetic correction'}
    (a.out_dir/'analysis_summary.json').write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
