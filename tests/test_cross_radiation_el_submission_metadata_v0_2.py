from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_cross_radiation_el_submission_metadata_v0_2.py"
META = ROOT / "submission" / "CROSS_RADIATION_EL_SUBMISSION_METADATA_V0_2.json"

spec = importlib.util.spec_from_file_location("el_metadata_v02", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError("validator module cannot be loaded")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_empty_v03_scaffold_stays_at_phase1_hold():
    x = json.loads(META.read_text())
    s = mod.validate_metadata(x)
    assert s["current_state"] == "AWAITING_PHASE1_AUTHOR_IDENTITY"
    assert s["ready_for_final_bundle"] is False
    assert s["scientific_results_changed"] is False


def test_v03_title_is_bound_to_current_candidate():
    x = json.loads(META.read_text())
    x["paper_title"] = "wrong title"
    with pytest.raises(ValueError, match="paper title drift"):
        mod.validate_metadata(x)


def test_v03_route_is_bound_to_current_candidate():
    x = json.loads(META.read_text())
    x["governance"]["submission_route"] = "Evolution Letters v0.2"
    with pytest.raises(ValueError, match="submission-route contract drift"):
        mod.validate_metadata(x)


def test_human_metadata_must_not_be_inferred():
    x = json.loads(META.read_text())
    x["governance"]["do_not_infer_missing_human_metadata"] = False
    with pytest.raises(ValueError, match="must not be inferred"):
        mod.validate_metadata(x)
