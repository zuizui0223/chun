#!/usr/bin/env python3
"""Conditional hue organization and exclusion sensitivity; no p-value selection."""
from __future__ import annotations
import argparse,json
from collections import defaultdict
from pathlib import Path
import numpy as np
from analyze_linoideae_mk_v0_2 import SEED,COLORS,load_snapshot,rooted_ingroup,subset,parsimony_scores,AmbiguousBinaryMk

def run(snapshot,out,permutations=9999):
 data=load_snapshot(snapshot);rows={r['tip_id']:r for r in data['rows']};results=[];exclusion_fits=[]
 for tag,text in data['trees'].items():
  tree=rooted_ingroup(text);names={t.name for t in tree.get_terminals()};groups=defaultdict(list)
  for n in sorted(names):groups[' '.join(rows[n]['source_taxon'].split()[:2])].append(n)
  rng=np.random.default_rng(SEED);draws=[sorted(str(rng.choice(groups[g])) for g in sorted(groups)) for i in range(3)]
  for policy in ('FIGURE2','FIGURES5','UNION'):
   mult={n:{COLORS.index(c) for c in ((rows[n]['figure2_states'] if policy=='FIGURE2' else rows[n]['figureS5_states']) if policy!='UNION' else rows[n]['figure2_states']+rows[n]['figureS5_states'])} for n in names}
   for draw,chosen in enumerate(draws):
    for exclusion in ('NONE','EXCLUDE_L_USITATISSIMUM'):
     sample=[n for n in chosen if exclusion=='NONE' or n!='LINO113'];t=subset(tree,set(sample));states={n:mult[n] for n in sample}
     sig=parsimony_scores(t,states,6,permutations,SEED,conditional_white=True)
     sig.update(tree=tag,coding=policy,draw=draw,exclusion=exclusion);results.append(sig)
   # Full admitted tree, source-crop exclusion, not selected using signal results.
   sample=names-{'LINO113'};t=subset(tree,sample);binary={n:{0 if c==0 else 1 for c in mult[n]} for n in sample}
   mk=AmbiguousBinaryMk(t,binary)
   for prior in ('equal','stationary'):
    for model in ('ER','ARD'):
     fit=mk.fit(model,prior,False);fit.update(tree=tag,coding=policy,exclusion='EXCLUDE_L_USITATISSIMUM');exclusion_fits.append(fit)
 out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
 result={'conditional_hue_tests':results,'crop_exclusion_fits':exclusion_fits,'null':'Each tip retains its definite WHITE, definite NONWHITE, or ambiguous binary status. Whole six-state vectors are shuffled only within those classes.','sampling':'One composite tip per source binomial; three deterministic seed-frozen draws. No accepted-taxonomy or natural-polymorphism assertion.','permutations':permutations,'seed':SEED}
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'tests':len(results),'p_range':[min(r['lower_tail_p'] for r in results),max(r['lower_tail_p'] for r in results)],'observed_over_null_range':[min(r['observed_over_null_mean'] for r in results),max(r['observed_over_null_mean'] for r in results)]}))
 return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--snapshot',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--permutations',type=int,default=9999);a=ap.parse_args();run(a.snapshot,a.out,a.permutations)
