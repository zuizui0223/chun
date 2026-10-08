from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
SCRIPT=ROOT/"scripts/build_integrated_paper_figure5_v0_1.py"
spec=importlib.util.spec_from_file_location("integrated_paper_fig5",SCRIPT)
mod=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def test_frozen_mse_figure5b_does_not_reclassify_fail(tmp_path):
    data={
       "methods":["all pigment-class donors","random two","nearest two"],
       "mse":[1.138379056242746,1.4059388616620114,1.2511674468445935],
       "donor_penalty":0.267559805419265,
       "locality_gain":0.15477141481741796,
       "net_penalty":0.11278839060184742,
       "result":"NOT_SUPPORTED",
    }
    mod.fig5b(data,tmp_path/"figure5b")
    assert (tmp_path/"figure5b.png").stat().st_size>10000
    assert (tmp_path/"figure5b.svg").stat().st_size>10000
    assert data["mse"][0]<data["mse"][2]<data["mse"][1]
    assert data["donor_penalty"]-data["locality_gain"]==pytest.approx(data["net_penalty"],abs=1e-12)


def test_figure5a_is_descriptive_and_never_claims_pair_independence(tmp_path):
    rng=np.random.default_rng(20261008)
    data={
       "patristic_distance":rng.uniform(.1,1.2,size=20).tolist(),
       "expression_rms":rng.uniform(.2,1.5,size=20).tolist(),
       "rho":0.607443846759381,
       "pair_count":20,
       "tip_count":11,
       "gene_count":21,
       "fine_codes":["code"]*20,
    }
    mod.fig5a(data,tmp_path/"figure5a")
    assert (tmp_path/"figure5a.png").stat().st_size>10000
    svg=(tmp_path/"figure5a.svg").read_text()
    assert "Pairs are not independent replicates" in svg
    assert "Taxon-vector permutations supply inference" in svg


def test_figure5_sources_are_frozen_and_no_claim_promotion():
    heldout=mod.load_json(mod.HELDOUT)
    decomp=mod.load_json(mod.DECOMP)
    reg=mod.load_json(mod.REG)
    assert heldout["decision"]=="NOT_SUPPORTED"
    assert decomp["frozen_primary_decision"]=="NOT_SUPPORTED"
    assert heldout["baseline_loss"]==pytest.approx(decomp["state_only_mse"],abs=1e-10)
    assert heldout["neighbor_loss"]==pytest.approx(decomp["nearest_two_mse"],abs=1e-10)
    assert decomp["random_two_expected_mse"]>decomp["nearest_two_mse"]>decomp["state_only_mse"]
    assert reg["primary_conditional_expression_memory"]["rho"]==pytest.approx(0.607443846759381,abs=1e-10)
