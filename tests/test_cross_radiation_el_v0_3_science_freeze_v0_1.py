from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"validate_cross_radiation_el_v0_3_science_freeze_v0_1.py"
FREEZE=ROOT/"data"/"cross_radiation_el_v0_3_science_freeze_v0_1.json"

spec=importlib.util.spec_from_file_location("freeze_validator",SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError("freeze validator cannot be loaded")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_freeze_manifest_declares_current_candidate_and_fallback():
    x=json.loads(FREEZE.read_text())
    assert x["status"]=="EL_V0_3_SCIENCE_FROZEN"
    assert x["current_candidate"]=="Evolution Letters v0.3"
    assert x["fallback_candidate"]=="Evolution Letters v0.2"
    assert x["science_changes_require_new_candidate_version"] is True
    assert x["paper1_science_changed"] is False


def test_protected_assets_are_unique_and_nontrivial():
    x=json.loads(FREEZE.read_text())
    paths=[row["path"] for row in x["protected_assets"]]
    assert len(paths)==len(set(paths))
    assert len(paths)>=20
    assert "manuscript/CROSS_RADIATION_EVOLUTION_LETTERS_V0_3_TEMPORAL_MEMORY_CANDIDATE.md" in paths
    assert "data/cross_radiation_evolution_letters_claim_registry_v0_1.json" in paths
    assert "results/flowerclades51_relative_time_halfdepth_v0_1/result_v0_1.json" in paths


def test_current_checkout_matches_all_frozen_git_blob_shas():
    x=json.loads(FREEZE.read_text())
    summary=mod.validate_freeze(x, ROOT)
    assert summary["protected_assets"]==len(x["protected_assets"])
    assert summary["mismatches"]==[]
    assert summary["missing"]==[]
    assert summary["status"]=="EL_V0_3_SCIENCE_FREEZE_VALID"


def test_metadata_remains_mutable_without_being_science():
    x=json.loads(FREEZE.read_text())
    assert "submission/CROSS_RADIATION_EL_SUBMISSION_METADATA_V0_2.json" in x["allowed_mutable_submission_assets"]
    protected={row["path"] for row in x["protected_assets"]}
    assert "submission/CROSS_RADIATION_EL_SUBMISSION_METADATA_V0_2.json" not in protected
