#!/usr/bin/env python3
"""Source-only 2019-published subspecies ↔ 2025-tree accession-prefix audit.

Tightens the 2019 taxon identity using *original Methods* information.
Does not select one among multiple DNA vouchers, infer tip/sample equivalence,
inspect qPCR expression vectors or perform a phylogenetic-memory test.
"""
from __future__ import annotations
import argparse
import collections
import json
from pathlib import Path

def check(source:dict, published:dict, trees:dict)->dict:
    taxa=source["taxa"]
    fixed=[x for x in taxa if x["phenotypically_fixed_sample"]]
    if len(taxa)!=30 or len(fixed)!=27:
        raise ValueError("the 2019 Table2 taxon/morph count changed")
    if len(set(x["qpcr_label"] for x in taxa))!=30:
        raise ValueError("2019 source labels duplicated")
    explicit=published["subspecies_from_published_methods"]
    if len(explicit)!=7 or len({x["qpcr_label"] for x in explicit})!=7:
        raise ValueError("seven published subspecies contract changed")
    byid={x["qpcr_label"]:x for x in fixed}
    if any(x["qpcr_label"] not in byid for x in explicit):
        raise ValueError("published subspecies not in frozen qPCR source")
    if len(trees["trees"])!=3:
        raise ValueError("three independent source-tree partitions required")
    rule={x["qpcr_label"]:x["tree_tip_prefix"] for x in explicit}
    if any(not s.endswith("_") for s in rule.values()):
        raise ValueError("nonanchored accession prefix")
    results=[]
    for tree in trees["trees"]:
        raw=tree["unique_candidate_tip_source_candidates"]+tree["ambiguous_multi_voucher_taxa"]
        if len(raw)!=22 or len({v["taxon"] for v in raw})!=22:
            raise ValueError("frozen 22 candidate source name stems changed")
        candidate={x["taxon"]:x for x in raw}
        rows=[]
        for source_row in fixed:
            taxon=source_row["qpcr_label"]
            old=candidate.get(taxon)
            if old is None:
                options=[]
            else:
                options=old.get("tip_ids",[old["tip"]] if "tip" in old else [])
            original=sorted(set(options))
            if taxon in rule:
                remaining=[tip for tip in original if tip.startswith(rule[taxon])]
                rationale="PUBLISHED_2019_SUBSPECIFIC_PREFIX"
            else:
                remaining=original
                rationale="2019_SPECIES_LEVEL_PREFIX_CANDIDATES_ONLY"
            rows.append({
                "qpcr_source_taxon":taxon,
                "visible_colour":source_row["table2_visible_colour"],
                "published_subspecies_rule":rule.get(taxon),
                "source_rule":rationale,
                "original_name_stem_tip_candidates":original,
                "remaining_tip_candidates":remaining,
                "remaining_count":len(remaining),
                "identity_classification":(
                    "NO_TREE_PREFIX_CANDIDATE" if len(remaining)==0 else
                    "UNIQUE_TREE_TIP_CANDIDATE_NOT_VOUCHER_VERIFIED" if len(remaining)==1 else
                    "MULTIPLE_2025_VOUCHERS_STILL_UNRESOLVED"
                ),
                "not_the_same_2019_flower_sample_confirmed":True
            })
        anymatch=[x for x in rows if x["remaining_count"]>=1]
        onlyone=[x for x in rows if x["remaining_count"]==1]
        multiple=[x for x in rows if x["remaining_count"]>1]
        state_all=collections.Counter(x["visible_colour"] for x in anymatch)
        state_one=collections.Counter(x["visible_colour"] for x in onlyone)
        pairs=lambda c:sum(n*(n-1)//2 for n in c.values())
        results.append({
            "tree":tree["source_tree_filename"],
            "original_tree_tips":tree["original_tree_tip_count"],
            "published_subspecies_rules_used":len(rule),
            "matched_taxon_candidates":len(anymatch),
            "matched_by_colour":dict(sorted(state_all.items())),
            "unique_candidate_taxa":len(onlyone),
            "unique_by_colour":dict(sorted(state_one.items())),
            "multiple_voucher_taxa":len(multiple),
            "ambiguous_taxa":[x["qpcr_source_taxon"] for x in multiple],
            "missing_source_taxa":[x["qpcr_source_taxon"] for x in rows if not x["remaining_count"]],
            "max_same_colour_pairs_all_candidate_taxa_not_admitted":pairs(state_all),
            "max_same_colour_pairs_one_tip_candidates_not_admitted":pairs(state_one),
            "source_taxa":rows,
            "no_expression_outcome_ever_calculated":True
        })
    if any(t["unique_candidate_taxa"]!=14 or
           t["max_same_colour_pairs_one_tip_candidates_not_admitted"]!=31
           for t in results):
        raise ValueError("source subspecies support does not reproduce the frozen target count")
    return {
        "version":"v0.1",
        "status":"HOLD_PUBLISHED_SUBSPECIES_RESOLVES_3_TIPS_BUT_14_TAXA_31_PAIRS_BELOW_SOURCE_GATE",
        "analysis_role":"RETROSPECTIVE_SOURCE_ONLY_SUBSPECIFIC_NAME_RECONCILIATION",
        "source_article_doi":published["source_study_doi"],
        "target_tree_source_doi":trees["source_archive_doi"],
        "comparison":"2019 originally printed subsp. identity vs 2025 labelled IQTREE DNA voucher candidates",
        "original_phylogenetic_source_2016_still_not_REPLACED":True,
        "prior_one_tip_candidate_taxa":11,
        "prior_one_tip_candidate_pairs":20,
        "current_one_tip_candidate_taxa":14,
        "current_one_tip_candidate_pairs":31,
        "original_design_min_taxa":20,
        "original_design_min_same_colour_pairs":40,
        "source_gate_is_not_the_gene_expression_test":True,
        "no_voucher_or_exact_sample_equivalence_proven":True,
        "no_gene_expression_phylogenetic_rho":True,
        "no_permutation_p_value":True,
        "no_independent_replication_admitted":True,
        "frozen_AJB_EL_unchanged":True,
        "trees":results
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-crosswalk",type=Path,required=True)
    p.add_argument("--published-subspecies",type=Path,required=True)
    p.add_argument("--tree-candidates",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    d=check(json.loads(a.source_crosswalk.read_text()),
            json.loads(a.published_subspecies.read_text()),
            json.loads(a.tree_candidates.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    for row in d["trees"]:
        print("ERICA_SOURCE_SUBSPECIES_ADMISSION",json.dumps({
            "tree":row["tree"],"taxa":row["unique_candidate_taxa"],
            "pair_ceiling":row["max_same_colour_pairs_one_tip_candidates_not_admitted"],
            "by_colour":row["unique_by_colour"],
            "still_multi_voucher":row["ambiguous_taxa"]
        }))
    print("NO_INDEPENDENT_EVOLUTIONARY_MEMORY_RESULT")

if __name__=="__main__":
    main()
