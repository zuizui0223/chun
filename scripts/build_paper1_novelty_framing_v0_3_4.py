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
        raise SystemExit(f"{label}: expected one occurrence, found {n}")
    return text.replace(old, new, 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True, help="Paper 1 science v0.2.2 source")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    a = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="paper1_v034_") as td:
        td = Path(td)
        base = td / "PAPER1_NOVELTY_FRAMING_V0_3_3.md"
        base_summary = td / "v033_summary.json"
        subprocess.run([
            sys.executable,
            "scripts/build_paper1_novelty_framing_v0_3_3.py",
            "--source", str(a.source),
            "--out", str(base),
            "--summary", str(base_summary),
        ], check=True)
        text = base.read_text(encoding="utf-8")

    text = replace_once(
        text,
        "# Standardized remeasurement reveals partial mechanistic replay during repeated flower-colour evolution in *Camellia*",
        "# Hierarchical molecular repeatability coexists with local flower-colour conservatism in *Camellia*",
        "title",
    )
    text = replace_once(
        text,
        "**Running head:** Mechanistic replay in flower-colour evolution",
        "**Running head:** Hierarchical flower-colour repeatability",
        "running head",
    )

    text = replace_once(
        text,
        "Repeated phenotypic evolution is often interpreted as evidence of mechanistic repeatability, yet comparative molecular studies usually report different subsets of the underlying pathway. We asked how much of a multivariate flower-colour transition is actually replayed when the biological systems are held constant and the observation rule is standardized.",
        "Similar flower-colour states can be generated through multiple molecular routes, yet comparative molecular studies usually report different subsets of the underlying pathway. We asked how repeatable the underlying multivariate pigment-network state change is when the same public biological systems are remeasured under one standardized observation rule, and separately whether realised wild-colour patterns and individual historical transition events show the same robustness at macroevolutionary scale.",
        "abstract premise",
    )
    text = replace_once(
        text,
        "The same five public RNA-seq systems were then remeasured with one frozen, outcome-independent pathway-wide protocol.",
        "The same five public RNA-seq systems were then remeasured using annotation-driven, outcome-independent quantification within the four prespecified pigment modules (hereafter `candidate-free`). These contrasts quantify colour-state-generating transcript changes within admitted systems and are not treated as direct observations of macroevolutionary branch events.",
        "abstract methods candidate-free definition",
    )
    text = replace_once(
        text,
        "The distinctive result is not mechanistic heterogeneity itself, but that standardized remeasurement of the same systems changes how much mechanistic replay is identifiable. Repeated flower-colour evolution shows partial, transition-class-dependent replay, while robust macroevolutionary pattern can persist without robust historical event identity.",
        "The distinctive result is not mechanistic heterogeneity itself, but a hierarchy of repeatability across biological levels. Standardized molecular contrasts show transition-class-dependent modular reuse rather than one invariant complete A/F/C/P programme, while realised wild colours retain a robust local phylogenetic pattern even though individual historical transition events are not robustly identified.",
        "abstract conclusion",
    )

    text = replace_once(
        text,
        "What has been harder to test empirically is the matched counterfactual: **hold the biological systems fixed, change only the observation rule, and ask how the inferred amount of mechanistic replay changes**. That same-system intervention is the central inferential move of this study.",
        "What has been harder to test empirically is the matched counterfactual: **hold the biological systems fixed, change only the observation rule, and ask how the inferred amount of molecular-state repeatability changes**. That same-system intervention is the central inferential move of the molecular arm. It does not convert within-system RNA-seq contrasts into independently observed macroevolutionary events; those historical events are addressed separately by the phylogenetic arm.",
        "introduction event boundary",
    )
    text = replace_once(
        text,
        "Our contribution is thus a **matched inferential audit across scales**, not a generic claim that convergence can be mechanistically heterogeneous.",
        "Our contribution is thus a **matched inferential audit across scales**, not a generic claim that convergence can be mechanistically heterogeneous and not an event-for-event matching of RNA-seq contrasts to reconstructed branches.",
        "introduction cross-scale boundary",
    )

    text = replace_once(
        text,
        "## Repeated flower-colour evolution shows partial rather than complete replay",
        "## Molecular repeatability is hierarchical and transition-class dependent",
        "discussion hierarchy heading",
    )
    text = replace_once(
        text,
        "The biological interpretation is not \"no repeatability.\" It is **partial mechanistic replay whose strength depends on transition class**.",
        "The biological interpretation is not \"no repeatability.\" It is **hierarchical molecular repeatability whose strength depends on transition class**. The RNA-seq contrasts quantify colour-state-generating transcript changes under a common observation rule; they are not direct observations of independent macroevolutionary branch transitions.",
        "discussion hierarchy framing",
    )
    text = replace_once(
        text,
        "The molecular and macro results together separate mechanistic accessibility from macroevolutionary realization.",
        "The molecular and macro results address different quantities and together separate mechanistic accessibility from macroevolutionary realization. Their juxtaposition is cross-scale rather than event-for-event: the molecular arm measures standardized colour-state-generating transcript changes, whereas the phylogenetic arm tests realised wild-colour structure and historical event identity.",
        "discussion cross-scale statement",
    )
    text = replace_once(
        text,
        "The standardized RNA-seq analysis compares frozen transcript-state modules; it is not a direct assay of pigment concentrations, enzyme activity, cell-specific expression, or causal regulatory variants.",
        "The standardized RNA-seq analysis compares frozen transcript-state modules; it is not a direct observation of independent evolutionary origins and is not a direct assay of pigment concentrations, enzyme activity, cell-specific expression, or causal regulatory variants. `Candidate-free` is used operationally for annotation-driven, outcome-independent quantification within prespecified A/F/C/P modules, not to imply a genome-wide hypothesis-free analysis.",
        "scope terminology boundary",
    )

    text = replace_once(
        text,
        "Standardizing observation on the same public *Camellia* systems changes how much mechanistic replay is identifiable.",
        "Standardizing observation on the same public *Camellia* systems changes how much molecular-state repeatability is identifiable.",
        "conclusion opening",
    )
    text = replace_once(
        text,
        "Repeated phenotype, repeated molecular programme, persistent macroevolutionary pattern, and identified historical event are therefore distinct evolutionary quantities.",
        "Colour-state generation, molecular module reuse, persistent macroevolutionary pattern, and identified historical event are therefore distinct evolutionary quantities.",
        "conclusion hierarchy",
    )

    required = [
        "annotation-driven, outcome-independent quantification within the four prespecified pigment modules",
        "not treated as direct observations of macroevolutionary branch events",
        "hierarchy of repeatability across biological levels",
        "not an event-for-event matching of RNA-seq contrasts to reconstructed branches",
        "not a direct observation of independent evolutionary origins",
    ]
    missing = [x for x in required if x not in text]
    if missing:
        raise SystemExit(f"required framing clauses missing: {missing}")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(text, encoding="utf-8")

    summary = {
        "framing_version": "v0.3.4",
        "science_version": "v0.2.2",
        "scientific_estimates_changed": False,
        "event_boundary_clarified": True,
        "candidate_free_definition_clarified": True,
        "hierarchical_repeatability_headline": True,
        "source_layer": "v0.3.3 novelty-forward framing",
    }
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
