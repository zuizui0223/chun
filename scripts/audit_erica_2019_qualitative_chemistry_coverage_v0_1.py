#!/usr/bin/env python3
"""Count original 2019 Erica Table 2 chemical *descriptors*, not molecular profiles.

The source paper provides qualitative anthocyanin production calls and
supplementary UPLC-MS/MS figures, not an admitted quantitative compound-by-
species table. Preserve the negative 22-taxon expression-memory outcome.
"""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path


def audit(table2:dict, crosswalk:dict, erica:dict, pet:dict)->dict:
    if table2["source_article_doi"]!="10.3389/fpls.2019.01565":
        raise ValueError("wrong chemical source article")
    if erica["status"]!="NOT_SUPPORTED_EXPLORATORY_TAXON_NAME_LEVEL":
        raise ValueError("source result no longer frozen as NOT_SUPPORTED")
    if len(table2["rows"])!=30 or len(crosswalk["taxa"])!=30:
        raise ValueError("2019 original Table 2 frame changed")
    chemical={r["qpcr_label"]:r for r in table2["rows"]}
    colour={r["qpcr_label"]:r for r in crosswalk["taxa"]}
    if len(chemical)!=30 or set(chemical)!=set(colour):
        raise ValueError("chemical qualitative descriptors do not match 30 original qPCR source IDs")
    labels=erica["source_taxa"]
    if len(labels)!=22 or len(set(labels))!=22:
        raise ValueError("22-taxon named-source exploratory cohort changed")
    if any(not colour[k]["phenotypically_fixed_sample"] for k in labels):
        raise ValueError("unadmitted colour-morph pseudo-tip")
    assay_categories=sorted(set(r["table2_anthocyanin_production_category"] for r in table2["rows"]))
    if not assay_categories:
        raise ValueError("missing source category vocabulary")
    cohort=[{"qpcr_label":k,
             "visible_colour":colour[k]["table2_visible_colour"],
             "original_table2_group":colour[k]["table2_group"],
             "published_qualitative_anthocyanin_category":
               chemical[k]["table2_anthocyanin_production_category"],
             "original_qualitative_gene_expression_category":
               chemical[k]["table2_gene_expression_category"]}
            for k in labels]
    hues=Counter(r["visible_colour"] for r in cohort)
    products=Counter(r["published_qualitative_anthocyanin_category"] for r in cohort)
    byhue={}
    for name in sorted(hues):
        byhue[name]=dict(sorted(Counter(r["published_qualitative_anthocyanin_category"]
                                        for r in cohort if r["visible_colour"]==name).items()))
    same_visible_pairs=0
    same_visible_and_same_descriptor=0
    same_descriptor_cross_visible=0
    categories_all=Counter()
    for a,b in combinations(cohort,2):
        same_hue=a["visible_colour"]==b["visible_colour"]
        same_coarse=(a["published_qualitative_anthocyanin_category"]==
                     b["published_qualitative_anthocyanin_category"])
        if same_hue:
            same_visible_pairs+=1
            if same_coarse:same_visible_and_same_descriptor+=1
        elif same_coarse:
            same_descriptor_cross_visible+=1
            categories_all[a["published_qualitative_anthocyanin_category"]]+=1
    if same_visible_pairs!=83 or same_visible_pairs!=erica["n_source_same_visible_colour_pairs"]:
        raise ValueError("existing 2019 visible-colour frame changed")
    if products["NORMAL_ANTHOCYANIN"]!=18:
        raise ValueError("normal production category count drift")
    return {
        "version":"v0.1",
        "status":"QUALITATIVE_UPLC_TABLE2_AVAILABLE_EXACT_SIX_COMPOUND_PROFILE_NOT_ADMITTED",
        "role":"SOURCE_ONLY_CHEMICAL_DATA_AVAILABILITY_AND_VISIBLE_COLOUR_CLASS_AUDIT",
        "study_doi":table2["source_article_doi"],
        "original_qpcr_source_doi":crosswalk["measurement_source_doi"],
        "source_table":"2019 Table 2 author-reported qualitative UPLC-MS/MS interpretation",
        "numeric_raw_HPLC_compound_matrix_verified":False,
        "original_2019_reported_UPLC_supplement_format":"PDF figure, not a downloaded row-by-compound quantitative matrix",
        "source_only_N_2019_measurement_labels":30,
        "source_only_N_examined_taxa":len(cohort),
        "source_taxa":cohort,
        "source_qualitative_production_counts":dict(sorted(products.items())),
        "source_visible_colour_counts":dict(sorted(hues.items())),
        "source_qualitative_chemistry_by_visible_colour":byhue,
        "same_visible_hue_unordered_taxon_pairs":same_visible_pairs,
        "same_visible_hue_and_same_qualitative_anthocyanin_label_pairs":same_visible_and_same_descriptor,
        "different_visible_hue_but_same_qualitative_anthocyanin_label_pairs":same_descriptor_cross_visible,
        "different_hue_shared_qualitative_categories":dict(sorted(categories_all.items())),
        "normal_category_means_chemical_compounds_identical":False,
        "reported_red_pink_no_detected_qualitative_anthocyanin_difference":True,
        "published_UPLC_graph_is_not_an_exact_six_bit_pigment_profile":True,
        "no_sexual_selection_pollinator_fitness_inference":True,
        "no_new_expression_phylogenetic_memory_statistic":True,
        "original_erica_NOT_SUPPORTED_retained":True,
        "original_erica_observed_rho":erica["observed_rho"],
        "original_erica_P":erica["p_one_sided"],
        "Petunieae_exact_biochemical_condition_is_not_met":True,
        "Petunieae_pigment_adjusted_result_unchanged":pet["decision"]=="RETROSPECTIVE_SUPPORT",
        "original_Camellia_AJB_EL_unchanged":True
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-qualitative-table2",type=Path,required=True)
    p.add_argument("--original-qpcr-crosswalk",type=Path,required=True)
    p.add_argument("--erica-fixed-outcome",type=Path,required=True)
    p.add_argument("--petunieae-adjusted",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    d=audit(*(json.loads(x.read_text(encoding="utf-8")) for x in (
        a.source_qualitative_table2,a.original_qpcr_crosswalk,
        a.erica_fixed_outcome,a.petunieae_adjusted)))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("ERICA_UPLC_QUALITATIVE_SOURCE_COUNTS",json.dumps({
        "n_taxa":d["source_only_N_examined_taxa"],
        "by_chemistry":d["source_qualitative_production_counts"],
        "by_hue":d["source_qualitative_chemistry_by_visible_colour"],
        "same_visible_hue_pairs":d["same_visible_hue_unordered_taxon_pairs"],
        "same_visible_same_qualitative_pairs":
            d["same_visible_hue_and_same_qualitative_anthocyanin_label_pairs"],
        "cross_visible_shared_qualitative_pairs":
            d["different_visible_hue_but_same_qualitative_anthocyanin_label_pairs"]
    },sort_keys=True))
    print("SOURCE_AVAILABILITY_GATE",d["status"])


if __name__=="__main__":main()
