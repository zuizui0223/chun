#!/usr/bin/env python3
"""Pre-branch tests for Camellia ultimate-cause hypotheses.

These tests deliberately precede inspection of the new nuclear topology. They use
only the frozen runtime91 taxon roster plus independently assembled visible-colour,
climate and mechanistic evidence. Traditional sections are used only as a
history proxy until the nuclear species tree is admitted.
"""
from __future__ import annotations
import argparse, csv, json, math, pathlib, re
from collections import Counter, defaultdict
import numpy as np


def read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def taxon_key(x):
    return re.sub(r'\s+', ' ', (x or '').strip()).casefold()


def norm_section(x):
    vals=[]
    for part in (x or '').split(';'):
        s=re.sub(r'^sect(?:ion)?\.?\s*', '', part.strip(), flags=re.I)
        s=re.sub(r'\s+', ' ', s).strip().casefold()
        if s and s not in vals: vals.append(s)
    return vals[0] if len(vals)==1 else ''


def p_empirical(k, n):
    return (k+1)/(n+1)


def concentration_test(rows, state, nperm, rng):
    labels=np.array([r['colour_state'] for r in rows], dtype=object)
    secs=np.array([r['section_norm'] for r in rows], dtype=object)
    n_state=int(np.sum(labels==state))
    if n_state < 2:
        return {'state':state,'n_state':n_state,'observed_sections':None,'expected_sections':None,'breadth_p':None,'observed_hhi':None,'hhi_p':None}
    def stats(lab):
        ss=secs[lab==state]
        c=Counter(ss.tolist())
        breadth=len(c)
        hhi=sum((v/len(ss))**2 for v in c.values())
        return breadth,hhi
    obs_b,obs_h=stats(labels)
    nb=np.empty(nperm,dtype=float); nh=np.empty(nperm,dtype=float)
    for i in range(nperm):
        p=rng.permutation(labels)
        nb[i],nh[i]=stats(p)
    return {
        'state':state,'n_state':n_state,'observed_sections':obs_b,
        'expected_sections':float(nb.mean()),'breadth_p':p_empirical(int(np.sum(nb<=obs_b)),nperm),
        'observed_hhi':obs_h,'expected_hhi':float(nh.mean()),'hhi_p':p_empirical(int(np.sum(nh>=obs_h)),nperm),
    }


def median_diff(values, labels):
    a=values[labels=='A']; w=values[labels=='W']
    if len(a)==0 or len(w)==0: return np.nan
    return float(np.median(a)-np.median(w))


def climate_direct_tests(rows, metrics, nperm, rng):
    labels=np.array([r['colour_state'] for r in rows],dtype=object)
    out=[]
    for m in metrics:
        vals=np.array([float(r[m]) for r in rows],dtype=float)
        obs=median_diff(vals,labels)
        null=np.empty(nperm)
        for i in range(nperm): null[i]=median_diff(vals,rng.permutation(labels))
        out.append({
            'metric':m,'n_A':int(np.sum(labels=='A')),'n_W':int(np.sum(labels=='W')),
            'median_A':float(np.median(vals[labels=='A'])),'median_W':float(np.median(vals[labels=='W'])),
            'A_minus_W':obs,
            'two_sided_p':p_empirical(int(np.sum(np.abs(null)>=abs(obs))),nperm),
            'A_colder_one_sided_p':p_empirical(int(np.sum(null<=obs)),nperm),
        })
    return out


def block_permute(labels, sections, rng):
    out=labels.copy()
    for s in sorted(set(sections)):
        idx=np.where(sections==s)[0]
        if len(idx)>1: out[idx]=rng.permutation(out[idx])
    return out


def climate_block_tests(rows, metrics, nperm, rng):
    labels=np.array([r['colour_state'] for r in rows],dtype=object)
    secs=np.array([r['section_norm'] for r in rows],dtype=object)
    movable_sections=sum(1 for s in set(secs) if len(set(labels[secs==s]))>1)
    out=[]
    for m in metrics:
        vals=np.array([float(r[m]) for r in rows],dtype=float)
        obs=median_diff(vals,labels)
        null=np.empty(nperm)
        for i in range(nperm): null[i]=median_diff(vals,block_permute(labels,secs,rng))
        out.append({
            'metric':m,'movable_sections':movable_sections,'A_minus_W':obs,
            'two_sided_p':p_empirical(int(np.sum(np.abs(null)>=abs(obs))),nperm),
            'A_colder_one_sided_p':p_empirical(int(np.sum(null<=obs)),nperm),
        })
    return out


def pairwise_climate_test(rows, metrics, nperm, rng):
    X=np.array([[float(r[m]) for m in metrics] for r in rows],dtype=float)
    mu=X.mean(axis=0); sd=X.std(axis=0,ddof=1); sd[sd==0]=1
    X=(X-mu)/sd
    labels=np.array([r['colour_state'] for r in rows],dtype=object)
    secs=np.array([r['section_norm'] for r in rows],dtype=object)
    pairs=[]
    for i in range(len(rows)):
        for j in range(i+1,len(rows)):
            if secs[i] and secs[i]==secs[j]:
                pairs.append((i,j,float(np.linalg.norm(X[i]-X[j]))))
    def stat(lab):
        same=[d for i,j,d in pairs if lab[i]==lab[j]]
        diff=[d for i,j,d in pairs if lab[i]!=lab[j]]
        if not same or not diff: return np.nan,np.nan,np.nan,len(same),len(diff)
        ms=float(np.mean(same)); md=float(np.mean(diff)); return md-ms,ms,md,len(same),len(diff)
    obs,ms,md,ns,nd=stat(labels)
    null=[]
    for _ in range(nperm):
        v,*_=stat(block_permute(labels,secs,rng))
        if not math.isnan(v): null.append(v)
    null=np.array(null,dtype=float)
    return {
        'n_pairs_same_colour':ns,'n_pairs_different_colour':nd,
        'mean_same_colour_distance':ms,'mean_different_colour_distance':md,
        'different_minus_same':obs,'one_sided_p_for_greater_divergence':p_empirical(int(np.sum(null>=obs)),len(null)),
        'n_valid_permutations':len(null),
    }


def mechanism_retention(mech):
    by=defaultdict(list)
    for r in mech:
        if 'white' in (r.get('colors') or '').lower(): by[r['independence_cluster']].append(r)
    rows=[]
    for cl,rs in sorted(by.items()):
        vals={(r.get('structural_gene_loss_required') or '').strip().lower() for r in rs}
        if 'yes' in vals: loss='required'
        elif 'no' in vals: loss='explicitly_not_required'
        else: loss='no_evidence_required'
        reversible=any((r.get('within_genotype_or_developmental_switch') or '').strip().lower()=='yes' for r in rs)
        rows.append({'independence_cluster':cl,'structural_loss_status':loss,'reversible_switch_evidence':reversible})
    c=Counter(r['structural_loss_status'] for r in rows)
    return rows,{
        'n_white_containing_independence_clusters':len(rows),
        'n_structural_loss_required':c['required'],
        'n_explicitly_not_required':c['explicitly_not_required'],
        'n_no_evidence_required':c['no_evidence_required'],
        'n_reversible_white_switch_clusters':sum(r['reversible_switch_evidence'] for r in rows),
    }


def write_csv(path, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows: path.write_text('',encoding='utf-8'); return
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--panel',required=True); ap.add_argument('--fan-colour',required=True)
    ap.add_argument('--climate',required=True); ap.add_argument('--mechanism',required=True)
    ap.add_argument('--out-dir',type=pathlib.Path,required=True); ap.add_argument('--permutations',type=int,default=100000); ap.add_argument('--seed',type=int,default=20260820)
    a=ap.parse_args(); rng=np.random.default_rng(a.seed)
    panel={taxon_key(r['source_taxon']) for r in read_csv(a.panel)}
    fan=read_csv(a.fan_colour); climate={taxon_key(r['taxon']):r for r in read_csv(a.climate)}
    colour=[]
    for r in fan:
        if taxon_key(r['taxon']) not in panel: continue
        sec=norm_section(r.get('section',''))
        if sec: colour.append({'taxon':r['taxon'],'colour_state':r['colour_state'],'section_norm':sec,'native_country_codes':r.get('native_country_codes','')})
    conc=[concentration_test(colour,s,a.permutations,rng) for s in ['A','W','Y']]
    climate_rows=[]
    for r in colour:
        c=climate.get(taxon_key(r['taxon']))
        if c and r['colour_state'] in {'A','W'}:
            climate_rows.append({**r,'bio1_median':c['bio1_median'],'bio6_median':c['bio6_median'],'bio1_iqr':c['bio1_iqr']})
    metrics=['bio1_median','bio6_median','bio1_iqr']
    direct=climate_direct_tests(climate_rows,metrics,a.permutations,rng)
    block=climate_block_tests(climate_rows,metrics,a.permutations,rng)
    pair=pairwise_climate_test(climate_rows,metrics,a.permutations,rng)
    mech_rows,mech_summary=mechanism_retention(read_csv(a.mechanism))
    A=next(x for x in conc if x['state']=='A'); Y=next(x for x in conc if x['state']=='Y')
    cold={r['metric']:r for r in direct}
    h2_support=all(cold[m]['A_minus_W']<0 and cold[m]['A_colder_one_sided_p']<0.05 for m in ['bio1_median','bio6_median'])
    summary={
        'n_runtime_colour_with_unambiguous_section':len(colour),
        'state_counts':dict(Counter(r['colour_state'] for r in colour)),
        'n_AW_colour_climate':len(climate_rows),
        'H1_ecological_filtering_history_proxy':{'status':'preliminary_support' if A['breadth_p']<0.05 and A['hhi_p']<0.05 else 'not_supported','A_result':A,'claim_ceiling':'traditional section is a history proxy; nuclear branch test remains decisive'},
        'H2_direct_cold_adaptation':{'status':'supported' if h2_support else 'not_supported','direct_tests':direct,'section_block_tests':block,'within_section_pairwise':pair,'claim_ceiling':'tests direct coarse visible-colour climate coupling, not pollinator mediation'},
        'H3_molecular_memory_retention':{'status':'compatible_and_supported_at_accessibility_level' if mech_summary['n_structural_loss_required']==0 and mech_summary['n_reversible_white_switch_clusters']>=2 else 'inconclusive','summary':mech_summary,'claim_ceiling':'absence of required structural loss plus reversible switches supports retention/accessibility, but does not prove macro reactivation on ancestral branches'},
        'H4_lineage_permissivity':{'status':'preliminary_support' if A['breadth_p']<0.05 and A['hhi_p']<0.05 else 'not_supported','claim_ceiling':'same statistic as H1 at section-proxy level; replace section with independent nuclear branches after PR31'},
        'H5_yellow_history_dependence':{'status':'preliminary_support' if Y['n_state']>=3 and Y['breadth_p']<0.05 and Y['hhi_p']<0.05 else 'underpowered_or_not_supported','Y_result':Y,'claim_ceiling':'current runtime91 contains few Y tips; full Fan seed result remains broader evidence'},
    }
    a.out_dir.mkdir(parents=True,exist_ok=True)
    write_csv(a.out_dir/'section_concentration.csv',conc); write_csv(a.out_dir/'climate_direct.csv',direct); write_csv(a.out_dir/'climate_section_block.csv',block); write_csv(a.out_dir/'mechanism_retention_clusters.csv',mech_rows)
    (a.out_dir/'climate_pairwise.json').write_text(json.dumps(pair,indent=2)+'\n',encoding='utf-8')
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
