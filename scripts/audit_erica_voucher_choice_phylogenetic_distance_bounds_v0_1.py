#!/usr/bin/env python3
"""Source-only voucher-choice sensitivity of patristic distances in Erica.

All tips in the original published molecular trees are used as candidates.
Do not choose a favourable accession, compute qPCR expression differences,
or compare to any expression outcome. Distance ranges are not evolutionary
time and are not posterior credible intervals.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import itertools
import json
import math
from pathlib import Path
import zipfile

from statistics import mean
from Bio import Phylo

MD5="d4363c6e604784b58c91d8a1d824a1f1"


def source_only_distance_envelope(zip_bytes: bytes, support: dict) -> dict:
    if hashlib.md5(zip_bytes).hexdigest()!=MD5:
        raise ValueError("original published ZIP checksum mismatch")
    if len(support["trees"])!=3 or support["current_one_tip_candidate_taxa"]!=14:
        raise ValueError("2019 source subspecies admission changed")
    output={
        "version":"v0.1",
        "status":"SOURCE_ONLY_DISTANCE_UNCERTAINTY_NO_EXPRESSION_ANCESTRY_TEST",
        "source_archive_original_md5":MD5,
        "source_contract":"published 2019 subspecies and unchanged 2025 IQ-TREE accession lists",
        "source_original_tree2016_not_replaced":True,
        "biological_unit":"distinct source taxon, not gene/stage/accession pair",
        "not_a_posterior_credible_interval":True,
        "not_absolute_time":True,
        "no_favourable_voucher_selected":True,
        "qPCR_expression_matrix_not_opened":True,
        "new_regulatory_memory_rho":None,
        "new_p_value":None,
        "independent_regulatory_memory_replication":False,
        "original_AJB_EL_unchanged":True,
        "trees":[]
    }
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        candidates=[n for n in z.namelist() if n.endswith(".treefile")
                    and "Phylogenetic analysis results/" in n]
        if len(candidates)!=3:raise ValueError("three original branch-length trees not present")
        paths={Path(n).name:n for n in candidates}
        for record in support["trees"]:
            name=record["tree"]
            if name not in paths:raise ValueError("tree source filename not found")
            tree=Phylo.read(io.StringIO(z.read(paths[name]).decode("utf-8-sig")),"newick")
            tips={t.name:t for t in tree.get_terminals()}
            if len(tips)!=len(tree.get_terminals()):
                raise ValueError("duplicate source tip ID")
            if len(tips)!=record["original_tree_tips"]:
                raise ValueError("original published terminal count drift")
            source_rows=[r for r in record["source_taxa"] if r["remaining_count"]>0]
            if len(source_rows)!=22:raise ValueError("source taxon candidate support drift")
            for row in source_rows:
                if not row["remaining_tip_candidates"] or len(row["remaining_tip_candidates"])!=row["remaining_count"]:
                    raise ValueError("taxon candidate set mismatch")
                if any(t not in tips for t in row["remaining_tip_candidates"]):
                    raise ValueError("admitted candidate ID not in source tree")
            per_colour={}
            for colour in sorted(set(r["visible_colour"] for r in source_rows)):
                per_colour[colour]=sorted(
                    (r for r in source_rows if r["visible_colour"]==colour),
                    key=lambda r:r["qpcr_source_taxon"])
            pair_rows=[]
            for colour,sr in per_colour.items():
                for left,right in itertools.combinations(sr,2):
                    d=[]
                    for a,b in itertools.product(left["remaining_tip_candidates"],
                                                right["remaining_tip_candidates"]):
                        dist=float(tree.distance(tips[a],tips[b]))
                        if not math.isfinite(dist) or dist<=0:
                            raise ValueError("nonpositive or missing original patristic distance")
                        d.append(dist)
                    pair_rows.append({
                        "source_colour":colour,
                        "left_taxon":left["qpcr_source_taxon"],
                        "right_taxon":right["qpcr_source_taxon"],
                        "candidate_voucher_pair_count":len(d),
                        "tip_distance_min":min(d),
                        "tip_distance_mean":float(mean(d)),
                        "tip_distance_max":max(d),
                        "relative_range_over_mean":(max(d)-min(d))/float(mean(d)),
                        "accession_choice_distance_variable":max(d)-min(d)>1e-12
                    })
            if len(pair_rows)!=83:raise ValueError("original 83 source candidate pairs changed")
            anyvar=sum(r["accession_choice_distance_variable"] for r in pair_rows)
            confident_rank=0
            for a,b in itertools.combinations(pair_rows,2):
                if a["tip_distance_max"]<b["tip_distance_min"]-1e-12 or b["tip_distance_max"]<a["tip_distance_min"]-1e-12:
                    confident_rank+=1
            rank_total=len(pair_rows)*(len(pair_rows)-1)//2
            clades=[]
            for r in source_rows:
                if r["remaining_count"]<2:continue
                ancestor=tree.common_ancestor([tips[k] for k in r["remaining_tip_candidates"]])
                desc={leaf.name for leaf in ancestor.get_terminals()}
                matched=set(r["remaining_tip_candidates"])
                clades.append({
                    "source_taxon":r["qpcr_source_taxon"],
                    "candidate_vouchers":r["remaining_count"],
                    "only_candidate_vouchers_descend_from_mrca":desc==matched,
                    "other_source_tips_inside_mrca":len(desc-matched)
                })
            output["trees"].append({
                "tree":name,
                "source_sample_tips":len(tips),
                "source_taxon_candidate_count":len(source_rows),
                "within_visible_colour_candidate_taxon_pairs":len(pair_rows),
                "source_only_fixed_pair_count":sum(r["candidate_voucher_pair_count"]==1 for r in pair_rows),
                "pair_distances_sensitive_to_accession_choice":anyvar,
                "rank_interval_total_comparisons":rank_total,
                "rank_interval_nonoverlapping_comparisons":confident_rank,
                "rank_interval_nonoverlap_fraction":confident_rank/rank_total,
                "mean_relative_distance_range":float(mean([r["relative_range_over_mean"] for r in pair_rows])),
                "max_relative_distance_range":max(r["relative_range_over_mean"] for r in pair_rows),
                "subspecies_constrained_multivoucher_monophyly":clades,
                "all_pair_distance_envelopes":pair_rows,
                "no_expression_association_test":True
            })
    return output


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-zip",type=Path,required=True)
    p.add_argument("--subspecies-result",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report=source_only_distance_envelope(a.source_zip.read_bytes(),
                                         json.loads(a.subspecies_result.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    for t in report["trees"]:
        print("ERICA_VOUCHER_CHOICE_SOURCE_DISTANCE_UNCERTAINTY",json.dumps({
            "tree":t["tree"],"candidate_pairs":t["within_visible_colour_candidate_taxon_pairs"],
            "unique_voucher_pairs":t["source_only_fixed_pair_count"],
            "accession_sensitive_pairs":t["pair_distances_sensitive_to_accession_choice"],
            "unambiguously_ranked_pair_comparisons":t["rank_interval_nonoverlapping_comparisons"],
            "pair_comparisons_total":t["rank_interval_total_comparisons"],
            "rank_fraction":t["rank_interval_nonoverlap_fraction"],
            "multi_voucher_monophyletic":sum(x["only_candidate_vouchers_descend_from_mrca"]
                 for x in t["subspecies_constrained_multivoucher_monophyly"]),
            "multi_voucher_groups":len(t["subspecies_constrained_multivoucher_monophyly"])
        },sort_keys=True))
    print("NO_EXPRESSION_VALUES_OR_INDEPENDENT_MEMORY_TEST")

if __name__=="__main__":
    main()
