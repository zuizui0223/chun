from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data/flowerclades51_relative_time_persistence_prereg_v0_1.json"

def test_relative_time_persistence_contract_is_frozen_before_curve_outcomes():
    x = json.loads(P.read_text())
    assert x["status"] == "FROZEN_BEFORE_RELATIVE_TIME_PERSISTENCE_OUTCOMES"
    assert x["source_hashes"]["final_dataset.csv"] == "a253308785e4cbd0e361b3ca04cdfdae29c523eefa843375cebf8030ee0874af"
    assert x["source_hashes"]["trees.zip"] == "ae5c82945e5bf9c29bcabc52d6029acd8d4f5be1fe9141fad95918eacb4f674d"
    assert x["analysis_role"] == "RETROSPECTIVE_RELATIVE_PHYLOGENETIC_TIME_PERSISTENCE"
    assert x["tree_preflight"]["all_51_ultrametric_within_cv_threshold"] is True
    assert x["tree_preflight"]["root_to_tip_cv_threshold"] == 1e-8
    assert x["common_frame"]["reuse_existing_28_completed_clade_frames"] is True
    assert x["distance_scale"] == "pairwise_patristic_distance_divided_by_twice_clade_root_to_tip_depth"
    assert x["primary_model"]["form"] == "p_same(d)=q+(1-q)*exp(-lambda*d)"
    assert x["primary_model"]["q"] == "finite_sample_same_state_probability_from_observed_state_counts"
    assert x["primary_outputs"] == ["lambda", "half_depth_ln2_over_lambda"]
    assert x["absolute_time_claim_allowed"] is False
    assert x["primary_cross_resolution_question"] == "does relative state-persistence timescale vary among coarse_intermediate_fine representations across clades"
    assert x["paper1_science_changed"] is False
