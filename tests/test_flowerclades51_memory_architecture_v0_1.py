from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"analyze_flowerclades51_memory_architecture_v0_1.py"

spec=importlib.util.spec_from_file_location("memarch",SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError("module load failed")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_memory_coordinates_match_definitions():
    c,i,f=0.55,0.60,0.65
    x=mod.memory_coordinates(c,i,f)
    assert np.isclose(x["amplitude"],0.10)
    assert np.isclose(x["scale_tilt"],0.10)
    assert np.isclose(x["intermediate_curvature"],0.00)


def test_orthogonal_axes_preserve_centered_sum_of_squares():
    x=np.array([
        [0.51,0.52,0.53],
        [0.60,0.57,0.54],
        [0.48,0.50,0.55],
        [0.66,0.66,0.66],
    ])
    z=mod.orthogonal_coordinates(x)
    left=((x-x.mean(axis=0))**2).sum()
    right=((z-z.mean(axis=0))**2).sum()
    assert np.isclose(left,right)


def test_architecture_analysis_uses_completed_clades_only():
    d=pd.DataFrame({
        "clade":["A","B","C"],
        "terminal_class":["PROFILE_SIGNALLED_FINE","HOLD_INSUFFICIENT_COMMON_FRAME_OR_STATE_VARIATION","PROFILE_NO_PHYLOGENETIC_SIGNAL"],
        "AUC_coarse":[0.51,np.nan,0.60],
        "AUC_intermediate":[0.52,np.nan,0.61],
        "AUC_fine":[0.53,np.nan,0.62],
    })
    out=mod.profile_architecture(d,bootstrap_replicates=20,seed=1)
    assert out["n_clades"]==2
    assert set(out["clades"])=={"A","C"}
    assert np.isclose(sum(out["variance_share"].values()),1.0)


def test_temporal_bridge_joins_by_clade_not_row_order():
    profiles=pd.DataFrame({
        "clade":["A","B","C"],
        "terminal_class":["PROFILE_NO_PHYLOGENETIC_SIGNAL"]*3,
        "AUC_coarse":[0.50,0.55,0.60],
        "AUC_intermediate":[0.51,0.56,0.61],
        "AUC_fine":[0.52,0.57,0.62],
    })
    persistence=pd.DataFrame({
        "clade":["C","A","B"],
        "slope":[-0.9,-0.1,-0.5],
        "area":[0.9,0.1,0.5],
    })
    out=mod.temporal_bridge(profiles,persistence)
    assert out["n_clades"]==3
    assert out["amplitude_vs_slope"]["rho"] < 0
    assert out["amplitude_vs_area"]["rho"] > 0
