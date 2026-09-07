#!/usr/bin/env python3
"""Summarize executed outputs; never turn a boundary fit into regular inference."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
from analyze_linoideae_mk_v0_2 import load_snapshot,rooted_ingroup

def rounded(x):
 if isinstance(x,float):return float(format(x,'.6g')) if 0<abs(x)<1e-4 else round(x,6)
 if isinstance(x,dict):return {k:rounded(v) for k,v in x.items()}
 if isinstance(x,list):return [rounded(v) for v in x]
 return x

def interval(rows,key):return [min(r[key] for r in rows),max(r[key] for r in rows)]

def build(manifest,results):
 data=load_snapshot(manifest);results=Path(results);a=json.loads((results/'analysis_results.json').read_text());h=json.loads((results/'conditional_hue_results.json').read_text())
 if len(a['primary_fits'])!=36 or len(a['taxon_balanced_fits'])!=180 or len(h['conditional_hue_tests'])!=54:raise ValueError('incomplete model execution')
 if len(a['phylogenetic_signal'])!=54 or len(h['crop_exclusion_fits'])!=36:raise ValueError('incomplete sensitivity execution')
 if any(r['permutations']!=9999 for r in a['phylogenetic_signal']+h['conditional_hue_tests']):raise ValueError('not the frozen 9999-permutation analysis')
 for p in a['conditional_profiles']:
  f=next(r for r in a['primary_fits'] if r['alignment']==p['alignment'] and r['coding']==p['coding'] and r['root_prior']=='equal' and r['model']=='ARD')
  if f['optimization_bound_hit'] or f['high_rate_plateau']:raise ValueError('invalid profile promoted from boundary/plateau fit')
 white=[r for r in a['phylogenetic_signal'] if r['state_space']=='WHITE_NONWHITE'];six=[r for r in a['phylogenetic_signal'] if r['state_space']=='SIX_COLOURS'];cond=h['conditional_hue_tests']
 ingroup=[r for r in data['rows'] if r['tip_id']!='LINO001']
 fields=('alignment','model','root_prior','n_tips','AIC','rate_ratio_return_to_gain','root_probability_white','optimization_bound_hit','high_rate_plateau')
 union=[{k:r[k] for k in fields} for r in a['primary_fits'] if r['coding']=='UNION']
 profiles=[{k:v for k,v in r.items() if k!='profile_points'} for r in a['conditional_profiles']]
 out={'version':'0.2','status':'EXECUTED_SECOND_RADIATION_CONDITIONAL_REANALYSIS','source_terminal_rows':len(data['rows']),'source_ingroup_rows':len(ingroup),'source_ingroup_colour_set_disagreements':sum(set(r['figure2_states'])!=set(r['figureS5_states']) for r in ingroup),'admitted_ingroup_tips':{tag:len(rooted_ingroup(text).get_terminals()) for tag,text in data['trees'].items()},'primary_binary_model_fits':36,'taxon_balanced_model_fits':180,'balanced_draws_per_tree_coding':10,'source_codings':['FIGURE2','FIGURES5','UNION'],'white_binary_signal':{'tests':len(white),'p_range':interval(white,'lower_tail_p'),'observed_over_null_range':interval(white,'observed_over_null_mean')},'six_colour_signal':{'tests':len(six),'p_range':interval(six,'lower_tail_p'),'observed_over_null_range':interval(six,'observed_over_null_mean')},'hue_signal_conditional_on_white_status':{'tests':len(cond),'p_range':interval(cond,'lower_tail_p'),'observed_over_null_range':interval(cond,'observed_over_null_mean'),'crop_exclusion_included':True,'nuclear_ITS_included':True,'null':'All tips retain their white/nonwhite/ambiguous mask. Exchange six-colour allowed-state vectors only within those classes.'},'union_primary_fits':union,'regular_conditional_profiles':profiles,'boundary_primary_fits':[{'tree':r['alignment'],'coding':r['coding'],'model':r['model'],'prior':r['root_prior']} for r in a['primary_fits'] if r['optimization_bound_hit'] or r['high_rate_plateau']],'ancestral_white_admission':'NOT_ROBUST_TO_SOURCE_CODING_MODEL_AND_ROOT_PRIOR','pooled_white_ancestry_effect_estimated':False,'paper1_science_changed':False,'interpretation':'Hue-specific phylogenetic organization is supported in Linoideae even conditional on white status. This is not a universal direction, confirmed white ancestor, pigment mechanism, or ecological causal test. Sensitivity combinations are not independent clades.'}
 return rounded(out)

def compare(expected,actual,path='summary'):
 if type(expected) is not type(actual):raise ValueError(path+': type mismatch')
 if isinstance(expected,dict):
  if set(expected)!=set(actual):raise ValueError(path+': key mismatch')
  for k in expected:compare(expected[k],actual[k],path+'.'+k)
 elif isinstance(expected,list):
  if len(expected)!=len(actual):raise ValueError(path+': length mismatch')
  for i,(x,y) in enumerate(zip(expected,actual)):compare(x,y,f'{path}[{i}]')
 elif isinstance(expected,float):
  if not math.isclose(expected,actual,rel_tol=2e-4,abs_tol=2e-5):raise ValueError(f'{path}: numeric drift {expected} != {actual}')
 elif expected!=actual:raise ValueError(f'{path}: value drift')

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--results-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--expected',type=Path);args=ap.parse_args();s=build(args.manifest,args.results_dir)
 if args.expected:compare(json.loads(args.expected.read_text()),s)
 args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
