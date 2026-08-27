#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


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


ABSTRACT = """## ABSTRACT

### Premise of the study

Similar flower-colour states can be generated repeatedly in independent lineages. The evolutionary question is not only whether colour changes recur, but how much of the underlying molecular transition is replayed each time. *Camellia* provides a comparative system with extensive colour diversity, contrasting pollination contexts, and molecular datasets.

### Methods

We represented mechanism on four prespecified pigment-state axes—anthocyanin (A), flavonol (F), carotenoid (C), and proanthocyanidin diversion (P)—across three anthocyanin-gain and two yellow-development dependence clusters. Literature states were treated as partially observed signatures, then five public RNA-seq systems were remeasured with one outcome-independent pathway-wide protocol. Accepted-species nuclear analyses tested wild-colour phylogenetic structure and event robustness.

### Key results

For anthocyanin gain, literature-compatible exact recurrence was 0.333–1.0, whereas standardized remeasurement fixed it at 0.333; pairwise A/F/C/P concordance narrowed from 0.333–1.0 to 0.333–0.5. For yellow development, exact recurrence narrowed from 0.5–1.0 to 0.5 and pairwise concordance from 0.25–1.0 to 0.75; A, C, and P were shared while F differed. Wild flower colours retained topology-robust local phylogenetic structure, but no accepted-species transition branch was robust to alternative colour coding.

### Conclusions

Repeated generation of similar flower colours does not replay one invariant pigment-state programme. Repeatability is modular and transition-class dependent, while generation, persistence, and event identity remain distinct evolutionary quantities.

**Key words:** anthocyanin; *Camellia*; evolutionary repeatability; flower-colour variation; modular evolution; phylogenetic conservatism; pigment network; RNA-seq"""

INTRODUCTION = """# INTRODUCTION

Flower-colour variation has a temporal as well as a spatial dimension. Across evolutionary history, similar visible states can arise repeatedly in independent lineages, creating natural replicates for asking how predictable phenotypic evolution is (Rausher, 2008). Repeated visible change, however, does not specify what has repeated underneath it. Genetic parallelism can range from the same mutation to the same gene, biochemical pathway, regulatory module, or only the final phenotype, and flower-colour systems already provide examples of both alternative biochemical routes and broader pathway-level convergence (Conte et al., 2012; Ng and Smith, 2016; Larter et al., 2018; Wheeler et al., 2023). The unresolved question we address is therefore not whether similar colours can arise by different mechanisms, but how much of a multivariate pigment-network transition is actually replayed when comparable colour states are generated repeatedly through evolutionary time.

Flower colour is especially useful for this question because a visible state is produced by interacting molecular branches rather than by one scalar pigment variable. Anthocyanins contribute many red, pink, purple, and blue phenotypes; flavonols can compete for precursors and alter copigmentation; carotenoids provide an independent route to yellow pigmentation; and proanthocyanidin-directed flux can divert shared substrates. We therefore treat anthocyanin (A), flavonol (F), carotenoid (C), and proanthocyanidin diversion (P) as a common four-axis state representation. This makes it possible to distinguish repetition of one complete programme from modular reuse in which only some pathway directions recur.

*Camellia* is a useful natural system for placing that repeatability question on an evolutionary time axis. The genus contains extensive red, pink, white, and yellow variation, multiple molecular contrasts, and dense nuclear phylogenomic resources (Wu et al., 2022; Zan et al., 2023; Zhang et al., 2023; Yan et al., 2024; Xiao et al., 2025). Genus-scale work makes a white ancestral state biologically plausible, although our accepted-species reconstructions retain W/Y uncertainty; we therefore use a white-like visible baseline only as evolutionary context, never as a molecular zero or a fixed ancestral-state premise (Fan et al., 2026). The genus also spans contrasting reproductive contexts. Two red-flowered species, *C. rusticana* and *C. japonica*, differ strongly in bee versus bird visual signalling and pollinator recruitment, while golden-flowered *C. petelotii* receives both honeybee and sunbird visits and shows substantial reproductive contribution from birds (Sun et al., 2017; Mori et al., 2023). Thus similar or contrasting visible states occur against heterogeneous ecological backgrounds, allowing molecular generation to be studied without equating hue with one pollination syndrome.

A difficulty is that the historical literature does not observe every component of the pigment network symmetrically. Candidate genes and assays are chosen for good biological reasons, but the resulting literature matrix contains different measured axes in different systems. Citation chasing illustrates why this matters: Luo et al. (2016) supplied a previously omitted *C. japonica* F-axis direction and exposed an additional literature-versus-standardized conflict, while dependence-collapsed A-specific ascertainment weakened to P=0.078125. Observation nonuniformity is therefore an identification problem, not the biological headline. To estimate temporal mechanistic replay, missing axes must remain missing or be measured under a common protocol rather than filled from visible colour expectations.

The time-axis question also has a second filter. Molecular states that are feasible or repeatedly generated need not be repeatedly established or retained across macroevolution. Conversely, visible flower colours may remain phylogenetically structured even when their molecular implementations differ. Generation, establishment/persistence, and event identity are therefore distinct quantities. A robust aggregate phylogenetic pattern does not by itself identify the branches on which particular changes occurred, and uncertain branch identity should stop branch-specific ecological attribution rather than be hidden by a more elaborate model (Revell, 2025).

Here we ask four linked questions. First, when three anthocyanin-gain and two yellow-development systems are expressed in the same A/F/C/P coordinates, how much complete mechanistic replay remains compatible with the published evidence? Second, how does that identified set change when the same public systems are remeasured with one frozen, outcome-independent pathway-wide protocol? Third, are realised wild flower colours locally structured across accepted-species nuclear phylogenies despite molecular implementation flexibility? Fourth, are individual historical transition events robust enough to support branch-specific causal interpretation? This design treats *Camellia* as a model system for repeated flower-colour generation through time, while using observation and event-identification gates to define how far the available evidence can support that biological interpretation."""

DISCUSSION = """# DISCUSSION

## Repeated generation does not replay one complete pigment programme

The central biological result concerns temporal repeatability. Similar flower-colour states can be generated more than once without replaying one invariant A/F/C/P transition. In the three anthocyanin-gain clusters, standardized measurement fixed exact whole-signature recurrence at 0.333 and restricted pairwise concordance to 0.333–0.5. In the two yellow-development systems, exact recurrence was 0.5 while three of four axes—A down, C up, and P down—were shared. Repeatability is therefore real but modular: the amount and identity of reused pigment-network directions depend on the transition class.

This is narrower than claiming that alternative mechanisms for similar flower colours are new. Such alternatives and pathway-level convergence are already well documented (Ng and Smith, 2016; Larter et al., 2018; Wheeler et al., 2023). The contribution here is to measure replay in one common multivariate state space across the same *Camellia* systems. That common representation separates phenotype-level recurrence from recurrence of the complete molecular transition that produced it.

Sequence-level observations fit this interpretation rather than replace it. Same-lineage FLS recurrence, DFR paralog substitution, and copy-specific ANS/ANR deployment show that reuse can occur at different molecular granularities. They are mechanistic examples of the larger result: a repeated visible state can be assembled from combinations of reused and non-reused modules.

## Standardized observation identifies how much replay is supported

Observation nonuniformity is part of the identification problem, but it is not the biological headline. The expanded literature remains strongly nonuniform across biological-system records, yet A-specific enrichment is not retained below 0.05 after dependence collapse (P=0.078125). More importantly, adding Luo et al. (2016) did not make the literature and standardized representations converge. It resolved *CJAPONICA:F* as down in the literature, whereas the standardized Joy Kendrick system was up, increasing the directly comparable anthocyanin cells to six but leaving only two agreements.

The literature nevertheless still permits complete three-cluster anthocyanin recurrence because unobserved C and P dimensions can be completed in multiple ways. Standardized measurement collapses that admissible set: exact recurrence becomes 0.333 and pairwise concordance 0.333–0.5. In the yellow class, four of five directly comparable literature cells agree with standardized directions, yet measuring the previously absent dimensions still removes exact whole-package recurrence. The result is therefore not a blanket reversal of candidate-gene studies. It is an identification result: observing the same multivariate coordinates reveals which part of apparent evolutionary replay survives common measurement.

This framing also keeps the novelty boundary clear. Dependence of repeatability estimates on discovery design is established in evolutionary genetics (Conte et al., 2012), and partial identification is not itself a new statistical idea. What is informative here is the empirical intervention on the observation process in the same biological systems and the resulting change in what can be said about molecular replay.

## Generation and persistence are different evolutionary filters

Mechanistic flexibility does not imply that visible flower colour should be randomly distributed through a phylogeny. The standardized molecular analyses ask how colour states can be generated; the accepted-species analysis asks where realised states persist. Despite taxonomy collapse, wild-colour auditing, and two nuclear topologies, a local nearest-same-colour signal remained robust. Thus flexible molecular generation coexists with local historical structure in visible-state realization.

This combination suggests a useful separation of evolutionary stages. A molecular state can be accessible but fail to establish; distinct molecular states can converge on a similar visible phenotype; and ecological, developmental, or historical backgrounds can affect which generated states persist through lineage diversification. The present public data do not identify which filter dominates in any particular branch, but they reject the shortcut from molecular accessibility to macroevolutionary transition frequency.

## Pattern can be identifiable when historical events are not

Ancestral-state uncertainty and model dependence are longstanding phylogenetic problems (Revell, 2025). The empirical result here is therefore not that ancestral reconstruction can be uncertain. It is the split under one robustness design: local visible-colour structure survives independent nuclear topologies and both wild-colour encodings, whereas no individual accepted-species transition branch survives strict versus dominant treatment of naturally variable species.

Aggregate structure can therefore be identifiable when the events generating it are not. That boundary matters for ecology. A branch-specific pollinator or climate explanation requires a branch whose colour transition is itself robustly identified. When that prerequisite fails, adding ecological covariates cannot recover a historical event that the trait data do not locate.

## Camellia separates visible colour from ecological function

The genus is valuable for the time-axis question precisely because visible hue does not map one-to-one onto ecological function. *C. rusticana* and *C. japonica* both have red flowers, yet experimental and spectral work indicates contrasting insect- versus bird-oriented visual strategies (Mori et al., 2023). In *C. petelotii*, both honeybees and sunbirds visit flowers and bird exclusion substantially reduces reproductive output (Sun et al., 2017). These examples do not establish the causes of any branch reconstructed in our macro analysis. Instead, they show why *Camellia* is a useful comparative material: molecular generation, visible state, sensory phenotype, and effective pollination can vary partly independently within one genus.

The next ecological step is therefore not to assign “red = bird” or “yellow = insect” to historical branches. It is to measure spectra, pigment chemistry, paralog-specific expression, floral rewards, effective pollen transfer, fruit and seed set, and flowering-window environment together in population-resolved systems. Such data can test how generated molecular states become ecologically differentiated and which states persist.

## Scope and limitations

The standardized RNA-seq analysis compares frozen transcript-state modules; it is not a direct assay of pigment concentrations, enzyme activity, cell-specific expression, or causal regulatory variants. A/F/C/P directions therefore define recurrence of this prespecified transcript-state representation. Candidate-selected studies and the standardized protocol answer related but non-identical questions, so disagreement shows a change in identified replay under observation scale rather than proof that either regime uniquely recovers the “true” mechanism.

All five systems were quantified against one annotation-informative *C. sinensis* RefSeq. Using one reference prevents outcome-dependent reference switching and produced high mapping rates in all admitted systems, but it can still miss species-specific paralogs or create differential mappability. Accordingly, our cross-system claims are at the gene-family/module level, not exact ortholog or paralog equivalence across species. Species-native genomes and metabolite, protein, or enzyme assays are important future sensitivities where comparable resources exist.

The raw workflows also use frozen read-prefix depths rather than full-depth differential-expression inference. Prefix depth and contrasts were fixed before outcomes, read integrity and fallback routes were audited, and module directions were not selected by significance. The present claims are therefore restricted to the reproducible fixed-depth observation regime. Full-depth and depth-sensitivity analyses remain useful robustness tests for precision and direction stability rather than hidden evidence that is being outcome-selected here.

## Implications for flower-colour variation through time

A useful hierarchy emerges. First, ask whether a visible state can be generated. Second, ask whether independent origins replay the same complete molecular transition or only selected modules. Third, ask which generated states establish and persist across the phylogeny. Finally, require robust historical event identity before attaching ecological causes to individual branches.

Under this hierarchy, *Camellia* flower-colour evolution is neither fully deterministic nor unconstrained. Complete pigment programmes are not repeatedly recovered, but selected modules recur; the degree of reuse differs between anthocyanin gain and yellow development; and realised visible states remain locally phylogenetically structured. The temporal structure of flower-colour variation is therefore best described as repeated generation with partial mechanistic replay, followed by a separate filter of macroevolutionary persistence."""

CONCLUSIONS = """# CONCLUSIONS

Flower-colour variation is repeatedly generated through evolutionary time, but repeated visible states need not replay one complete molecular programme. In *Camellia*, standardized A/F/C/P remeasurement fixes anthocyanin whole-signature recurrence at one third, while yellow development retains stronger modular reuse through shared A-, C-, and P-axis directions. The result is not absence of repeatability; it is repeatability at a level below one invariant whole pigment-state package.

At the macro scale, realised wild colours retain topology-robust local phylogenetic structure even though individual transition branches are not robust to alternative treatment of naturally variable species. Generation, establishment/persistence, and event identity must therefore be separated. *Camellia* is useful not because one hue has one ecological meaning, but because repeated visible states, diverse molecular implementations, and contrasting pollination contexts coexist within one comparative system. The next step is to connect those stages with population-resolved measurements of molecular state, sensory phenotype, reproductive function, and environment."""

ADDITIONAL_REFS = [
    "Conte, G. L., M. E. Arnegard, C. L. Peichel, and D. Schluter. 2012. The probability of genetic parallelism and convergence in natural populations. *Proceedings of the Royal Society B: Biological Sciences* 279: 5039–5047. https://doi.org/10.1098/rspb.2012.2146",
    "Larter, M., A. Dunbar-Wallis, A. E. Berardi, and S. D. Smith. 2018. Convergent evolution at the pathway level: Predictable regulatory changes during flower color transitions. *Molecular Biology and Evolution* 35: 2159–2169. https://doi.org/10.1093/molbev/msy117",
    "Mori, S., Y. Hasegawa, and Y. Moriguchi. 2023. Color strategies of camellias recruiting different pollinators. *Phytochemistry* 207: 113559. https://doi.org/10.1016/j.phytochem.2022.113559",
    "Ng, J., and S. D. Smith. 2016. Widespread flower color convergence in Solanaceae via alternate biochemical pathways. *New Phytologist* 209: 407–417. https://doi.org/10.1111/nph.13576",
    "Revell, L. J. 2025. Ancestral state reconstruction of phenotypic characters. *Evolutionary Biology* 52: 1–25. https://doi.org/10.1007/s11692-025-09645-y",
    "Sun, S.-G., Z.-H. Huang, Z.-B. Chen, and S.-Q. Huang. 2017. Nectar properties and the role of sunbirds as pollinators of the golden-flowered tea (*Camellia petelotii*). *American Journal of Botany* 104: 468–476. https://doi.org/10.3732/ajb.1600428",
    "Wheeler, L. C., A. Dunbar-Wallis, K. Schutz, and S. D. Smith. 2023. Evolutionary walks through flower colour space driven by gene expression in *Petunia* and allies (Petunieae). *Proceedings of the Royal Society B: Biological Sciences* 290: 20230275. https://doi.org/10.1098/rspb.2023.0275",
    "Xiao, H., D. Zhang, J. Li, H. Yin, L. Chen, Z. Wang, W. Liu, and F. Geng. 2025. The molecular basis underlying phenotypic diversity in *Camellia* flower coloration and the evolution of research paradigms. *Scientia Horticulturae* 353: 114474. https://doi.org/10.1016/j.scienta.2025.114474",
]


def first_author_key(ref: str) -> str:
    return ref.split(",", 1)[0].strip().lower()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()
    text = args.source.read_text(encoding="utf-8")

    text = replace_once(text,
        "# Repeated flower-colour change does not imply repeated pigment-state packages in *Camellia*",
        "# Repeated generation of flower-colour states does not replay one pigment-state programme in *Camellia*",
        "title")
    text = replace_once(text,
        "**Running head:** Modular recurrence and flower-colour realization",
        "**Running head:** Temporal repeatability of flower colour",
        "running head")
    old_banner = "> Draft v0.2.2. The Paper 1 candidate-free and macroevolutionary results remain frozen. The literature-conditioned molecular layer was reopened after backward/forward citation chasing recovered Luo et al. (2016), which resolves the literature-side CJAPONICA F axis. This manuscript is governed by `data/paper1_authoritative_results_v0_2_2.csv`, `data/paper1_main_figure_manifest_v0_2_2.csv`, and `data/paper1_reference_registry_v0_2_2.csv`."
    new_banner = "> Draft v0.3.2 temporal framing revision. Scientific estimates remain Paper 1 v0.2.2. This framing places repeated generation and mechanistic replay through evolutionary time at the biological centre; observation-regime and event-identification analyses remain identification tools and no estimate, contrast, figure input, or inferential gate is changed here."
    text = replace_once(text, old_banner, new_banner, "banner")

    text = replace_between(text, "## ABSTRACT", "---", ABSTRACT)
    text = replace_between(text, "# INTRODUCTION", "# MATERIALS AND METHODS", INTRODUCTION)
    text = replace_between(text, "# DISCUSSION", "# CONCLUSIONS", DISCUSSION)
    text = replace_between(text, "# CONCLUSIONS", "# DATA AVAILABILITY AND REPRODUCIBILITY", CONCLUSIONS)

    marker = "# LITERATURE CITED\n\n"
    if text.count(marker) != 1:
        raise SystemExit("literature marker drift")
    pre, rest = text.split(marker, 1)
    next_head = rest.find("\n# ")
    if next_head < 0:
        refs_text, post = rest, ""
    else:
        refs_text, post = rest[:next_head], rest[next_head:]
    refs = [x.strip() for x in refs_text.strip().split("\n\n") if x.strip()]
    existing = {x.rsplit("https://doi.org/", 1)[-1].strip().lower() for x in refs if "https://doi.org/" in x}
    for ref in ADDITIONAL_REFS:
        doi = ref.rsplit("https://doi.org/", 1)[-1].strip().lower()
        if doi not in existing:
            refs.append(ref)
            existing.add(doi)
    refs.sort(key=first_author_key)
    text = pre + marker + "\n\n".join(refs) + post

    required = [
        "Repeated generation of flower-colour states does not replay one pigment-state programme",
        "repeated generation with partial mechanistic replay",
        "P=0.078125",
        "0.333–1.0",
        "0.333–0.5",
        "0.25–1.0",
        "pairwise concordance from 0.25–1.0 to 0.75",
        "no accepted-species transition branch was robust",
        "10.3389/fpls.2015.01257",
        "10.1016/j.phytochem.2022.113559",
        "10.3732/ajb.1600428",
        "10.1098/rspb.2012.2146",
        "10.1016/j.scienta.2025.114474",
    ]
    missing = [x for x in required if x not in text]
    if missing:
        raise SystemExit(f"temporal framing missing required tokens: {missing}")

    forbidden = [
        "anthocyanin enrichment detectable even after dependence collapse",
        "A-specific ascertainment remains significant after dependence collapse",
        "A/F/C/P coverage = 9/4/1/3",
        "coverage was 5/3/1/2",
    ]
    retained = [x for x in forbidden if x in text]
    if retained:
        raise SystemExit(f"temporal framing retained superseded claims: {retained}")

    frozen = [
        "46 of 50 nontrivial splits were shared and normalized RF distance was 0.08",
        "strict P=0.00116 and dominant P=0.000080",
        "The strict×dominant shared robust event count was therefore zero",
        "Candidate-free measurement point-identified exact-signature recurrence at **0.5** and pairwise concordance at **0.75**",
    ]
    lost = [x for x in frozen if x not in text]
    if lost:
        raise SystemExit(f"temporal framing lost frozen science tokens: {lost}")

    abstract_text = ABSTRACT.split("**Key words:**", 1)[0]
    wc = len(re.findall(r"\b[\w’'-]+\b", abstract_text))
    if wc > 250:
        raise SystemExit(f"abstract exceeds 250 words: {wc}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text.rstrip() + "\n", encoding="utf-8")
    summary = {
        "document_version": "Paper 1 framing v0.3.2",
        "source_science_version": "Paper 1 v0.2.2",
        "biological_headline": "repeated generation through evolutionary time and partial mechanistic replay",
        "model_system": "Camellia",
        "observation_role": "identification strategy, not biological headline",
        "scientific_results_changed_by_framing": False,
        "abstract_words": wc,
        "expected_reference_contract": "v0.5 / 25 DOI rows",
        "status": "paper1 temporal framing v0.3.2 built",
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
