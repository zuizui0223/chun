#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
from Bio import Phylo
from scipy.stats import rankdata

ROOT=Path(__file__).resolve().parents[1]
BASE_PATH=ROOT/"scripts"/"analyze_gesnerioideae_biochemical_hidden_memory_v0_1.py"
spec=importlib.util.spec_from_file_location("base_hidden_memory",BASE_PATH)
base=importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

PERMUTATIONS=9999
SEED=20260920


def rebuild_null(gate_path:Path, frame_path:Path, tree_path:Path,
                 permutations:int=PERMUTATIONS, seed:int=SEED)->dict:
    gate=json.loads(gate_path.read_text())
    frame=json.loads(frame_path.read_text())
    rows=frame["rows"]
    tips=[r["tree_tip"] for r in rows]

    tree=Phylo.read(str(tree_path),"newick")
    keep=set(tips)
    for terminal in list(tree.get_terminals()):
        if terminal.name not in keep:
            tree.prune(terminal)
    terminals={t.name:t for t in tree.get_terminals()}

    coarse_labels=[r["coarse_state"] for r in rows]
    fine_labels=[r["fine_state"] for r in rows]
    cmap={x:i for i,x in enumerate(sorted(set(coarse_labels)))}
    fmap={x:i for i,x in enumerate(sorted(set(fine_labels)))}
    coarse=np.array([cmap[x] for x in coarse_labels],dtype=np.int8)
    fine=np.array([fmap[x] for x in fine_labels],dtype=np.int16)

    ii,jj=base.same_coarse_pair_indices(coarse)
    dist=np.array([
        tree.distance(terminals[tips[int(a)]],terminals[tips[int(b)]])
        for a,b in zip(ii,jj)
    ],dtype=float)
    ranks=rankdata(-dist,method="average").astype(float)
    y=fine[ii]==fine[jj]
    observed=base.auc_from_y_ranks(y,ranks)

    rng=np.random.default_rng(seed)
    null=np.empty(permutations,dtype=float)
    for b in range(permutations):
        p=base.permute_fine_within_coarse(fine,coarse,rng)
        null[b]=base.auc_from_y_ranks(p[ii]==p[jj],ranks)

    return {
        "observed":float(observed),
        "null":null,
        "tips":len(rows),
        "same_coarse_pairs":int(len(ii)),
        "same_fine_pairs":int(y.sum()),
        "different_fine_pairs":int(len(y)-y.sum()),
        "coarse_state_count":len(cmap),
        "fine_state_count":len(fmap),
        "gate_status":gate["status"],
    }


def audit(gate_path:Path, frame_path:Path, tree_path:Path,
          frozen_result_path:Path, schistanthe_result_path:Path)->dict:
    frozen=json.loads(frozen_result_path.read_text())
    sch=json.loads(schistanthe_result_path.read_text())
    x=rebuild_null(gate_path,frame_path,tree_path)
    null=x.pop("null")

    null_mean=float(null.mean())
    q95=float(np.quantile(null,0.95))
    critical_centered=float(q95-null_mean)
    observed_centered=float(x["observed"]-null_mean)
    sch_effect=float(sch["centered_auc_effect"])

    if abs(x["observed"]-float(frozen["conditional_auc"]))>1e-12:
        raise ValueError("observed AUC drift from frozen prospective result")
    if abs(null_mean-float(frozen["null_mean_auc"]))>1e-12:
        raise ValueError("null mean drift from frozen prospective result")
    if abs(observed_centered-float(frozen["centered_auc_effect"]))>1e-12:
        raise ValueError("centered effect drift from frozen prospective result")

    return {
        "version":"v0.1",
        "status":"POST_OUTCOME_GESNERIOIDEAE_FAIL_INFORMATIVENESS_AUDIT",
        "analysis_role":"POST_OUTCOME_DIAGNOSTIC_NO_PROSPECTIVE_DECISION_CHANGE",
        "prospective_terminal_status":frozen["status"],
        "prospective_terminal_status_changed":False,
        "promotion_gate_pass_changed":False,
        "eligible_tips":x["tips"],
        "same_coarse_pairs":x["same_coarse_pairs"],
        "same_fine_pairs":x["same_fine_pairs"],
        "different_fine_pairs":x["different_fine_pairs"],
        "coarse_state_count":x["coarse_state_count"],
        "fine_state_count":x["fine_state_count"],
        "observed_conditional_auc":x["observed"],
        "null_mean_auc":null_mean,
        "one_sided_alpha_0_05_auc_critical":q95,
        "one_sided_alpha_0_05_centered_effect_critical":critical_centered,
        "observed_centered_effect":observed_centered,
        "observed_margin_to_critical_effect":float(observed_centered-critical_centered),
        "schistanthe_prospective_centered_effect":sch_effect,
        "schistanthe_effect_minus_gesnerioideae_critical_effect":float(sch_effect-critical_centered),
        "schistanthe_sized_point_effect_would_cross_gesnerioideae_null_critical_value":bool(sch_effect>=critical_centered),
        "diagnostic_interpretation":(
            "This audit measures the exact one-sided null critical effect for the frozen Gesnerioideae design. "
            "It is not a power analysis and does not change the prospective FAIL. The Schistanthe comparison asks only "
            "whether a point effect of the observed Schistanthe magnitude would exceed this design's null critical threshold."
        ),
        "permutations":PERMUTATIONS,
        "seed":SEED,
        "no_posthoc_rescue":True,
        "el_v0_3_science_changed":False,
        "paper1_science_changed":False,
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--gate",type=Path,required=True)
    ap.add_argument("--frame",type=Path,required=True)
    ap.add_argument("--tree",type=Path,required=True)
    ap.add_argument("--frozen-result",type=Path,required=True)
    ap.add_argument("--schistanthe-result",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    out=audit(a.gate,a.frame,a.tree,a.frozen_result,a.schistanthe_result)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
