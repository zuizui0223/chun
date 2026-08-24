#!/usr/bin/env python3
"""Convert candidate-free real-data summaries to the frozen recurrence input schema.

This adapter deliberately separates direction estimation from significance filtering.
A direction is retained whenever the prespecified design identifies it; P-values and
consistency diagnostics are carried as metadata and never used post hoc to erase an
unfavourable direction.

Inputs are optional so systems can be added as their independent workflows complete:
- Joy Kendrick pilot_result.json
- C. sinensis stage_series_summary.json
- C. nitidissima trajectory_summary.json

Output primary columns are consumed by analyze_observation_corrected_recurrence_v0_1.py:
measurement_id,dependence_cluster,transition_class,axis,direction,status,source
Additional columns preserve effect/uncertainty provenance.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

AXES=("A","F","C","P")
DIRS={"up","down","same"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def finite(x) -> bool:
    return isinstance(x,(int,float)) and math.isfinite(float(x))


def base(mid,cluster,tclass,axis,direction,status,source,**extra):
    if axis not in AXES: raise ValueError(axis)
    if status=="resolved" and direction not in DIRS:
        raise ValueError(f"resolved direction must be up/down/same: {direction}")
    if status=="unresolved": direction="unresolved"
    return {
        "measurement_id":mid,"dependence_cluster":cluster,
        "transition_class":tclass,"axis":axis,"direction":direction,
        "status":status,"source":source,**extra
    }


def from_joy(path: Path):
    s=load(path)
    if s.get("contrast")!="CF_CJ_JOY_RED_PINK":
        raise ValueError("unexpected Joy contrast")
    out=[]
    for axis in AXES:
        e=s.get("effects",{}).get(axis,{})
        d=e.get("direction","unresolved")
        ok=e.get("effect_status")=="ok" and d in DIRS
        out.append(base(
            f"CF_CJ_JOY_RED_PINK:{axis}","CJAPONICA","anthocyanin_gain",axis,
            d,"resolved" if ok else "unresolved","Joy_Kendrick_candidate_free",
            estimator="red_minus_pink_Hedges_g",
            effect_value=e.get("hedges_g",""),
            uncertainty_metric="not_thresholded",
            uncertainty_value="",
            consistency_metric="same_cultivar_3v3",
            consistency_value="1" if ok else "",
            resolution_rule="effect_status_ok_and_finite_direction; significance not required"
        ))
    return out


def from_cs(path: Path):
    s=load(path)
    if s.get("dependence_cluster")!="CSIN_WHITE_PINK":
        raise ValueError("unexpected C. sinensis cluster")
    out=[]
    for axis in AXES:
        e=s.get("axes",{}).get(axis,{})
        d=e.get("primary_direction","unresolved")
        ok=e.get("status")=="stage_consistent" and d in DIRS
        out.append(base(
            f"CF_CS_WHITE_PINK_STAGE_SERIES:{axis}","CSIN_WHITE_PINK","anthocyanin_gain",axis,
            d,"resolved" if ok else "unresolved","C_sinensis_white_pink_candidate_free",
            estimator="equal_weight_mean_stagewise_Hedges_g",
            effect_value=e.get("equal_weight_mean_hedges_g",""),
            uncertainty_metric="stage_sign_consistency",
            uncertainty_value=e.get("sign_consistency",""),
            consistency_metric="estimable_stages",
            consistency_value=e.get("n_stages_estimable",""),
            resolution_rule=">=4/5 stages estimable and >=0.8 same-sign consistency; frozen upstream"
        ))
    return out


def from_cn(path: Path):
    s=load(path)
    if s.get("dependence_cluster")!="CNITIDISSIMA":
        raise ValueError("unexpected C. nitidissima cluster")
    out=[]
    for axis in AXES:
        e=s.get("axes",{}).get(axis,{})
        d=e.get("trend_direction","unresolved")
        if d=="flat": d="same"
        slope=e.get("slope")
        ok=(e.get("status")=="computed_all_five_prespecified_stages" and
            e.get("n_stages_resolved")==5 and finite(slope) and d in DIRS)
        out.append(base(
            f"CF_CN_ORDERED_S1_S5:{axis}","CNITIDISSIMA","yellow_development",axis,
            d,"resolved" if ok else "unresolved","C_nitidissima_candidate_free",
            estimator="OLS_slope_all_five_prespecified_stage_means",
            effect_value=slope if slope is not None else "",
            uncertainty_metric="exact_5factorial_stage_order_permutation_p",
            uncertainty_value=e.get("exact_order_p_two_sided",""),
            consistency_metric="adjacent_direction_consistency",
            consistency_value=e.get("adjacent_direction_consistency",""),
            resolution_rule="all 5 stages scorable and finite slope; P-value retained as uncertainty, not a direction filter"
        ))
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--joy",type=Path)
    ap.add_argument("--cs",type=Path)
    ap.add_argument("--cn",type=Path)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--summary",type=Path)
    a=ap.parse_args()
    rows=[]; systems=[]
    if a.joy: rows.extend(from_joy(a.joy)); systems.append("CJAPONICA")
    if a.cs: rows.extend(from_cs(a.cs)); systems.append("CSIN_WHITE_PINK")
    if a.cn: rows.extend(from_cn(a.cn)); systems.append("CNITIDISSIMA")
    if not rows: raise ValueError("at least one real-data summary is required")
    a.out.parent.mkdir(parents=True,exist_ok=True)
    fields=["measurement_id","dependence_cluster","transition_class","axis","direction","status","source",
            "estimator","effect_value","uncertainty_metric","uncertainty_value","consistency_metric","consistency_value","resolution_rule"]
    with a.out.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    sm={
        "status":"candidate_free_measurement_registry_built",
        "systems":systems,"n_rows":len(rows),
        "resolved_rows":sum(r["status"]=="resolved" for r in rows),
        "direction_policy":"direction is retained whenever the prespecified design identifies it; significance thresholds never select favourable axes",
        "system_rules":{
            "CJAPONICA":"effect status ok in frozen same-cultivar 3v3 contrast",
            "CSIN_WHITE_PINK":">=4/5 stage effects and >=0.8 same-sign consistency (pre-frozen upstream)",
            "CNITIDISSIMA":"all 5 stages scorable + finite ordered slope; exact permutation P retained as uncertainty only"
        }
    }
    sp=a.summary or a.out.with_suffix(".summary.json")
    sp.write_text(json.dumps(sm,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(sm,indent=2,ensure_ascii=False))

if __name__=="__main__": main()
