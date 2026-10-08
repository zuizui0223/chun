#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

MARKER = "<!-- v1.0-compatibility-only: repeated generation with partial mechanistic replay -->"
TITLE_034 = "# Hierarchical molecular repeatability coexists with local flower-colour conservatism in *Camellia*"
TITLE_033 = "# Standardized remeasurement reveals partial mechanistic replay during repeated flower-colour evolution in *Camellia*"
RUNNING_034 = "**Running head:** Hierarchical flower-colour repeatability"
RUNNING_033 = "**Running head:** Mechanistic replay in flower-colour evolution"

AJB_ABSTRACT_V10_034 = """## ABSTRACT

### Premise of the study

Similar flower-colour states can arise through multiple molecular routes, but studies often observe different pathway subsets. We asked how repeatable pigment-network state changes are when the same public systems are remeasured under one observation rule, and whether wild-colour patterns and individual historical events show the same robustness.

### Methods

We represented mechanism on four prespecified axes—anthocyanin (A), flavonol (F), carotenoid (C), and proanthocyanidin diversion (P). Literature evidence for three anthocyanin-gain and two yellow-development dependence clusters was treated as partially observed A/F/C/P signatures. The same five public RNA-seq systems were remeasured using annotation-driven, outcome-independent quantification within these prespecified modules (candidate-free). These molecular contrasts measure colour-state-generating transcript changes, not direct macroevolutionary branch events. Separately, accepted-species analyses varied nuclear topology and wild-colour coding.

### Key results

For anthocyanin gain, literature-compatible exact recurrence was 0.333–1.0, whereas standardized remeasurement fixed it at 0.333; pairwise concordance narrowed from 0.333–1.0 to 0.333–0.5. For yellow development, exact recurrence narrowed from 0.5–1.0 to 0.5 and pairwise concordance from 0.25–1.0 to 0.75; A, C, and P were shared while F differed. Wild colours retained topology-robust local phylogenetic structure, but no accepted-species transition branch was robust to alternative colour coding.

### Conclusions

Repeatability is hierarchical rather than all-or-none. Standardized molecular contrasts show transition-class-dependent modular reuse without one invariant A/F/C/P programme, while a robust macroevolutionary colour pattern can persist without robust identification of individual historical events."""


SIMPSON_CLARIFICATIONS = [
    {
        "label": "abstract anthocyanin index floor",
        "old": "For anthocyanin gain, literature-compatible exact recurrence was 0.333–1.0, whereas standardized remeasurement fixed it at 0.333",
        "new": "For anthocyanin gain, the complete-signature index narrowed from 0.333–1.0 to its 0.333 floor"
    },
    {
        "label": "abstract yellow index floor",
        "old": "For yellow development, exact recurrence narrowed from 0.5–1.0 to 0.5",
        "new": "For yellow development, the index narrowed from 0.5–1.0 to its 0.5 floor"
    },
    {
        "label": "methods index definition",
        "old": "Two summary statistics were retained: exact-signature recurrence, which asks how many independent clusters share one complete four-axis signature, and pairwise axis concordance, the fraction of A/F/C/P directions matching across cluster pairs.",
        "new": "Two summary statistics were retained: exact-signature Simpson concentration (R = sum_s(c_s/n)^2, with c_s counting the dependence clusters with a given complete A/F/C/P signature), and pairwise axis concordance (the mean fraction of matching A/F/C/P directions across distinct-cluster pairs). Simpson concentration includes self-matches: its minimum is 1/n when no two distinct clusters share a complete signature, and the fraction of distinct-cluster pairs with identical complete signatures is (nR - 1)/(n - 1)."
    },
    {
        "label": "results anthocyanin index floor",
        "old": "Candidate-free remeasurement reduced exact-signature recurrence to **0.333 exactly** and pairwise concordance to **0.333–0.5**.",
        "new": "Candidate-free remeasurement reduced exact-signature Simpson concentration to **0.333 exactly**, its three-cluster floor (zero matching complete signatures between distinct clusters), and pairwise concordance to **0.333–0.5**."
    },
    {
        "label": "results yellow index floor",
        "old": "Candidate-free measurement point-identified exact-signature recurrence at **0.5** and pairwise concordance at **0.75**.",
        "new": "Candidate-free measurement point-identified exact-signature Simpson concentration at **0.5**, its two-cluster floor (zero matching complete signatures between distinct clusters), and pairwise concordance at **0.75**."
    },
    {
        "label": "discussion cross-class Simpson floor",
        "old": "Yellow development is more repeatable: both standardized trajectories share A down, C up, and P down while differing at F, yielding exact recurrence 0.5 and pairwise concordance 0.75. Evolution therefore reuses selected modules without replaying one invariant four-axis programme.",
        "new": "The two yellow-development trajectories share A down, C up, and P down while differing at F, with pairwise axis concordance of 0.75. Their exact-signature concentration of 0.5 is the two-cluster floor, just as the anthocyanin value of 0.333 is the three-cluster floor: neither class contains an identical complete signature across distinct clusters. Differences in those mathematical floors do not establish that one class has stronger exact whole-package replay. These contrasts instead show partial alignment of transcript-module directions without one invariant four-axis programme."
    }
]


def apply_simpson_clarifications(text: str) -> str:
    """Submission-wording-only fixes. Never touch frozen source science or numerical estimates."""
    for edit in SIMPSON_CLARIFICATIONS:
        old = edit["old"]
        count = text.count(old)
        if count != 1:
            raise SystemExit(f'{edit["label"]}: expected one source span, found {count}')
        text = text.replace(old, edit["new"], 1)
    return text


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

    text = a.source.read_text(encoding="utf-8")
    if text.count(TITLE_034) != 1:
        raise SystemExit("v1.0 v0.3.4 source title drift")
    if text.count(RUNNING_034) != 1:
        raise SystemExit("v1.0 v0.3.4 running-head drift")
    if MARKER in text:
        raise SystemExit("v1.0 source unexpectedly contains compatibility marker")

    compat = text.replace(TITLE_034, TITLE_033, 1).replace(RUNNING_034, RUNNING_033, 1)
    compat = compat.replace(TITLE_033, TITLE_033 + "\n\n" + MARKER, 1)

    with tempfile.TemporaryDirectory(prefix="paper1_v10_submit_v034_") as td:
        compat_source = Path(td) / "PAPER1_NOVELTY_V034_SUBMISSION_COMPAT.md"
        compat_summary = Path(td) / "submission_summary.json"
        compat_source.write_text(compat, encoding="utf-8")
        subprocess.run([
            sys.executable,
            "scripts/build_paper1_submission_v1_0.py",
            "--source", str(compat_source),
            "--appendix-map", str(a.appendix_map),
            "--figure-manifest", str(a.figure_manifest),
            "--out", str(a.out),
            "--summary", str(compat_summary),
        ], check=True)
        summary = json.loads(compat_summary.read_text(encoding="utf-8"))

    out = a.out.read_text(encoding="utf-8")
    if out.count(MARKER) != 1:
        raise SystemExit(f"v1.0 compatibility marker count drift in output: {out.count(MARKER)}")
    out = out.replace(MARKER + "\n\n", "", 1).replace(MARKER, "", 1)
    if MARKER in out or "repeated generation with partial mechanistic replay" in out:
        raise SystemExit("v1.0 compatibility token leaked into final manuscript")

    if out.count(TITLE_033) != 1 or out.count(RUNNING_033) != 1:
        raise SystemExit("v1.0 compatibility title/running-head output drift")
    out = out.replace(TITLE_033, TITLE_034, 1).replace(RUNNING_033, RUNNING_034, 1)

    if out.count("## ABSTRACT") != 1 or out.count("**Key words:**") != 1:
        raise SystemExit("could not uniquely locate AJB abstract boundaries")
    prefix = out.split("## ABSTRACT", 1)[0].rstrip()
    suffix = out.split("**Key words:**", 1)[1]
    out = prefix + "\n\n" + AJB_ABSTRACT_V10_034 + "\n\n**Key words:**" + suffix

    # Editorial metric-definition correction after frozen v0.3.4 provenance is built.
    out = apply_simpson_clarifications(out)
    words = abstract_word_count(out)
    if words > 250:
        raise SystemExit(f"AJB v1.0 v0.3.4 abstract exceeds 250 words: {words}")

    required = [
        "Hierarchical molecular repeatability coexists with local flower-colour conservatism",
        "annotation-driven, outcome-independent quantification within these prespecified modules",
        "not direct macroevolutionary branch events",
        "hierarchical rather than all-or-none",
        "matched inferential audit across scales",
        "not an event-for-event matching of RNA-seq contrasts to reconstructed branches",
        "not a direct observation of independent evolutionary origins",
    ]
    missing = [x for x in required if x not in out]
    if missing:
        raise SystemExit(f"v1.0 v0.3.4 output missing event-boundary tokens: {missing}")

    a.out.write_text(out.rstrip() + "\n", encoding="utf-8")

    summary.update({
        "source_manuscript": "provenance/PAPER1_NOVELTY_FRAMING_V0_3_4.md",
        "source_framing_version": "Paper 1 v0.3.4 event-boundary-safe novelty framing",
        "compatibility_marker_removed": True,
        "v0_3_4_title_restored": True,
        "v0_3_4_running_head_restored": True,
        "event_boundary_clarified": True,
        "candidate_free_definition_clarified": True,
        "simpson_index_definition_clarified": True,
        "simpson_metric_estimates_unchanged": True,
        "abstract_word_count": words,
        "biological_headline": "hierarchical transition-class-dependent molecular repeatability with separate macro pattern and event identity",
        "novelty_headline": "hierarchical transition-class-dependent molecular repeatability plus separate macro pattern/event identity",
        "status": "submission-clean Paper 1 AJB v1.0 built from event-boundary-safe framing v0.3.4",
    })
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
