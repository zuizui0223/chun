#!/usr/bin/env python3
"""Cross-system synthesis of quantitative Camellia pigment-state vectors.

Expression effects and metabolite ion-intensity effects are not pooled as if
commensurate. The comparable unit is the biological independence cluster and
whether a pre-defined relative allocation contrast has the same direction.
"""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
from scipy.stats import beta


def exact_sign_p(y,n):
    N=y+n;k=min(y,n)
    if N==0:return None
    return min(1.0,2*sum(math.comb(N,i) for i in range(k+1))/(2**N))

def main():
    p=argparse.ArgumentParser();p.add_argument('--csin',type=Path,required=True);p.add_argument('--cret',type=Path,required=True);p.add_argument('--cjap',type=Path,required=True);p.add_argument('--systems-output',type=Path,required=True);p.add_argument('--summary-output',type=Path,required=True);a=p.parse_args()
    cs=json.loads(a.csin.read_text());cr=json.loads(a.cret.read_text());cj=json.loads(a.cjap.read_text())
    systems=[
      {'independence_cluster':'CSIN_WHITE_PINK','quantitative_layer':'reported_expression','contrast':'anthocyanin_minus_flavonol','positive':cs['S6_anthocyanin_minus_flavonol_positive_stages']=='5/5','within_system_evidence':cs['S6_anthocyanin_minus_flavonol_positive_stages'],'effect_value':'','effect_unit':'stage-direction consistency','heterogeneity_note':'FLS changes sign through development while DFR remains pink-directed'},
      {'independence_cluster':'CRETICULATA','quantitative_layer':'reported_metabolites','contrast':'anthocyanin_minus_flavonol','positive':float(cr['anthocyanin_minus_flavonol_red_white'])>0,'within_system_evidence':'red vs white','effect_value':cr['anthocyanin_minus_flavonol_red_white'],'effect_unit':'difference of class log2 fold changes','heterogeneity_note':'broad enzyme homolog families have mixed paralog directions; highlighted UFGT set is cleaner'},
      {'independence_cluster':'CJAPONICA','quantitative_layer':'reported_metabolites','contrast':'anthocyanin_minus_flavonol','positive':float(cj['anthocyanin_minus_flavonol_T4_CK'])>0,'within_system_evidence':'crimson T4 vs white CK','effect_value':cj['anthocyanin_minus_flavonol_T4_CK'],'effect_unit':'difference of class log2 fold changes','heterogeneity_note':'five-colour gradient; anthocyanin rises strongly while flavonol total declines'},
      {'independence_cluster':'CSIN_WHITE_PINK','quantitative_layer':'reported_expression','contrast':'anthocyanin_minus_proanthocyanidin','positive':True,'within_system_evidence':cs['S6_anthocyanin_minus_PA_positive_stages'],'effect_value':'','effect_unit':'stage-direction consistency','heterogeneity_note':'only 3/5 stages positive; PA cannot be merged with FLS'},
      {'independence_cluster':'CRETICULATA','quantitative_layer':'reported_metabolites','contrast':'anthocyanin_minus_proanthocyanidin','positive':float(cr['anthocyanin_minus_PA_red_white'])>0,'within_system_evidence':'red vs white','effect_value':cr['anthocyanin_minus_PA_red_white'],'effect_unit':'difference of class log2 fold changes','heterogeneity_note':'PA total slightly white-enriched while anthocyanin is strongly red-enriched'},
      {'independence_cluster':'CJAPONICA','quantitative_layer':'reported_metabolites','contrast':'anthocyanin_minus_proanthocyanidin','positive':float(cj['anthocyanin_minus_PA_T4_CK'])>0,'within_system_evidence':'crimson T4 vs white CK','effect_value':cj['anthocyanin_minus_PA_T4_CK'],'effect_unit':'difference of class log2 fold changes','heterogeneity_note':'PA total declines moderately across colour intensity while anthocyanin rises'},
    ]
    for r in systems:r['claim_ceiling']='independence-cluster concordance only; expression and metabolite effect magnitudes are not pooled across assays'
    summaries=[]
    for contrast in ['anthocyanin_minus_flavonol','anthocyanin_minus_proanthocyanidin']:
        rs=[r for r in systems if r['contrast']==contrast]
        y=sum(bool(r['positive']) for r in rs);n=len(rs)-y
        lo,hi=beta.ppf([.025,.975],1+y,1+n)
        summaries.append({'contrast':contrast,'n_independence_clusters':len(rs),'n_positive_systems':y,'n_negative_systems':n,'exact_two_sided_sign_p':exact_sign_p(y,n),'beta11_posterior_mean_directional_concordance':(1+y)/(2+len(rs)),'beta11_ci025':lo,'beta11_ci975':hi,'posterior_p_direction_gt_half':1-beta.cdf(.5,1+y,1+n),'posterior_p_direction_gt_0_75':1-beta.cdf(.75,1+y,1+n),'interpretation':('three-system concordance supports state-vector separation but is not statistically mature' if contrast=='anthocyanin_minus_flavonol' else 'overall contrast is positive in all systems but C. sinensis is developmentally heterogeneous'),'claim_ceiling':'selected quantitative systems; not a natural frequency estimate and not a pooled common effect size'})
    a.systems_output.parent.mkdir(parents=True,exist_ok=True)
    for path,data in [(a.systems_output,systems),(a.summary_output,summaries)]:
        with path.open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader()
            for r in data:
                q={k:(f'{v:.8f}' if isinstance(v,float) else v) for k,v in r.items()};w.writerow(q)

if __name__=='__main__':main()
