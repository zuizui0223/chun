#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

V032_BANNER = (
    "> Draft v0.3.2 temporal framing revision. Scientific estimates remain Paper 1 v0.2.2. This framing places repeated generation and mechanistic replay through evolutionary time at the biological centre; observation-regime and event-identification analyses remain identification tools and no estimate, contrast, figure input, or inferential gate is changed here."
)
V02_BANNER = (
    "> Draft v0.2. This manuscript is governed by `data/paper1_authoritative_results_v0_2.csv`, "
    "`data/paper1_main_figure_manifest_v0_2.csv`, and `data/paper1_reference_registry_v0_2.csv`. "
    "The v0.1 manuscript is retained as provenance and must not be patched back into the molecular framing when it conflicts with the v0.2 result hierarchy."
)
SCIENCE_REGISTRY_V022 = (
    "The current result set is frozen in `data/paper1_authoritative_results_v0_2_2.csv`; Main and Supplement figure roles are frozen in `data/paper1_main_figure_manifest_v0_2_2.csv`. This patch changes only the literature-conditioned molecular layer after citation chasing; candidate-free measurements, yellow-development results and macroevolutionary inputs are unchanged."
)
LEGACY_REGISTRY = (
    "The current result set is frozen in `data/paper1_authoritative_results_v0_2.csv`; Main and Supplement figure roles are frozen in `data/paper1_main_figure_manifest_v0_2.csv`. Superseded analyses remain in repository history but do not re-enter positive claims."
)

AJB_ABSTRACT_V09 = """## ABSTRACT

### Premise of the study

Similar flower-colour states can be generated repeatedly in independent lineages. The evolutionary question is not only whether colour changes recur, but how much of the underlying molecular transition is replayed each time. *Camellia* provides a comparative system with extensive colour diversity, contrasting pollination contexts, and molecular datasets.

### Methods

We represented mechanism on four prespecified pigment-state axes—anthocyanin (A), flavonol (F), carotenoid (C), and proanthocyanidin diversion (P)—across three anthocyanin-gain and two yellow-development dependence clusters. Literature states were treated as partially observed signatures, then five public RNA-seq systems were remeasured with one outcome-independent pathway-wide protocol. Accepted-species nuclear analyses tested wild-colour phylogenetic structure and event robustness.

### Key results

For anthocyanin gain, literature-compatible exact recurrence was 0.333–1.0, whereas standardized remeasurement fixed it at 0.333; pairwise A/F/C/P concordance narrowed from 0.333–1.0 to 0.333–0.5. For yellow development, exact recurrence narrowed from 0.5–1.0 to 0.5 and pairwise concordance from 0.25–1.0 to 0.75; A, C, and P were shared while F differed. Wild flower colours retained topology-robust local phylogenetic structure, but no accepted-species transition branch was robust to alternative colour coding.

### Conclusions

Repeated generation of similar flower colours does not replay one invariant pigment-state programme. Repeatability is modular and transition-class dependent, while generation, persistence, and event identity remain distinct evolutionary quantities."""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected exactly one block, found {n}")
    return text.replace(old, new, 1)


def abstract_word_count(text: str) -> int:
    block = text.split("## ABSTRACT", 1)[1].split("**Key words:**", 1)[0]
    body = "\n".join(line for line in block.splitlines() if not line.startswith("#"))
    return len(re.findall(r"\b[\w’'-]+\b", body))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--appendix-map", type=Path, required=True)
    ap.add_argument("--figure-manifest", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    a = ap.parse_args()

    source = a.source.read_text(encoding="utf-8")
    compat = replace_once(source, V032_BANNER, V02_BANNER, "v0.3.2 banner compatibility")
    compat = replace_once(compat, SCIENCE_REGISTRY_V022, LEGACY_REGISTRY, "v0.2.2 registry compatibility")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paper1_v09_") as td:
        td = Path(td)
        compat_path = td / "PAPER1_TEMPORAL_V032_COMPAT.md"
        base_summary = td / "v06_summary.json"
        compat_path.write_text(compat, encoding="utf-8")
        subprocess.run(
            [
                sys.executable,
                "scripts/build_paper1_submission_v0_6.py",
                "--source", str(compat_path),
                "--appendix-map", str(a.appendix_map),
                "--figure-manifest", str(a.figure_manifest),
                "--out", str(a.out),
                "--summary", str(base_summary),
            ],
            check=True,
        )
        inherited = json.loads(base_summary.read_text(encoding="utf-8"))

    out = a.out.read_text(encoding="utf-8")
    if out.count("## ABSTRACT") != 1 or out.count("**Key words:**") != 1:
        raise SystemExit("could not uniquely locate AJB abstract boundaries")
    prefix = out.split("## ABSTRACT", 1)[0].rstrip()
    suffix = out.split("**Key words:**", 1)[1]
    out = prefix + "\n\n" + AJB_ABSTRACT_V09 + "\n\n**Key words:**" + suffix

    words = abstract_word_count(out)
    if words > 250:
        raise SystemExit(f"AJB v0.9 abstract exceeds 250 words: {words}")

    required = [
        "Repeated generation of flower-colour states does not replay one pigment-state programme",
        "repeated generation with partial mechanistic replay",
        "P=0.078125",
        "0.333–1.0",
        "0.333–0.5",
        "0.25–1.0",
        "10.3389/fpls.2015.01257",
        "10.1016/j.phytochem.2022.113559",
        "10.3732/ajb.1600428",
        "The strict×dominant shared robust event count was therefore zero",
    ]
    missing = [x for x in required if x not in out]
    if missing:
        raise SystemExit(f"AJB v0.9 output missing temporal/science tokens: {missing}")

    forbidden = [
        "Draft v0.2", "Draft v0.3", "Draft v0.3.2", "`data/", "`docs/", "`scripts/",
        "A/F/C/P coverage = 9/4/1/3", "coverage was 5/3/1/2",
        "anthocyanin-axis ascertainment remained enriched after dependence collapse",
        "ecological Fig. 6",
    ]
    retained = [x for x in forbidden if x in out]
    if retained:
        raise SystemExit(f"AJB v0.9 output retains stale/internal tokens: {retained}")

    a.out.write_text(out.rstrip() + "\n", encoding="utf-8")
    summary = {
        **inherited,
        "submission_version": "v0.9",
        "source_manuscript": str(a.source),
        "source_science_version": "Paper 1 v0.2.2",
        "source_framing_version": "Paper 1 v0.3.2 temporal framing",
        "reference_contract": "paper1_reference_registry_v0_5.csv (25 DOI rows)",
        "abstract_word_count": words,
        "biological_headline": "repeated generation through evolutionary time and partial mechanistic replay",
        "scientific_results_changed_by_submission_formatting": False,
        "status": "submission-clean Paper 1 AJB v0.9 built from science v0.2.2 + temporal framing v0.3.2",
    }
    a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
