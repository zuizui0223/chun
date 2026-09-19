from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"analyze_flowerclades51_resolution_opportunity_v0_1.py"

spec=importlib.util.spec_from_file_location("opp",SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError("module load failed")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_pair_same_q_is_without_replacement_probability():
    assert np.isclose(mod.pair_same_q(["A","A","B","B"]),1/3)


def test_shannon_entropy_zero_for_single_state():
    assert np.isclose(mod.shannon_entropy(["A","A","A"]),0.0)


def test_metrics_detect_zero_and_nonzero_compression_opportunity():
    mapping={"red":"NONWHITE","pink":"NONWHITE","white":"WHITE"}
    zero=mod.compression_metrics(["red"]*5+["white"]*5,mapping)
    yes=mod.compression_metrics(["red"]*5+["pink"]*5+["white"]*5,mapping)
    assert zero["compression_opportunity"] is False
    assert zero["state_collapse_count"]==0
    assert yes["compression_opportunity"] is True
    assert yes["state_collapse_count"]==1
    assert yes["entropy_loss"]>0
    assert yes["pair_collision_gain"]>0


def test_analyze_metrics_keeps_opportunity_and_realization_separate():
    d=pd.DataFrame({
        "clade":["A","B","C","D"],
        "fine_states":[2,3,4,3],
        "coarse_states":[2,2,2,2],
        "state_collapse_fine_to_coarse":[0,1,2,1],
        "entropy_loss_fine_to_coarse":[0.0,0.2,0.8,0.4],
        "collision_gain_fine_to_coarse":[0.0,0.1,0.5,0.2],
        "amplitude":[0.1,0.2,-0.1,0.0],
        "scale_tilt":[0.0,0.02,0.08,-0.01],
    })
    out=mod.analyze_metrics(d)
    assert out["zero_opportunity"]["n_clades"]==1
    assert out["zero_opportunity"]["all_scale_tilt_zero"] is True
    assert out["opportunity"]["n_clades"]==3
    assert out["opportunity"]["positive_tilt_clades"]==2
