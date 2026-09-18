from __future__ import annotations

import importlib.util
from io import StringIO
from pathlib import Path

import numpy as np
from Bio import Phylo

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_flowerclades51_relative_time_halfdepth_v0_1.py"
spec = importlib.util.spec_from_file_location("halfdepth", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_pair_same_baseline_is_exact_without_replacement():
    states=np.array(["A","A","B","B"],dtype=object)
    assert np.isclose(mod.pair_same_baseline(states),1/3)


def test_half_depth_is_ln2_over_lambda():
    assert np.isclose(mod.half_depth(2.0), np.log(2)/2)


def test_relative_depth_reaches_one_at_crown_split():
    tree=Phylo.read(StringIO("(A:1,B:1,(C:0.5,D:0.5):0.5);"),"newick")
    tips=tree.get_terminals()
    ii,jj=np.triu_indices(4,1)
    dist=np.array([tree.distance(tips[int(a)],tips[int(b)]) for a,b in zip(ii,jj)],float)
    d=mod.relative_divergence_depth(tree,dist)
    assert d.min()>=0
    assert d.max()<=1+1e-12
    assert np.isclose(d.max(),1.0)


def test_lambda_fit_recovers_synthetic_decay():
    rng=np.random.default_rng(4)
    q=0.25
    true_lambda=3.0
    base_d=np.linspace(0.05,1.0,25)
    d=np.repeat(base_d,800)
    p=q+(1-q)*np.exp(-true_lambda*d)
    same=rng.random(len(d))<p
    fit=mod.fit_lambda(d,same,q)
    assert 2.7 < fit["lambda"] < 3.3
    assert fit["pseudo_loglik"] > fit["null_loglik"]
