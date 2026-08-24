#!/usr/bin/env python3
"""Fail if candidate-free real-data directions drift from canonical literature orientation."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read(path: Path):
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError(f"empty input: {path}")
    return rows


def one(rows, key, value):
    out = [r for r in rows if r[key] == value]
    if len(out) != 1:
        raise ValueError(f"expected one {key}={value}, found {len(out)}")
    return out[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bridge", type=Path, required=True)
    ap.add_argument("--edge-registry", type=Path, required=True)
    ap.add_argument("--orientation", type=Path, required=True)
    ap.add_argument("--joy-contrasts", type=Path, required=True)
    ap.add_argument("--cs-contrasts", type=Path, required=True)
    ap.add_argument("--cn-contrasts", type=Path, required=True)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()

    bridge = read(a.bridge)
    edges = {r["edge_id"]: r for r in read(a.edge_registry)}
    orient = {r["edge_id"]: r for r in read(a.orientation)}
    if set(edges) != set(orient):
        raise ValueError("orientation registry must match edge registry exactly")

    required_systems = {"CJAPONICA", "CSIN_WHITE_PINK", "CNITIDISSIMA"}
    bm = {r["system_key"]: r for r in bridge}
    if set(bm) != required_systems:
        raise ValueError(f"bridge systems must be exactly {sorted(required_systems)}; got {sorted(bm)}")

    checked = []
    for key, b in sorted(bm.items()):
        edge_id = b["literature_anchor_edge"]
        if edge_id not in edges:
            raise ValueError(f"unknown literature anchor: {edge_id}")
        e, o = edges[edge_id], orient[edge_id]
        if e["dependence_cluster"] != b["dependence_cluster"]:
            raise ValueError(f"cluster drift for {key}")
        if o["transition_class"] != b["transition_class"]:
            raise ValueError(f"transition class drift for {key}")
        if o["canonical_target"] != b["canonical_target"]:
            raise ValueError(f"canonical target drift for {key}")
        source_visible, target_visible = e["source_state_visible"], e["target_state_visible"]
        if o["orientation"].lower() == "reverse":
            source_visible, target_visible = target_visible, source_visible
        elif o["orientation"].lower() != "forward":
            raise ValueError(f"bad canonical orientation for {edge_id}: {o['orientation']}")
        if source_visible != b["source_visible"] or target_visible != b["target_visible"]:
            raise ValueError(
                f"visible-state frame drift for {key}: canonical={source_visible}->{target_visible}, "
                f"bridge={b['source_visible']}->{b['target_visible']}"
            )
        checked.append(key)

    joy = one(read(a.joy_contrasts), "contrast_id", "CF_CJ_JOY_RED_PINK")
    b = bm["CJAPONICA"]
    if (joy["dependence_cluster"], joy["source_condition"], joy["target_condition"]) != (
        b["dependence_cluster"], b["source_condition_rule"], b["target_condition_rule"]
    ):
        raise ValueError("Joy contrast is not in canonical pink-to-red frame")

    cs = read(a.cs_contrasts)
    if len(cs) != 5:
        raise ValueError(f"C. sinensis bridge expects five stage strata; found {len(cs)}")
    b = bm["CSIN_WHITE_PINK"]
    for stage in range(1, 6):
        r = one(cs, "contrast_id", f"CF_CS_S{stage}_WHITE_PINK")
        expected_source = b["source_condition_rule"].format(stage=stage)
        expected_target = b["target_condition_rule"].format(stage=stage)
        if (r["dependence_cluster"], r["source_condition"], r["target_condition"]) != (
            b["dependence_cluster"], expected_source, expected_target
        ):
            raise ValueError(f"C. sinensis S{stage} is not in canonical white-to-pink frame")

    cn = one(read(a.cn_contrasts), "contrast_id", "CF_CN_S1_S5_ENDPOINT")
    b = bm["CNITIDISSIMA"]
    if (cn["dependence_cluster"], cn["source_condition"], cn["target_condition"]) != (
        b["dependence_cluster"], b["source_condition_rule"], b["target_condition_rule"]
    ):
        raise ValueError("C. nitidissima endpoint frame is not canonical S1-to-S5")
    if b["direction_frame"] != "ordered_slope_source_to_target":
        raise ValueError("C. nitidissima primary direction must come from ordered S1-to-S5 slope")

    summary = {
        "status": "candidate_free_canonical_bridge_valid",
        "systems": checked,
        "anthocyanin_candidate_free_clusters": ["CJAPONICA", "CSIN_WHITE_PINK"],
        "yellow_candidate_free_clusters": ["CNITIDISSIMA"],
        "direction_rule": "all candidate-free directions are already expressed toward the canonical biological target",
    }
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
