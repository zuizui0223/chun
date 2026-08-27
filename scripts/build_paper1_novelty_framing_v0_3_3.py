#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


TITLE_032 = "# Repeated generation of flower-colour states does not replay one pigment-state programme in *Camellia*"
TITLE_033 = "# Standardized remeasurement reveals partial mechanistic replay during repeated flower-colour evolution in *Camellia*"
RUNNING_032 = "**Running head:** Temporal repeatability of flower colour"
RUNNING_033 = "**Running head:** Mechanistic replay in flower-colour evolution"
BANNER_032 = (
    "> Draft v0.3.2 temporal framing revision. Scientific estimates remain Paper 1 v0.2.2. "
    "This framing places repeated generation and mechanistic replay through evolutionary time at the biological centre; "
    "observation-regime and event-identification analyses remain identification tools and no estimate, contrast, figure input, "
    "or inferential gate is changed here."
)
BANNER_033 = (
    "> Draft v0.3.3 novelty-forward framing revision. Scientific estimates remain Paper 1 v0.2.2. "
    "The distinctive contribution is framed as a matched same-system observation intervention plus a separate macro pattern/event-identity robustness test; "
    "no estimate, contrast, figure input, or inferential gate is changed here."
)

ABSTRACT = """## ABSTRACT

### Premise of the study

Repeated phenotypic evolution is often interpreted as evidence of mechanistic repeatability, yet comparative molecular studies usually report different subsets of the underlying pathway. We asked how much of a multivariate flower-colour transition is actually replayed when the biological systems are held constant and the observation rule is standardized.

### Methods

We represented mechanism on four prespecified pigment-state axes—anthocyanin (A), flavonol (F), carotenoid (C), and proanthocyanidin diversion (P). Literature evidence for three anthocyanin-gain and two yellow-development dependence clusters was treated as partially observed A/F/C/P signatures. The same five public RNA-seq systems were then remeasured with one frozen, outcome-independent pathway-wide protocol. Separately, accepted-species analyses tested whether phylogenetic colour structure and individual transition events survived alternative nuclear topologies and wild-colour codings.

### Key results

For anthocyanin gain, literature-compatible exact recurrence was 0.333–1.0, whereas standardized remeasurement fixed it at 0.333; pairwise concordance narrowed from 0.333–1.0 to 0.333–0.5. For yellow development, exact recurrence narrowed from 0.5–1.0 to 0.5 and pairwise concordance from 0.25–1.0 to 0.75; A, C, and P were shared while F differed. Wild colours retained topology-robust local phylogenetic structure, but no accepted-species transition branch was robust to alternative colour coding.

### Conclusions

The distinctive result is not mechanistic heterogeneity itself, but that standardized remeasurement of the same systems changes how much mechanistic replay is identifiable. Repeated flower-colour evolution shows partial, transition-class-dependent replay, while robust macroevolutionary pattern can persist without robust historical event identity.

**Key words:** anthocyanin; *Camellia*; evolutionary repeatability; flower-colour variation; mechanistic replay; modular evolution; pigment network; RNA-seq"""

INTRODUCTION = """# INTRODUCTION

Repeated evolution is one of the strongest natural experiments available for asking whether evolution is predictable. Similar phenotypes arising independently can reflect repeated use of the same mutation, gene, pathway, regulatory module, or only the same endpoint phenotype (Rausher, 2008; Conte et al., 2012). Flower-colour evolution has been especially productive in showing both alternative routes to similar colours and convergence at broader biochemical or pathway levels (Ng and Smith, 2016; Larter et al., 2018; Wheeler et al., 2023). The existence of mechanistic heterogeneity is therefore not the unresolved problem. The unresolved problem is **how much mechanistic replay is identifiable when the evidence used to compare origins has itself been generated under different observation rules**.

Most comparative syntheses necessarily aggregate mechanisms discovered by heterogeneous study designs. Different studies target different genes, paralogs, pathway branches, developmental stages, or omic layers, so an apparent degree of convergence reflects both biological reuse and which coordinates were measured. Candidate-gene and discovery-method effects on estimated parallelism are already recognized in evolutionary genetics (Conte et al., 2012). What has been harder to test empirically is the matched counterfactual: **hold the biological systems fixed, change only the observation rule, and ask how the inferred amount of mechanistic replay changes**. That same-system intervention is the central inferential move of this study.

Flower colour is well suited to such a test because a visible state is generated by interacting molecular branches rather than by one scalar pigment variable. Anthocyanins contribute many red, pink, purple, and blue phenotypes; flavonols compete for precursors and alter copigmentation; carotenoids provide an independent route to yellow pigmentation; and proanthocyanidin-directed flux can divert shared substrates. We therefore place all admitted contrasts in one prespecified four-axis state space: anthocyanin (A), flavonol (F), carotenoid (C), and proanthocyanidin diversion (P). Literature mechanisms can then remain partially observed rather than being completed from colour expectations, and exact recurrence can be bounded over unresolved axes before the same systems are remeasured under one pathway-wide rule.

*Camellia* provides an unusually useful natural system for this matched replay test. The genus contains repeated red, pink, white, and yellow states, multiple public molecular contrasts, and dense nuclear phylogenomic resources (Wu et al., 2022; Zan et al., 2023; Zhang et al., 2023; Yan et al., 2024; Xiao et al., 2025). Genus-scale work makes a white ancestral state biologically plausible, although our accepted-species reconstruction retains W/Y uncertainty; white is therefore used only as a visible evolutionary context, never as a molecular zero or fixed ancestral premise (Fan et al., 2026). The genus also spans contrasting reproductive contexts. Red-flowered *C. rusticana* and *C. japonica* differ strongly in bee- versus bird-oriented signalling, while golden-flowered *C. petelotii* receives both honeybee and sunbird visits and substantial bird reproductive service (Sun et al., 2017; Mori et al., 2023). Thus molecular state, visible hue, sensory phenotype, and pollination context can vary partly independently within one genus.

The literature audit also shows why the matched design matters. Citation chasing recovered Luo et al. (2016), which resolved a previously missing *C. japonica* F-axis direction and created an additional literature-versus-standardized conflict. At the same time, dependence-collapsed A-specific ascertainment weakened to P=0.078125. Observation nonuniformity is therefore not itself the biological result; it is the reason a common measurement space is needed before temporal repeatability can be interpreted.

A second identification problem appears at the macroevolutionary scale. A molecular state that can be generated repeatedly need not be repeatedly established or retained, and a robust aggregate trait pattern need not imply robust knowledge of the historical branches on which transitions occurred. We therefore use a second matched robustness design: accepted taxa are held fixed while nuclear topology and wild-colour coding are varied. This separates the question "is colour phylogenetically structured?" from the stronger question "which individual historical transitions are robustly identified?" (Revell, 2025).

Our contribution is thus a **matched inferential audit across scales**, not a generic claim that convergence can be mechanistically heterogeneous. First, we ask how much complete A/F/C/P replay remains compatible with published evidence and how that identified set changes when the same public systems are remeasured with one frozen, outcome-independent protocol. Second, we ask whether realised wild colours retain phylogenetic structure across independent nuclear topologies and alternative colour codings, and whether any individual transition branches survive the stricter event-identity gate. This design directly tests how far repeated visible evolution can be read as repeated molecular programme and how far a robust macro pattern can be read as a set of identified historical events."""

DISCUSSION = """# DISCUSSION

## Same-system remeasurement changes how much mechanistic replay is identifiable

The strongest result is a matched observation intervention. The biological systems are held fixed while the observation rule changes from literature-selected measurements to one frozen A/F/C/P protocol. Under literature-selected observation, complete anthocyanin-gain recurrence remains compatible with the unresolved dimensions, with exact recurrence spanning 0.333–1.0 and pairwise concordance 0.333–1.0. Standardized remeasurement of those same systems fixes exact recurrence at 0.333 and contracts pairwise concordance to 0.333–0.5. The contribution is therefore not merely the statement that similar colours can have different mechanisms. It is the empirical demonstration, in the same admitted systems, that **the amount of molecular replay supported by the evidence changes when the observation process is standardized**.

Luo et al. (2016) makes this point sharper rather than weaker. Adding a previously omitted literature-side *CJAPONICA:F=down* direction did not make the literature and standardized representations converge; the standardized Joy Kendrick system is F up. The number of directly comparable anthocyanin cells therefore increased to six while agreement remained only two. More literature information exposed another disagreement instead of recovering one invariant programme.

This same-system comparison is distinct from prior work demonstrating alternate biochemical routes, pathway-level convergence, or discovery-method effects on genetic parallelism (Conte et al., 2012; Ng and Smith, 2016; Larter et al., 2018; Wheeler et al., 2023). Those studies establish the conceptual possibility of hierarchical convergence and ascertainment effects. Here the observation process is treated as an empirical intervention on a fixed set of public biological systems, and the consequence is quantified as a contraction of the multivariate recurrence that remains identifiable.

## Repeated flower-colour evolution shows partial rather than complete replay

The biological interpretation is not "no repeatability." It is **partial mechanistic replay whose strength depends on transition class**. Anthocyanin-gain systems show limited whole-package recurrence after standardization. Yellow development is more repeatable: both standardized trajectories share A down, C up, and P down while differing at F, yielding exact recurrence 0.5 and pairwise concordance 0.75. Evolution therefore reuses selected modules without replaying one invariant four-axis programme.

Sequence-level observations support this multiscale view. Same-lineage FLS recurrence, DFR paralog substitution, and copy-specific ANS/ANR deployment show that reuse can occur at different molecular granularities. A recurrent visible state can be assembled from a mixture of reused and non-reused components, so the appropriate unit of evolutionary predictability is not necessarily the whole pathway package.

## A second matched audit separates macro pattern from event identity

The macro analysis provides an independent cross-scale result. Holding the accepted taxon set fixed, local nearest-same-colour structure survives two independently inferred nuclear topologies and alternative wild-colour codings. Yet no individual accepted-species transition branch survives strict versus dominant treatment of naturally variable species. The robust result is therefore an aggregate pattern, not a robust set of historical events.

Ancestral-state uncertainty and coding sensitivity are not new methodological discoveries (Revell, 2025). The contribution is the explicit paired test within the same study: **a positive pattern-level result is allowed to coexist with a failed event-identity gate rather than being converted into a stronger historical narrative**. This matters because ecological attribution requires an event to be located before a cause can be assigned to it.

## Generation, establishment, and persistence are separate evolutionary filters

The molecular and macro results together separate mechanistic accessibility from macroevolutionary realization. Multiple molecular implementations are feasible and selected modules recur, yet realised wild colour remains locally phylogenetically structured. Being able to generate a colour state is therefore not equivalent to that state repeatedly establishing and persisting through lineage diversification.

This is where ecology enters the argument. *Camellia* is valuable because visible hue does not map one-to-one onto reproductive function: red *C. rusticana* and *C. japonica* show contrasting pollinator-oriented signals, and *C. petelotii* receives substantial service from both birds and bees (Sun et al., 2017; Mori et al., 2023). These observations motivate ecological filtering and persistence, but they do not identify the causes of any particular reconstructed branch. A branch-specific pollinator or climate explanation remains outside the claim ceiling when event identity itself is unstable.

## Novelty boundary and general implication

The paper does not claim priority for same-phenotype/different-mechanism, pathway-level convergence, candidate-gene bias, partial identification, or uncertainty in ancestral reconstruction. Its novelty is the **combination of two matched empirical tests**. At the molecular scale, the same biological systems are compared before and after standardizing observation, revealing how much mechanistic replay survives a common state representation. At the macro scale, the same accepted taxon set is tested for robust aggregate colour structure and for the stronger requirement of robust individual event identity.

Together these tests show why repeated phenotype, repeated mechanism, persistent phylogenetic pattern, and identified historical event should not be treated as interchangeable forms of evidence. For flower-colour evolution, predictability is hierarchical: some modules are reused, complete programmes are not invariantly replayed, realised states remain structured through time, and historical event identity can still fail.

## Scope and limitations

The standardized RNA-seq analysis compares frozen transcript-state modules; it is not a direct assay of pigment concentrations, enzyme activity, cell-specific expression, or causal regulatory variants. A/F/C/P directions therefore define recurrence of this prespecified transcript-state representation. Candidate-selected studies and the standardized protocol answer related but non-identical questions, so disagreement shows a change in identified replay under observation scale rather than proof that either regime uniquely recovers the true mechanism.

All five systems were quantified against one annotation-informative *C. sinensis* RefSeq. Using one reference prevents outcome-dependent reference switching and produced high mapping rates in all admitted systems, but it can still miss species-specific paralogs or create differential mappability. Accordingly, cross-system claims remain at the gene-family/module level rather than exact ortholog or paralog equivalence across species. Species-native genomes and metabolite, protein, or enzyme assays remain important future sensitivities where comparable resources exist.

The raw workflows use frozen read-prefix depths rather than full-depth differential-expression inference. Prefix depth and contrasts were fixed before outcomes, read integrity and fallback routes were audited, and module directions were not selected by significance. The present claims are therefore restricted to the reproducible fixed-depth observation regime. Full-depth and depth-sensitivity analyses remain useful robustness tests for precision and direction stability rather than hidden outcome-selected evidence."""

CONCLUSIONS = """# CONCLUSIONS

Standardizing observation on the same public *Camellia* systems changes how much mechanistic replay is identifiable. Literature-selected evidence permits much broader recurrence, whereas one frozen pathway-wide A/F/C/P representation fixes anthocyanin whole-signature recurrence at one third and reveals stronger but still incomplete modular replay in yellow development. The key contribution is therefore not simply that repeated colours can use different mechanisms, but that the inferred degree of replay changes under a matched observation intervention on the same biological systems.

At the macro scale, realised wild colours retain topology-robust local phylogenetic structure while individual transition branches fail the strict-versus-dominant event-identity gate. Repeated phenotype, repeated molecular programme, persistent macroevolutionary pattern, and identified historical event are therefore distinct evolutionary quantities. *Camellia* provides a model system in which those levels can be separated rather than collapsed into one adaptive story."""


def replace_between(text: str, start: str, end: str, replacement: str) -> str:
    if text.count(start) != 1 or text.count(end) != 1:
        raise SystemExit(f"section marker drift: {start!r} / {end!r}")
    a = text.index(start)
    b = text.index(end, a)
    return text[:a] + replacement.rstrip() + "\n\n" + text[b:]


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

    with tempfile.TemporaryDirectory(prefix="paper1_v033_") as td:
        td = Path(td)
        base = td / "PAPER1_TEMPORAL_FRAMING_V0_3_2.md"
        base_summary = td / "v032_summary.json"
        subprocess.run([
            sys.executable,
            "scripts/build_paper1_temporal_framing_v0_3_2.py",
            "--source", str(a.source),
            "--out", str(base),
            "--summary", str(base_summary),
        ], check=True)
        text = base.read_text(encoding="utf-8")

    text = replace_once(text, TITLE_032, TITLE_033, "title")
    text = replace_once(text, RUNNING_032, RUNNING_033, "running head")
    text = replace_once(text, BANNER_032, BANNER_033, "governance banner")
    text = replace_between(text, "## ABSTRACT", "---", ABSTRACT)
    text = replace_between(text, "# INTRODUCTION", "# MATERIALS AND METHODS", INTRODUCTION)
    text = replace_between(text, "# DISCUSSION", "# CONCLUSIONS", DISCUSSION)
    text = replace_between(text, "# CONCLUSIONS", "# DATA AVAILABILITY AND REPRODUCIBILITY", CONCLUSIONS)

    required = [
        "same biological systems are held constant and the observation rule is standardized",
        "matched observation intervention",
        "0.333–1.0",
        "0.333–0.5",
        "0.25–1.0",
        "P=0.078125",
        "two agreements",
        "matched inferential audit across scales",
        "robust aggregate colour structure",
        "10.3389/fpls.2015.01257",
        "10.1016/j.phytochem.2022.113559",
        "10.3732/ajb.1600428",
        "The strict×dominant shared robust event count was therefore zero",
    ]
    missing = [x for x in required if x not in text]
    if missing:
        raise SystemExit(f"v0.3.3 missing required novelty/science tokens: {missing}")

    forbidden = [
        "first demonstration that repeated flower colour",
        "first pathway-level",
        "first micro-to-macro",
        "white as a molecular zero",
        "anthocyanin enrichment detectable even after dependence collapse",
    ]
    retained = [x for x in forbidden if x in text]
    if retained:
        raise SystemExit(f"v0.3.3 retained overclaim/stale tokens: {retained}")

    # Science-bearing Methods + Results must remain byte-identical to the v0.3.2 base.
    with tempfile.TemporaryDirectory(prefix="paper1_v033_check_") as td:
        td = Path(td)
        base2 = td / "base.md"
        s2 = td / "summary.json"
        subprocess.run([
            sys.executable,
            "scripts/build_paper1_temporal_framing_v0_3_2.py",
            "--source", str(a.source),
            "--out", str(base2),
            "--summary", str(s2),
        ], check=True)
        base_text = base2.read_text(encoding="utf-8")
    start = "# MATERIALS AND METHODS"
    end = "# DISCUSSION"
    if base_text.split(start, 1)[1].split(end, 1)[0] != text.split(start, 1)[1].split(end, 1)[0]:
        raise SystemExit("v0.3.3 changed Methods/Results science body")

    abstract_body = ABSTRACT.split("**Key words:**", 1)[0]
    wc = len(re.findall(r"\b[\w’'-]+\b", abstract_body))
    if wc > 250:
        raise SystemExit(f"v0.3.3 abstract exceeds 250 words: {wc}")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(text.rstrip() + "\n", encoding="utf-8")
    summary = {
        "document_version": "Paper 1 framing v0.3.3",
        "source_science_version": "Paper 1 v0.2.2",
        "source_framing_version": "v0.3.2",
        "novelty_headline": "same-system standardized remeasurement quantifies how much mechanistic replay survives",
        "cross_scale_novelty": "matched molecular observation intervention plus separate macro pattern/event-identity robustness test",
        "scientific_results_changed_by_framing": False,
        "methods_results_byte_identical": True,
        "abstract_words": wc,
        "reference_contract": "v0.5 / 25 DOI rows unchanged",
        "status": "novelty-forward framing v0.3.3 built",
    }
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
