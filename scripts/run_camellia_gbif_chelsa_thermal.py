#!/usr/bin/env python3
"""Fast Camellia thermal-niche screen: GBIF + local CHELSA BIO1/BIO6.

This is the decisive preliminary test for the simple cold-enabler hypothesis.
It deliberately restricts climate to mean annual temperature (BIO1) and minimum
temperature of the coldest month (BIO6), and treats species as replicate units.
"""
from __future__ import annotations
import argparse, csv, json, math, pathlib, time
from collections import Counter
import numpy as np
import rasterio
from run_camellia_gbif_worldclim_niche import (
    read_csv, write_csv, gbif_match, fetch_occurrences, keep_occurrence,
    thin_records, exact_label_permutation,
)

def decode_temp(raw, scale, offset):
    val=float(raw)*scale+offset
    if scale==1.0 and offset==0.0 and val>100:
        val=float(raw)*0.1-273.15
    return float(val)

def systematic_cap(rows, cap=120):
    if len(rows)<=cap: return rows
    rows=sorted(rows,key=lambda r:(float(r['decimalLatitude']),float(r['decimalLongitude']),str(r.get('key',''))))
    idx=np.linspace(0,len(rows)-1,cap,dtype=int)
    return [rows[i] for i in sorted(set(idx.tolist()))]

def sample_one(path, points):
    coords=[(float(r['decimalLongitude']),float(r['decimalLatitude'])) for r in points]
    with rasterio.open(path) as src:
        sc=float(src.scales[0] if src.scales else 1.0); off=float(src.offsets[0] if src.offsets else 0.0)
        vals=[]
        for v in src.sample(coords,indexes=1,masked=True):
            x=v[0]
            vals.append(None if np.ma.is_masked(x) else decode_temp(float(x),sc,off))
        meta={'scale':sc,'offset':off,'dtype':str(src.dtypes[0]),'crs':str(src.crs),'nodata':src.nodata}
    return vals,meta

def summarize(seed, rows):
    out={'taxon':seed['taxon'],'colour_state':seed['colour_state'],'pigment_proxy':seed['pigment_proxy'],'analysis_role':seed['analysis_role'],'n_points':len(rows)}
    for b in (1,6):
        v=np.array([float(r[f'bio{b}']) for r in rows if r.get(f'bio{b}') not in (None,'')],dtype=float)
        for n,x in [('mean',np.mean(v)),('median',np.median(v)),('q05',np.quantile(v,.05)),('q95',np.quantile(v,.95)),('iqr',np.quantile(v,.75)-np.quantile(v,.25))]:
            out[f'bio{b}_{n}']=float(x)
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--taxa',type=pathlib.Path,required=True); ap.add_argument('--bio1',type=pathlib.Path,required=True); ap.add_argument('--bio6',type=pathlib.Path,required=True); ap.add_argument('--out-dir',type=pathlib.Path,required=True); ap.add_argument('--min-points',type=int,default=5); ap.add_argument('--cap-points',type=int,default=120); a=ap.parse_args(); a.out_dir.mkdir(parents=True,exist_ok=True)
    taxa=read_csv(a.taxa); species=[]; audit=[]; matches=[]; points_out=[]; raster_meta={}
    for seed in taxa:
        taxon=seed['taxon'].strip(); m=gbif_match(taxon); matches.append({**seed,**m})
        if not m['usageKey']:
            audit.append({'taxon':taxon,'status':'no_gbif_match'}); continue
        key=int(m['usageKey']); raw=[]; total=0
        for country in [x.strip() for x in seed['native_country_codes'].split(';') if x.strip()]:
            rr,n=fetch_occurrences(key,country,3000); raw.extend(rr); total+=n
        raw=list({str(r.get('key',i)):r for i,r in enumerate(raw)}.values()); reasons=Counter(); clean=[]
        for r in raw:
            keep,reason=keep_occurrence(r); reasons[reason]+=1
            if keep: clean.append(r)
        thin=systematic_cap(thin_records(clean),a.cap_points)
        if len(thin)<a.min_points:
            audit.append({'taxon':taxon,'gbif_taxon_key':key,'gbif_total':total,'n_fetched':len(raw),'n_clean':len(clean),'n_thinned_capped':len(thin),'filter_reasons_json':json.dumps(dict(reasons),sort_keys=True),'status':'insufficient_points'}); continue
        b1,m1=sample_one(a.bio1,thin); b6,m6=sample_one(a.bio6,thin); raster_meta={'bio1':m1,'bio6':m6}
        clim=[]
        for i,r in enumerate(thin):
            if b1[i] is None or b6[i] is None: continue
            q={'taxon':taxon,'colour_state':seed['colour_state'],'gbif_key':r.get('key',''),'latitude':r['decimalLatitude'],'longitude':r['decimalLongitude'],'bio1':b1[i],'bio6':b6[i]}; clim.append(q); points_out.append(q)
        if len(clim)>=a.min_points: species.append(summarize(seed,clim)); status='admit'
        else: status='insufficient_climate_points'
        audit.append({'taxon':taxon,'gbif_taxon_key':key,'gbif_total':total,'n_fetched':len(raw),'n_clean':len(clean),'n_thinned_capped':len(thin),'n_climate':len(clim),'filter_reasons_json':json.dumps(dict(reasons),sort_keys=True),'status':status})
        print(taxon,total,len(raw),len(clean),len(thin),len(clim),flush=True); time.sleep(.1)
    write_csv(a.out_dir/'gbif_taxon_matches.csv',matches); write_csv(a.out_dir/'occurrence_filter_audit.csv',audit); write_csv(a.out_dir/'thinned_thermal_points.csv',points_out); write_csv(a.out_dir/'species_thermal_niches.csv',species)
    (a.out_dir/'chelsa_temperature_metadata.json').write_text(json.dumps(raster_meta,indent=2)+'\n')
    tests=[]
    for metric in ('bio1_median','bio6_median','bio6_q05','bio1_iqr'):
        aa=[float(r[metric]) for r in species if r['colour_state']=='A']; yy=[float(r[metric]) for r in species if r['colour_state']=='Y']
        if len(aa)>=2 and len(yy)>=2:
            x=exact_label_permutation(aa,yy); tests.append({'metric':metric,'n_A':len(aa),'n_Y':len(yy),'A_mean':float(np.mean(aa)),'Y_mean':float(np.mean(yy)),**x,'scope':'species-level exact permutation; native-country GBIF filtering; not phylogenetically corrected'})
    write_csv(a.out_dir/'A_vs_Y_thermal_tests.csv',tests)
    bt={r['taxon']:r for r in species}; pair=[]
    if 'Camellia japonica' in bt and 'Camellia rusticana' in bt:
        for metric in ('bio1_median','bio6_median','bio6_q05'):
            pair.append({'metric':metric,'japonica':bt['Camellia japonica'][metric],'rusticana':bt['Camellia rusticana'][metric],'rusticana_minus_japonica':float(bt['Camellia rusticana'][metric])-float(bt['Camellia japonica'][metric])})
    write_csv(a.out_dir/'japonica_rusticana_thermal_pair.csv',pair)
    summary={'n_taxa_seeded':len(taxa),'n_species_admitted':len(species),'admitted_by_colour':dict(Counter(r['colour_state'] for r in species)),'thermal_provider':'CHELSA v2.1 1981-2010 BIO1/BIO6','claim_ceiling':'direct preliminary species-level thermal association; not phylogenetically corrected or causal'}
    (a.out_dir/'analysis_summary.json').write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
