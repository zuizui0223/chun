from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location(
    "module_class_influence",
    ROOT/"scripts/audit_petunieae_module_heldout_class_influence_v0_1.py"
)
m=importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(m)

SOURCE=ROOT/"results/petunieae_module_heldout_transfer_v0_1/result_v0_1.json"
FROZEN=ROOT/"results/petunieae_module_heldout_transfer_v0_1/class_influence_v0_1.json"


def test_original_reported_within_class_source_loss_influence_is_replayed():
    source=json.loads(SOURCE.read_text(encoding="utf-8"))
    actual=m.influence(source)
    frozen=json.loads(FROZEN.read_text(encoding="utf-8"))
    assert actual.keys()==frozen.keys()
    assert actual["status"]==frozen["status"]
    assert actual["n_original_species"]==47
    assert actual["n_original_source_chemical_states"]==6
    assert actual["n_original_module_tests"]==3
    for a,b in zip(actual["module_class_influence"],frozen["module_class_influence"]):
        assert a["module_id"]==b["module_id"]
        assert a["n_positive_original_individual_classes"]==b["n_positive_original_individual_classes"]
        assert a["n_positive_one_class_omissions"]==b["n_positive_one_class_omissions"]
        assert a["min_original_group_omission_gain"]==pytest.approx(b["min_original_group_omission_gain"],abs=1e-13)
        assert a["max_original_group_omission_gain"]==pytest.approx(b["max_original_group_omission_gain"],abs=1e-13)
        assert len(a["omit_one_class_rows"])==len(b["omit_one_class_rows"])==6
        for x,y in zip(a["omit_one_class_rows"],b["omit_one_class_rows"]):
            assert x["omitted_sixbit_code"]==y["omitted_sixbit_code"]
            assert x["remaining_species"]==y["remaining_species"]
            assert x["remaining_recipients_gain"]==pytest.approx(y["remaining_recipients_gain"],abs=1e-13)


def test_flavonol_is_positive_in_all_six_omissions_but_other_modules_not():
    r=json.loads(FROZEN.read_text(encoding="utf-8"))
    by={x["module_id"]:x for x in r["module_class_influence"]}
    assert by["FLAVONOL_BRANCH_AND_ACTIVATION"]["n_positive_original_individual_classes"]==4
    assert by["FLAVONOL_BRANCH_AND_ACTIVATION"]["n_positive_one_class_omissions"]==6
    assert by["FLAVONOL_BRANCH_AND_ACTIVATION"]["min_original_group_omission_gain"]==pytest.approx(
        0.012045534579780666,abs=1e-14)
    assert by["LATE_ANTHOCYANIN_EXECUTION"]["n_positive_one_class_omissions"]==0
    assert by["EARLY_SHARED_AND_REGULATORY"]["n_positive_one_class_omissions"]==0
    assert r["no_retraining_or_reselecting_k2_donor_weights"]
    assert r["no_new_statistical_pvalues_or_unequal_gene_number_inference"]
    assert r["source_module_prediction_decisions_unchanged"]
    assert r["original_full_21_gene_prediction_still_FAIL"]


def test_changed_source_class_count_does_not_produce_sensitivity():
    d=json.loads(SOURCE.read_text(encoding="utf-8"))
    d["module_results"][0]["per_original_pigment_class"][0]["n_species"]=5
    with pytest.raises(ValueError,match="coverage changed"):
        m.influence(d)
