#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest, wilcoxon

ROOT=Path(__file__).resolve().parents[1]
HIDDEN=ROOT/"data"/"flowerclades51_hidden_fine_memory_clades_v0_1.csv"
PROFILE=ROOT/"results"/"flowerclades51_resolution_profile_v0_1"/"flowerclades51_resolution_profile_summary_v0_1.csv"
DESIGN=ROOT/"data"/"cryptic_hidden_memory_no_global_signal_design_v0_1.json"


def read_rows(path:Path)->list[dict]:
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))


def group_summary(vals:list[float])->dict:
    a=np.asarray(vals,float)
    nz=a[a!=0]
    pos=int(np.sum(nz>0))
    neg=int(np.sum(nz<0))
    p=float(binomtest(pos,len(nz),0.5,alternative="greater").pvalue) if len(nz) else float("nan")
    if len(nz):
        try:
            w=wilcoxon(nz,alternative="greater",zero_method="wilcox")
            wp=float(w.pvalue)
            ws=float(w.statistic)
        except ValueError:
            wp=float("nan"); ws=float("nan")
    else:
        wp=float("nan"); ws=float("nan")
    return {
      "n":int(len(a)),
      "nonzero_n":int(len(nz)),
      "positive":pos,
      "negative":neg,
      "positive_fraction_nonzero":float(pos/len(nz)) if len(nz) else None,
      "median_centered_auc_effect":float(np.median(a)),
      "mean_centered_auc_effect":float(np.mean(a)),
      "sign_test_p_one_sided":p,
      "wilcoxon_statistic":ws,
      "wilcoxon_p_one_sided":wp,
    }


def build()->dict:
    design=json.loads(DESIGN.read_text())
    hidden={r["clade"]:r for r in read_rows(HIDDEN)}
    profile={r["clade"]:r for r in read_rows(PROFILE)}
    if len(hidden)!=21:
        raise ValueError(f"expected 21 hidden-memory opportunity clades, got {len(hidden)}")

    focal=[]
    signalled=[]
    rows=[]
    for clade,h in hidden.items():
        if clade not in profile:
            raise ValueError(f"missing frozen global profile for {clade}")
        term=profile[clade]["terminal_class"]
        effect=float(h["centered_auc_effect"])
        row={"clade":clade,"global_terminal_class":term,"hidden_centered_auc_effect":effect,"hidden_p_one_sided":float(h["p_one_sided"])}
        rows.append(row)
        if term=="PROFILE_NO_PHYLOGENETIC_SIGNAL":
            focal.append(effect)
        elif term.startswith("PROFILE_SIGNALLED_"):
            signalled.append(effect)
        else:
            raise ValueError(f"unexpected terminal class in hidden-memory frame: {clade} {term}")

    focal_summary=group_summary(focal)
    signalled_summary=group_summary(signalled)
    supported=bool(focal_summary["median_centered_auc_effect"]>0 and focal_summary["sign_test_p_one_sided"]<=0.05)

    return {
      "version":"v0.1",
      "status":"CRYPTIC_HIDDEN_MEMORY_NO_GLOBAL_SIGNAL_EXPLORATORY_RESULT",
      "analysis_role":design["analysis_role"],
      "opportunity_clades_total":len(hidden),
      "globally_no_signal":focal_summary,
      "globally_signalled":signalled_summary,
      "primary":{
        "test":"exact one-sided binomial sign test among globally no-signal opportunity clades",
        "support_rule":design["primary_test"]["support_rule"],
        "supported":supported,
      },
      "rows":rows,
      "interpretation":(
        design["interpretation_if_supported"] if supported
        else design["interpretation_if_not_supported"]
      ),
      "architectural_implication":(
        "Global unconditional signal status and within-coarse hidden fine-state organization are not interchangeable measurements. "
        "The focal subgroup can contain positive hidden effects even when the global profile does not cross its frozen phylogenetic-signal gates; subgroup-level inferential wording follows the frozen sign-test decision."
      ),
      "claim_boundary":design["boundaries"],
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False,
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    out=build()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":out["status"],
      "globally_no_signal":out["globally_no_signal"],
      "globally_signalled":out["globally_signalled"],
      "primary":out["primary"],
      "interpretation":out["interpretation"]
    },indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
