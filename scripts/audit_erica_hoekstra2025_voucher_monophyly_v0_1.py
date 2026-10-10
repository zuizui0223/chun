#!/usr/bin/env python3
"""Source-only clade coherence audit for Hoekstra2025 Erica voucher prefixes.

Uses pinned exact archived .treefile bytes, not speculative taxa and does
NOT calculate colour/expression phylogenetic association or choose vouchers.
"""
from __future__ import annotations
import argparse, collections, hashlib, io, json, pathlib, zipfile
from Bio import Phylo

EXPECTED_MD5="d4363c6e604784b58c91d8a1d824a1f1"
TREE_FILE_SUFFIX=".treefile"
TREE_KINDS={"Combined":"combined","nuclear":"nuclear","plastid":"plastid"}

def match_names(tips, ref):
    species=[r for r in ref["taxa"] if r["phenotypically_fixed_sample"]]
    if len(species)!=27: raise ValueError("unexpected original fixed source panel")
    out=[]
    for r in species:
        old=r["collapsed_species_lineage"].removeprefix("Erica_")
        published=r["table2_taxon"].replace(" ","_")
        def prefix(k):
            return {tip for tip in tips if tip==k or tip.startswith(k+"_")}
        names=sorted(prefix(old)|prefix(published))
        out.append((r["qpcr_label"],r["table2_visible_colour"],names))
    return out

def inspect(original_zip:bytes,reference:dict)->dict:
    if hashlib.md5(original_zip).hexdigest()!=EXPECTED_MD5:
        raise ValueError("source ZIP MD5 mismatch")
    out={"version":"v0.1","source_archive_published_md5":EXPECTED_MD5,
         "analysis_role":"PRE_OUTCOME_SOURCE_ONLY_VOUCHER_CLADE_COHERENCE",
         "new_gene_expression_phylogenetic_statistic":False,
         "original_2016_tree_replaced":False,
         "same_specimen_qpcr_voucher_identity_proven":False,
         "admitted_independent_replication":False,
         "no_adaptation_selection_or_absolute_time_claim":True,
         "original_AJB_EL_science_unchanged":True,"trees":[]}
    with zipfile.ZipFile(io.BytesIO(original_zip)) as z:
        files=[n for n in z.namelist() if n.endswith(TREE_FILE_SUFFIX)
               and "Phylogenetic analysis results/" in n]
        if len(files)!=3:
            raise ValueError(f"expected exactly three molecular IQTREE original trees, got {len(files)}")
        for name in sorted(files):
            tree=Phylo.read(io.StringIO(z.read(name).decode("utf-8-sig")),"newick")
            tips=tree.get_terminals()
            byname={t.name:t for t in tips}
            if len(byname)!=len(tips):raise ValueError("duplicated terminal DNA sample ID")
            all_source=match_names(set(byname),reference)
            details=[]
            for source,colour,matches in all_source:
                one={"source_taxon":source,"source_colour":colour,"candidate_accession_tips":matches,
                     "n_tip_candidates":len(matches),
                     "molecular_phylogeny_source_coherence_only":True}
                if len(matches)>1:
                    ancestor=tree.common_ancestor([byname[x] for x in matches])
                    descendant={z.name for z in ancestor.get_terminals()}
                    one["candidate_tips_monophyletic_in_full_tree"]=(descendant==set(matches))
                    one["extra_unmatched_tree_tips_inside_MRCA"]=len(descendant-set(matches))
                    one["total_tree_tips_inside_MRCA"]=len(descendant)
                else:
                    one["candidate_tips_monophyletic_in_full_tree"]=None
                details.append(one)
            single=[r for r in details if r["n_tip_candidates"]==1]
            multi=[r for r in details if r["n_tip_candidates"]>1]
            monophyly=collections.Counter(str(r["candidate_tips_monophyletic_in_full_tree"]) for r in multi)
            all_found=[r for r in details if r["n_tip_candidates"]>0]
            all_counts=collections.Counter(r["source_colour"] for r in all_found)
            singles=collections.Counter(r["source_colour"] for r in single)
            out["trees"].append({
                "original_tree_file":name,
                "original_sample_terminal_count":len(tips),
                "n_source_candidate_lineages":len(all_found),
                "single_voucher_candidate_lineages":len(single),
                "multi_voucher_candidate_lineages":len(multi),
                "multi_voucher_monophyly_counts":dict(monophyly),
                "candidate_potential_pair_ceiling":sum(n*(n-1)//2 for n in all_counts.values()),
                "single_voucher_possible_pairs":sum(n*(n-1)//2 for n in singles.values()),
                "original_tree_branch_length_tips":sum(t.branch_length is not None for t in tips),
                "source_taxon_rows":details,
                "no_phenotype_expression_tree_pair_test":True
            })
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip",type=pathlib.Path,required=True)
    p.add_argument("--crosswalk",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    a=p.parse_args()
    r=inspect(a.zip.read_bytes(),json.loads(a.crosswalk.read_text(encoding="utf-8")))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    for t in r["trees"]:
        print("ERICA_MULTIVOUCHER_CLADE_SUMMARY",json.dumps({
            "tree":t["original_tree_file"].split("/")[-1],
            "source_candidate":t["n_source_candidate_lineages"],
            "single":t["single_voucher_candidate_lineages"],
            "multi":t["multi_voucher_candidate_lineages"],
            "monophyly":t["multi_voucher_monophyly_counts"],
            "ambiguous_species":[{"source":x["source_taxon"],"n_vouchers":x["n_tip_candidates"],
                                  "monophyletic":x["candidate_tips_monophyletic_in_full_tree"],
                                  "unmatched_descendants":x.get("extra_unmatched_tree_tips_inside_MRCA")}
                                 for x in t["source_taxon_rows"] if x["n_tip_candidates"]>1]
        },sort_keys=True))
    print("NO_EXPRESSION_GENE_MEMORY_P_VALUE_CALCULATED")

if __name__=="__main__":main()
