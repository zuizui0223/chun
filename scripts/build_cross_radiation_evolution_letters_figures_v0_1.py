#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def save(fig, path:Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches='tight')
    plt.close(fig)


def fig1(out:Path):
    x=json.loads((ROOT/'results/iris_intermediate_resolution_v0_1/iris_intermediate_resolution_result_v0_1.json').read_text())
    labels=['Coarse','Intermediate','Fine']
    vals=[x['observed']['AUC_coarse'],x['observed']['AUC_intermediate'],x['observed']['AUC_fine']]
    fig,ax=plt.subplots(figsize=(6.2,4.3))
    ax.bar(labels, vals)
    ax.axhline(0.5, linestyle='--', linewidth=1)
    ax.set_ylim(0.42,0.52)
    ax.set_ylabel('Same-state phylogenetic AUC')
    ax.set_title('Prospective Iris test: intermediate optimum fails')
    ax.text(1, vals[1]-0.003, 'FAIL', ha='center', va='top')
    save(fig,out/'fig1_iris_profile.png')


def fig2(out:Path):
    p=ROOT/'results/flowerclades51_resolution_profile_v0_1/flowerclades51_resolution_profile_summary_v0_1.csv'
    d=pd.read_csv(p)
    d=d[d['terminal_class']!='HOLD_INSUFFICIENT_COMMON_FRAME_OR_STATE_VARIATION'].copy()
    d['fine_minus_coarse']=d['AUC_fine']-d['AUC_coarse']
    d=d.sort_values('fine_minus_coarse').reset_index(drop=True)
    x=np.arange(len(d))
    fig,ax=plt.subplots(figsize=(11.5,5.5))
    ax.plot(x,d['AUC_coarse'],marker='o',linewidth=1,label='Coarse')
    ax.plot(x,d['AUC_intermediate'],marker='o',linewidth=1,label='Intermediate')
    ax.plot(x,d['AUC_fine'],marker='o',linewidth=1,label='Fine')
    ax.axhline(0.5,linestyle='--',linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(d['clade'],rotation=70,ha='right')
    ax.set_ylabel('Same-state phylogenetic AUC')
    ax.set_title('Standardized visible-colour profiles across 28 completed clades')
    ax.legend(frameon=False,ncol=3)
    save(fig,out/'fig2_visible_clades_profiles.png')


def fig3(out:Path):
    d=pd.read_csv(ROOT/'data/flowerclades51_tree_moderator_candidates_v0_1.csv')
    d=d[d['target_contrast'].isin(['intermediate_minus_coarse','fine_minus_intermediate'])].copy()
    predictors=['log_n_tips','pair_distance_cv','branch_length_cv','root_to_tip_cv']
    fig,ax=plt.subplots(figsize=(8.4,4.8))
    xpos=np.arange(len(predictors))
    for j,contrast in enumerate(['intermediate_minus_coarse','fine_minus_intermediate']):
        sub=d[d['target_contrast']==contrast].set_index('predictor').loc[predictors]
        shift=(-0.08 if j==0 else 0.08)
        ax.plot(xpos+shift,sub['relative_loo_improvement'],marker='o',linewidth=1,label=contrast.replace('_',' '))
    ax.axhline(0,linestyle='--',linewidth=1)
    ax.set_xticks(xpos)
    ax.set_xticklabels(['log tips','pair-distance CV','branch-length CV','root-to-tip CV'],rotation=20,ha='right')
    ax.set_ylabel('LOO improvement over intercept')
    ax.set_title('No tree-only predictor qualifies for the full resolution profile')
    ax.legend(frameon=False)
    save(fig,out/'fig3_tree_moderators.png')


def fig4(out:Path):
    x=json.loads((ROOT/'data/petunieae_biochemical_resolution_profile_result_v0_1.json').read_text())
    labels=['Coarse','Intermediate','Fine']
    vals=[x['observed']['AUC_coarse'],x['observed']['AUC_intermediate'],x['observed']['AUC_fine']]
    fig,ax=plt.subplots(figsize=(6.2,4.3))
    ax.bar(labels,vals)
    ax.axhline(0.5,linestyle='--',linewidth=1)
    ax.set_ylim(0.48,0.73)
    ax.set_ylabel('Same-state phylogenetic AUC')
    ax.set_title('Petunieae biochemical profile')
    ax.text(2,vals[2]+0.008,'P = 0.0001',ha='center',va='bottom')
    save(fig,out/'fig4_petunieae_profile.png')


def fig5(out:Path):
    x=json.loads((ROOT/'data/resolution_profile_representation_identifiability_v0_1.json').read_text())
    labels=['Visible-colour\nstandardized','Biochemical\ncomposition','Mixed pigment/hue\nprospective']
    vals=[x['training_composition']['standardized_visible_colour'],x['training_composition']['biochemical_composition'],x['training_composition']['mixed_pigment_hue_prospective']]
    fig,ax=plt.subplots(figsize=(7.0,4.5))
    ax.bar(labels,vals)
    ax.set_ylabel('Completed exact-profile units')
    ax.set_title('Representation-type moderator remains non-identifiable')
    ax.text(1,vals[1]+0.6,'singleton biochemical class',ha='center')
    save(fig,out/'fig5_representation_training.png')


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out-dir',type=Path,default=ROOT/'figures/cross_radiation_el_v0_1'); a=ap.parse_args()
    for fn in (fig1,fig2,fig3,fig4,fig5): fn(a.out_dir)
    expected=[a.out_dir/f'fig{i}_{name}.png' for i,name in [(1,'iris_profile'),(2,'visible_clades_profiles'),(3,'tree_moderators'),(4,'petunieae_profile'),(5,'representation_training')]]
    assert all(p.is_file() and p.stat().st_size>5000 for p in expected)
    print(json.dumps({'status':'CROSS_RADIATION_EL_FIGURES_BUILT','outputs':[str(p) for p in expected]},indent=2))

if __name__=='__main__': main()
