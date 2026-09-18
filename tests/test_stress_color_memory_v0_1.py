from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_stress_color_memory_v0_1.py"
spec = importlib.util.spec_from_file_location("stressmemory", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_focal_baseline_matches_random_partner_probability():
    states=np.array(["white","white","white","red","red"],dtype=object)
    assert np.isclose(mod.focal_partner_baseline(states,"white"),2/4)


def test_focal_curve_is_positive_when_same_color_is_near():
    states=np.array(["white","white","red","red"],dtype=object)
    dist=np.array([
        [0.0,0.1,0.9,0.9],
        [0.1,0.0,0.9,0.9],
        [0.9,0.9,0.0,0.1],
        [0.9,0.9,0.1,0.0],
    ])
    out=mod.focal_memory_curve(dist,states,"white",n_bins=2)
    assert out["area"] > 0
    assert out["bins"][0]["excess_retention"] > out["bins"][-1]["excess_retention"]


def test_stress_minus_white_contrast_averages_available_stress_colors():
    scores={"white":0.4,"red":0.1,"purple":0.3}
    assert np.isclose(mod.stress_minus_white(scores,["pink","red","purple","yellow"]),-0.2)
