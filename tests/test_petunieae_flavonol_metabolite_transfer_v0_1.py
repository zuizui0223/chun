from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
P=ROOT/"scripts/analyze_petunieae_flavonol_metabolite_transfer_v0_1.py"
spec=importlib.util.spec_from_file_location("petunieae_flavonol_metabolite_transfer",P)
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)

DESIGN=ROOT/"data/petunieae_flavonol_metabolite_transfer_design_v0_1.json"
ORIGINAL=ROOT/"data/petunieae_nested_regulatory_memory_preregistered_design_v0_1.json"
PREDICTOR=ROOT/"data/petunieae_nested_regulatory_leaveoneout_prediction_design_v0_1.json"


def test_original_chemistry_target_panels_distinct_same_source_three_three():
    d=json.loads(DESIGN.read_text(encoding="utf-8"))
    groups,ids=m.check_groups(d)
    assert [x["id"] for x in groups]==[
        "FLAVONOL_CONCENTRATION","ANTHOCYANIDIN_AMOUNT_POSITIVE_VARYING"]
    assert [len(x) for x in ids]==[3,3]
    assert [x["columns"] for x in groups]==[
        ["myr_mgg","quer_mgg","kaem_mgg"],
        ["Del_mgg","Pet_mgg","Malv_mgg"]
    ]
    assert d["original_cohort"]["n_tips"]==47
    assert d["original_cohort"]["n_exact_anthocyanidin_presence_classes"]==6
    assert d["null"]["seed"]==20261020 and d["null"]["iterations"]==9999
    assert d["prediction"]["no_alternative_k_search"]
    assert d["caveats"]["no_direct_UV_reflectance_pollinator_fitness_measured"]
    assert d["caveats"]["previous_Camellia_AJB_EL_science_untouched"]


def test_same_fixed_donors_and_training_only_metabolite_scale():
    from run_petunieae_nested_regulatory_leaveoneout_prediction_v0_1 import weights,loss_gain
    X=np.array([
        [.2,.3,.4,.5,.6,.7],
        [.3,.3,.5,.4,.7,.6],
        [.4,.6,.9,.8,.7,.6],
        [.6,.7,.9,.8,.5,.6],
        [1,2,3,4,5,6],
        [1,3,4,5,6,7],
        [2,3,5,6,7,8],
        [4,3,7,8,9,10]
    ])
    code=["000000"]*4+["000111"]*4
    n=8
    distance=np.abs(np.arange(n)[:,None]-np.arange(n)[None,:]).astype(float)
    name=[f"t{k:02d}" for k in range(n)]
    W0,W2=weights(distance,code,name,k=2)
    out=m.group_losses(X,W0,W2,[[0,1,2],[3,4,5]],code)
    assert len(out)==2
    full=loss_gain(X,W0,W2)
    assert np.mean([z["baseline_class_MSE"] for z in out])==pytest.approx(full["state_only_mse"])
    assert np.mean([z["nearest_two_MSE"] for z in out])==pytest.approx(full["phylogenetic_neighbor_mse"])
    for z in out:
        assert len(z["per_class"])==2
        assert z["n_compounds"]==3
        assert np.isfinite(z["relative_gain"])
        assert z["donor_rule_unmodified"]


def test_two_original_chemical_families_holm_no_gene_selection():
    assert m.holm_two([.003,.12])==pytest.approx([.006,.12])
    assert m.holm_two([.31,.015])==pytest.approx([.31,.03])
    assert m.classify(-.05,.001)=="NOT_SUPPORTED_PRACTICAL_TRANSFER"
    assert m.classify(.08,.08)=="NOT_SUPPORTED_LOCALITY_AFTER_MULTIPLICITY"
    assert m.classify(.08,.01)=="SUPPORTED_RETROSPECTIVE_METABOLITE_TRANSFER"
    with pytest.raises(ValueError):
        m.holm_two([.01])


def test_missing_source_fails_not_fabricating_P():
    d=json.loads(DESIGN.read_text(encoding="utf-8"))
    orig=json.loads(ORIGINAL.read_text(encoding="utf-8"))
    pred=json.loads(PREDICTOR.read_text(encoding="utf-8"))
    with pytest.raises((ValueError,FileNotFoundError)):
        m.analyze(ROOT/"an_unverified_2023_source",
                  d,orig,pred,iterations_override=199)
