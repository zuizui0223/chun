#!/usr/bin/env python3
"""Execute the pre-frozen Petunieae phenotype-axis -> molecular-subspace gate.

Primary response variables follow the gate literally:
- pigment amount = raw summed anthocyanin mass fraction;
- hue = abundance-weighted anthocyanidin hydroxylation index among anthocyanin-positive taxa.

The source authors' log(pigment*100+1) transform is retained only as a labelled sensitivity
because that response transformation was not frozen in the pre-result gate. It cannot alter
the prospective PASS/MIXED/HOLD/FAIL classification.
"""
from __future__ import annotations
import argparse, copy, json, math
from pathlib import Path

import numpy as np
import pandas as pd
from Bio import Phylo
from scipy.linalg import solve_triangular

ANTHOCYANINS=(
    ('Pel_mgg',1.0),('Cyan_mgg',2.0),('Peon_mgg',2.0),
    ('Del_mgg',3.0),('Pet_mgg',3.0),('Malv_mgg',3.0),
)
SUBSPACES={
    'EARLY_CORE':('CHS','CHI','F3H'),
    'BRANCHING_HUE':('F3primeH','F35H','MTlike'),
    'LATE_OUTPUT':('DFR','ANS'),
    'REGULATORY':('AN1','AN11','JAF13','MYB27','MybsG6'),
}
SOURCE_ALIASES={
    "F3'H":'F3primeH',"F3'5'H":'F35H','MT':'MTlike','SG6-MYBs':'MybsG6',
}
OUTGROUP='BROW'

def r8(x):
    if x is None:return None
    return round(float(x),8)

def source_files(source:Path):
    m=json.loads((source/'source_manifest.json').read_text())
    if m['required_duplicate_identity']!='PASS_PHYLOCCA_PHYLOPCA_CSV_AND_TREE_OSF_METADATA_IDENTICAL':
        raise ValueError('source duplicate-identity gate not passed')
    if m['authoritative_prefix']!='phyloCCA':raise ValueError('unexpected authoritative source root')
    by={x['name']:source/'processed'/x['local_name'] for x in m['downloaded']}
    required={'tpm10k-mgg-combined-with-flavs.csv','11genestre_dated_pruned.tre','phyloCCA_expression_HPLC-with-flavs-final.r'}
    if set(by)!=required:raise ValueError(f'unexpected authoritative source set: {sorted(by)}')
    if any(not by[x].is_file() for x in required):raise ValueError('authoritative source file missing')
    return m,by

def deterministic_pc1(frame:pd.DataFrame, genes:tuple[str,...]):
    X=np.log1p(frame.loc[:,genes].to_numpy(dtype=float))
    mu=X.mean(axis=0);sd=X.std(axis=0,ddof=1)
    if np.any(~np.isfinite(sd)) or np.any(sd<=0):raise ValueError('non-identifiable subspace standardization')
    Z=(X-mu)/sd
    U,s,Vt=np.linalg.svd(Z,full_matrices=False)
    load=Vt[0].copy();score=U[:,0]*s[0]
    # Fix arbitrary SVD sign for byte-stable replay. AICc is sign invariant.
    if load.sum()<0:load=-load;score=-score
    var=float((s[0]**2)/(s@s))
    return score,var,{g:r8(v) for g,v in zip(genes,load)}

def covariance(tree,names):
    depths=tree.depths();tips={x.name:x for x in tree.get_terminals()}
    if not set(names)<=set(tips):raise ValueError('requested taxon absent from tree')
    n=len(names);V=np.zeros((n,n),float)
    for i,a in enumerate(names):
        V[i,i]=depths[tips[a]]
        for j in range(i):
            b=names[j];v=depths[tree.common_ancestor(a,b)];V[i,j]=V[j,i]=v
    if np.any(~np.isfinite(V)) or np.any(np.diag(V)<=0):raise ValueError('invalid Brownian covariance')
    return V

def pgls(y,x,V):
    y=np.asarray(y,float);x=np.asarray(x,float);n=len(y)
    if len(x)!=n or V.shape!=(n,n) or n<=5:raise ValueError('PGLS dimension failure')
    eps=1e-8*float(np.mean(np.diag(V)));V2=V+np.eye(n)*eps
    L=np.linalg.cholesky(V2);yw=solve_triangular(L,y,lower=True)
    X=np.column_stack((np.ones(n),x));Xw=solve_triangular(L,X,lower=True)
    beta=np.linalg.lstsq(Xw,yw,rcond=None)[0];res=yw-Xw@beta;rss=float(res@res)
    sig2=rss/n
    if sig2<=0:raise ValueError('nonpositive residual variance')
    logdet=2*float(np.log(np.diag(L)).sum())
    ll=-.5*(n*(math.log(2*math.pi)+1+math.log(sig2))+logdet)
    k=3;aic=2*k-2*ll;aicc=aic+2*k*(k+1)/(n-k-1)
    return {'n':n,'beta0':r8(beta[0]),'beta1':r8(beta[1]),'sigma2_mle':r8(sig2),'log_likelihood':r8(ll),'AICc':r8(aicc),'covariance_jitter':r8(eps)}

def pgls_null(y,V):
    y=np.asarray(y,float);n=len(y);eps=1e-8*float(np.mean(np.diag(V)));V2=V+np.eye(n)*eps
    L=np.linalg.cholesky(V2);yw=solve_triangular(L,y,lower=True);Xw=solve_triangular(L,np.ones((n,1)),lower=True)
    beta=np.linalg.lstsq(Xw,yw,rcond=None)[0];res=yw-Xw@beta;rss=float(res@res);sig2=rss/n
    logdet=2*float(np.log(np.diag(L)).sum());ll=-.5*(n*(math.log(2*math.pi)+1+math.log(sig2))+logdet)
    k=2;aic=2*k-2*ll;aicc=aic+2*k*(k+1)/(n-k-1)
    return {'n':n,'beta0':r8(beta[0]),'sigma2_mle':r8(sig2),'log_likelihood':r8(ll),'AICc':r8(aicc),'covariance_jitter':r8(eps)}

def axis_fit(frame,tree,response,names):
    d=frame.set_index('key_0').loc[names]
    V=covariance(tree,names);null=pgls_null(response,V);fits={}
    for tag,genes in SUBSPACES.items():
        if any(g not in d for g in genes):raise ValueError(f'{tag} missing frozen member gene')
        score,var,loads=deterministic_pc1(d,genes);fit=pgls(response,score,V)
        fit.update({'genes':list(genes),'pc1_variance_fraction':r8(var),'pc1_loadings':loads,'delta_AICc_vs_null':r8(fit['AICc']-null['AICc'])})
        fits[tag]=fit
    ranked=sorted(fits,key=lambda k:(fits[k]['AICc'],k));best=ranked[0];margin=fits[ranked[1]]['AICc']-fits[best]['AICc']
    for k in fits:fits[k]['delta_AICc_from_best']=r8(fits[k]['AICc']-fits[best]['AICc'])
    return {'n_taxa':len(names),'null_model':null,'models':fits,'ranking':ranked,'best_subspace':best,'best_margin_AICc':r8(margin)}

def run(source:Path):
    manifest,files=source_files(source)
    df=pd.read_csv(files['tpm10k-mgg-combined-with-flavs.csv'])
    required={'key_0',*(g for xs in SUBSPACES.values() for g in xs),*(c for c,_ in ANTHOCYANINS)}
    if not required<=set(df.columns):raise ValueError('required processed columns missing: '+','.join(sorted(required-set(df.columns))))
    if len(df)!=60 or df['key_0'].duplicated().any():raise ValueError('expected 60 unique processed taxa')
    if df[list(required-{'key_0'})].isna().any().any():raise ValueError('missing values in frozen analysis columns')
    tree=Phylo.read(str(files['11genestre_dated_pruned.tre']),'newick');tips=[x.name for x in tree.get_terminals()]
    if len(tips)!=60 or len(set(tips))!=60 or set(tips)!=set(df['key_0']):raise ValueError('processed table/tree one-to-one join failed')
    if tips.count(OUTGROUP)!=1:raise ValueError('source-defined Browallia outgroup absent')
    tree=copy.deepcopy(tree);tree.prune(OUTGROUP);tree.root.branch_length=0
    pet_tips=[x.name for x in tree.get_terminals()]
    depths=tree.depths();dvals=[depths[x] for x in tree.get_terminals()]
    # Source dated tree should be ultrametric up to printed rounding.
    ultrametric_spread=max(dvals)-min(dvals)
    if ultrametric_spread>1e-4:raise ValueError('source dated tree is unexpectedly non-ultrametric')
    dfi=df.set_index('key_0')
    amount=pd.Series(0.0,index=dfi.index)
    numerator=pd.Series(0.0,index=dfi.index)
    for col,w in ANTHOCYANINS:
        amount=amount+dfi[col].astype(float);numerator=numerator+w*dfi[col].astype(float)
    amount_names=pet_tips
    amount_y=amount.loc[amount_names].to_numpy(float)
    hue_names=[n for n in pet_tips if amount[n]>0]
    hue_y=(numerator.loc[hue_names]/amount.loc[hue_names]).to_numpy(float)
    amount_fit=axis_fit(df,tree,amount_y,amount_names)
    hue_fit=axis_fit(df,tree,hue_y,hue_names)
    # Source-method sensitivity only: Wheeler et al. multiply pigment mass fractions by 100 then log(x+1).
    amount_log_fit=axis_fit(df,tree,np.log1p(amount_y*100.0),amount_names)
    coverage=(len(amount_names)>=30 and len(amount_names)>=20 and len(hue_names)>=20 and len(SUBSPACES)>=3)
    hue_pass=(hue_fit['best_subspace']=='BRANCHING_HUE' and hue_fit['best_margin_AICc']>=2)
    amount_pass=(amount_fit['best_subspace'] in {'LATE_OUTPUT','REGULATORY'} and amount_fit['best_margin_AICc']>=2 and amount_fit['best_subspace']!='BRANCHING_HUE')
    expected_without_margin=(hue_fit['best_subspace']=='BRANCHING_HUE' or amount_fit['best_subspace'] in {'LATE_OUTPUT','REGULATORY'})
    if not coverage:classification='PETUNIEAE_PROSPECTIVE_BRIDGE_HOLD'
    elif hue_pass and amount_pass:classification='PETUNIEAE_PROSPECTIVE_BRIDGE_PASS'
    elif hue_pass or amount_pass or expected_without_margin:classification='PETUNIEAE_PROSPECTIVE_BRIDGE_MIXED'
    else:classification='PETUNIEAE_PROSPECTIVE_BRIDGE_FAIL'
    return {
      'version':'v0.1','source_osf_node':'zg9cu','source_doi':'10.1098/rspb.2023.0275',
      'source_manifest_version':manifest['version'],'source_duplicate_identity':manifest['required_duplicate_identity'],
      'source_defined_outgroup_excluded':'BROWALLIA_AMERICANA_BROW','source_rows':len(df),'petunieae_taxa':len(amount_names),'anthocyanin_positive_hue_taxa':len(hue_names),
      'tree_tip_join':'PASS_60_OF_60_BEFORE_SOURCE_OUTGROUP_EXCLUSION','dated_tree_root_to_tip_range':[r8(min(dvals)),r8(max(dvals))],'dated_tree_ultrametric_spread':r8(ultrametric_spread),
      'frozen_subspaces':{k:list(v) for k,v in SUBSPACES.items()},'source_aliases':SOURCE_ALIASES,
      'primary_amount_response':'RAW_SUMMED_ANTHOCYANIN_MASS_FRACTION_AS_FROZEN','hue_response':'ABUNDANCE_WEIGHTED_HYDROXYLATION_1_2_3_ANTHOCYANIN_POSITIVE_ONLY',
      'amount_axis':amount_fit,'hue_axis':hue_fit,
      'source_method_sensitivity_log_amount':{'response':'log(total_anthocyanin*100+1)_NOT_USED_FOR_GATE','fit':amount_log_fit},
      'pre_frozen_gate_components':{'coverage_pass':bool(coverage),'hue_axis_pass':bool(hue_pass),'amount_axis_pass':bool(amount_pass)},
      'pre_frozen_gate':classification,
      'prospective_replication_admitted':classification=='PETUNIEAE_PROSPECTIVE_BRIDGE_PASS',
      'interpretation_boundary':'Primary gate uses the raw summed anthocyanin amount specified before OSF value inspection. The source-method log-amount sensitivity cannot upgrade the preregistered classification. A PASS/MIXED/FAIL concerns phenotype-axis to molecular-subspace alignment, not universal causal genes, ecology, or transition direction.',
      'paper1_science_changed':False,
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    x=run(a.source);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n');print(json.dumps({'classification':x['pre_frozen_gate'],'petunieae_taxa':x['petunieae_taxa'],'hue_taxa':x['anthocyanin_positive_hue_taxa'],'amount_best':x['amount_axis']['best_subspace'],'amount_margin':x['amount_axis']['best_margin_AICc'],'hue_best':x['hue_axis']['best_subspace'],'hue_margin':x['hue_axis']['best_margin_AICc'],'log_amount_sensitivity_best':x['source_method_sensitivity_log_amount']['fit']['best_subspace'],'log_amount_sensitivity_margin':x['source_method_sensitivity_log_amount']['fit']['best_margin_AICc']},indent=2))
if __name__=='__main__':main()
