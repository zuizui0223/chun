#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

V031_BANNER = (
    "> Draft v0.3.1 framing revision. The scientific source is Paper 1 v0.2.1, whose only biological update is the formal-database-expanded literature-ascertainment layer. "
    "Novelty framing remains governed by the 2026-08-27 prior-art audit; the framing step changes no estimate, contrast, figure input, or inferential gate."
)
V03_BANNER = (
    "> Draft v0.3 framing revision. The scientific result set remains Paper 1 v0.2. Novelty framing was "
    "revised after the 2026-08-27 high-recall prior-art audit; no biological estimate, contrast, figure input, "
    "or inferential gate is changed by this document."
)
SCIENCE_REGISTRY_SENTENCE = (
    "The current result set is frozen in `data/paper1_authoritative_results_v0_2_1.csv`; Main and Supplement figure roles are frozen in "
    "`data/paper1_main_figure_manifest_v0_2_1.csv`. This patch changes the literature-ascertainment layer only; superseded analyses remain in "
    "repository history and do not re-enter positive claims."
)
LEGACY_REGISTRY_SENTENCE = (
    "The current result set is frozen in `data/paper1_authoritative_results_v0_2.csv`; Main and Supplement figure roles are frozen in "
    "`data/paper1_main_figure_manifest_v0_2.csv`. Superseded analyses remain in repository history but do not re-enter positive claims."
)

AJB_ABSTRACT_V08 = """## ABSTRACT

### Premise of the study

Repeated change can suggest reuse of the same mechanism, but recurrence may depend on which pathway components are observed. We asked whether flower-colour mechanistic recurrence in *Camellia* survives standardized remeasurement and how it relates to macroevolutionary pattern.

### Methods

We represented mechanisms on four pigment-state axes—anthocyanin (A), flavonol (F), carotenoid (C), and proanthocyanidin diversion (P). A reproducible OpenAlex/Crossref/PubMed audit expanded the literature matrix, after which five public RNA-seq systems with auditable raw data were reanalyzed using one frozen annotation-driven all-paralog protocol. We also audited accepted taxonomy and wild colours, tested local colour structure on two nuclear topologies, and required transition events to survive alternative colour codings.

### Key results

The database-expanded literature matrix contained 11 systems and six dependence clusters; anthocyanin-axis ascertainment remained enriched after dependence collapse (P=0.046875). Candidate-free remeasurement fixed exact-signature recurrence at 0.333 and pairwise concordance at 0.333–0.5 for anthocyanin gain. For yellow development, exact recurrence was 0.5 and concordance 0.75; both trajectories reused A, C, and P directions but differed in F. No invariant whole A/F/C/P package recurred. Nearest-same-colour clustering survived topology and wild-colour sensitivity, but no accepted-species transition branch survived strict versus dominant coding.

### Conclusions

Repeated *Camellia* flower-colour change does not imply repetition of one complete pigment-state package. Broader literature coverage strengthened the diagnosis of an anthocyanin-heavy observation regime without changing the matched standardized recurrence estimator. Robust macroevolutionary pattern likewise need not identify historical events."""


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
    compat = replace_once(source, V031_BANNER, V03_BANNER, "v0.3.1 banner compatibility")
    compat = replace_once(compat, SCIENCE_REGISTRY_SENTENCE, LEGACY_REGISTRY_SENTENCE, "v0.2.1 registry compatibility")

    with tempfile.TemporaryDirectory(prefix="paper1_v08_") as td:
        td = Path(td)
        compat_path = td / "PAPER1_AJB_MANUSCRIPT_V0_3_COMPAT.md"
        base_summary = td / "v07_summary.json"
        compat_path.write_text(compat, encoding="utf-8")
        subprocess.run(
            [
                sys.executable,
                "scripts/build_paper1_submission_v0_7.py",
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
    abstract_marker = "## ABSTRACT"
    keyword_marker = "**Key words:**"
    if out.count(abstract_marker) != 1 or out.count(keyword_marker) != 1:
        raise SystemExit("could not uniquely locate AJB abstract boundaries")
    prefix = out.split(abstract_marker, 1)[0].rstrip()
    suffix = out.split(keyword_marker, 1)[1]
    out = prefix + "\n\n" + AJB_ABSTRACT_V08 + "\n\n" + keyword_marker + suffix

    words = abstract_word_count(out)
    if words > 250:
        raise SystemExit(f"AJB v0.8 abstract exceeds 250 words: {words}")

    required = [
        "11 systems and six dependence clusters",
        "P=0.046875",
        "Candidate-free remeasurement fixed exact-signature recurrence at 0.333",
        "exact recurrence was 0.5 and concordance 0.75",
        "10.1007/s10722-025-02606-6",
        "The molecular result should not be read as the first demonstration",
        "event instability is not itself a new methodological discovery",
        "The ecological value of the present result is an inferential boundary",
        "strict×dominant shared robust event count was therefore zero",
    ]
    missing = [x for x in required if x not in out]
    if missing:
        raise SystemExit(f"AJB v0.8 output missing required science/framing tokens: {missing}")

    forbidden = ["Draft v0.2", "Draft v0.3", "Draft v0.3.1", "`data/", "`docs/", "`scripts/", "ecological Fig. 6"]
    retained = [x for x in forbidden if x in out]
    if retained:
        raise SystemExit(f"AJB v0.8 output retains internal/stale tokens: {retained}")

    a.out.write_text(out.rstrip() + "\n", encoding="utf-8")
    summary = {
        **inherited,
        "submission_version": "v0.8",
        "source_manuscript": str(a.source),
        "source_science_version": "Paper 1 v0.2.1",
        "source_framing_version": "Paper 1 v0.3.1",
        "reference_contract": "paper1_reference_registry_v0_4.csv (22 DOI rows)",
        "formal_database_update_included": True,
        "abstract_word_count": words,
        "scientific_results_changed_by_submission_formatting": False,
        "status": "submission-clean Paper 1 AJB v0.8 built from science v0.2.1 + novelty framing v0.3.1",
    }
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
