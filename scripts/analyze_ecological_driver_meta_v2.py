#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
from statistics import mean,median

def read_csv(p):
    with open(p,newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def fnum(x):
    x=(x or '').strip();return None if x=='' else float(x)
def lnrr(r):
    a=fnum(r.get('numerator_value'));b=fnum(r.get('denominator_value'))
    return None if a is None or b is None else math.log(a/b)
def rr_summary(rows):
    ys=[lnrr(r) for r in rows];ys=[x for x in ys if x is not None]
    return {'k':len(ys),'positive':sum(x>0 for x in ys),'mean_lnRR':mean(ys),'geometric_mean_RR':math.exp(mean(ys)),'median_RR':median(math.exp(x) for x in ys),'min_RR':min(math.exp(x) for x in ys),'max_RR':max(math.exp(x) for x in ys)}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--effects',required=True);ap.add_argument('--studies',required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    e=read_csv(a.effects);s=read_csv(a.studies)
    ids=[r['effect_id'] for r in e];assert len(ids)==len(set(ids))
    errors=[]
    for r in e:
        y=lnrr(r);stored=fnum(r.get('effect_value'))
        if r.get('effect_metric')=='lnRR' and y is not None and stored is not None and abs(y-stored)>0.01:errors.append((r['effect_id'],stored,y))
    if errors:raise SystemExit(errors)
    cross=[r for r in e if r['axis']=='pollinator_service' and r['outcome']=='fruit_set'];taxa=[r['taxon'] for r in cross];assert len(cross)==3 and len(set(taxa))==3
    cross_sum=rr_summary(cross);cross_sum.update({'k_independent_species':len(set(taxa)),'visible_states':sorted({r['visible_state'] for r in cross})})
    loo=[]
    for i,r in enumerate(cross):
        z=rr_summary([x for j,x in enumerate(cross) if i!=j]);loo.append({'omitted':r['effect_id'],'RR':z['geometric_mean_RR']})
    cross_sum['leave_one_out_RR_min']=min(x['RR'] for x in loo);cross_sum['leave_one_out_RR_max']=max(x['RR'] for x in loo);cross_sum['formal_inverse_variance_pooling']=False
    ole_ids={'ECO_BIRD_OLEIFERA_FRUIT','ECO_BEE_OLEIFERA_LIU2025_CAGE'};ole=[r for r in e if r['effect_id'] in ole_ids];assert len(ole)==2
    ole_sum=rr_summary(ole);ole_sum.update({'independent_studies':2,'pollinator_contrasts':['bird access','Apis cerana introduction'],'secondary_same_study_RR':math.exp(lnrr(next(r for r in e if r['effect_id']=='ECO_BEE_OLEIFERA_LIU2025_OPEN')))})
    grad=[r for r in e if r['axis'] in {'pollinator_reliability','pollinator_reliability_gradient'}];expected=[]
    for r in grad:
        v=fnum(r.get('effect_value'))
        if v is None:continue
        if 'abundance' in r['contrast'] or 'visit_density' in r['contrast']:ok=v>0 if 'fruit_set' in r['outcome'] else v<0
        elif 'nest_distance' in r['contrast']:ok=v<0
        else:ok=False
        expected.append((r['effect_id'],ok,v))
    reliability={'k_effect_rows':len(expected),'expected_direction_count':sum(x[1] for x in expected),'all_expected_direction':all(x[1] for x in expected),'effects':[{'effect_id':x[0],'value':x[2],'expected_direction':x[1]} for x in expected]}
    chai=next(r for r in e if r['effect_id']=='ECO_PL_PUBIPETALA_FRUIT');y=lnrr(chai);aa,nn,cc,mm=(int(chai[k]) for k in ('events_num','n_num','events_den','n_den'));se=math.sqrt((1/aa-1/nn)+(1/cc-1/mm))
    pollen={'pubipetala_RR':math.exp(y),'pubipetala_SE_lnRR':se,'pubipetala_CI95_RR':[math.exp(y-1.96*se),math.exp(y+1.96*se)],'petelotii_reported_null':True,'oleifera_visit_density_gradient_P':0.004,'oleifera_cross_vs_open_sensitivity_RR':math.exp(lnrr(next(r for r in e if r['effect_id']=='ECO_PL_OLEIFERA_SELFSTERILITY_SENS'))),'formal_pooling':False}
    med_axes={'climate_pollinator_mediation','climate_phenology_pollination','season_weather_pollination','pollinator_service_weather'};med=[r for r in s if r['ecological_axis'] in med_axes and r['admission_status'] in {'admit_primary','admit_mediation'}];med_taxa=sorted({r['taxon'] for r in med})
    mediation={'k_studies':len(med),'k_taxa':len(med_taxa),'taxa':med_taxa,'interpretation':'independent systems support environment/flowering-window modulation of pollinator service, but effects are heterogeneous and are not pooled on one scale'}
    abiotic=[r for r in s if r['ecological_axis']=='abiotic_pigment_manipulation'];sensory=[r for r in e if r['axis']=='sensory_pollinator']
    summary={'registry_effects':len(e),'registered_studies':len(s),'cross_species_pollinator_service':cross_sum,'oleifera_within_species_service_replication':ole_sum,'pollinator_reliability_gradients':reliability,'pollen_limitation':pollen,'climate_season_pollinator_mediation':mediation,'direct_abiotic_floral_pigment':{'k_independent_experiments':len(abiotic),'formal_pooling':False,'ceiling':'one cold+dark floral experiment; direct abiotic flower-pigment meta-analysis remains under-replicated'},'sensory_aliasing':{'k_same_hue_pair_experiments':len(sensory),'red_pair_visit_RR':math.exp(lnrr(sensory[0])) if sensory else None},'decision':{'best_supported_driver_layer':'pollinator service/reliability with climate/season mediation','not_supported_as_general_model':'visible red/A -> bird syndrome; direct red/A -> cold adaptation','formal_random_effects_status':'not justified for cross-species fruit-set service because sampling variances remain unavailable for all three species','paper1_implication':'ecological layer can be stated quantitatively as triangulated service/reliability evidence, while accepted-species branch-specific causation remains unidentifiable'}}
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n');print(json.dumps(summary,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
