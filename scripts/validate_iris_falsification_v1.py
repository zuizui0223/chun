#!/usr/bin/env python3
"""Validate the frozen prospective Iris falsification endpoint and detect drift."""
from __future__ import annotations

import json
import math
from pathlib import Path

EXPECTED = Path("analysis/iris_fine_state_falsification_result_v1.json")
GENERATED = Path("analysis/_generated/iris_falsification_v1/result.json")


def compare(expected, actual, path="result"):
    if type(expected) is not type(actual):
        raise AssertionError(f"{path}: type drift {type(expected).__name__} != {type(actual).__name__}")
    if isinstance(expected, dict):
        if set(expected) != set(actual):
            raise AssertionError(f"{path}: key drift expected={sorted(expected)} actual={sorted(actual)}")
        for key in expected:
            compare(expected[key], actual[key], f"{path}.{key}")
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            raise AssertionError(f"{path}: length drift {len(expected)} != {len(actual)}")
        for i, (x, y) in enumerate(zip(expected, actual)):
            compare(x, y, f"{path}[{i}]")
    elif isinstance(expected, float):
        if not math.isclose(expected, actual, rel_tol=1e-12, abs_tol=1e-12):
            raise AssertionError(f"{path}: numeric drift {expected} != {actual}")
    elif expected != actual:
        raise AssertionError(f"{path}: value drift {expected!r} != {actual!r}")


def semantic_checks(r):
    assert r["classification"] == "MIXED", r["classification"]
    assert r["admission_pass"] is True
    assert r["tree"]["n_tree_overlap"] == 205
    assert r["tree"]["coverage_fraction_of_226"] >= 0.80
    assert r["permutations"] == 9999 and r["seed"] == 20260908

    primary = r["primary"]
    single = r["sensitivities"]["single_coarse_only"]["result"]
    binary = r["sensitivities"]["white_nonwhite"]["result"]

    assert primary["support_gate_p_le_0_01_and_ratio_lt_1"] is True
    assert primary["p_lower"] == 0.0001
    assert primary["observed_over_null_mean"] < 1

    assert single["support_gate_p_le_0_01_and_ratio_lt_1"] is False
    assert single["p_lower"] == 0.0308
    assert single["observed_over_null_mean"] < 1

    assert binary["support_gate_p_le_0_01_and_ratio_lt_1"] is True
    assert binary["p_lower"] == 0.0001
    assert binary["observed_over_null_mean"] < 1

    # MIXED is required by the prefreeze: primary support + one supportive and
    # one failing admitted trait sensitivity is neither 4/4 replication nor refutation.
    assert primary["support_gate_p_le_0_01_and_ratio_lt_1"]
    assert binary["support_gate_p_le_0_01_and_ratio_lt_1"]
    assert not single["support_gate_p_le_0_01_and_ratio_lt_1"]


def main():
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    semantic_checks(expected)
    if GENERATED.exists():
        actual = json.loads(GENERATED.read_text(encoding="utf-8"))
        compare(expected, actual)
        semantic_checks(actual)
        print("validated frozen Iris result against regenerated endpoint: MIXED")
    else:
        print("validated frozen Iris result semantics: MIXED (no regenerated result present)")


if __name__ == "__main__":
    main()
