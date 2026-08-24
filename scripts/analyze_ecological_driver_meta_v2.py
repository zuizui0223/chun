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
    ids=[r['effect_id'] for r in e]
    assert len(ids)==len(set(ids))
    errors=[]
    for r in e:
        y=lnrr(r);stored=fnum(r.get('effect_value'))
        if r.get('effect_metric')=='lnRR' and y is not None and stored is not None and abs(y-stored)>0.01:errors.append((r['effect_id'],stored,y))
    if errors:raise SystemExit(errors)

    # Genus-level primary service synthesis: exactly one bird-access contrast per species.
    cross=[r for r in e if r['axis']=='pollinator_service' and r['outcome']=='fruit_set']
    taxa=[r['taxon'] for r in cross]
    assert len(cross)==3 and len(set(taxa))==3
    cross_sum=rr_summary(cross);cross_sum.update({'k_independent_species':3,'visible_states':sorted({r['visible_state'] for r in cross})})
    loo=[]
    for i,r in enumerate(cross):
        z=rr_summary([x for j,x in enumerate(cross) if i!=j]);loo.append({'omitted':r['effect_id'],'RR':z['geometric_mean_RR']})
    cross_sum['leave_one_out_RR_min']=min(x['RR'] for x in loo);cross_sum['leave_one_out_RR_max']=max(x['RR'] for x in loo);cross_sum['formal_inverse_variance_pooling']=False

    # C. oleifera triangulation: same species, independent studies/designs. Never count as extra genus-level species.
    zhang=next(r for r in e if r['effect_id']=='ECO_BIRD_OLEIFERA_FRUIT')
    liu_cage=next(r for r in e if r['effect_id']=='ECO_BEE_OLEIFERA_CAGE_2020_21')
    liu_open=next(r for r in e if r['effect_id']=='ECO_BEE_OLEIFERA_OPEN_2020_21')
    xie=next(r for r in e if r['effect_id']=='ECO_RELIABILITY_OLEIFERA_PL_VD')
    li_abund=next(r for r in e if r['effect_id']=='ECO_RELIABILITY_OLEIFERA_WILDBEE')
    ole={'independent_quantitative_studies_min':4,'bird_access_RR':math.exp(lnrr(zhang)),'managed_A_cerana_cage_RR':math.exp(lnrr(liu_cage)),'managed_A_cerana_open_field_RR_same_study':math.exp(lnrr(liu_open)),'Andrena_visit_density_vs_pollen_limitation_slope':fnum(xie['effect_value']),'wild_bee_abundance_vs_fruit_set':li_abund['effect_metric'],'interpretation':'independent exclusion, managed-bee manipulation and abundance-gradient studies converge on strong pollinator-service limitation within C. oleifera; correlated outcomes are not pooled as independent species'}

    # Pollen limitation and compatible-pollen potential are kept distinct.
    chai=next(r for r in e if r['effect_id']=='ECO_PL_PUBIPETALA_FRUIT');y=lnrr(chai)
    aa,nn,cc,mm=(int(chai[k]) for k in ('events_num','n_num','events_den','n_den'));se=math.sqrt((1/aa-1/nn)+(1/cc-1/mm))
    wang=next(r for r in e if r['effect_id']=='ECO_CROSS_OLEIFERA_FRUIT')
    pollen={'pubipetala_RR':math.exp(y),'pubipetala_SE_lnRR':se,'pubipetala_CI95_RR':[math.exp(y-1.96*se),math.exp(y+1.96*se)],'petelotii_reported_null':True,'oleifera_cross_vs_open_context_RR':math.exp(lnrr(wang)),'formal_pooling':False,'ceiling':'cross-vs-open breeding-system contrast is context, not a pollen-supplementation replicate'}

    # Climate/season mediation: count independent taxa from admitted studies, not effect rows.
    med_axes={'climate_phenology_pollination','season_weather_pollination','pollinator_service_weather'}
    med=[r for r in s if r['ecological_axis'] in med_axes and r['admission_status'] in {'admit_primary','admit_mediation'}]
    mediation={'k_studies':len(med),'k_taxa':len({r['taxon'] for r in med}),'taxa':sorted({r['taxon'] for r in med}),'hainanica_visit_RR':math.exp(lnrr(next(r for r in e if r['effect_id']=='ECO_CLIMMED_HAINANICA_VISITS'))),'hainanica_pollen_deposition_RR':math.exp(lnrr(next(r for r in e if r['effect_id']=='ECO_CLIMMED_HAINANICA_POLLEN'))),'perpetua_nectar_RR':math.exp(lnrr(next(r for r in e if r['effect_id']=='ECO_SEASON_PERPETUA_NECTAR'))),'interpretation':'independent systems support environment/flowering-window modulation of pollinator service; heterogeneous outcomes are not pooled on one scale'}

    abiotic=[r for r in s if r['ecological_axis']=='abiotic_pigment_manipulation'];sensory=[r for r in e if r['axis']=='sensory_pollinator']
    summary={'registry_effects':len(e),'registered_studies':len(s),'cross_species_pollinator_service':cross_sum,'oleifera_within_species_triangulation':ole,'pollen_limitation':pollen,'climate_season_pollinator_mediation':mediation,'direct_abiotic_floral_pigment':{'k_independent_experiments':len(abiotic),'formal_pooling':False,'ceiling':'one cold+dark floral experiment; direct abiotic flower-pigment meta-analysis remains under-replicated'},'sensory_aliasing':{'k_same_hue_pair_experiments':len(sensory),'red_pair_visit_RR':math.exp(lnrr(sensory[0])) if sensory else None},'decision':{'best_supported_driver_layer':'pollinator service/reliability with climate/season mediation','not_supported_as_general_model':'visible red/A -> bird syndrome; direct red/A -> cold adaptation','formal_random_effects_status':'not justified for cross-species fruit-set service because sampling variances remain unavailable for all three species','paper1_implication':'ecological layer can be stated quantitatively as triangulated service/reliability evidence, while accepted-species branch-specific causation remains unidentifiable'}}
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(summary,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
