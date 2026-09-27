from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"gate_merianieae_informativeness_v0_1.py"
spec=importlib.util.spec_from_file_location("m",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_auc_perfect_ordering():
    score=np.array([4,3,2,1],float)
    y=np.array([1,1,0,0],bool)
    assert mod.auc_from_score_labels(score,y)==1.0


def test_permute_within_coarse_preserves_group_counts():
    fine=np.array(["a","a","b","c","c","d"],object)
    coarse=np.array(["X","X","X","Y","Y","Y"],object)
    rng=np.random.default_rng(1)
    p=mod.permute_within_coarse(fine,coarse,rng)
    assert sorted(p[:3].tolist())==["a","a","b"]
    assert sorted(p[3:].tolist())==["c","c","d"]
