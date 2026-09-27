from __future__ import annotations

import importlib.util
import numpy as np
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"analyze_merianieae_pollinator_conditioned_memory_v0_1.py"
spec=importlib.util.spec_from_file_location("m",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_group_permutation_preserves_each_stratum():
    fine=np.array(["a","b","c","c","d","d"],object)
    groups=[("X","bee"),("X","bee"),("X","bird"),("X","bird"),("Y","bee"),("Y","bee")]
    p=mod.permute_within_groups(fine,groups,np.random.default_rng(2))
    assert sorted(p[:2].tolist())==["a","b"]
    assert sorted(p[2:4].tolist())==["c","c"]
    assert sorted(p[4:].tolist())==["d","d"]
