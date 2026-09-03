#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path


def read_csv(p:Path):
    with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--design',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    rows=read_csv(a.design);by={r['layer']:r for r in rows};assert len(by)==len(rows)
    required={'plant_frame','full_bloom_targeted','spectral','pigment_chemistry','nectar','pollinator_effectiveness','fitness','rnaseq_discovery','metabolomics_discovery'}
    assert required==set(by), f'design layer drift: {set(by)}'
    for layer in required:
        assert by[layer]['paired_across_seasons']=='yes'
    primary=['full_bloom_targeted','spectral','pigment_chemistry','nectar','pollinator_effectiveness','fitness']
    assert all(int(by[x]['n_units_per_season'])==15 for x in primary)
    assert int(by['rnaseq_discovery']['n_units_per_season'])==6
    assert int(by['metabolomics_discovery']['n_units_per_season'])==6
    n=15;sign_flip_space=2**n;min_exact_p=1/sign_flip_space
    # Normal-approximation planning number only; final inference is exact/randomization based.
    # For a paired standardized effect d, n ~= ((z.975+z.80)/d)^2; with n=15 the
    # detectable d is about 0.72 by normal approximation and ~0.78 under exact t-power.
    detectable_d_planning=0.778
    summary={
      'analysis':'cperpetua_seasonal_test_design_v0.1',
      'primary_independence_unit':'tagged GBG plant',
      'paired_plants':15,
      'exact_sign_flip_assignments':sign_flip_space,
      'minimum_one_sided_raw_exact_p':min_exact_p,
      'planning_detectable_paired_standardized_effect_80pct_power_two_sided_alpha05_approx':detectable_d_planning,
      'primary_layers':primary,
      'discovery_rnaseq_pairs':6,
      'discovery_metabolomics_pairs':6,
      'primary_statistical_gate':'plant-paired winter-summer latent-state shift; exact sign-flip/randomization inference with prespecified A/F/C/P axes and multiplicity control; no outcome-based gene or wavelength selection',
      'causal_bridge_gate':'seasonal latent-state evidence is not called a pollinator-mediated fitness mechanism unless plant-level seasonal changes are also linked to effective pollination and fruit/seed outcomes in the same tagged population',
      'decision':'the minimal design reuses the published 15-plant GBG frame and makes targeted molecular/spectral measurements primary; RNA-seq/metabolomics are discovery validation rather than the sole inferential gate'
    }
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,ensure_ascii=False));return 0

if __name__=='__main__':raise SystemExit(main())
