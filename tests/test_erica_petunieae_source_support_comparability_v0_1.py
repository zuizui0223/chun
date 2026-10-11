from __future__ import annotations
import importlib.util
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts/audit_erica_petunieae_source_support_comparability_v0_1.py"
spec=importlib.util.spec_from_file_location("comparability",SCRIPT)
module=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

PATHS=[
 "data/erica_table2_visible_colour_qpcr_taxon_crosswalk_v0_1.json",
 "results/erica_voucher_averaged_developmental_memory_v0_1/result_v0_1.json",
 "results/petunieae_nested_regulatory_memory_v0_1/result_v0_1.json",
 "results/petunieae_pigment_adjusted_regulatory_memory_v0_1/result_v0_1.json",
]

def inputs():
    return [json.loads((ROOT/x).read_text(encoding="utf-8")) for x in PATHS]

def test_original_pairs_and_visible_colour_red_dominance():
    r=module.audit(*inputs())
    e=r["erica"]
    s=e["state_support"]
    assert s["tip_counts"]=={"pink":6,"red":12,"white":2,"yellow":2}
    assert s["within_state_pairs"]=={"pink":15,"red":66,"white":1,"yellow":1}
    assert s["total_within_state_pairs"]==83
    assert s["largest_single_state_pair_share"]==pytest.approx(66/83,abs=1e-13)
    assert s["inverse_pair_share_concentration"]==pytest.approx(
        83**2/(66**2+15**2+1+1),abs=1e-13)
    assert e["same_visible_hue_pairs_within_original_comparison_group"]==6
    assert e["same_visible_hue_pairs_across_original_comparison_groups"]==77
    assert e["fraction_same_visible_hue_pairs_within_original_comparison_group"]==pytest.approx(6/83)
    assert e["retrospective_decision"]=="NOT_SUPPORTED_EXPLORATORY_TAXON_NAME_LEVEL"

def test_petunieae_is_finer_measured_pigment_class_with_different_pair_balance():
    r=module.audit(*inputs())
    p=r["petunieae"]
    counts=p["state_support"]
    assert counts["tip_counts"]=={
        "000000":6,"000010":6,"000011":6,
        "000100":10,"000110":6,"000111":13
    }
    assert counts["total_within_state_pairs"]==183
    assert counts["within_state_pairs"]["000111"]==78
    assert counts["largest_single_state_pair_share"]==pytest.approx(78/183,abs=1e-13)
    assert p["adjusted_expression_rho"]==pytest.approx(0.511199259788796)
    assert p["adjusted_expression_permutation_p"]==.0002
    assert p["original_nearest_two_prediction_still_FAIL"]

def test_no_false_meta_analysis_or_causal_claim():
    r=module.audit(*inputs())
    assert r["status"]=="EVIDENCE_ESTIMANDS_NOT_EQUIVALENT_CANNOT_TEST_EFFECT_DIFFERENCE"
    limits=r["scientific_inference"]
    assert limits["effect_sizes_not_same_parameter"]
    assert limits["statistical_power_not_directly_comparable"]
    assert limits["no_new_p_values_computed"]
    assert limits["cannot_claim_erica_biological_memory_absent"]
    assert not limits["population_level_cross_taxon_effect_difference_tested"]
    assert limits["original_camellia_AJB_and_EL_science_unchanged"]

def test_drift_of_source_taxa_fails_closed():
    d=inputs()
    d[1]["source_taxa"][0]="Erica_not_a_source_taxon"
    with pytest.raises((ValueError,KeyError)):
        module.audit(*d)
