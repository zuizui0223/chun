#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

V033_BANNER = (
    "> Draft v0.3.3 novelty-forward framing revision. Scientific estimates remain Paper 1 v0.2.2. "
    "The distinctive contribution is framed as a matched same-system observation intervention plus a separate macro pattern/event-identity robustness test; "
    "no estimate, contrast, figure input, or inferential gate is changed here."
)
V032_BANNER = (
    "> Draft v0.3.2 temporal framing revision. Scientific estimates remain Paper 1 v0.2.2. "
    "This framing places repeated generation and mechanistic replay through evolutionary time at the biological centre; "
    "observation-regime and event-identification analyses remain identification tools and no estimate, contrast, figure input, "
    "or inferential gate is changed here."
)
TITLE_033 = "# Standardized remeasurement reveals partial mechanistic replay during repeated flower-colour evolution in *Camellia*"
TITLE_032 = "# Repeated generation of flower-colour states does not replay one pigment-state programme in *Camellia*"
RUNNING_033 = "**Running head:** Mechanistic replay in flower-colour evolution"
RUNNING_032 = "**Running head:** Temporal repeatability of flower colour"

AJB_ABSTRACT_V10 = """## ABSTRACT

### Premise of the study

Repeated phenotypic evolution can imply mechanistic repeatability, yet molecular studies often report different pathway subsets. We asked how much of a multivariate flower-colour transition is actually replayed when the biological systems are held constant and the observation rule is standardized.

### Methods

We represented mechanism on four prespecified pigment-state axes—anthocyanin (A), flavonol (F), carotenoid (C), and proanthocyanidin diversion (P). Literature evidence for three anthocyanin-gain and two yellow-development dependence clusters was treated as partially observed A/F/C/P signatures. The same five public RNA-seq systems were then remeasured with one frozen, outcome-independent pathway-wide protocol. Separately, accepted-species analyses tested whether phylogenetic colour structure and individual transition events survived alternative nuclear topologies and wild-colour codings.

### Key results

For anthocyanin gain, literature-compatible exact recurrence was 0.333–1.0, whereas standardized remeasurement fixed it at 0.333; pairwise concordance narrowed from 0.333–1.0 to 0.333–0.5. For yellow development, exact recurrence narrowed from 0.5–1.0 to 0.5 and pairwise concordance from 0.25–1.0 to 0.75; A, C, and P were shared while F differed. Wild colours retained topology-robust local phylogenetic structure, but no accepted-species transition branch was robust to alternative colour coding.

### Conclusions

The distinctive result is not mechanistic heterogeneity itself, but that standardized remeasurement of the same systems changes how much mechanistic replay is identifiable. Repeated flower-colour evolution shows partial, transition-class-dependent replay, while robust macroevolutionary pattern can persist without robust historical event identity."""


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
    compat = replace_once(source, V033_BANNER, V032_BANNER, "v0.3.3 banner compatibility")
    compat = replace_once(compat, TITLE_033, TITLE_032, "v0.3.3 title compatibility")
    compat = replace_once(compat, RUNNING_033, RUNNING_032, "v0.3.3 running-head compatibility")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paper1_v10_") as td:
        td = Path(td)
        compat_path = td / "PAPER1_NOVELTY_V033_COMPAT.md"
        base_summary = td / "v09_summary.json"
        compat_path.write_text(compat, encoding="utf-8")
        subprocess.run([
            sys.executable,
            "scripts/build_paper1_submission_v0_9.py",
            "--source", str(compat_path),
            "--appendix-map", str(a.appendix_map),
            "--figure-manifest", str(a.figure_manifest),
            "--out", str(a.out),
            "--summary", str(base_summary),
        ], check=True)
        inherited = json.loads(base_summary.read_text(encoding="utf-8"))

    out = a.out.read_text(encoding="utf-8")
    out = replace_once(out, TITLE_032, TITLE_033, "restore novelty title")
    out = replace_once(out, RUNNING_032, RUNNING_033, "restore novelty running head")

    if out.count("## ABSTRACT") != 1 or out.count("**Key words:**") != 1:
        raise SystemExit("could not uniquely locate AJB abstract boundaries")
    prefix = out.split("## ABSTRACT", 1)[0].rstrip()
    suffix = out.split("**Key words:**", 1)[1]
    out = prefix + "\n\n" + AJB_ABSTRACT_V10 + "\n\n**Key words:**" + suffix

    words = abstract_word_count(out)
    if words > 250:
        raise SystemExit(f"AJB v1.0 abstract exceeds 250 words: {words}")

    required = [
        "Standardized remeasurement reveals partial mechanistic replay",
        "matched observation intervention",
        "matched inferential audit across scales",
        "P=0.078125",
        "0.333–1.0",
        "0.333–0.5",
        "0.25–1.0",
        "agreement remained only two",
        "The strict×dominant shared robust event count was therefore zero",
        "10.3389/fpls.2015.01257",
        "10.1016/j.phytochem.2022.113559",
        "10.3732/ajb.1600428",
    ]
    missing = [x for x in required if x not in out]
    if missing:
        raise SystemExit(f"AJB v1.0 output missing novelty/science tokens: {missing}")

    forbidden = [
        "Draft v0.2", "Draft v0.3", "Draft v0.3.2", "Draft v0.3.3",
        "`data/", "`docs/", "`scripts/", "GitHub Actions",
        "first demonstration that repeated flower colour", "first micro-to-macro",
        "anthocyanin-axis ascertainment remained enriched after dependence collapse",
        "ecological Fig. 6",
    ]
    retained = [x for x in forbidden if x in out]
    if retained:
        raise SystemExit(f"AJB v1.0 output retains stale/internal/overclaim tokens: {retained}")

    a.out.write_text(out.rstrip() + "\n", encoding="utf-8")
    summary = {
        **inherited,
        "submission_version": "v1.0",
        "source_manuscript": str(a.source),
        "source_science_version": "Paper 1 v0.2.2",
        "source_framing_version": "Paper 1 v0.3.3 novelty-forward framing",
        "reference_contract": "paper1_reference_registry_v0_5.csv (25 DOI rows)",
        "abstract_word_count": words,
        "novelty_headline": "same-system standardized remeasurement quantifies how much mechanistic replay survives",
        "scientific_results_changed_by_submission_formatting": False,
        "status": "submission-clean Paper 1 AJB v1.0 built from science v0.2.2 + novelty framing v0.3.3",
    }
    a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
