#!/usr/bin/env python3
"""Screen newly generated ecological-persistence hypotheses from frozen chun evidence.

This script does not inspect the new nuclear topology.  It asks what the current
pollination-function and mechanistic evidence can already say about hypotheses
that were generated *after* the direct cold-adaptation hypothesis failed.
"""
from __future__ import annotations
import argparse,csv,json,math,pathlib,random
from collections import Counter,defaultdict


def read_csv(p):
    with open(p,newline='',encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def temporal_modulation(text):
    s=(text or '').lower()
    if not s or s in {'not_tested','none','unknown'}:
        return False
    keys=('season','winter','summer','cloud','rain','weather')
    return any(k in s for k in keys)


def contingency_mi(rows):
    n=len(rows)
    xs=Counter(r['visible_state'] for r in rows)
    ys=Counter(r['pollinator_function_class'] for r in rows)
    xy=Counter((r['visible_state'],r['pollinator_function_class']) for r in rows)
    mi=0.0
    for (x,y),c in xy.items():
        pxy=c/n; px=xs[x]/n; py=ys[y]/n
        mi += pxy*math.log(pxy/(px*py))
    return mi


def perm_p(rows,nperm,seed):
    rng=random.Random(seed)
    obs=contingency_mi(rows)
    states=[r['visible_state'] for r in rows]
    ge=0
    for _ in range(nperm):
        p=states[:]; rng.shuffle(p)
        rr=[dict(r,visible_state=s) for r,s in zip(rows,p)]
        if contingency_mi(rr) >= obs-1e-15: ge += 1
    return obs,(ge+1)/(nperm+1)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pollination',required=True)
    ap.add_argument('--mechanism',required=True)
    ap.add_argument('--prebranch',required=True)
    ap.add_argument('--out-dir',type=pathlib.Path,required=True)
    ap.add_argument('--permutations',type=int,default=100000)
    ap.add_argument('--seed',type=int,default=20260820)
    a=ap.parse_args(); a.out_dir.mkdir(parents=True,exist_ok=True)

    poll=read_csv(a.pollination)
    mech=read_csv(a.mechanism)
    pre=read_csv(a.prebranch)

    temporal=[r for r in poll if temporal_modulation(r.get('environmental_or_seasonal_modulation'))]
    by_state=defaultdict(set); n_by_state=Counter()
    for r in poll:
        by_state[r['visible_state']].add(r['pollinator_function_class']); n_by_state[r['visible_state']]+=1
    multi={s:sorted(v) for s,v in by_state.items() if n_by_state[s]>=2}
    heterogeneous={s:v for s,v in multi.items() if len(v)>1}
    mi,mi_p=perm_p(poll,a.permutations,a.seed)

    white_clusters=defaultdict(list)
    for r in mech:
        if 'white' in (r.get('colors') or '').lower(): white_clusters[r['independence_cluster']].append(r)
    n_loss=sum(any((x.get('structural_gene_loss_required') or '').lower()=='yes' for x in rs) for rs in white_clusters.values())
    n_rev=sum(any((x.get('within_genotype_or_developmental_switch') or '').lower()=='yes' for x in rs) for rs in white_clusters.values())

    premap={r['hypothesis']:r for r in pre}
    h2=premap.get('H2_direct_cold_adaptation',{})

    registry=[
      {
        'hypothesis':'H6_pollinator_reliability_filter',
        'status':'new_supported_as_plausibility_not_macro_causation',
        'current_evidence':f"{len(temporal)}/{len(poll)} pollination taxa have explicit season/weather modulation; annual-mean direct-cold hypothesis={h2.get('status','not_supported')}",
        'prediction':'flower-colour/sensory transitions align more strongly with flowering-season pollinator unreliability than with annual mean BIO1/BIO6',
        'decisive_test':'rooted branch histories + flowering-season BIO4/BIO15/monthly weather + pollinator regime transitions',
        'falsifier':'no improvement over annual climate/null after phylogeny and phenology control'
      },
      {
        'hypothesis':'H7_ecological_preadaptation_vs_genetic_permissivity',
        'status':'new_competing_hypothesis',
        'current_evidence':'A-state historical concentration is strong, but section concentration alone cannot distinguish genomic permissivity from correlated floral ecology',
        'prediction':'flower size/shape, nectar and flowering season shift before or with pigment transitions; controlling them reduces residual lineage effect',
        'decisive_test':'branch-order model comparing floral architecture/phenology/nectar -> pollinator -> pigment versus pigment-first models',
        'falsifier':'lineage effect remains strong after ecological preadaptation traits are controlled'
      },
      {
        'hypothesis':'H8_latent_sensory_state_filter',
        'status':'preliminary_support',
        'current_evidence':f"{len(heterogeneous)}/{len(multi)} multi-taxon visible states contain >1 pollinator-function class; hue-function MI permutation P={mi_p:.6f}",
        'prediction':'UV/fluorescence/spectral + morphology + reward states predict pollinator function better than A/W/Y visible hue',
        'decisive_test':'phylogenetic model comparison: visible hue only vs latent sensory phenotype',
        'falsifier':'visible hue predicts pollinator function as well as or better than latent sensory traits'
      },
      {
        'hypothesis':'H9_ecological_hysteresis_of_retained_pathways',
        'status':'new_compatible_with_micro_evidence',
        'current_evidence':f"white-containing clusters={len(white_clusters)}; structural-loss-required={n_loss}; reversible-switch clusters={n_rev}",
        'prediction':'W<->A/Y reversals occur without pathway loss and transition rates depend on previous state + ecological regime, producing lag/hysteresis',
        'decisive_test':'rooted stochastic maps with context-dependent transition rates and branch lag between ecological and pigment changes',
        'falsifier':'reacquisition consistently requires de-novo structural recovery or transition rates are history-independent'
      },
      {
        'hypothesis':'H10_flowering_window_not_annual_mean_climate',
        'status':'new_generated_by_negative_direct_climate_result',
        'current_evidence':'annual BIO1/BIO6 direct-cold model is not supported after history control, while multiple field systems show seasonal/weather-dependent pollinator weighting',
        'prediction':'flowering-season extremes/variability and pollinator activity windows explain floral-state persistence better than annual climatic means',
        'decisive_test':'monthly occurrence/phenology + monthly temperature/precipitation + pollinator activity matched to flowering windows',
        'falsifier':'annual means retain equal/greater predictive power after flowering-window variables are included'
      }
    ]

    with (a.out_dir/'hypothesis_registry.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(registry[0]));w.writeheader();w.writerows(registry)
    summary={
      'n_pollination_taxa':len(poll),
      'n_temporal_weather_modulated_pollination_taxa':len(temporal),
      'temporal_weather_taxa':[r['taxon'] for r in temporal],
      'multi_taxon_visible_states':multi,
      'heterogeneous_pollinator_states':heterogeneous,
      'n_heterogeneous_multi_taxon_states':len(heterogeneous),
      'n_multi_taxon_states':len(multi),
      'visible_hue_pollinator_mutual_information':mi,
      'visible_hue_pollinator_permutation_p':mi_p,
      'white_containing_mechanistic_clusters':len(white_clusters),
      'structural_loss_required_clusters':n_loss,
      'reversible_switch_clusters':n_rev,
      'interpretation':'new hypotheses are generated from the conjunction of strong lineage concentration, failure of a universal direct-cold model, retained pathway accessibility, and pollinator-function aliasing; only H8 has a direct current diagnostic, while H6/H7/H9/H10 require branch or temporal data for causal tests'
    }
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
