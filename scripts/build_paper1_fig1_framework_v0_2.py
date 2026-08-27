#!/usr/bin/env python3
"""Build Paper 1 Fig. 1 from the frozen inferential hierarchy and observation contract."""
from __future__ import annotations
import argparse,csv,json,textwrap
from pathlib import Path
import matplotlib.pyplot as plt

def read(p):
    with p.open(newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
    if not rows: raise ValueError(f'empty input: {p}')
    return rows

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--framework',type=Path,required=True); ap.add_argument('--observation',type=Path,required=True); ap.add_argument('--out-dir',type=Path,required=True); a=ap.parse_args()
    fw=read(a.framework); ob=read(a.observation)
    if [int(r['order']) for r in fw] != [1,2,3,4,5,6]: raise ValueError('framework order drift')
    lit={r['feature']:r for r in ob if r['regime']=='published_literature'}
    cf={r['feature']:r for r in ob if r['regime']=='candidate_free'}
    if [int(lit[f'{x}_axis_system_coverage']['value']) for x in ('A','F','C','P')] != [8,4,1,3]: raise ValueError('literature coverage drift')
    if int(cf['canonical_systems']['value'])!=5 or int(cf['canonical_cluster_axis_cells']['value'])!=20 or int(cf['resolved_cluster_axis_cells']['value'])!=19 or int(cf['significance_filter']['value'])!=0: raise ValueError('candidate-free contract drift')
    a.out_dir.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(1,2,figsize=(16.5,6.0),gridspec_kw={'width_ratios':[1.55,1]})
    ax=axes[0]; ax.axis('off'); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.set_title('A  Observation-to-realization hierarchy')
    ys=[.87,.72,.57,.42,.27,.12]
    for i,(r,y) in enumerate(zip(fw,ys)):
        title=textwrap.fill(r['title'],width=23,break_long_words=False)
        ax.text(.045,y,title,fontsize=9.6,weight='bold',va='center',linespacing=1.0)
        ax.text(.39,y,r['empirical_anchor'],fontsize=8.2,va='center',wrap=True)
        if i<len(fw)-1: ax.annotate('',xy=(.017,y-.08),xytext=(.017,y-.035),arrowprops={'arrowstyle':'->','lw':1.4})
    ax.text(.51,.015,'Each layer is measured separately; downstream outcomes do not fill upstream missing states.',ha='center',fontsize=8.4,weight='bold')
    ax=axes[1]; ax.set_title('B  The observation regime changes what is identifiable')
    axes_names=['A','F','C','P']; vals=[8,4,1,3]
    ax.bar(range(4),vals); ax.set_xticks(range(4),axes_names); ax.set_ylabel('Published biological systems measuring axis'); ax.set_ylim(0,9)
    for i,v in enumerate(vals): ax.text(i,v+.15,str(v),ha='center',fontsize=9)
    ax.text(.38,.98,'Candidate-free protocol:',transform=ax.transAxes,va='top',fontsize=9.5,weight='bold')
    ax.text(.38,.90,'5 systems × 4 axes = 20 canonical cells\n19 resolved; 1 unresolved kept unresolved\n0 significance/expected-direction filters',transform=ax.transAxes,va='top',fontsize=8.8)
    ax.text(.38,.64,'Observed literature recurrence\n≠ biological recurrence by definition',transform=ax.transAxes,va='top',fontsize=9,weight='bold')
    fig.suptitle('Mechanistic feasibility, observation, recurrence, realization and event identity are distinct quantities',fontsize=12)
    fig.tight_layout(rect=[0,.02,1,.93])
    svg=a.out_dir/'paper1_fig1_framework_v0_2.svg'; png=a.out_dir/'paper1_fig1_framework_v0_2.png'
    fig.savefig(svg,bbox_inches='tight'); fig.savefig(png,dpi=300,bbox_inches='tight'); plt.close(fig)
    s={'status':'paper1_fig1_framework_built','framework_rows':len(fw),'observation_rows':len(ob),'claim_boundary':'conceptual synthesis of frozen empirical layers; no new biological inference','outputs':[str(svg),str(png)]}
    (a.out_dir/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8'); print(json.dumps(s,indent=2))
if __name__=='__main__': main()
