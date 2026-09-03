#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,itertools,json,math
from pathlib import Path
import numpy as np

COLS=['plant_id','season','full_bloom_stage','A','F','C','P','bee_hex_contrast','uv_reflectance_300_400','fluorescence_index','anthocyanin_total','flavonol_total','carotenoid_total','flavan3ol_total','nectar_volume','sucrose_ratio','temperature_c','bird_visitation','bird_effectiveness','bee_visitation','bee_effectiveness','fruit_set','seed_set']
NUM=COLS[3:]
TCRIT90_DF14=1.7613101358


def read_csv(p):
    with Path(p).open(newline='',encoding='utf-8-sig') as f:
        r=csv.DictReader(f);rows=list(r);return r.fieldnames,rows

def sign_matrix(n=15):
    return np.asarray(list(itertools.product((-1.0,1.0),repeat=n)),dtype=float)

def right_p(d,signs):
    d=np.asarray(d,float);obs=float(np.mean(d));vals=(signs@d)/len(d)
    return float(np.mean(vals>=obs-1e-12))

def left_p(d,signs):
    d=np.asarray(d,float);obs=float(np.mean(d));vals=(signs@d)/len(d)
    return float(np.mean(vals<=obs+1e-12))

def multivar_p(D,signs):
    D=np.asarray(D,float);s=np.sqrt(np.mean(D**2,axis=0));s=np.where(s==0,1.0,s)
    obs=float(np.sum((np.mean(D,axis=0)/s)**2));means=(signs@D)/D.shape[0];vals=np.sum((means/s)**2,axis=1)
    return obs,float(np.mean(vals>=obs-1e-12))

def standard_fit_predict(rows,train,test,features,outcome):
    X=np.array([[r[f] for f in features] for r in rows],float);y=np.array([r[outcome] for r in rows],float)
    mu=X[train].mean(axis=0);sd=X[train].std(axis=0,ddof=0);sd=np.where(sd==0,1.0,sd)
    Xt=(X[train]-mu)/sd;Xs=(X[test]-mu)/sd
    Xt=np.column_stack([np.ones(len(train)),Xt]);Xs=np.column_stack([np.ones(len(test)),Xs])
    beta=np.linalg.lstsq(Xt,y[train],rcond=None)[0]
    return Xs@beta

def lopo_predictions(rows,features,outcome):
    plants=sorted({r['plant_id'] for r in rows});pred=np.full(len(rows),np.nan)
    for plant in plants:
        test=[i for i,r in enumerate(rows) if r['plant_id']==plant];train=[i for i,r in enumerate(rows) if r['plant_id']!=plant]
        assert len(test)==2 and len(train)==28
        pred[test]=standard_fit_predict(rows,train,test,features,outcome)
    assert np.isfinite(pred).all();return pred

def pair_deltas(rows,col):
    by={}
    for r in rows:by[(r['plant_id'],r['season'])]=r
    return np.array([by[(f'P{i:02d}','winter')][col]-by[(f'P{i:02d}','summer')][col] for i in range(1,16)],float)

def write_csv(path,rows):
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',required=True);ap.add_argument('--bounds',required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    cols,raw=read_csv(a.data);assert cols==COLS;assert len(raw)==30
    assert sorted({r['plant_id'] for r in raw})==[f'P{i:02d}' for i in range(1,16)]
    assert {(r['plant_id'],r['season']) for r in raw}=={(f'P{i:02d}',s) for i in range(1,16) for s in ('summer','winter')}
    assert all(r['full_bloom_stage']=='full_bloom' for r in raw)
    rows=[]
    for r in raw:
        z={'plant_id':r['plant_id'],'season':r['season'],'full_bloom_stage':r['full_bloom_stage']}
        for c in NUM:
            assert r[c].strip()!='',f'missing {c} for {r["plant_id"]} {r["season"]}'
            z[c]=float(r[c]);assert math.isfinite(z[c])
        z['season_code']=1.0 if r['season']=='winter' else 0.0
        assert 0<=z['fruit_set']<=1 and 0<=z['seed_set']<=1
        assert z['bird_visitation']>=0 and z['bee_visitation']>=0 and z['bird_effectiveness']>=0 and z['bee_effectiveness']>=0
        z['bird_service']=z['bird_visitation']*z['bird_effectiveness'];z['bee_service']=z['bee_visitation']*z['bee_effectiveness']
        total=z['bird_service']+z['bee_service'];assert total>0
        z['bird_share']=z['bird_service']/total;z['effective_service_total']=total
        rows.append(z)
    rows=sorted(rows,key=lambda r:(r['plant_id'],0 if r['season']=='summer' else 1))
    signs=sign_matrix();assert signs.shape==(32768,15)

    # G0: replicate historical reward + guild direction with exact paired tests.
    d_nv=pair_deltas(rows,'nectar_volume');d_sr=pair_deltas(rows,'sucrose_ratio');d_bs=pair_deltas(rows,'bird_share')
    p_nv=right_p(d_nv,signs);p_sr=right_p(d_sr,signs);p_bs=right_p(d_bs,signs)
    reward_bonf=min(1.0,2*min(p_nv,p_sr));g0=(max(d_nv.mean(),d_sr.mean())>0 and reward_bonf<0.05 and d_bs.mean()>0 and p_bs<0.05)

    # Gate A / G2: exact four-axis winter-summer latent-state shift.
    D=np.column_stack([pair_deltas(rows,c) for c in ('A','F','C','P')]);T,pA=multivar_p(D,signs);g2=pA<0.05

    # G1: equivalence requires pre-unblind frozen raw-unit bounds for A/F/C/P + primary bee contrast.
    bcols,braw=read_csv(a.bounds);assert bcols==['axis','bound_abs_raw_units','status','source_note']
    B={r['axis']:r for r in braw};assert set(B)=={'A','F','C','P','BEE_HEX'}
    eq_rows=[]
    for axis,col in [('A','A'),('F','F'),('C','C'),('P','P'),('BEE_HEX','bee_hex_contrast')]:
        r=B[axis];assert r['status']=='FROZEN_PRE_UNBLIND';bound=float(r['bound_abs_raw_units']);assert bound>0 and r['source_note'].strip()
        d=pair_deltas(rows,col);m=float(d.mean());se=float(d.std(ddof=1)/math.sqrt(15));lo=m-TCRIT90_DF14*se;hi=m+TCRIT90_DF14*se
        passed=lo>-bound and hi<bound
        eq_rows.append({'axis':axis,'bound':bound,'mean_delta':m,'ci90_low':lo,'ci90_high':hi,'equivalent':passed})
    g1=all(r['equivalent'] for r in eq_rows)

    # G3: prespecified winter decrease in Apis color-hexagon contrast.
    d_hex=pair_deltas(rows,'bee_hex_contrast');p3=left_p(d_hex,signs);g3=d_hex.mean()<0 and p3<0.05

    # G4: sensory adds held-out prediction beyond reward + observation temperature.
    base4=['nectar_volume','sucrose_ratio','temperature_c'];sens4=base4+['bee_hex_contrast']
    pb=lopo_predictions(rows,base4,'bird_share');ps=lopo_predictions(rows,sens4,'bird_share');y=np.array([r['bird_share'] for r in rows])
    plant_diff4=[]
    for i in range(15):
        ix=[2*i,2*i+1];plant_diff4.append(float(np.mean((y[ix]-pb[ix])**2-(y[ix]-ps[ix])**2)))
    rmse4b=float(np.sqrt(np.mean((y-pb)**2)));rmse4s=float(np.sqrt(np.mean((y-ps)**2)));p4=right_p(plant_diff4,signs);g4=rmse4s<rmse4b and np.mean(plant_diff4)>0 and p4<0.05

    # G5: effective service adds joint fruit+seed held-out predictive information.
    base5=['season_code','nectar_volume','sucrose_ratio','temperature_c'];serv5=base5+['effective_service_total']
    diffs5=np.zeros(15);sq_b=[];sq_s=[];endpoint=[]
    for outcome in ('fruit_set','seed_set'):
        p0=lopo_predictions(rows,base5,outcome);p1=lopo_predictions(rows,serv5,outcome);yy=np.array([r[outcome] for r in rows])
        sq_b.extend(((yy-p0)**2).tolist());sq_s.extend(((yy-p1)**2).tolist())
        for i in range(15):
            ix=[2*i,2*i+1];diffs5[i]+=float(np.mean((yy[ix]-p0[ix])**2-(yy[ix]-p1[ix])**2))/2
        endpoint.append({'endpoint':outcome,'baseline_rmse':float(np.sqrt(np.mean((yy-p0)**2))),'service_rmse':float(np.sqrt(np.mean((yy-p1)**2)))})
    rmse5b=float(np.sqrt(np.mean(sq_b)));rmse5s=float(np.sqrt(np.mean(sq_s)));p5=right_p(diffs5,signs);g5=rmse5s<rmse5b and diffs5.mean()>0 and p5<0.05

    if g0 and g2 and g3 and g4 and g5:classification='M_SENSORY_PLUS_REWARD'
    elif (g3 or g4) and not g5:classification='M_BEHAVIOR_WITHOUT_FITNESS'
    elif g2 and not g3 and not g4:classification='M_GENERAL_SEASONAL_PHYSIOLOGY'
    elif g0 and g1 and not g3 and not g4:classification='M_REWARD_ONLY'
    elif (not g2) and (not g1):classification='LATENT_STATE_UNRESOLVED'
    else:classification='MIXED_UNRESOLVED'

    gates=[
      {'gate':'G0','pass':g0,'statistic':f'reward_bonf_p={reward_bonf:.6g}; bird_share_p={p_bs:.6g}'},
      {'gate':'G1','pass':g1,'statistic':'all A/F/C/P/BEE_HEX 90% CIs inside frozen bounds'},
      {'gate':'G2','pass':g2,'statistic':f'T={T:.6g}; exact_p={pA:.6g}'},
      {'gate':'G3','pass':g3,'statistic':f'mean_winter_minus_summer={d_hex.mean():.6g}; left_p={p3:.6g}'},
      {'gate':'G4','pass':g4,'statistic':f'baseline_rmse={rmse4b:.6g}; sensory_rmse={rmse4s:.6g}; exact_p={p4:.6g}'},
      {'gate':'G5','pass':g5,'statistic':f'baseline_joint_rmse={rmse5b:.6g}; service_joint_rmse={rmse5s:.6g}; exact_p={p5:.6g}'}]
    write_csv(a.out_dir/'gate_results.csv',gates);write_csv(a.out_dir/'equivalence_results.csv',eq_rows);write_csv(a.out_dir/'fitness_endpoint_rmse.csv',endpoint)
    summary={'analysis':'cperpetua_future_seasonal_data_v0.1','n_plants':15,'n_rows':30,'exact_sign_assignments':32768,'classification':classification,'gates':{r['gate']:bool(r['pass']) for r in gates},'gateA_exact_p':pA,'equivalence_all_primary':g1,'bee_hex_left_p':p3,'sensory_incremental_p':p4,'service_fitness_incremental_p':p5,'claim_ceiling':'extant paired seasonal ecological-filter classification only; historical accepted-species flower-colour transition causation remains outside scope'}
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2,ensure_ascii=False));return 0

if __name__=='__main__':raise SystemExit(main())
