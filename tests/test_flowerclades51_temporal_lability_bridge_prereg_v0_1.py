from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "data/flowerclades51_temporal_lability_bridge_prereg_v0_1.json"


def test_temporal_lability_bridge_prereg_is_frozen_before_clade_predictor_extraction():
    x = json.loads(PREREG.read_text())
    assert x["status"] == "FROZEN_BEFORE_CLADE_LEVEL_LABILITY_VALUE_EXTRACTION"
    assert x["source_article_doi"] == "10.1002/ajb2.70146"
    assert x["source_appendix"] == "Appendix S2"
    assert x["analysis_role"] == "RETROSPECTIVE_BIOLOGICAL_MODERATOR_BRIDGE"
    assert x["primary_predictor"] == "source_stochastic_map_mean_flower_transition_count"
    assert x["primary_outcomes"] == [
        "AUC_intermediate_minus_AUC_coarse",
        "AUC_fine_minus_AUC_intermediate",
    ]
    assert x["model"] == "one_predictor_plus_intercept"
    assert x["qualification_rule"]["validation"] == "leave_one_clade_out"
    assert x["qualification_rule"]["must_improve_both_independent_contrasts"] is True
    assert x["post_hoc_predictor_switch_forbidden"] is True
    assert x["prospective_claim_allowed"] is False
    assert x["paper1_science_changed"] is False
