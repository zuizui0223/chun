#!/usr/bin/env python3
from __future__ import annotations
import argparse, collections, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from Bio import Phylo
from scipy.stats import rankdata

SEED=20260913
B=9999
TABLE_SHA='5843d4cd4eb253046f97349fa6bd285ca77e43e7a9c3aaa0e78fae3e8e391edd'
TREE_SHA='95b4a688d3d71417b712b37a2b04cdc22a9431be3172d6509def4435f5fd8614'
OUTGROUP='BROWALLIA_AMERICANA_BROW'
COMPOUNDS=['Pel_mgg','Cyan_mgg','Peon_mgg','Del_mgg','Pet_mgg','Malv_mgg']
NAMES=['coarse','intermediate','fine']


def sha256(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()


def source_files(source:Path):
    m=json.loads((source/'source_manifest.json').read_text())
    if m['required_duplicate_identity']!='PASS_PHYLOCCA_PHYLOPCA_CSV_AND_TREE_OSF_METADATA_IDENTICAL':
        raise ValueError('source duplicate-identity gate not passed')
    if m['authoritative_prefix']!='phyloCCA': raise ValueError('unexpected authoritative source root')
    by={x['name']:source/'processed'/x['local_name'] for x in m['downloaded']}
    table=by['tpm10k-mgg-combined-with-flavs.csv']; tree=by['11genestre_dated_pruned.tre']
    if sha256(table)!=TABLE_SHA or sha256(tree)!=TREE_SHA: raise ValueError('frozen source hash mismatch')
    return m,table,tree


def state_codes(row):
    vals=[float(row[c]) for c in COMPOUNDS]
    fine=''.join('1' if v>0 else '0' for v in vals)
    pel=vals[0]>0
    cya=(vals[1]>0 or vals[2]>0)
    dele=(vals[3]>0 or vals[4]>0 or vals[5]>0)
    inter=f'{int(pel)}{int(cya)}{int(dele)}'
    coarse='1' if any(v>0 for v in vals) else '0'
    return coarse,inter,fine


def enc(states):
    d={v:i for i,v in enumerate(sorted(set(states)))}
    return np.array([d[x] for x in states],dtype=np.int16)


def auc(states,ii,jj,ranks):
    same=states[ii]==states[jj]
    n1=int(same.sum()); n0=len(same)-n1
    if n1==0 or n0==0: raise ValueError('AUC undefined: same-state pair response has one class')
    u=float(ranks[same].sum())-n1*(n1+1)/2.0
    return u/(n1*n0)


def upper(null,obs):
    return (1.0+float(np.count_nonzero(null>=obs)))/(len(null)+1.0)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--prereg',type=Path,default=Path('data/petunieae_biochemical_resolution_profile_prereg_v0_1.json'))
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    p=json.loads(a.prereg.read_text())
    if p['status']!='FROZEN_BEFORE_PETUNIEAE_BIOCHEMICAL_RESOLUTION_AUC_COMPUTATION': raise ValueError('prereg status drift')
    if p['primary_statistic']['permutations']!=B or p['primary_statistic']['seed']!=SEED: raise ValueError('permutation contract drift')
    manifest,table_path,tree_path=source_files(a.source)
    df=pd.read_csv(table_path)
    req={'key_0',*COMPOUNDS}
    if not req<=set(df.columns): raise ValueError(f'missing source columns {sorted(req-set(df.columns))}')
    if len(df)!=60 or df['key_0'].duplicated().any(): raise ValueError('expected 60 unique processed source rows')
    if df[COMPOUNDS].isna().any().any(): raise ValueError('missing primary compound values')
    df=df[df['key_0']!=OUTGROUP].copy()
    if len(df)!=59: raise ValueError('source-defined outgroup exclusion did not yield 59 taxa')

    tree=Phylo.read(str(tree_path),'newick')
    tips=[t.name for t in tree.get_terminals()]
    if len(tips)!=60 or len(set(tips))!=60 or set(tips)!=set(pd.read_csv(table_path)['key_0']): raise ValueError('source table/tree pre-prune join failure')
    tree.prune(OUTGROUP); tree.root.branch_length=0
    tips=[t.name for t in tree.get_terminals()]
    if set(tips)!=set(df['key_0']): raise ValueError('Petunieae table/tree join failure after outgroup prune')

    by=df.set_index('key_0')
    raw={name:state_codes(by.loc[name]) for name in tips}
    fine0=collections.Counter(v[2] for v in raw.values())
    rare=sorted(k for k,v in fine0.items() if v<5)
    retained=[name for name in tips if raw[name][2] not in set(rare)]
    states={
      'coarse':[raw[n][0] for n in retained],
      'intermediate':[raw[n][1] for n in retained],
      'fine':[raw[n][2] for n in retained],
    }
    reasons=[]
    if len(retained)<20: reasons.append('COMMON_TIPS_LT_20')
    for nm in NAMES:
        if len(set(states[nm]))<2: reasons.append(f'{nm.upper()}_STATES_LT_2')
    if reasons:
        out={
          'version':'v0.1','status':'PETUNIEAE_BIOCHEMICAL_RESOLUTION_PROFILE_RESULT',
          'terminal_class':'HOLD_INSUFFICIENT_COMMON_FRAME_OR_STATE_VARIATION',
          'programme_role':p['programme_role'],'prospective_label':p['prospective_label'],
          'source_table_sha256':TABLE_SHA,'source_tree_sha256':TREE_SHA,
          'source_rows_before_outgroup':60,'petunieae_taxa_before_rare_filter':59,
          'rare_fine_states_excluded':rare,'eligible_tips':len(retained),'hold_reasons':reasons,
          'resolution_profile_AUC_computed':False,'winner_computed':False,'paper1_science_changed':False,
        }
        a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2)); return

    n=len(retained); ii,jj=np.triu_indices(n,1)
    terminals={t.name:t for t in tree.get_terminals()}
    dist=np.array([tree.distance(terminals[retained[int(i)]],terminals[retained[int(j)]]) for i,j in zip(ii,jj)],float)
    ranks=rankdata(-dist,method='average')
    encs={nm:enc(states[nm]) for nm in NAMES}
    obs=np.array([auc(encs[nm],ii,jj,ranks) for nm in NAMES],float)
    null=np.empty((3,B),float)
    rng=np.random.default_rng(SEED); base=np.arange(n)
    for b in range(B):
        perm=rng.permutation(base)
        for q,nm in enumerate(NAMES): null[q,b]=auc(encs[nm][perm],ii,jj,ranks)
    ps=np.array([upper(null[q],obs[q]) for q in range(3)])
    sig=(obs>0.5)&(ps<=0.05)
    order=np.argsort(-obs,kind='stable'); w=int(order[0]); r=int(order[1])
    delta=float(obs[w]-obs[r]); pwin=upper(null[w]-null[r],delta)
    if not bool(sig.any()): terminal='PROFILE_NO_PHYLOGENETIC_SIGNAL'
    elif bool(sig[w]) and delta>0 and pwin<=0.05:
        terminal={'coarse':'PROFILE_SIGNALLED_COARSE','intermediate':'PROFILE_SIGNALLED_INTERMEDIATE','fine':'PROFILE_SIGNALLED_FINE'}[NAMES[w]]
    else: terminal='PROFILE_SIGNALLED_TIED'
    pairwise={}
    for x in range(3):
        for y in range(x+1,3):
            d=float(obs[x]-obs[y]); pairwise[f'{NAMES[x]}_minus_{NAMES[y]}']={'observed':d,'p_gt_zero':upper(null[x]-null[y],d)}
            pairwise[f'{NAMES[y]}_minus_{NAMES[x]}']={'observed':-d,'p_gt_zero':upper(null[y]-null[x],-d)}
    out={
      'version':'v0.1','status':'PETUNIEAE_BIOCHEMICAL_RESOLUTION_PROFILE_RESULT','terminal_class':terminal,
      'programme_role':p['programme_role'],'prospective_label':p['prospective_label'],
      'source_osf_node':manifest['osf_node'],'source_table_sha256':TABLE_SHA,'source_tree_sha256':TREE_SHA,
      'seed':SEED,'permutations':B,
      'primary_frame':{
        'source_rows_before_outgroup':60,'petunieae_taxa_before_rare_filter':59,
        'rare_fine_states_excluded':rare,'eligible_tips':n,
        'coarse_state_counts':dict(sorted(collections.Counter(states['coarse']).items())),
        'intermediate_state_counts':dict(sorted(collections.Counter(states['intermediate']).items())),
        'fine_state_counts':dict(sorted(collections.Counter(states['fine']).items())),
      },
      'observed':dict(zip([f'AUC_{x}' for x in NAMES],[float(x) for x in obs])),
      'p_signal_one_sided':dict(zip(NAMES,[float(x) for x in ps])),
      'winner':NAMES[w],'runner_up':NAMES[r],'winner_minus_runner_up':delta,'p_winner_gt_runner':pwin,
      'pairwise_differences':pairwise,
      'post_hoc_upgrade_allowed':False,
      'do_not_count_as_new_prospective_replication':True,
      'paper1_science_changed':False,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'terminal_class':terminal,'eligible_tips':n,'AUC':dict(zip(NAMES,obs.tolist())),'p_signal':dict(zip(NAMES,ps.tolist())),'winner':NAMES[w],'p_winner_gt_runner':pwin,'rare_fine_states_excluded':rare},indent=2))

if __name__=='__main__': main()
