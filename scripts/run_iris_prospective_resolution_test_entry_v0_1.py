#!/usr/bin/env python3
"""Execution shim for the frozen Iris outcome runner.

The v0.1 runner used dict.get(src, default_accession_label(src)); Python evaluates
that default expression eagerly even when src is present in the full frozen map.
This shim neutralizes only that unused fallback. The full 226-row mapping is
materialized independently from the pre-outcome species-label rule and supplied
with --crosswalk. No trait coding, statistic, permutation, threshold, or decision
rule is changed here.
"""
from __future__ import annotations

import run_iris_prospective_resolution_test_v0_1 as core


def _unused_fallback(_: str) -> str:
    return "__UNUSED_BECAUSE_FULL_FROZEN_MAP_IS_REQUIRED__"


core.default_accession_label = _unused_fallback
raise SystemExit(core.main())
