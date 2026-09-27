#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

PATHS={
    "visible_batch": ROOT/"results/flowerclades51_hidden_fine_memory_v0_1/summary_v0_1.json",
    "external": ROOT/"data/cross_radiation_hierarchical_rule_v0_2.json",
    "petunieae": ROOT/"results/petunieae_hidden_memory_v0_1/summary_v0_1.json",
    "schistanthe": ROOT/"results/schistanthe_hidden_memory_v0_1/result_v0_1.json",
    "gesnerioideae": ROOT/"results/gesnerioideae_biochemical_hidden_memory_v0_1/summary_v0_1.json",
    "gesnerioideae_info": ROOT/"results/gesnerioideae_fail_informativeness_v0_1/summary_v0_1.json",
    "ng2018": ROOT/"data/ng2018_solanaceae_source_schema_hold_v0_1.json",
    "iochrominae": ROOT/"data/iochrominae_preservation_mirror_hold_v0_4.json",
    "ruellia": ROOT/"data/ruellia51_hidden_memory_prediction_v0_1.json",
}


def load(name:str)->dict:
    return json.loads(PATHS[name].read_text())


def build()->dict:
    a=load("visible_batch")
    ext=load("external")
    pet=load("petunieae")
    sch=load("schistanthe")
    ges=load("gesnerioideae")
    info=load("gesnerioideae_info")
    ng=load("ng2018")
    ioch=load("iochrominae")
    rue=load("ruellia")

    assert a["positive_effect_clades"]==18 and a["n_clades"]==21
    assert ext["hierarchical_fine_state_rule"]["supporting_external_radiations"]==3
    assert pet["status"]=="PETUNIEAE_HIERARCHICAL_HIDDEN_MEMORY_RETROSPECTIVE_RESULT"
    assert sch["status"]=="PROSPECTIVE_SCHISTANTHE_HIDDEN_MEMORY_PASS"
    assert ges["status"]=="PROSPECTIVE_GESNERIOIDEAE_BIOCHEMICAL_HIDDEN_MEMORY_FAIL"
    assert info["prospective_terminal_status_changed"] is False
    assert info["schistanthe_sized_point_effect_would_cross_gesnerioideae_null_critical_value"] is False
    assert ng["biological_decision"]=="NONE_SOURCE_SCHEMA_HOLD"
    assert ioch["biological_decision"]=="NONE_SOURCE_TRANSPORT_HOLD"
    assert rue["status"]=="FROZEN_BEFORE_RUELLIA51_HPLC_OUTCOME_OPENING"

    return {
      "version":"v0.3",
      "status":"HIERARCHICAL_EVOLUTIONARY_MEMORY_SYNTHESIS_V0_3_POST_PROSPECTIVE_BIOCHEMICAL_FAIL",
      "programme_role":"POST_V0_3_EXTENSION_SYNTHESIS_WITH_PROSPECTIVE_VISIBLE_PASS_AND_PROSPECTIVE_BIOCHEMICAL_FAIL",
      "candidate_headline":"Hierarchical evolutionary memory is recurrent but not universal across flower-colour representations.",
      "conceptual_claim":(
        "Broad phenotype classes can contain finer lineage-structured states, so evolutionary memory is often hierarchical rather than concentrated at one globally optimal resolution. "
        "That architecture recurs strongly in visible flower colour and prospectively replicates there, but it is not guaranteed to produce a significant hidden-memory signal in every biochemical representation."
      ),
      "evidence":{
        "standardized_visible_batch":{
          "source":str(PATHS["visible_batch"].relative_to(ROOT)),
          "opportunity_clades":a["n_clades"],
          "positive_clades":a["positive_effect_clades"],
          "median_centered_auc_effect":a["median_centered_auc_effect"],
          "wilcoxon_p":a["wilcoxon_effect_gt_zero_p"],
          "sign_p":a["sign_effect_gt_zero_p"],
          "role":"retrospective standardized prevalence"
        },
        "external_nonexchangeable_radiations":{
          "source":str(PATHS["external"].relative_to(ROOT)),
          "supporting_n":ext["hierarchical_fine_state_rule"]["supporting_external_radiations"],
          "testable_n":ext["hierarchical_fine_state_rule"]["testable_external_radiations"],
          "systems":ext["hierarchical_fine_state_rule"]["supporting_ids"],
          "role":"independent qualitative concordance; no pooled P value"
        },
        "petunieae_retrospective_biochemical":{
          "source":str(PATHS["petunieae"].relative_to(ROOT)),
          "eligible_tips":pet["eligible_tips"],
          "centered_auc_effect":pet["centered_auc_effect"],
          "p_one_sided":pet["p_one_sided"],
          "role":"retrospective biochemical same-estimand support"
        },
        "schistanthe_prospective_visible":{
          "source":str(PATHS["schistanthe"].relative_to(ROOT)),
          "status":sch["status"],
          "retained_tips":sch["retained_tips"],
          "centered_auc_effect":sch["centered_auc_effect"],
          "p_one_sided":sch["p_one_sided"],
          "role":"independent prospective visible-colour PASS"
        },
        "gesnerioideae_prospective_biochemical":{
          "source":str(PATHS["gesnerioideae"].relative_to(ROOT)),
          "status":ges["status"],
          "eligible_tips":ges["eligible_tips"],
          "centered_auc_effect":ges["centered_auc_effect"],
          "p_one_sided":ges["p_one_sided"],
          "role":"prospective biochemical FAIL under the frozen rule"
        },
        "gesnerioideae_fail_informativeness":{
          "source":str(PATHS["gesnerioideae_info"].relative_to(ROOT)),
          "one_sided_alpha_0_05_centered_effect_critical":info["one_sided_alpha_0_05_centered_effect_critical"],
          "schistanthe_centered_effect":info["schistanthe_prospective_centered_effect"],
          "schistanthe_sized_point_effect_crosses_critical":info["schistanthe_sized_point_effect_would_cross_gesnerioideae_null_critical_value"],
          "interpretive_role":"post-outcome diagnostic only; does not change FAIL and is not a power analysis"
        }
      },
      "prospective_nonvisible_frontier":{
        "ng2018":{
          "status":ng["status"],
          "biological_decision":ng["biological_decision"],
          "counts_as_replication":ng["consequences"]["counts_as_replication"]
        },
        "iochrominae":{
          "status":ioch["status"],
          "biological_decision":ioch["biological_decision"],
          "counts_as_prospective_replication":ioch["consequences"]["counts_as_prospective_replication"]
        },
        "ruellia":{
          "status":rue["status"],
          "outcome_opened":rue["held_out_system"]["row_level_CHUN_state_patterns_opened_at_freeze"],
          "current_blocker":rue["current_blocker"]
        }
      },
      "inference":{
        "visible_colour":"SUPPORTED_RECURRENT_HIERARCHICAL_MEMORY_WITH_INDEPENDENT_PROSPECTIVE_PASS",
        "biochemical_cross_representation":"MIXED_AND_NOT_PROSPECTIVELY_GENERALIZED",
        "universal_significant_hidden_memory_rule":"NOT_SUPPORTED_AFTER_PROSPECTIVE_GESNERIOIDEAE_FAIL",
        "universal_nonzero_biological_effect":"NOT_IDENTIFIED_BY_CURRENT_TESTS",
        "why_fail_is_not_erased":(
          "Gesnerioideae remains a prospective FAIL with a negative centered point effect and P=0.5005. "
          "The informativeness audit only shows that its 5% critical centered effect (+0.07199) exceeds the independently observed Schistanthe effect (+0.06416), limiting how strongly this 30-tip test can exclude Schistanthe-sized effects."
        )
      },
      "strongest_current_positive_statement":(
        "Fine flower-colour states repeatedly retain lineage history inside broader phenotype classes, including an independent prospective visible-colour replication; "
        "however, the first completed prospective biochemical test failed, so hierarchical memory is best treated as a recurrent and contingent evolutionary architecture rather than a universal property of every representation."
      ),
      "ecological_evolutionary_implication":(
        "Coarse ecological display classes need not erase lineage-specific evolutionary information: finer states can remain phylogenetically structured within the same broad phenotype. "
        "The amount of hidden history realized inside a coarse state varies among radiations and representations, making hierarchical state-space organization itself a biological axis of variation rather than a fixed optimal resolution."
      ),
      "novelty_ceiling":[
        "do not claim a universal hierarchical-memory law",
        "do not claim prospective biochemical validation",
        "do not relabel or rescue the Gesnerioideae prospective FAIL",
        "do not treat source/schema HOLDs as biological negatives",
        "do not pool P values across nonexchangeable evidence tiers",
        "do not infer ecological or molecular cause from phylogenetic organization alone"
      ],
      "submission_state":{
        "current_submission":"Evolution Letters v0.3",
        "current_submission_changed":False,
        "v0_8_or_v0_9_promoted":False,
        "ruellia_specific_promotion_rule_changed":False
      },
      "next_gate":(
        "Do not broaden candidate hunting. Reopen prospective biochemical generalization only if the already-frozen Ruellia authoritative tree gate clears or a currently blocked authoritative non-visible source becomes exactly recoverable under its frozen admission rule."
      ),
      "el_v0_3_science_changed":False,
      "paper1_science_changed":False
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    out=build()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
