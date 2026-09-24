#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]

ARCH=ROOT/"results/flowerclades51_memory_architecture_v0_1/summary_v0_1.json"
HIDDEN=ROOT/"data/flowerclades51_hidden_fine_memory_clades_v0_1.csv"
OPP=ROOT/"data/flowerclades51_resolution_opportunity_metrics_v0_1.csv"
PET=ROOT/"results/petunieae_hidden_memory_v0_1/summary_v0_1.json"
SYN=ROOT/"data/hierarchical_evolutionary_memory_synthesis_v0_2.json"
SCH=ROOT/"results/schistanthe_hidden_memory_v0_1/result_v0_1.json"
RUE=ROOT/"data/ruellia51_hidden_memory_prediction_v0_1.json"
GATE=ROOT/"data/cross_radiation_evolution_letters_v0_8_hierarchical_memory_gate.json"


def figure_specs()->list[dict]:
    return [
        {"figure":1,"filename":"fig1_memory_architecture.png",
         "sources":[str(ARCH.relative_to(ROOT))]},
        {"figure":2,"filename":"fig2_hidden_memory_clades.png",
         "sources":[str(HIDDEN.relative_to(ROOT))]},
        {"figure":3,"filename":"fig3_hidden_vs_global_tilt.png",
         "sources":[str(HIDDEN.relative_to(ROOT)),str(OPP.relative_to(ROOT))]},
        {"figure":4,"filename":"fig4_petunieae_hidden_memory.png",
         "sources":[str(PET.relative_to(ROOT))]},
        {"figure":5,"filename":"fig5_evidence_tiers.png",
         "sources":[str(SYN.relative_to(ROOT)),str(SCH.relative_to(ROOT)),str(RUE.relative_to(ROOT)),str(GATE.relative_to(ROOT))]},
    ]


def git_blob_sha(path:Path)->str:
    data=path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()


def load_hidden_architecture_join()->pd.DataFrame:
    h=pd.read_csv(HIDDEN)
    o=pd.read_csv(OPP)[["clade","amplitude","scale_tilt","intermediate_curvature"]]
    d=h.merge(o,on="clade",how="inner",validate="one_to_one")
    if len(d)!=21:
        raise ValueError(f"expected 21 opportunity clades, found {len(d)}")
    return d


def _save(fig,path:Path):
    fig.savefig(path,dpi=300,bbox_inches="tight")
    plt.close(fig)


def fig1(out:Path):
    x=json.loads(ARCH.read_text())
    names=["Memory\namplitude","Scale\ntilt","Intermediate\ncurvature"]
    keys=["amplitude","scale_tilt","intermediate_curvature"]
    y=np.array([x["variance_share"][k]*100 for k in keys])
    lo=np.array([x["variance_share_bootstrap95"][k][0]*100 for k in keys])
    hi=np.array([x["variance_share_bootstrap95"][k][1]*100 for k in keys])
    fig,ax=plt.subplots(figsize=(6.6,4.8))
    pos=np.arange(3)
    ax.bar(pos,y)
    ax.errorbar(pos,y,yerr=np.vstack([y-lo,hi-y]),fmt="none",capsize=4)
    ax.set_xticks(pos,names)
    ax.set_ylabel("Between-clade profile variance (%)")
    ax.set_title("Most profile variation is overall memory amplitude")
    ax.set_ylim(0,102)
    for i,v in enumerate(y):
        ax.text(i,v+2.5,f"{v:.1f}%",ha="center",va="bottom")
    ax.spines[["top","right"]].set_visible(False)
    _save(fig,out/"fig1_memory_architecture.png")


def fig2(out:Path):
    d=pd.read_csv(HIDDEN).sort_values("centered_auc_effect")
    fig,ax=plt.subplots(figsize=(7.2,7.4))
    y=np.arange(len(d))
    sig=d["p_one_sided"]<=0.05
    ax.axvline(0,linewidth=1,linestyle="--")
    ax.scatter(d.loc[~sig,"centered_auc_effect"],y[~sig],label="P > 0.05")
    ax.scatter(d.loc[sig,"centered_auc_effect"],y[sig],marker="D",label="P ≤ 0.05")
    med=float(d["centered_auc_effect"].median())
    ax.axvline(med,linewidth=1,linestyle=":")
    ax.set_yticks(y,d["clade"])
    ax.set_xlabel("Within-coarse hidden-memory effect\nObserved conditional AUC − permutation-null mean")
    ax.set_title("Fine identity retains hidden phylogenetic memory in 18/21 clades")
    ax.text(0.98,0.02,f"median = {med:+.3f} AUC",transform=ax.transAxes,ha="right",va="bottom")
    ax.legend(frameon=False,loc="lower right")
    ax.spines[["top","right"]].set_visible(False)
    _save(fig,out/"fig2_hidden_memory_clades.png")


def _spearman_rho(a:pd.Series,b:pd.Series)->float:
    ar=a.rank(method="average").to_numpy(float)
    br=b.rank(method="average").to_numpy(float)
    return float(np.corrcoef(ar,br)[0,1])


def fig3(out:Path):
    d=load_hidden_architecture_join()
    fig,ax=plt.subplots(figsize=(6.2,5.2))
    ax.axhline(0,linewidth=1,linestyle="--")
    ax.axvline(0,linewidth=1,linestyle="--")
    ax.scatter(d["scale_tilt"],d["centered_auc_effect"])
    neg=d[d["scale_tilt"]<0]
    for row in neg.itertuples():
        ax.annotate(row.clade,(row.scale_tilt,row.centered_auc_effect),
                    xytext=(4,4),textcoords="offset points",fontsize=8)
    rho=_spearman_rho(d["scale_tilt"],d["centered_auc_effect"])
    ax.text(0.03,0.97,f"Spearman ρ = {rho:.2f}\n5/6 coarse-tilted clades retain hidden memory",
            transform=ax.transAxes,ha="left",va="top")
    ax.set_xlabel("Global scale tilt (AUC fine − AUC coarse)")
    ax.set_ylabel("Within-coarse hidden-memory effect")
    ax.set_title("Hidden fine memory is distinct from the global winning scale")
    ax.spines[["top","right"]].set_visible(False)
    _save(fig,out/"fig3_hidden_vs_global_tilt.png")


def fig4(out:Path):
    x=json.loads(PET.read_text())
    fig,ax=plt.subplots(figsize=(6.4,3.4))
    null=float(x["null_mean_auc"])
    lo=float(x["null_q025"]); hi=float(x["null_q975"])
    obs=float(x["conditional_auc"])
    ax.hlines(0,lo,hi,linewidth=5,label="Permutation-null 95% interval")
    ax.plot(null,0,"o",label="Null mean")
    ax.plot(obs,0,"D",markersize=9,label="Observed")
    ax.set_xlim(min(0.44,lo-0.02),max(0.73,obs+0.02))
    ax.set_yticks([])
    ax.set_xlabel("Within-coarse conditional AUC")
    ax.set_title("Petunieae: fine biochemical identity remains organized within coarse states")
    ax.text(obs,0.13,f"effect = {x['centered_auc_effect']:+.3f}\nP = {x['p_one_sided']:.4f}",
            ha="center",va="bottom")
    ax.legend(frameon=False,loc="lower left")
    ax.spines[["top","right","left"]].set_visible(False)
    _save(fig,out/"fig4_petunieae_hidden_memory.png")


def fig5(out:Path):
    s=json.loads(SYN.read_text())
    sch=json.loads(SCH.read_text())
    r=json.loads(RUE.read_text())
    g=json.loads(GATE.read_text())
    fig,ax=plt.subplots(figsize=(8.4,6.6))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    boxes=[
      (0.50,0.87,"Tier A — standardized visible color\n21 opportunity clades; 18 positive\nmedian hidden effect +0.0270"),
      (0.50,0.69,"Tier B — biochemical Petunieae\nretrospective same-estimand bridge\n+0.1879 AUC; P = 0.0001"),
      (0.50,0.51,"Tier C — external radiations\nLinoideae • Angraecinae • Antirrhineae\n3/3 source-faithful support; not pooled"),
      (0.50,0.31,"Tier D — prospective Schistanthe PASS\n129 tips • centered effect +0.0642\nP = 0.0033"),
      (0.50,0.11,"Tier E — prospective biochemical Ruellia\noutcome unopened\ncross-representation gate still pending"),
    ]
    for x,y,t in boxes:
        ax.text(x,y,t,ha="center",va="center",
                bbox=dict(boxstyle="round,pad=0.55",fill=False),fontsize=9.5)
    for y1,y2 in [(0.80,0.76),(0.62,0.58),(0.44,0.38),(0.24,0.18)]:
        ax.annotate("",xy=(0.5,y2),xytext=(0.5,y1),arrowprops=dict(arrowstyle="->"))
    ax.text(0.02,0.98,"Evidence tiers remain separate; nonexchangeable P-values are not pooled",ha="left",va="top",fontsize=8.5)
    ax.text(0.98,0.02,
            f"Schistanthe: {sch['status']}\nRuellia: {r['status']}\nv0.8 remains non-current",
            ha="right",va="bottom",fontsize=7.8)
    ax.set_title("Hierarchical evolutionary memory: retrospective prevalence, prospective validation, biochemical gate",pad=12)
    _save(fig,out/"fig5_evidence_tiers.png")


def build_all(outdir:Path)->dict:
    outdir.mkdir(parents=True,exist_ok=True)
    fig1(outdir); fig2(outdir); fig3(outdir); fig4(outdir); fig5(outdir)
    specs=figure_specs()
    source_paths=sorted({p for row in specs for p in row["sources"]})
    blobs={p:git_blob_sha(ROOT/p) for p in source_paths}
    rows=[]
    for spec in specs:
        p=outdir/spec["filename"]
        rows.append({
            **spec,
            "bytes":p.stat().st_size,
            "source_git_blob_sha":{s:blobs[s] for s in spec["sources"]},
        })
    manifest={
        "version":"v0.1",
        "status":"EL_V0_8_HIERARCHICAL_MEMORY_FIGURES_BUILT",
        "candidate":"Evolution Letters v0.8 hierarchical memory with Schistanthe",
        "current_submission_unchanged":"Evolution Letters v0.3",
        "figures":rows,
        "science_changed":False,
    }
    (outdir/"figure_build_manifest_v0_1.json").write_text(
        json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return manifest


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",type=Path,required=True)
    a=ap.parse_args()
    x=build_all(a.outdir)
    print(json.dumps({"status":x["status"],"figures":[(q["figure"],q["filename"],q["bytes"]) for q in x["figures"]]},indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
