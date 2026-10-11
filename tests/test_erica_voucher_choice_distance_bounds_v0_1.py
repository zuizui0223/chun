from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"scripts/audit_erica_voucher_choice_phylogenetic_distance_bounds_v0_1.py"
spec=importlib.util.spec_from_file_location("erica_voucher_distance",P)
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)
SOURCE=ROOT/"results/erica_2019_subspecies_to_2025_voucher_prefix_gate_v0_1.json"
DESIGN=ROOT/"data/erica_predeclared_visible_colour_developmental_gene_memory_design_v0_1.json"


def test_developmental_gene_expression_not_opened_at_source_admission():
    r=json.loads(SOURCE.read_text(encoding="utf-8"))
    design=json.loads(DESIGN.read_text(encoding="utf-8"))
    assert r["current_one_tip_candidate_taxa"]==14
    assert r["current_one_tip_candidate_pairs"]==31
    assert design["frame"]["eligible_joined_tips_at_least"]==20
    assert design["frame"]["eligible_within_visible_color_pairs_at_least"]==40
    assert not r["no_voucher_or_exact_sample_equivalence_proven"] is False
    assert r["no_gene_expression_phylogenetic_rho"]
    assert r["no_permutation_p_value"]
    assert r["no_independent_replication_admitted"]
    for x in r["trees"]:
        assert x["unique_candidate_taxa"]==14 and x["multiple_voucher_taxa"]==8
        assert x["max_same_colour_pairs_all_candidate_taxa_not_admitted"]==83


def test_archive_identity_failure_does_not_open_a_phylogenetic_outcome():
    support=json.loads(SOURCE.read_text(encoding="utf-8"))
    with pytest.raises(ValueError,match="checksum"):
        m.source_only_distance_envelope(b"not a valid original molecular archive",support)


def test_each_source_taxon_has_only_one_visibility_class():
    source=json.loads(SOURCE.read_text(encoding="utf-8"))
    for t in source["trees"]:
        rows=t["source_taxa"]
        assert len(rows)==27 and len({r["qpcr_source_taxon"] for r in rows})==27
        assert set(r["visible_colour"] for r in rows)=={"red","pink","white","yellow"}
        assert all(r["not_the_same_2019_flower_sample_confirmed"] for r in rows)
