from __future__ import annotations

import importlib.util
import io
from pathlib import Path

import numpy as np
from Bio import Phylo

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"predict_merianieae_temporal_realization_v0_1.py"
spec=importlib.util.spec_from_file_location("m",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_pair_baseline():
    s=np.array(["a","a","b","b"],object)
    assert np.isclose(mod.pair_baseline(s),2/6)


def test_ultrametric_signed_area_returns_ready():
    tree=Phylo.read(io.StringIO("((A:1,B:1):1,(C:1,D:1):1);"),"newick")
    x=mod.signed_area(tree,["A","B","C","D"],np.array(["a","a","b","b"],object))
    assert x["status"]=="MERIANIEAE_TEMPORAL_REALIZATION_PREDICTION_FROZEN_PRE_AUC"
    assert np.isfinite(x["fine_persistence_area"])
