from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VERDICT=ROOT/"data/erica_2025_uct_phylogenomics_tree_source_verdict_v0_1.json"

def test_audited_filenames_match_real_hosted_inventory_not_imagined_tree():
    d=json.loads(VERDICT.read_text())
    assert d["status"]=="PASS_EXACT_SOURCE_INVENTORY_NOT_AN_ERICA_SPECIES_TREE_SOURCE"
    assert d["publication"]["figshare_article_id"]==27134208
    assert d["publication"]["data_doi"]=="10.25375/uct.27134208"
    files=d["actual_original_file_inventory"]
    assert len(files)==4
    assert set(x["name"] for x in files)=={
        "ALL_Erica303_combined_HybPiper.fasta",
        "ALL_Erica303_genomic_HybPiper.fasta",
        "ALL_Erica303_transcripts_HybPiper.fasta",
        "Readme.txt",
    }
    assert all(x["size_bytes"]>0 for x in files)
    assert all(len(x["source_md5"])==32 for x in files)
    assert not d["record_contains_newick_nexus_species_tree"]
    assert not d["match_to_2019_30_qpcr_taxon_labels_possible_from_these_files"]
    assert not d["independent_regulatory_phylogenetic_memory_rho_calculated"]
    assert not d["independent_replication_admitted"]
    assert d["original_camellia_ajb_and_el_submission_unchanged"]

def test_unrelated_phylogenomic_target_reference_has_no_tree_for_empirical_test():
    d=json.loads(VERDICT.read_text())
    assert d["source_only_result_does_not_prove_no_other_public_erica_trees_exist"]
    assert d["alternative_2025_study_might_have_separate_unverified_tree_outputs"]
    assert d["original_2016_treebase_s18291_unrecovered"]
    assert d["original_2024_supp7_unrecovered"]
    assert "target-reference" in d["actual_original_file_inventory"][0]["role"]
