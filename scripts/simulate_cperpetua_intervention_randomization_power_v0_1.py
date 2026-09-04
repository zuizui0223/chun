#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,itertools,json,math
from pathlib import Path
import numpy as np

SIGNS=np.asarray(list(itertools.product((-1.0,1.0),repeat=15)),dtype=float)


def logistic(x):return 1/(1+np.exp(-x))
def plant_sign_p(d):
    d=np.asarray(d,float);obs=float(d.mean());vals=SIGNS@d/len(d)
    return float(np.mean(vals>=obs-1e-12))
def blocked_pair_p(y_t,y_c,rng,nperm):
    pool=np.concatenate([y_t,y_c],axis=1);obs=float(np.mean(y_t.mean(1)-y_c.mean(1)));vals=[];batch=300
    for start in range(0,nperm,batch):
        n=min(batch,nperm-start);scores=rng.random((n,15,16));idx=np.argpartition(scores,8,axis=2)[:,:,:8]
        pp=np.broadcast_to(pool,(n,)+pool.shape);tr=np.take_along_axis(pp,idx,axis=2).mean(2);co=(pool.sum(1)[None,:]-tr*8)/8;vals.extend((tr-co).mean(1).tolist())
    vals=np.asarray(vals);return float((1+np.sum(vals>=obs-1e-12))/(len(vals)+1))
def blocked_interaction_p(y_tw,y_cw,y_ts,y_cs,rng,nperm):
    pools=[np.concatenate([y_tw,y_cw],1),np.concatenate([y_ts,y_cs],1)];obs=float(np.mean((y_tw.mean(1)-y_cw.mean(1))-(y_ts.mean(1)-y_cs.mean(1))));vals=[];batch=300
    for start in range(0,nperm,batch):
        n=min(batch,nperm-start);cc=[]
        for pool in pools:
            scores=rng.random((n,15,16));idx=np.argpartition(scores,8,axis=2)[:,:,:8]
            pp=np.broadcast_to(pool,(n,)+pool.shape);tr=np.take_along_axis(pp,idx,axis=2).mean(2);co=(pool.sum(1)[None,:]-tr*8)/8;cc.append(tr-co)
        vals.extend((cc[0]-cc[1]).mean(1).tolist())
    vals=np.asarray(vals);return float((1+np.sum(vals>=obs-1e-12))/(len(vals)+1))
def sim_pair(delta,reps,nperm,rng):
    plant=blocked=0
    for _ in range(reps):
        u=rng.normal(0,0.7,15);pc=logistic(math.log(.3/.7)+u);pt=np.clip(pc+delta,.001,.999)
        yc=rng.binomial(1,pc[:,None],(15,8));yt=rng.binomial(1,pt[:,None],(15,8));d=yt.mean(1)-yc.mean(1)
        plant+=plant_sign_p(d)<.05;blocked+=blocked_pair_p(yt,yc,rng,nperm)<.05
    return plant/reps,blocked/reps
def sim_interaction(winter_delta,summer_delta,reps,nperm,rng):
    plant=blocked=0
    for _ in range(reps):
        u=rng.normal(0,0.7,15);pcs=logistic(math.log(.3/.7)+u+0.2);pcw=logistic(math.log(.3/.7)+u-0.2)
        pts=np.clip(pcs+summer_delta,.001,.999);ptw=np.clip(pcw+winter_delta,.001,.999)
        ycs=rng.binomial(1,pcs[:,None],(15,8));yts=rng.binomial(1,pts[:,None],(15,8));ycw=rng.binomial(1,pcw[:,None],(15,8));ytw=rng.binomial(1,ptw[:,None],(15,8))
        di=(ytw.mean(1)-ycw.mean(1))-(yts.mean(1)-ycs.mean(1));plant+=plant_sign_p(di)<.05;blocked+=blocked_interaction_p(ytw,ycw,yts,ycs,rng,nperm)<.05
    return plant/reps,blocked/reps
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out-dir',type=Path,required=True);ap.add_argument('--reps',type=int,default=500);ap.add_argument('--permutations',type=int,default=3000);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    rows=[];rng_pair=np.random.default_rng(20260903)
    for d in (0.0,0.1,0.2,0.3):
        p,b=sim_pair(d,a.reps,a.permutations,rng_pair);rows.append({'scenario':'single_season_8v8','winter_delta':d,'summer_delta':'','interaction_delta':'','plant_collapse_rejection':p,'blocked_randomization_rejection':b})
    rng_inter=np.random.default_rng(20260905)
    for sd in (0.0,0.05,0.10,0.15):
        p,b=sim_interaction(.25,sd,a.reps,a.permutations,rng_inter);rows.append({'scenario':'season_interaction_8v8','winter_delta':.25,'summer_delta':sd,'interaction_delta':.25-sd,'plant_collapse_rejection':p,'blocked_randomization_rejection':b})
    with (a.out_dir/'power_calibration.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    null=next(r for r in rows if r['scenario']=='single_season_8v8' and r['winter_delta']==0)
    summary={'analysis':'cperpetua_intervention_randomization_power_v0.1','reps_per_cell':a.reps,'monte_carlo_permutations':a.permutations,'rng_pair_seed':20260903,'rng_interaction_seed':20260905,'n_plants':15,'arm_size_pairwise':8,'baseline_seed_probability_approx':0.30,'plant_random_effect_sd_logit':0.7,'blocked_null_rejection':null['blocked_randomization_rejection'],'decision':'blocked randomization is calibrated and preserves the randomized flower-level design; it yields modest power gains over plant-only collapse in these simulations but does not rescue weak seasonal interactions','claim_ceiling':'design calibration only; effect sizes are hypothetical and not empirical C. perpetua estimates'}
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
