#!/usr/bin/env python3
"""Describe original colour/pigment state support across the two *different* estimands.

No new biological outcome, gene-level analysis, P value, taxon filtering,
hypothesis switching, or false direct Petunieae-vs-Erica effect comparison.
"""
from __future__ import annotations
import argparse
import collections
import itertools
import json
from pathlib import Path


def nchoose2(n: int)->int:
    if n<0:raise ValueError("negative count")
    return n*(n-1)//2


def pair_concentration(counts: dict[str,int])->dict:
    pairs={key:nchoose2(int(n)) for key,n in sorted(counts.items())}
    total=sum(pairs.values())
    if total==0:raise ValueError("no within-state pairs")
    share={name:float(n/total) for name,n in pairs.items()}
    squared=sum(v*v for v in share.values())
    return {"tip_counts":dict(sorted(counts.items())),
            "within_state_pairs":pairs,"total_within_state_pairs":total,
            "pair_share_by_state":share,
            "largest_single_state_pair_share":max(share.values()),
            "inverse_pair_share_concentration":1/squared,
            "inverse_concentration_is_not_independent_replication_count":True}


def audit(crosswalk:dict,erica:dict,petunieae:dict,pet_adjusted:dict)->dict:
    assert crosswalk["source_article_doi"]=="10.3389/fpls.2019.01565"
    assert erica["status"]=="NOT_SUPPORTED_EXPLORATORY_TAXON_NAME_LEVEL"
    assert erica["original_2016_Erica_primary_test_HOLD"] is True
    assert pet_adjusted["decision"]=="RETROSPECTIVE_SUPPORT"
    if erica["n_taxa"]!=22 or petunieae["retained_tips"]!=47:
        raise ValueError("original source cohort drift")
    original_by={r["qpcr_label"]:r for r in crosswalk["taxa"]}
    selected=[original_by[key] for key in erica["source_taxa"]]
    if len(selected)!=22 or len({x["qpcr_label"] for x in selected})!=22:
        raise ValueError("Erica source taxa repeated or missing")
    hue_counts=dict(sorted(collections.Counter(x["table2_visible_colour"] for x in selected).items()))
    if hue_counts!={"pink":6,"red":12,"white":2,"yellow":2}:
        raise ValueError("source hue frame changed")
    hue=pair_concentration(hue_counts)
    if hue["total_within_state_pairs"]!=83 or erica["n_source_same_visible_colour_pairs"]!=83:
        raise ValueError("Erica pair count mismatch")

    within_source_group=0
    across_source_group=0
    pair_groups=collections.Counter()
    for x,y in itertools.combinations(selected,2):
        if x["table2_visible_colour"]!=y["table2_visible_colour"]:
            continue
        if x["table2_group"]==y["table2_group"]:
            within_source_group+=1
            pair_groups[x["table2_group"]]+=1
        else:
            across_source_group+=1
    if within_source_group+across_source_group!=83:
        raise ValueError("source grouped pairs mismatch")

    pet_counts={k:int(n) for k,n in petunieae["fine_state_counts"].items()}
    p=pair_concentration(pet_counts)
    if p["total_within_state_pairs"]!=183 or p["total_within_state_pairs"]!=(
        petunieae["primary_conditional_expression_memory"]["same_fine_unordered_pairs"]):
        raise ValueError("Petunieae source pair counts drift")
    if pet_adjusted["n_pairs"]!=183 or pet_adjusted["n_tips"]!=47:
        raise ValueError("adjusted paired frame mismatch")

    return {
        "version":"v0.1","status":"EVIDENCE_ESTIMANDS_NOT_EQUIVALENT_CANNOT_TEST_EFFECT_DIFFERENCE",
        "role":"POST_OUTCOME_SOURCE_SUPPORT_AND_COMPARABILITY_AUDIT_NO_NEW_HYPOTHESIS_TEST",
        "erica":{
            "source_article_doi":crosswalk["source_article_doi"],
            "unit":"2019 named taxa / same visible red-pink-white-yellow class",
            "tree":"2025 molecular branch length averaged over candidate accessions; source qPCR flowers are not the actual DNA specimens",
            "phenotype_condition":"visible flower hue, not chemically identical anthocyanidin-presence state",
            "state_support":hue,
            "source_original_A_to_J_close_relative_groups_represented":dict(sorted(
                collections.Counter(x["table2_group"] for x in selected).items())),
            "same_visible_hue_pairs_within_original_comparison_group":within_source_group,
            "same_visible_hue_pairs_across_original_comparison_groups":across_source_group,
            "within_original_group_pair_counts":dict(sorted(pair_groups.items())),
            "fraction_same_visible_hue_pairs_within_original_comparison_group":within_source_group/83,
            "estimated_conditional_rho":erica["observed_rho"],
            "permutation_p":erica["p_one_sided"],
            "retrospective_decision":erica["status"],
            "source_original_tip_primary_still_HOLD":True
        },
        "petunieae":{
            "source_article_doi":petunieae["source_article_doi"],
            "unit":"47 species on exact same published tree and six nominal chemical-presence bit codes",
            "phenotype_condition":"exact original six-bit anthocyanidin-presence codes in the retained 47, only Del/Pet/Malv vary",
            "state_support":p,
            "adjusted_expression_rho":pet_adjusted["abundance_adjusted_rho"],
            "adjusted_expression_permutation_p":pet_adjusted["p_one_sided"],
            "adjusted_retrospective_decision":pet_adjusted["decision"],
            "original_nearest_two_prediction_still_FAIL":True
        },
        "scientific_inference":{
            "population_level_cross_taxon_effect_difference_tested":False,
            "effect_sizes_not_same_parameter":True,
            "statistical_power_not_directly_comparable":True,
            "pair_share_concentration_is_descriptive_only":True,
            "visible_red_in_erica_may_hide_biochemical_routes":True,
            "cannot_claim_plant_general_expression_memory_law":True,
            "cannot_claim_erica_biological_memory_absent":True,
            "no_new_p_values_computed":True,
            "no_gene_or_colour_posthoc_reselection":True,
            "original_camellia_AJB_and_EL_science_unchanged":True
        }
    }


def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--erica-colour-source",type=Path,required=True)
    arg.add_argument("--erica-outcome",type=Path,required=True)
    arg.add_argument("--petunieae-gene-outcome",type=Path,required=True)
    arg.add_argument("--petunieae-pigment-adjusted",type=Path,required=True)
    arg.add_argument("--out",type=Path,required=True)
    a=arg.parse_args()
    inputs=[json.loads(f.read_text(encoding="utf-8")) for f in [
        a.erica_colour_source,a.erica_outcome,
        a.petunieae_gene_outcome,a.petunieae_pigment_adjusted]]
    result=audit(*inputs)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("ERICA_PETUNIEAE_SOURCE_BALANCE",json.dumps({
        "erica":result["erica"]["state_support"],
        "erica_within_original_group":result["erica"]["same_visible_hue_pairs_within_original_comparison_group"],
        "petunieae":result["petunieae"]["state_support"]},sort_keys=True))
    print("EVIDENCE_COMPARISON_GATE",result["status"])


if __name__=="__main__":
    main()
