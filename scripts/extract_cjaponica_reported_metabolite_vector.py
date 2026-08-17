#!/usr/bin/env python3
"""Quantify the C. japonica white-to-crimson metabolite-state vector.

Source: Fu et al. 2021, PMC8226227, Supplementary Table S2 embedded in
Data_Sheet_1.docx. Cultivar order from the source study:
CK=white, T1=pink, T2=deep pink, T3=red, T4=crimson; n=3 per state.

This is one independence cluster (CJAPONICA). The analysis uses reported
metabolite intensities and keeps anthocyanin, flavonol, proanthocyanidin and
flavanol dimensions separate.
"""
from __future__ import annotations

import argparse,csv,json,math
from pathlib import Path
from statistics import mean,stdev

from docx import Document
from scipy.stats import spearmanr

GROUPS={
    'CK_white':['CK1','CK2','CK3'],
    'T1_pink':['T1-1','T1-2','T1-3'],
    'T2_deep_pink':['T2-1','T2-2','T2-3'],
    'T3_red':['T3-1','T3-2','T3-3'],
    'T4_crimson':['T4-1','T4-2','T4-3'],
}
ORDER=list(GROUPS)
TARGET_CLASSES=['Anthocyanins','Flavonols','Proanthocyanidins','Flavanols']


def fnum(x):
    try:
        s=str(x or '').strip().replace(',','')
        return float(s) if s else 0.0
    except Exception:return 0.0


def hedges_g(a,b):
    a=list(a);b=list(b)
    if len(a)<2 or len(b)<2:return None
    va=stdev(a)**2;vb=stdev(b)**2;df=len(a)+len(b)-2
    sp=math.sqrt(((len(a)-1)*va+(len(b)-1)*vb)/df)
    if sp==0:return None
    d=(mean(a)-mean(b))/sp
    return (1-3/(4*(len(a)+len(b))-9))*d


def find_metabolite_table(doc):
    for t in doc.tables:
        if len(t.rows)<3:continue
        h0=[c.text.strip() for c in t.rows[0].cells]
        h1=[c.text.strip() for c in t.rows[1].cells] if len(t.rows)>1 else []
        if h0[:3]==['Compounds','Class I','Class II'] and 'CK1' in h1 and 'T4-3' in h1:
            return t,h1
    raise SystemExit('Supplementary Table S2 metabolite matrix not found')


def read_matrix(path):
    doc=Document(path);table,headers=find_metabolite_table(doc);rows=[]
    for r in table.rows[2:]:
        vals=[c.text.strip() for c in r.cells]
        if not vals or not vals[0]:continue
        rec={headers[i]:vals[i] for i in range(min(len(headers),len(vals)))}
        rows.append(rec)
    return rows


def main():
    p=argparse.ArgumentParser();p.add_argument('--docx',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);a=p.parse_args()
    rows=read_matrix(a.docx);out=[];compound=[]
    for cls in TARGET_CLASSES:
        rs=[r for r in rows if r.get('Class II')==cls]
        rep_totals={}
        for group,samples in GROUPS.items():
            rep_totals[group]=[sum(fnum(r.get(s)) for r in rs) for s in samples]
        mean_totals={g:mean(v) for g,v in rep_totals.items()}
        log_reps={g:[math.log2(x+1) for x in v] for g,v in rep_totals.items()}
        flat=[x for g in ORDER for x in log_reps[g]];rank=[i for i,g in enumerate(ORDER) for _ in log_reps[g]]
        rho,pv=spearmanr(rank,flat)
        ck=mean_totals['CK_white'];t4=mean_totals['T4_crimson'];t3=mean_totals['T3_red']
        out.append({'independence_cluster':'CJAPONICA','metabolite_class':cls,'n_compounds':len(rs),
          **{f'{g}_mean_total_intensity':mean_totals[g] for g in ORDER},
          'T4_crimson_minus_CK_white_log2_total':math.log2((t4+1)/(ck+1)),
          'T3_red_minus_CK_white_log2_total':math.log2((t3+1)/(ck+1)),
          'T4_vs_CK_hedges_g_log2_total':hedges_g(log_reps['T4_crimson'],log_reps['CK_white']),
          'spearman_colour_order_vs_log2_rep_total':rho,'spearman_p':pv,
          'claim_ceiling':'within-study reported metabolite-class state vector; one C. japonica independence cluster'})
        for r in rs:
            means={g:mean([fnum(r.get(s)) for s in samples]) for g,samples in GROUPS.items()}
            compound.append({'independence_cluster':'CJAPONICA','compound':r.get('Compounds',''),'metabolite_class':cls,
              **{f'{g}_mean_intensity':means[g] for g in ORDER},
              'T4_gt_CK':means['T4_crimson']>means['CK_white'],
              'monotonic_CK_T1_T2_T3_T4':all(means[ORDER[i]]<=means[ORDER[i+1]] for i in range(len(ORDER)-1)),
              'claim_ceiling':'reported compound mean across three replicates; compounds are not independent studies'})
    look={r['metabolite_class']:r for r in out};contr=[]
    anth=look['Anthocyanins']
    for cls,label in [('Flavonols','anthocyanin_minus_flavonol'),('Proanthocyanidins','anthocyanin_minus_proanthocyanidin')]:
        x=look[cls]
        for cmp in ['T4_crimson_minus_CK_white','T3_red_minus_CK_white']:
            key=cmp+'_log2_total'
            contr.append({'independence_cluster':'CJAPONICA','contrast':cmp,'state_vector_axis':label,
              'difference_of_log2_total_effects':float(anth[key])-float(x[key]),
              'claim_ceiling':'within-study relative allocation effect; biochemical dimensions kept separate'})
    a.out_dir.mkdir(parents=True,exist_ok=True)
    def write(name,data):
        with (a.out_dir/name).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]) if data else ['empty']);w.writeheader();w.writerows(data)
    write('metabolite_class_effects.csv',out);write('compound_effects.csv',compound);write('state_vector_contrasts.csv',contr)
    ac=look['Anthocyanins'];fl=look['Flavonols'];pa=look['Proanthocyanidins']
    summary={'independence_cluster':'CJAPONICA','phenotype_order':'CK=white; T1=pink; T2=deep pink; T3=red; T4=crimson','n_metabolites':len(rows),'anthocyanin_compounds':ac['n_compounds'],'flavonol_compounds':fl['n_compounds'],'PA_compounds':pa['n_compounds'],'anthocyanin_T4_CK_log2_total':ac['T4_crimson_minus_CK_white_log2_total'],'flavonol_T4_CK_log2_total':fl['T4_crimson_minus_CK_white_log2_total'],'PA_T4_CK_log2_total':pa['T4_crimson_minus_CK_white_log2_total'],'anthocyanin_colour_order_rho':ac['spearman_colour_order_vs_log2_rep_total'],'flavonol_colour_order_rho':fl['spearman_colour_order_vs_log2_rep_total'],'anthocyanin_T4_CK_hedges_g':ac['T4_vs_CK_hedges_g_log2_total'],'anthocyanin_minus_flavonol_T4_CK':next(r['difference_of_log2_total_effects'] for r in contr if r['contrast']=='T4_crimson_minus_CK_white' and r['state_vector_axis']=='anthocyanin_minus_flavonol'),'anthocyanin_minus_PA_T4_CK':next(r['difference_of_log2_total_effects'] for r in contr if r['contrast']=='T4_crimson_minus_CK_white' and r['state_vector_axis']=='anthocyanin_minus_proanthocyanidin'),'claim_ceiling':'one C. japonica cultivar-gradient system; quantitative metabolite corroboration, not cross-study pooled effect'}
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
