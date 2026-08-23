#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import matplotlib.pyplot as plt


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--summary',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    s=json.loads(a.summary.read_text())
    cross=s['cross_species_pollinator_service'];ole=s['oleifera_within_species_service_replication'];rel=s['pollinator_reliability_gradients'];med=s['climate_season_pollinator_mediation'];abi=s['direct_abiotic_floral_pigment']
    rows=[('C. japonica (A)',6.3508771929824555),('C. petelotii (Y)',3.0358227079538556),('C. oleifera (W)',2.2872827081427265)]
    fig=plt.figure(figsize=(13.5,8.5));gs=fig.add_gridspec(2,2,height_ratios=[1.0,1.08])

    ax=fig.add_subplot(gs[0,0]);labels=[x[0] for x in rows];vals=[x[1] for x in rows];y=range(len(rows));ax.barh(list(y),vals);ax.set_yticks(list(y),labels);ax.invert_yaxis();ax.axvline(1,linestyle='--',linewidth=1);ax.set_xlabel('Fruit-set risk ratio: pollinator access / exclusion');ax.set_title('A  Cross-species pollinator-service magnitude')
    for i,v in enumerate(vals):ax.text(v+0.08,i,f'{v:.2f}×',va='center')
    ax.text(0.98,0.05,f"geometric mean = {cross['geometric_mean_RR']:.2f}×\nleave-one-out = {cross['leave_one_out_RR_min']:.2f}–{cross['leave_one_out_RR_max']:.2f}×",transform=ax.transAxes,ha='right',va='bottom',fontsize=10)

    ax=fig.add_subplot(gs[0,1]);olevals=[2.2872827081427265,2.56140350877193];labs=['bird access\nZhang 2024','A. cerana cage\nLiu 2025'];ax.bar(labs,olevals);ax.axhline(1,linestyle='--',linewidth=1);ax.set_ylabel('Fruit-set risk ratio');ax.set_ylim(0,3.05);ax.set_title('B  Independent service replication within C. oleifera')
    for i,v in enumerate(olevals):ax.text(i,v+0.06,f'{v:.2f}×',ha='center')
    ax.text(0.5,0.94,f"2-study geometric mean = {ole['geometric_mean_RR']:.2f}×\nreliability gradients expected direction = {rel['expected_direction_count']}/{rel['k_effect_rows']}",transform=ax.transAxes,ha='center',va='top',fontsize=10,bbox=dict(boxstyle='round,pad=0.3',fill=False))

    ax=fig.add_subplot(gs[1,:]);ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off');ax.set_title('C  A conditional ecological-filtering model is supported at the mechanism/service level')
    boxes=[
      (0.08,0.61,'Molecular\naccessibility','multiple routes'),
      (0.27,0.61,'Latent floral state','pigment • spectra\nreward • phenology'),
      (0.55,0.61,'Pollinator service\n/ reliability',f"RR 3.53 across A/Y/W\n{rel['expected_direction_count']}/{rel['k_effect_rows']} gradients"),
      (0.76,0.61,'Reproductive\nsuccess','service-dependent'),
      (0.93,0.61,'Evolutionary\npersistence','local colour\nconservatism'),
    ]
    for x,y0,title,sub in boxes:
        ax.text(x,y0,title,ha='center',va='center',fontsize=10.5,bbox=dict(boxstyle='round,pad=0.45',fill=False));ax.text(x,y0-0.20,sub,ha='center',va='center',fontsize=9)
    for x1,x2 in [(0.13,0.21),(0.34,0.47),(0.63,0.70),(0.82,0.88)]:ax.annotate('',xy=(x2,0.61),xytext=(x1,0.61),arrowprops=dict(arrowstyle='->',lw=1.2))
    ax.text(0.55,0.91,'Flowering-window climate / season',ha='center',va='center',fontsize=10.5,bbox=dict(boxstyle='round,pad=0.4',fill=False));ax.text(0.55,0.79,f"{med['k_studies']} studies / {med['k_taxa']} taxa",ha='center',fontsize=9)
    ax.annotate('',xy=(0.55,0.70),xytext=(0.55,0.84),arrowprops=dict(arrowstyle='->',lw=1.2));ax.annotate('',xy=(0.47,0.61),xytext=(0.34,0.84),arrowprops=dict(arrowstyle='->',lw=1.0))
    ax.text(0.50,0.12,f"Direct abiotic floral-pigment evidence: {abi['k_independent_experiments']} independent experiment (cold + darkness confounded)\nAccepted-species transition causation: still not identifiable across strict × dominant wild-colour scenarios",ha='center',va='center',fontsize=9.8)
    fig.suptitle('Fig. 6  Reproductive-service filtering is quantitatively supported, but historical colour-transition causation remains unresolved',fontsize=14)
    fig.tight_layout(rect=[0,0,1,0.95]);fig.savefig(a.out_dir/'Fig6_ecological_filtering_v2.png',dpi=240,bbox_inches='tight');fig.savefig(a.out_dir/'Fig6_ecological_filtering_v2.svg',bbox_inches='tight');plt.close(fig)

if __name__=='__main__':main()
