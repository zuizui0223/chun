#!/usr/bin/env python3
"""Convert candidate-free real-data summaries to the frozen recurrence input schema.

Canonical dependence-cluster, transition-class, and direction-frame metadata come from
one frozen bridge table rather than being duplicated in code. Direction estimation is
separate from significance filtering: P-values/consistency diagnostics are retained as
metadata and never used post hoc to erase an unfavourable direction.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

AXES = ("A", "F", "C", "P")
DIRS = {"up", "down", "same"}
SYSTEMS = ("CJAPONICA", "CRETICULATA", "CSIN_WHITE_PINK", "CNITIDISSIMA")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_bridge(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    required = {
        "system_key", "dependence_cluster", "transition_class", "literature_anchor_edge",
        "canonical_target", "source_visible", "target_visible", "source_condition_rule",
        "target_condition_rule", "direction_frame",
    }
    if not rows or not required <= set(rows[0]):
        missing = sorted(required - set(rows[0] if rows else []))
        raise ValueError(f"canonical bridge is empty or missing columns: {missing}")
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row["system_key"]
        if key in out:
            raise ValueError(f"duplicate bridge system_key: {key}")
        out[key] = row
    missing_systems = sorted(set(SYSTEMS) - set(out))
    if missing_systems:
        raise ValueError(f"canonical bridge missing systems: {missing_systems}")
    return out


def finite(x) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(float(x))


def base(mid, cfg, axis, direction, status, source, **extra):
    if axis not in AXES:
        raise ValueError(axis)
    if status == "resolved" and direction not in DIRS:
        raise ValueError(f"resolved direction must be up/down/same: {direction}")
    if status == "unresolved":
        direction = "unresolved"
    return {
        "measurement_id": mid,
        "dependence_cluster": cfg["dependence_cluster"],
        "transition_class": cfg["transition_class"],
        "axis": axis,
        "direction": direction,
        "status": status,
        "source": source,
        "literature_anchor_edge": cfg["literature_anchor_edge"],
        "canonical_target": cfg["canonical_target"],
        "direction_frame": cfg["direction_frame"],
        **extra,
    }


def from_joy(path: Path, cfg):
    if cfg["direction_frame"] != "target_minus_source":
        raise ValueError("Joy bridge must use target_minus_source")
    s = load_json(path)
    if s.get("contrast") != "CF_CJ_JOY_RED_PINK":
        raise ValueError("unexpected Joy contrast")
    out = []
    for axis in AXES:
        e = s.get("effects", {}).get(axis, {})
        d = e.get("direction", "unresolved")
        ok = e.get("effect_status") == "ok" and d in DIRS
        out.append(base(
            f"CF_CJ_JOY_RED_PINK:{axis}", cfg, axis, d,
            "resolved" if ok else "unresolved", "Joy_Kendrick_candidate_free",
            estimator="red_minus_pink_Hedges_g",
            effect_value=e.get("hedges_g", ""),
            uncertainty_metric="not_thresholded",
            uncertainty_value="",
            consistency_metric="same_cultivar_3v3",
            consistency_value="1" if ok else "",
            resolution_rule="effect_status_ok_and_direction_resolved; significance not required",
        ))
    return out


def from_cr(path: Path, cfg):
    if cfg["direction_frame"] != "target_minus_source":
        raise ValueError("C. reticulata bridge must use target_minus_source")
    s = load_json(path)
    if s.get("contrast") != "CF_CR_MN_FB_WHITE_RED" or s.get("dependence_cluster") != cfg["dependence_cluster"]:
        raise ValueError("unexpected C. reticulata contrast or cluster")
    out = []
    for axis in AXES:
        e = s.get("effects", {}).get(axis, {})
        d = e.get("direction", "unresolved")
        ok = e.get("effect_status") == "ok" and d in DIRS
        out.append(base(
            f"CF_CR_MN_FB_WHITE_RED:{axis}", cfg, axis, d,
            "resolved" if ok else "unresolved", "C_reticulata_MN_sector_candidate_free",
            estimator="red_region_minus_white_region_Hedges_g",
            effect_value=e.get("hedges_g", ""),
            uncertainty_metric="not_thresholded",
            uncertainty_value="",
            consistency_metric="same_cultivar_same_stage_3v3",
            consistency_value="1" if ok else "",
            resolution_rule="effect_status_ok_and_direction_resolved; significance not required",
        ))
    return out


def from_cs(path: Path, cfg):
    if cfg["direction_frame"] != "target_minus_source":
        raise ValueError("C. sinensis bridge must use target_minus_source")
    s = load_json(path)
    if s.get("dependence_cluster") != cfg["dependence_cluster"]:
        raise ValueError("unexpected C. sinensis cluster")
    out = []
    for axis in AXES:
        e = s.get("axes", {}).get(axis, {})
        d = e.get("primary_direction", "unresolved")
        ok = e.get("status") == "stage_consistent" and d in DIRS
        out.append(base(
            f"CF_CS_WHITE_PINK_STAGE_SERIES:{axis}", cfg, axis, d,
            "resolved" if ok else "unresolved", "C_sinensis_white_pink_candidate_free",
            estimator="equal_weight_mean_stagewise_Hedges_g",
            effect_value=e.get("equal_weight_mean_hedges_g", ""),
            uncertainty_metric="stage_sign_consistency",
            uncertainty_value=e.get("sign_consistency", ""),
            consistency_metric="estimable_stages",
            consistency_value=e.get("n_stages_estimable", ""),
            resolution_rule=">=4/5 stages estimable and >=0.8 same-sign consistency; frozen upstream",
        ))
    return out


def from_cn(path: Path, cfg):
    if cfg["direction_frame"] != "ordered_slope_source_to_target":
        raise ValueError("C. nitidissima bridge must use ordered_slope_source_to_target")
    s = load_json(path)
    if s.get("dependence_cluster") != cfg["dependence_cluster"]:
        raise ValueError("unexpected C. nitidissima cluster")
    out = []
    for axis in AXES:
        e = s.get("axes", {}).get(axis, {})
        d = e.get("trend_direction", "unresolved")
        if d == "flat":
            d = "same"
        slope = e.get("slope")
        ok = (
            e.get("status") == "computed_all_five_prespecified_stages"
            and e.get("n_stages_resolved") == 5
            and finite(slope)
            and d in DIRS
        )
        out.append(base(
            f"CF_CN_ORDERED_S1_S5:{axis}", cfg, axis, d,
            "resolved" if ok else "unresolved", "C_nitidissima_candidate_free",
            estimator="OLS_slope_all_five_prespecified_stage_means",
            effect_value=slope if slope is not None else "",
            uncertainty_metric="exact_5factorial_stage_order_permutation_p",
            uncertainty_value=e.get("exact_order_p_two_sided", ""),
            consistency_metric="adjacent_direction_consistency",
            consistency_value=e.get("adjacent_direction_consistency", ""),
            resolution_rule="all 5 stages scorable and finite slope; P-value retained as uncertainty, not a direction filter",
        ))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bridge", type=Path, required=True)
    ap.add_argument("--joy", type=Path)
    ap.add_argument("--cr", type=Path)
    ap.add_argument("--cs", type=Path)
    ap.add_argument("--cn", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path)
    a = ap.parse_args()
    bridge = load_bridge(a.bridge)
    rows = []
    systems = []
    if a.joy:
        rows.extend(from_joy(a.joy, bridge["CJAPONICA"]))
        systems.append("CJAPONICA")
    if a.cr:
        rows.extend(from_cr(a.cr, bridge["CRETICULATA"]))
        systems.append("CRETICULATA")
    if a.cs:
        rows.extend(from_cs(a.cs, bridge["CSIN_WHITE_PINK"]))
        systems.append("CSIN_WHITE_PINK")
    if a.cn:
        rows.extend(from_cn(a.cn, bridge["CNITIDISSIMA"]))
        systems.append("CNITIDISSIMA")
    if not rows:
        raise ValueError("at least one real-data summary is required")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "measurement_id", "dependence_cluster", "transition_class", "axis", "direction", "status", "source",
        "literature_anchor_edge", "canonical_target", "direction_frame", "estimator", "effect_value",
        "uncertainty_metric", "uncertainty_value", "consistency_metric", "consistency_value", "resolution_rule",
    ]
    with a.out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    sm = {
        "status": "candidate_free_measurement_registry_built",
        "bridge": str(a.bridge),
        "systems": systems,
        "n_rows": len(rows),
        "resolved_rows": sum(r["status"] == "resolved" for r in rows),
        "direction_policy": "direction is retained whenever the prespecified design identifies it; significance thresholds never select favourable axes",
        "system_rules": {
            "CJAPONICA": "effect status ok in frozen same-cultivar 3v3 contrast",
            "CRETICULATA": "effect status ok in frozen same-cultivar same-stage white-region vs red-region 3v3 contrast",
            "CSIN_WHITE_PINK": ">=4/5 stage effects and >=0.8 same-sign consistency (pre-frozen upstream)",
            "CNITIDISSIMA": "all 5 stages scorable + finite ordered slope; exact permutation P retained as uncertainty only",
        },
    }
    sp = a.summary or a.out.with_suffix(".summary.json")
    sp.write_text(json.dumps(sm, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(sm, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
