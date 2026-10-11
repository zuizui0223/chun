from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"scripts/analyze_erica_voucher_averaged_developmental_memory_v0_1.py"
spec=importlib.util.spec_from_file_location("erica_species_mean",PATH)
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)
DESIGN=ROOT/"data/erica_voucher_averaged_developmental_memory_design_v0_1.json"
SOURCE=ROOT/"results/erica_2019_subspecies_to_2025_voucher_prefix_gate_v0_1.json"


def test_genuinely_distinct_source_level_estimator_and_null_contract():
    d=json.loads(DESIGN.read_text())
    assert d["status"]=="RETROSPECTIVE_NEW_SPECIES_LEVEL_ESTIMAND_DESIGN_COMMITTED_BEFORE_ITS_NUMERIC_OUTCOME"
    assert d["source"]["reference_source_already_public_and_outcome_exposed"]
    assert d["support"]["source_taxa"]==22
    assert d["support"]["unordered_within_colour_taxon_pairs"]==83
    assert d["support"]["fixed_features"]==21
    assert d["operational_distance"]["one_tree_tip_per_species_not_selected"]
    assert d["operational_distance"]["ambiguous_species_nonmonophyly_acknowledged"]
    assert d["main_test"]["seed"]==20261011
    assert d["main_test"]["n_permutations"]==9999
    assert d["governance"]["original_Erica_2026_primary_HOLD"]
    assert d["governance"]["no_new_same_tip_exact_pigment_memory_replication"]


def test_frozen_taxon_order_and_pair_count_not_derived_from_expression():
    support=json.loads(SOURCE.read_text())
    design=json.loads(DESIGN.read_text())
    rows=m.frozen_taxon_frame(support,design)
    assert len(rows)==22
    assert [r["qpcr_source_taxon"] for r in rows]==sorted(r["qpcr_source_taxon"] for r in rows)
    colours=[r["visible_colour"] for r in rows]
    a,b=m.same_hue_pairs(colours)
    assert len(a)==len(b)==83
    assert all(colours[i]==colours[j] and i<j for i,j in zip(a,b))


def test_permutation_statistic_uses_taxa_not_83_independent_pairs():
    d=np.array([[0.,1.,4.,5.],[1.,0.,3.,4.],[4.,3.,0.,1.],[5.,4.,1.,0.]])
    x=np.array([[0.,0.],[0.5,.5],[3.,2.],[3.5,2.5]])
    ii,jj=m.same_hue_pairs(["red","red","pink","pink"])
    assert list(ii)==[0,2] and list(jj)==[1,3]
    # Two within-colour pair distances are not enough for a nonconstant Spearman
    # predictor (both tree distances are 1), so the fail-closed result must apply.
    with pytest.raises(ValueError,match="uninformative"):
        m.rank_corr(d,x,ii,jj)


def test_exact_tree_checksum_and_frozen_gene_matrix_before_outcomes():
    source=json.loads(SOURCE.read_text())
    with pytest.raises(ValueError,match="MD5"):
        m.source_tip_mean_distances(b"not the published real molecular ZIP",
                                   source,[r["qpcr_source_taxon"] for r in m.frozen_taxon_frame(
                                       source,json.loads(DESIGN.read_text()))])
