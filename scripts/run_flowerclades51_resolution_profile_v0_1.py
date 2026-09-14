#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,collections,hashlib,io,json,re,zipfile
from pathlib import Path
import numpy as np
from Bio import Phylo
from scipy.stats import rankdata
from numba import njit,prange

SEED=20260913; B=9999
CSV_SHA='a253308785e4cbd0e361b3ca04cdfdae29c523eefa843375cebf8030ee0874af'
TREES_SHA='ae5c82945e5bf9c29bcabc52d6029acd8d4f5be1fe9141fad95918eacb4f674d'
MAP={'black':('DARK','NONWHITE'),'purple':('COOL','NONWHITE'),'green':('COOL','NONWHITE'),'orange':('WARM','NONWHITE'),'pink':('WARM','NONWHITE'),'red':('WARM','NONWHITE'),'white':('WHITE','WHITE'),'yellow':('WARM','NONWHITE')}
NAMES=['coarse','intermediate','fine']

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def norm(x): return re.sub(r'\s+',' ',str(x).strip().replace('_',' ')).lower()
def enc(a):
 d={v:i for i,v in enumerate(sorted(set(a)))}
 return np.array([d[x] for x in a],dtype=np.int8)
def auc(labels,ii,jj,ranks):
 y=labels[ii]==labels[jj]; n1=int(y.sum()); n0=len(y)-n1
 return (float(ranks[y].sum())-n1*(n1+1)/2)/(n1*n0),n1
def eup(x,o): return (1+float(np.count_nonzero(x>=o)))/(len(x)+1)

@njit(parallel=True)
def perm3(perms,ii,jj,ranks,c,i,f,npc,npi,npf):
 Bn=perms.shape[0]; m=ii.shape[0]
 oc=np.empty(Bn); oi=np.empty(Bn); of=np.empty(Bn)
 bc=npc*(npc+1)/2.; bi=npi*(npi+1)/2.; bf=npf*(npf+1)/2.
 for b in prange(Bn):
  p=perms[b]; sc=0.; si=0.; sf=0.
  for k in range(m):
   a=p[ii[k]]; d=p[jj[k]]; r=ranks[k]
   if c[a]==c[d]: sc+=r
   if i[a]==i[d]: si+=r
   if f[a]==f[d]: sf+=r
  oc[b]=(sc-bc)/(npc*(m-npc)); oi[b]=(si-bi)/(npi*(m-npi)); of[b]=(sf-bf)/(npf*(m-npf))
 return oc,oi,of

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--csv',type=Path,required=True); ap.add_argument('--trees',type=Path,required=True); ap.add_argument('--outdir',type=Path,required=True); a=ap.parse_args()
 if sha(a.csv)!=CSV_SHA or sha(a.trees)!=TREES_SHA: raise SystemExit('source hash mismatch')
 src=collections.defaultdict(list)
 with a.csv.open(newline='',encoding='utf-8-sig') as f:
  for r in csv.DictReader(f): src[r['clade'].strip()].append((r['species'].strip(),r['flower_color'].strip()))
 z=zipfile.ZipFile(a.trees); members={Path(m).stem.lower():m for m in z.namelist() if not m.endswith('/') and not m.startswith('__MACOSX/') and not m.endswith('.DS_Store')}
 rows=[]; details={}
 for clade in sorted(src):
  vals=src[clade]; counts=collections.Counter(x[1] for x in vals)
  unknown=set(counts)-set(MAP)
  if unknown: raise SystemExit(f'{clade}: unknown source colour tokens {sorted(unknown)}')
  rare={k for k,v in counts.items() if v<5}; ret=[x for x in vals if x[1] not in rare]
  fs=[x[1] for x in ret]; ins=[MAP[x][0] for x in fs]; cs=[MAP[x][1] for x in fs]
  reasons=[]
  if len(ret)<20: reasons.append('COMMON_TIPS_LT_20')
  if len(set(fs))<2: reasons.append('FINE_STATES_LT_2')
  if len(set(ins))<2: reasons.append('INTERMEDIATE_STATES_LT_2')
  if len(set(cs))<2: reasons.append('COARSE_STATES_LT_2')
  if reasons:
   details[clade]={'status':'HOLD_INSUFFICIENT_COMMON_FRAME_OR_STATE_VARIATION','hold_reasons':reasons,'eligible_tips':len(ret)}
   rows.append([clade,'HOLD_INSUFFICIENT_COMMON_FRAME_OR_STATE_VARIATION',len(ret),'','','','','','','',';'.join(reasons)])
   continue
  tree=Phylo.read(io.StringIO(z.read(members[clade.lower()]).decode('utf-8-sig')),'newick')
  rb={norm(s):c for s,c in ret}; tips=[t for t in tree.get_terminals() if norm(t.name) in rb]
  fine_s=np.array([rb[norm(t.name)] for t in tips],object); int_s=np.array([MAP[x][0] for x in fine_s],object); coarse_s=np.array([MAP[x][1] for x in fine_s],object)
  c=enc(coarse_s); i=enc(int_s); f=enc(fine_s); n=len(tips); ii,jj=np.triu_indices(n,1)
  dist=np.array([tree.distance(tips[int(x)],tips[int(y)]) for x,y in zip(ii,jj)],float); ranks=rankdata(-dist,method='average')
  oc,npc=auc(c,ii,jj,ranks); oi,npi=auc(i,ii,jj,ranks); of,npf=auc(f,ii,jj,ranks); obs=np.array([oc,oi,of])
  rng=np.random.default_rng(SEED); base=np.arange(n,dtype=np.int32); perms=np.empty((B,n),dtype=np.int32)
  for b in range(B): perms[b]=rng.permutation(base)
  nc,ni,nf=perm3(perms,ii.astype(np.int32),jj.astype(np.int32),ranks,c,i,f,npc,npi,npf); null=[nc,ni,nf]
  ps=[eup(null[q],obs[q]) for q in range(3)]; sig=[obs[q]>.5 and ps[q]<=.05 for q in range(3)]
  o=np.argsort(-obs,kind='stable'); w=int(o[0]); r=int(o[1]); d=float(obs[w]-obs[r]); pw=eup(null[w]-null[r],d)
  if not any(sig): decision='PROFILE_NO_PHYLOGENETIC_SIGNAL'
  elif sig[w] and d>0 and pw<=.05: decision={'coarse':'PROFILE_SIGNALLED_COARSE','intermediate':'PROFILE_SIGNALLED_INTERMEDIATE','fine':'PROFILE_SIGNALLED_FINE'}[NAMES[w]]
  else: decision='PROFILE_SIGNALLED_TIED'
  details[clade]={'status':'FLOWERCLADES51_EXACT_PROFILE_RESULT','decision':decision,'eligible_tips':n,'AUC_coarse':oc,'AUC_intermediate':oi,'AUC_fine':of,'p_signal':dict(zip(NAMES,ps)),'winner':NAMES[w],'runner_up':NAMES[r],'p_winner_gt_runner':pw,'rare_fine_states_excluded':sorted(rare)}
  rows.append([clade,decision,n,oc,oi,of,ps[0],ps[1],ps[2],pw,''])
 z.close(); classes=collections.Counter(v.get('decision',v['status']) for v in details.values()); completed=sum('decision' in v for v in details.values())
 out={'version':'v0.1','status':'FLOWERCLADES51_BATCH_RESULT','seed_each_clade':SEED,'permutations_per_clade':B,'clades_total':51,'clades_completed_exact_profile':completed,'clades_hold':51-completed,'terminal_class_counts':dict(sorted(classes.items())),'results':details,'paper1_science_changed':False}
 a.outdir.mkdir(parents=True,exist_ok=True); (a.outdir/'flowerclades51_resolution_profile_full_v0_1.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 with (a.outdir/'flowerclades51_resolution_profile_summary_v0_1.csv').open('w',newline='') as f:
  w=csv.writer(f); w.writerow(['clade','terminal_class','eligible_tips','AUC_coarse','AUC_intermediate','AUC_fine','p_coarse_signal','p_intermediate_signal','p_fine_signal','p_winner_gt_runner','hold_reasons']); w.writerows(rows)
 print(json.dumps({'completed':completed,'classes':dict(classes)},indent=2))
if __name__=='__main__': main()
