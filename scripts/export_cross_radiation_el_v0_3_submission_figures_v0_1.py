#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BUILDER=ROOT/"scripts"/"build_cross_radiation_evolution_letters_figures_v0_3_temporal_memory.py"


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-dir",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    a=ap.parse_args()
    a.out_dir.mkdir(parents=True,exist_ok=True)
    a.manifest.parent.mkdir(parents=True,exist_ok=True)

    spec=importlib.util.spec_from_file_location("frozen_v03_figures",BUILDER)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    original_save=mod.save
    produced=[]

    def save_pdf(fig,path:Path):
        target=path.with_suffix(".pdf")
        target.parent.mkdir(parents=True,exist_ok=True)
        fig.tight_layout()
        fig.savefig(target,format="pdf",bbox_inches="tight")
        mod.plt.close(fig)
        produced.append(target)

    mod.save=save_pdf
    try:
        for fn in (mod.fig1,mod.fig2,mod.fig3,mod.fig4,mod.fig5):
            fn(a.out_dir)
    finally:
        mod.save=original_save

    expected=[
      a.out_dir/"fig1_iris_profile.pdf",
      a.out_dir/"fig2_visible_clades_profiles.pdf",
      a.out_dir/"fig3_tree_moderators.pdf",
      a.out_dir/"fig4_petunieae_profile.pdf",
      a.out_dir/"fig5_relative_time_persistence.pdf",
    ]
    if produced!=expected:
        raise RuntimeError(f"submission figure set drift: {produced}")
    rows=[]
    for i,p in enumerate(expected,1):
        if not p.exists() or p.stat().st_size<=0:
            raise RuntimeError(f"missing submission PDF: {p}")
        rows.append({
          "figure":i,
          "filename":p.name,
          "format":"pdf",
          "bytes":p.stat().st_size,
          "sha256":sha256(p),
          "source_builder":str(BUILDER.relative_to(ROOT)),
          "source_builder_modified":False
        })
    out={
      "version":"v0.1",
      "status":"EL_V0_3_SUBMISSION_VECTOR_FIGURES_EXPORTED",
      "figures":rows,
      "accepted_initial_submission_format":"PDF",
      "frozen_science_builder_modified":False,
      "scientific_results_changed":False
    }
    a.manifest.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
