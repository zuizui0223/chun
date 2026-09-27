#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"data"/"hierarchical_evolutionary_memory_synthesis_v0_3.json"
STRUCT=ROOT/"results"/"hidden_memory_realization_structural_predictors_v0_1"/"summary_v0_1.json"
CRYPTIC=ROOT/"results"/"cryptic_hidden_memory_no_global_signal_v0_1"/"summary_v0_1.json"
TEMP=ROOT/"results"/"hidden_memory_vs_relative_persistence_v0_1"/"summary_v0_1.json"
INFO=ROOT/"data"/"future_hidden_memory_informativeness_gate_v0_1.json"


def load(p:Path)->dict:
    return json.loads(p.read_text())


def build()->dict:
    base=load(BASE)
    struct=load(STRUCT)
    cryptic=load(CRYPTIC)
    temp=load(TEMP)
    info=load(INFO)

    visible=base["evidence"]["standardized_visible_batch"]
    sch=base["evidence"]["schistanthe_prospective_visible"]
    pet=base["evidence"]["petunieae_retrospective_biochemical"]
    ges=base["evidence"]["gesnerioideae_prospective_biochemical"]

    assert base["status"]=="HIERARCHICAL_EVOLUTIONARY_MEMORY_SYNTHESIS_V0_3_POST_PROSPECTIVE_BIOCHEMICAL_FAIL"
    assert visible["opportunity_clades"]==21 and visible["positive_clades"]==18
    assert sch["status"]=="PROSPECTIVE_SCHISTANTHE_HIDDEN_MEMORY_PASS"
    assert ges["status"]=="PROSPECTIVE_GESNERIOIDEAE_BIOCHEMICAL_HIDDEN_MEMORY_FAIL"
    assert struct["primary"]["supported"] is False
    assert struct["primary"]["rho"] < 0
    assert struct["primary"]["leave_one_clade_out"]["negative_count"]==21
    assert cryptic["decision"]=="PRIMARY_EXACT_SIGN_TEST_NOT_SUPPORTED"
    assert cryptic["globally_no_signal"]["positive"]==8
    assert cryptic["globally_no_signal"]["n"]==10
    assert temp["primary"]["supported"] is False
    assert temp["primary"]["rho"] > 0
    assert temp["primary"]["leave_one_clade_out"]["positive_count"]==21
    assert info["status"]=="FROZEN_FOR_FUTURE_NOT_YET_SELECTED_HIDDEN_MEMORY_SYSTEMS"

    return {
      "version":"v0.4",
      "status":"HIERARCHICAL_EVOLUTIONARY_MEMORY_SYNTHESIS_V0_4_REALIZATION_ARCHITECTURE",
      "programme_role":"POST_V0_3_EXTENSION_SYNTHESIS_OF_HIDDEN_MEMORY_REALIZATION",
      "candidate_headline":"Hidden flower-colour history is a distinct evolutionary coordinate, not a by-product of phenotype compression.",
      "foundation":{
        "visible_standardized":{
          "opportunity_clades":visible["opportunity_clades"],
          "positive_clades":visible["positive_clades"],
          "median_centered_auc_effect":visible["median_centered_auc_effect"],
          "wilcoxon_p":visible["wilcoxon_p"],
          "sign_p":visible["sign_p"]
        },
        "prospective_visible":{
          "system":"Schistanthe",
          "status":sch["status"],
          "centered_auc_effect":sch["centered_auc_effect"],
          "p_one_sided":sch["p_one_sided"],
          "retained_tips":sch["retained_tips"]
        },
        "biochemical":{
          "petunieae_role":"retrospective same-estimand support",
          "petunieae_centered_effect":pet["centered_auc_effect"],
          "petunieae_p":pet["p_one_sided"],
          "gesnerioideae_status":ges["status"],
          "gesnerioideae_centered_effect":ges["centered_auc_effect"],
          "gesnerioideae_p":ges["p_one_sided"],
          "generalization":"MIXED_NOT_PROSPECTIVELY_GENERALIZED"
        }
      },
      "core_architecture":{
        "opportunity":"Does the fine phenotype contain distinctions that are genuinely collapsed by the coarse representation?",
        "global_signal":"Does phenotype identity show detectable unconditional phylogenetic organization across the whole radiation?",
        "temporal_persistence":"How much exact fine-state similarity remains above its frequency baseline across relative evolutionary divergence?",
        "hidden_realization":"After coarse membership is held fixed, do finer states retain additional lineage organization?",
        "informativeness":"Can the frozen design resolve a benchmark-sized hidden-memory effect? This is a design property, not a biological axis."
      },
      "realization_tests":{
        "trivial_compression_explanation":{
          "source":"results/hidden_memory_realization_structural_predictors_v0_1/summary_v0_1.json",
          "frozen_prediction":"more fine-to-coarse pair-collision gain -> stronger hidden memory",
          "rho":struct["primary"]["rho"],
          "permutation_p_two_sided":struct["primary"]["permutation_p_two_sided"],
          "leave_one_clade_out_negative":struct["primary"]["leave_one_clade_out"]["negative_count"],
          "n_clades":struct["n_clades"],
          "decision":"NOT_SUPPORTED",
          "interpretation":"The amount of pairwise collision created by coarse coding does not explain hidden-memory strength; all leave-one-clade-out correlations point opposite to the frozen positive prediction."
        },
        "cryptic_memory_inside_global_no_signal":{
          "source":"results/cryptic_hidden_memory_no_global_signal_v0_1/summary_v0_1.json",
          "no_signal_clades":cryptic["globally_no_signal"]["n"],
          "positive_hidden_effects":cryptic["globally_no_signal"]["positive"],
          "median_centered_auc_effect":cryptic["globally_no_signal"]["median_centered_auc_effect"],
          "sign_test_p_one_sided":cryptic["globally_no_signal"]["sign_test_p_one_sided"],
          "decision":"PRIMARY_NOT_SUPPORTED",
          "interpretation":"Eight of ten globally no-signal clades retain positive hidden effects, but the frozen exact sign test narrowly misses 0.05. Global no-signal therefore does not descriptively imply absence of nested history, but the subgroup claim is not inferentially promoted."
        },
        "relative_fine_persistence_relation":{
          "source":"results/hidden_memory_vs_relative_persistence_v0_1/summary_v0_1.json",
          "rho":temp["primary"]["rho"],
          "permutation_p_two_sided":temp["primary"]["permutation_p_two_sided"],
          "leave_one_clade_out_positive":temp["primary"]["leave_one_clade_out"]["positive_count"],
          "bootstrap_q025":temp["primary"]["bootstrap"]["q025"],
          "bootstrap_q975":temp["primary"]["bootstrap"]["q975"],
          "fine_minus_coarse_area_rho":temp["secondary_descriptive"]["fine_area_minus_coarse_area"]["rho"],
          "fine_minus_coarse_area_p":temp["secondary_descriptive"]["fine_area_minus_coarse_area"]["p_two_sided_asymptotic"],
          "decision":"PRIMARY_NOT_SUPPORTED",
          "interpretation":"Overall fine-colour persistence shows a stable positive point association with hidden memory but misses the frozen permutation threshold. Hidden memory is especially not reducible to a global fine-over-coarse persistence advantage."
        }
      },
      "updated_inference":[
        "The recurrent within-coarse signal is not explained by the trivial combinatorial amount of fine-state collision introduced by coarse coding.",
        "Unconditional global signal and hidden within-coarse organization can disagree at the clade level; 8/10 globally no-signal opportunity clades have positive hidden effects, although the frozen subgroup sign test narrowly misses 0.05.",
        "Overall fine-state temporal persistence may covary with hidden-memory realization, but the frozen 21-clade test remains formally unsupported at P=0.06147.",
        "The fine-minus-coarse persistence advantage is almost unrelated to hidden-memory strength, reinforcing that global resolution winner and nested organization are different coordinates.",
        "The remaining among-radiation variation in hidden-memory realization is therefore biological structure to explain, not a representation-geometry artifact already accounted for by the current metrics."
      ],
      "strongest_current_positive_statement":"Fine flower-colour states repeatedly retain lineage history inside broader phenotype classes, including an independent prospective visible-colour replication. That hidden organization is not a trivial consequence of coarse coding and is not equivalent to a global fine-resolution advantage. Its strength varies among radiations as a distinct evolutionary coordinate; a temporal-persistence link is directionally consistent but not yet confirmed.",
      "biological_interpretation":"A coarse floral phenotype can function as an ecological or display category while containing finer lineage-specific histories. How strongly those histories remain organized is not fixed by the amount of state compression itself. This makes the realization of nested phenotypic history a property of radiation-specific evolutionary trajectories, potentially shaped by transition dynamics, lineage constraints or ecology, none of which is yet causally identified.",
      "current_unresolved_mechanism":{
        "abiotic_heterogeneity":"SOURCE_HOLD",
        "published_transition_lability":"SOURCE_HOLD",
        "prospective_biochemical_generalization":"MIXED_WITH_RUELLIA_STILL_OUTCOME_UNOPENED",
        "causal_mechanism_identified":False
      },
      "future_test_rule":{
        "do_not_fit_more_retrospective_predictor_variants":True,
        "new_systems_use_informativeness_gate":"data/future_hidden_memory_informativeness_gate_v0_1.json",
        "next_clean_test":"Freeze one biologically external realization predictor before a genuinely new eligible radiation's hidden-memory outcome is opened.",
        "specific_temporal_prediction":"In a future independent system, stronger absolute fine-state persistence should predict stronger hidden within-coarse memory; freeze this before the hidden-memory outcome is opened.",
        "ruellia_note":"Do not retrofit the new realization predictor onto the already-frozen Ruellia outcome gate."
      },
      "claim_boundary":[
        "do not claim cryptic memory is inferentially established in the globally no-signal subgroup",
        "do not promote the P=0.06147 persistence relation as supported",
        "do not use bootstrap or Wilcoxon secondary results to rescue frozen primary failures",
        "do not claim hidden memory is independent evidence from analyses that reuse the same source trees and states",
        "do not infer a causal ecological or molecular mechanism",
        "do not modify frozen Evolution Letters v0.3"
      ],
      "submission_state":{
        "current_submission":"Evolution Letters v0.3",
        "current_submission_changed":False,
        "hierarchical_extension_promoted":False,
        "ruellia_specific_promotion_rule_changed":False
      },
      "paper1_science_changed":False,
      "el_v0_3_science_changed":False
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
