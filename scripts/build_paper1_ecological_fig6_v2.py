#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import matplotlib.pyplot as plt


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--summary',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    s=json.loads(a.summary.read_text())
    cross=s['cross_species_pollinator_service'];ole=s['oleifera_within_species_service_replication'];rel=s['pollinator_reliability_gradients'];med=s['climate_season_pollinator_mediation'];abi=s['direct_abiotic_floral_pigment']
    rows=[('C. japonica (A)',6.3508771929824555),('C. petelotii (Y)',3.0358227079538556),('C. oleifera (W)',2.2872827081427265)]
    fig=plt.figure(figsize=(13.5,8.2))
    gs=fig.add_gridspec(2,2,height_ratios=[1.05,0.95])
    ax=fig.add_subplot(gs[0,0]);labels=[x[0] for x in rows];vals=[x[1] for x in rows];y=range(len(rows));ax.barh(list(y),vals);ax.set_yticks(list(y),labels);ax.invert_yaxis();ax.axvline(1,linestyle='--',linewidth=1);ax.set_xlabel('Fruit-set risk ratio: pollinator access / exclusion');ax.set_title('A  Cross-species pollinator-service magnitude')
    for i,v in enumerate(vals):ax.text(v+0.08,i,f'{v:.2f}×',va='center')
    ax.text(0.98,0.05,f"geometric mean = {cross['geometric_mean_RR']:.2f}×\nleave-one-out = {cross['leave_one_out_RR_min']:.2f}–{cross['leave_one_out_RR_max']:.2f}×",transform=ax.transAxes,ha='right',va='bottom',fontsize=10)

    ax=fig.add_subplot(gs[0,1]);olevals=[2.2872827081427265,2.56140350877193];labs=['bird access\nZhang 2024','A. cerana cage\nLiu 2025'];ax.bar(labs,olevals);ax.axhline(1,linestyle='--',linewidth=1);ax.set_ylabel('Fruit-set risk ratio');ax.set_title('B  Independent service replication within C. oleifera')
    for i,v in enumerate(olevals):ax.text(i,v+0.05,f'{v:.2f}×',ha='center')
    ax.text(0.5,0.05,f"2-study geometric mean = {ole['geometric_mean_RR']:.2f}×\nreliability gradients expected direction = {rel['expected_direction_count']}/{rel['k_effect_rows']}",transform=ax.transAxes,ha='center',va='bottom',fontsize=10)

    ax=fig.add_subplot(gs[1,:]);ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off');ax.set_title('C  Ecological support is strongest for reproductive service and its environmental mediation')
    items=[
      (0.11,'Molecular\naccessibility','supported'),
      (0.34,'Pollinator service\n/ reliability',f"RR 3.53 across A/Y/W\n{rel['expected_direction_count']}/{rel['k_effect_rows']} gradients"),
      (0.58,'Flowering-window\nclimate / season',f"{med['k_studies']} studies / {med['k_taxa']} taxa"),
      (0.82,'Evolutionary\npersistence','local colour\nconservatism'),
    ]
    for x,title,sub in items:
        ax.text(x,0.62,title,ha='center',va='center',fontsize=11,bbox=dict(boxstyle='round,pad=0.5',fill=False));ax.text(x,0.39,sub,ha='center',va='center',fontsize=9.5)
    for x1,x2 in zip([0.18,0.41,0.65],[0.27,0.51,0.75]):ax.annotate('',xy=(x2,0.62),xytext=(x1,0.62),arrowprops=dict(arrowstyle='->',lw=1.2))
    ax.text(0.50,0.17,f"Direct abiotic floral-pigment evidence: {abi['k_independent_experiments']} independent experiment (cold + darkness confounded)\nAccepted-species transition causation: still not identifiable across strict × dominant wild-colour scenarios",ha='center',va='center',fontsize=10)
    fig.suptitle('Fig. 6  Reproductive-service filtering is quantitatively supported, but historical colour-transition causation remains unresolved',fontsize=14)
    fig.tight_layout(rect=[0,0,1,0.95]);fig.savefig(a.out_dir/'Fig6_ecological_filtering_v2.png',dpi=240,bbox_inches='tight');fig.savefig(a.out_dir/'Fig6_ecological_filtering_v2.svg',bbox_inches='tight');plt.close(fig)

if __name__=='__main__':main()
