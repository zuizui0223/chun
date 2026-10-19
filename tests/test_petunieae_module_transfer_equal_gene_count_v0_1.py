from __future__ import annotations
import importlib.util
import itertools
import json
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
SCRIPT=ROOT/"scripts/audit_petunieae_module_transfer_equal_gene_count_v0_1.py"
spec=importlib.util.spec_from_file_location("petunieae_equal_gene_transfer",SCRIPT)
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)

P=ROOT/"results/petunieae_module_heldout_transfer_v0_1/result_v0_1.json"
M=ROOT/"data/petunieae_functional_module_memory_design_v0_1.json"
O=ROOT/"data/petunieae_nested_regulatory_memory_preregistered_design_v0_1.json"
D=ROOT/"data/petunieae_nested_regulatory_leaveoneout_prediction_design_v0_1.json"


def test_gene_pool_fixed_9_4_8_and_all_four_gene_combinations_counted():
    orig=json.loads(O.read_text(encoding="utf-8"))
    modules=json.loads(M.read_text(encoding="utf-8"))
    from analyze_petunieae_functional_module_memory_v0_1 import module_partition
    mod,inds=module_partition(modules,orig)
    assert [m["id"] for m in mod]==[
        "LATE_ANTHOCYANIN_EXECUTION",
        "FLAVONOL_BRANCH_AND_ACTIVATION",
        "EARLY_SHARED_AND_REGULATORY"]
    assert [len(list(itertools.combinations(x,4))) for x in inds]==[126,1,70]
    assert [len(x) for x in inds]==[9,4,8]
    frozen=json.loads(P.read_text(encoding="utf-8"))
    assert len(frozen["module_results"])==3
    assert frozen["module_results"][1]["predictive_decision"]=="SUPPORTED_EXPLORATORY_MODULE_PREDICTION"
    assert frozen["original_full_21_gene_prediction_still_FAIL"]


def test_summary_reports_raw_overlapping_gene_panels_not_p_values():
    rows=[{"relative_gain_vs_original_class_mean":x} for x in [-.1,.2,.1,.3]]
    r=m.summarize(rows)
    assert r["n_panels"]==4
    assert r["n_positive_gain"]==3
    assert r["median_gain"]==pytest.approx(.15)
    assert r["all_shared_gene_panels_not_independent_evidence"]
    with pytest.raises(ValueError):
        m.summarize([])


def test_unverified_source_cannot_generate_predictive_gene_count_outcomes():
    objects=[json.loads(x.read_text(encoding="utf-8")) for x in [O,D,M,P]]
    with pytest.raises((ValueError,FileNotFoundError)):
        m.analyze(ROOT/"no_verified_Petunieae_source_bytes",*objects)
