#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected exactly one block, found {n}")
    return text.replace(old, new, 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    a = ap.parse_args()

    text = a.source.read_text(encoding="utf-8")

    science_banner = (
        "> Draft v0.2.1. The Paper 1 v0.2 biological results are retained except for the literature-ascertainment layer reopened by the 2026-08-27 formal database search. "
        "This manuscript is governed by `data/paper1_authoritative_results_v0_2_1.csv`, `data/paper1_main_figure_manifest_v0_2_1.csv`, and `data/paper1_reference_registry_v0_2_1.csv`. "
        "The five-system candidate-free recurrence and macroevolutionary results remain unchanged."
    )
    legacy_banner = (
        "> Draft v0.2. This manuscript is governed by `data/paper1_authoritative_results_v0_2.csv`, "
        "`data/paper1_main_figure_manifest_v0_2.csv`, and `data/paper1_reference_registry_v0_2.csv`. "
        "The v0.1 manuscript is retained as provenance and must not be patched back into the molecular framing when it conflicts with the v0.2 result hierarchy."
    )

    science_discussion = (
        "The comparison is not a test of whether candidate-gene papers are “right” or “wrong.” Candidate-selected studies often ask targeted "
        "biological questions and can resolve specific causal nodes more precisely than a broad module score. The candidate-free protocol asks a "
        "different question: if the same systems are measured with one outcome-independent pathway-wide representation, what multivariate recurrence "
        "remains identifiable? The formal database expansion provides an additional robustness check on the observation layer: adding an independent "
        "*C. semiserrata* red/white transcriptomic system increased A-axis coverage and made anthocyanin enrichment detectable even after dependence "
        "collapse, yet the study could not be added to the standardized arm without auditable public raw reads. Broader literature coverage therefore "
        "strengthened the ascertainment diagnosis while leaving the matched candidate-free recurrence estimator unchanged."
    )
    legacy_discussion = (
        "The comparison is not a test of whether candidate-gene papers are “right” or “wrong.” Candidate-selected studies often ask targeted "
        "biological questions and can resolve specific causal nodes more precisely than a broad module score. The candidate-free protocol asks a "
        "different question: if the same systems are measured with one outcome-independent pathway-wide representation, what multivariate recurrence "
        "remains identifiable?"
    )

    compat = replace_once(text, science_banner, legacy_banner, "science banner compatibility")
    compat = replace_once(compat, science_discussion, legacy_discussion, "science discussion compatibility")

    with tempfile.TemporaryDirectory(prefix="paper1_v031_") as td:
        td = Path(td)
        compat_path = td / "science_v0_2_1_compat.md"
        base_out = td / "framing_v0_3.md"
        base_summary = td / "framing_v0_3_summary.json"
        compat_path.write_text(compat, encoding="utf-8")
        subprocess.run(
            [
                sys.executable,
                "scripts/build_paper1_novelty_framed_v0_3.py",
                "--source", str(compat_path),
                "--out", str(base_out),
                "--summary", str(base_summary),
            ],
            check=True,
        )
        framed = base_out.read_text(encoding="utf-8")

    base_banner = (
        "> Draft v0.3 framing revision. The scientific result set remains Paper 1 v0.2. Novelty framing was "
        "revised after the 2026-08-27 high-recall prior-art audit; no biological estimate, contrast, figure input, "
        "or inferential gate is changed by this document."
    )
    new_banner = (
        "> Draft v0.3.1 framing revision. The scientific source is Paper 1 v0.2.1, whose only biological update is the formal-database-expanded literature-ascertainment layer. "
        "Novelty framing remains governed by the 2026-08-27 prior-art audit; the framing step changes no estimate, contrast, figure input, or inferential gate."
    )
    framed = replace_once(framed, base_banner, new_banner, "framing banner")

    base_novelty_discussion = (
        "The comparison is not a test of whether candidate-gene papers are “right” or “wrong,” nor is observation-method dependence itself a new "
        "concept (Conte et al., 2012). Candidate-selected studies often ask targeted biological questions and can resolve specific causal nodes more "
        "precisely than a broad module score. The candidate-free protocol asks the narrower matched question: if the same systems are measured with "
        "one outcome-independent pathway-wide representation, what multivariate recurrence remains identifiable and how much does the identified "
        "set contract relative to literature-selected observation?"
    )
    combined_discussion = (
        "The comparison is not a test of whether candidate-gene papers are “right” or “wrong,” nor is observation-method dependence itself a new "
        "concept (Conte et al., 2012). Candidate-selected studies often ask targeted biological questions and can resolve specific causal nodes more "
        "precisely than a broad module score. The candidate-free protocol asks the narrower matched question: if the same systems are measured with "
        "one outcome-independent pathway-wide representation, what multivariate recurrence remains identifiable and how much does the identified "
        "set contract relative to literature-selected observation? The formal database expansion supplies an additional empirical check on that layer: "
        "the independent *C. semiserrata* red/white system increased A-axis coverage and made anthocyanin ascertainment enrichment detectable after "
        "dependence collapse, but no auditable public raw RNA-seq accession was located, so the five-system standardized common-set estimator did not change."
    )
    framed = replace_once(framed, base_novelty_discussion, combined_discussion, "combined observation discussion")

    required = [
        "A/F/C/P coverage = 9/4/1/3",
        "coverage was 5/3/1/2",
        "0.00278854",
        "0.046875",
        "10.1007/s10722-025-02606-6",
        "The molecular result should not be read as the first demonstration",
        "observation-method dependence itself a new concept",
        "event instability is not itself a new methodological discovery",
        "The ecological value of the present result is an inferential boundary",
        "Candidate-free remeasurement fixed exact-signature recurrence at 0.333",
        "pairwise concordance at **0.75**",
        "The strict×dominant shared robust event count was therefore zero",
    ]
    missing = [x for x in required if x not in framed]
    if missing:
        raise SystemExit(f"v0.3.1 framing missing required tokens: {missing}")

    forbidden = [
        "> Draft v0.2.",
        "> Draft v0.3 framing revision.",
        "published coverage was A/F/C/P = 8/4/1/3",
        "anthocyanin-enrichment probability weakened to 0.140625",
    ]
    retained = [x for x in forbidden if x in framed]
    if retained:
        raise SystemExit(f"v0.3.1 framing retained superseded tokens: {retained}")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(framed.rstrip() + "\n", encoding="utf-8")
    summary = {
        "document_version": "Paper 1 framing v0.3.1",
        "source_science_version": "Paper 1 v0.2.1",
        "source_science_file": str(a.source),
        "scientific_results_changed_by_framing": False,
        "formal_database_update_preserved": True,
        "journal_reference_contract": "v0.4 / 22 DOI rows",
        "status": "novelty framing v0.3.1 built from science v0.2.1",
    }
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
