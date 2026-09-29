# Flower-colour variation through evolutionary time

## Program-level position

`chun` is the **evolutionary-time arm** of a broader research programme on the spatiotemporal organization of flower-colour variation.

The umbrella question is:

> **How is flower-colour variation organized, retained and transformed across evolutionary time and geographic space?**

The programme now has two deliberately parallel axes:

- **`chun` — evolutionary time:** how long flower-colour identity retains lineage history as lineages diverge, at what phenotypic resolution that history is expressed, and whether broad phenotype classes can contain finer hidden history;
- **`fcp` — geographic space:** how within-species flower-colour variation is organized geographically, from local coexistence and neighbourhood structure to differentiation among populations.

The shared empirical architecture is:

> **Local or lineage-conditioned structure is recurrent, while one universal global template is not supported.**

This is a programme-level synthesis, not a claim that the two repositories share a dataset, statistical model or inferential unit.

## Two temporal layers inside CHUN

The repository contains two distinct but complementary temporal questions.

### Layer 1 — mechanistic generation in Camellia

The current Camellia Paper 1 asks whether repeated visible flower-colour change replays the same molecular transition.

Its central result remains bounded:

> **Repeated visible flower-colour change does not require replay of one invariant complete pigment-state programme; molecular repeatability is modular and transition-class dependent.**

This layer separates mechanistic accessibility, observation regime, realized lineage pattern and historical-event identity.

### Layer 2 — cross-radiation temporal memory

The Evolution Letters programme asks a different question:

> **As lineages diverge, how long does flower-colour identity retain evolutionary history, and is there one phenotypic resolution at which that history is universally strongest?**

The current frozen v0.3 answer is:

> **Exact visible flower-colour memory generally decays with relative evolutionary divergence, but the phenotypic scale carrying that memory is radiation-specific rather than universal.**

The post-v0.3 hierarchical-memory extension adds:

> **Fine flower-colour states can retain lineage history inside broader phenotype classes; this hidden history is recurrent in visible colour, not a trivial state-compression artifact, but not universal across all phenotype representations.**

The two temporal layers must not be pooled statistically. Paper 1 concerns mechanistic recurrence in Camellia; the cross-radiation programme concerns temporal retention, phenotype resolution and nested lineage history across radiations.

## Current cross-radiation evidence

The temporal-memory programme is broadly triangulated but not biologically exhaustive.

### Standardized visible-colour frame

From the predefined Flower-clades-51 source:

- 32 clades are eligible for direct fine-colour temporal-persistence analysis;
- 28 complete the standardized three-resolution profile;
- 21 have genuine fine-to-coarse opportunity for hidden-memory analysis;
- ineligible or insufficient-state clades remain HOLD rather than being rescued after outcomes are known.

### Prospective falsification of a universal scale

The preregistered Iris intermediate-resolution prediction failed.

Across the 28 completed standardized clades, coarse, fine, tied and no-signal profiles all occur, with zero unique intermediate winners.

Four simple pre-outcome tree-geometry predictors fail qualification.

The supported conclusion is therefore not that another phenotype scale replaces the intermediate scale universally; it is that **no single privileged resolution is supported across radiations**.

### Temporal decay

Among 32 eligible visible-colour clades:

- 23/32 have negative excess-retention slopes;
- median slope = -0.1897;
- 23/32 have positive integrated excess-retention area.

Thus exact visible flower colour generally retains more excess similarity among shallower relatives and loses that excess with increasing relative divergence depth.

The time axis is relative phylogenetic depth, not calibrated absolute time.

### Hidden within-coarse history

Among 21 radiations with genuine fine-to-coarse opportunity:

- 18/21 hidden-memory effects are positive;
- median centered effect = +0.0270 AUC;
- one-sided Wilcoxon P = 3.34e-5;
- sign-test P = 7.45e-4.

A frozen structural prediction that more state collision should mechanically create stronger hidden memory is not supported:

- rho = -0.2571;
- permutation P = 0.26023;
- all 21 leave-one-clade-out correlations are negative.

Hidden history is therefore not explained by the trivial amount of phenotype compression.

### Independent prospective and cross-representation tests

The independent prospective Schistanthe visible-colour test passes:

- 129 retained tips;
- centered effect = +0.06416 AUC;
- P = 0.0033.

Biochemical evidence is mixed:

- Petunieae retrospective: +0.18794 AUC, P = 0.0001;
- Gesnerioideae prospective: -0.00779 AUC, P = 0.5005, frozen FAIL;
- Ruellia remains outcome-unopened because the authoritative author-used tree is unavailable.

Linoideae, Angraecinae and Antirrhineae provide three additional independent source-specific qualitative concordances for finer organization conditional on coarser states, but their statistics and phenotype dimensions are not pooled with the standardized AUC frame.

## What is and is not comprehensive

The temporal programme is comparatively broad with respect to inferential failure modes. It has directly tested:

1. a proposed universal resolution optimum;
2. temporal decay of exact colour memory;
3. heterogeneity in the phenotype scale carrying memory;
4. hidden history inside coarse phenotype classes;
5. the trivial compression-artifact explanation;
6. equivalence between global signal and hidden organization;
7. equivalence between hidden memory and a global fine-resolution advantage;
8. prospective transport to an independent visible-colour radiation;
9. cross-representation generalization;
10. explicit negative, FAIL and HOLD outcomes.

It is **not** exhaustive in the biological sampling sense. It does not provide:

- a random or complete census of angiosperm radiations;
- full coverage of spectra, pigments, regulatory states and developmental modules;
- a calibrated absolute-time decay law shared across clades;
- an identified ecological cause of memory decay;
- an identified developmental or molecular cause of hidden-memory realization;
- a direct harmonized link from macroevolutionary temporal memory to contemporary population-level spatial sorting.

The source-first replacement search was intentionally stopped under a frozen candidate budget rather than becoming an open-ended search. That reduces selection bias; it does not make the taxonomic sample exhaustive.

See `docs/TEMPORAL_PROGRAM_COVERAGE_AND_FCP_SISTER_V0_1.md` for the explicit coverage audit.

## Relation to FCP: the spatial sister arm

The companion `fcp` project is the geographic-space arm.

The strongest sister-paper symmetry is now:

| Research axis | `chun` — evolutionary time | `fcp` — geographic space |
|---|---|---|
| Coordinate | relative evolutionary divergence | geographic separation / neighbourhood |
| Local structure | recent relatives retain excess colour similarity | nearby observations can retain excess colour similarity |
| Heterogeneity | memory strength and carrying resolution differ among radiations | spatial organization and transition geography differ among species |
| Universal-template test | no universal privileged phenotype resolution | no confirmed universal global transition boundary |
| Nested/local structure | fine lineage history can remain inside coarse phenotype classes | within-species variation can be locally structured without one shared global map |
| Current causal gap | why memory decays and why hidden history is realized | why variation is locally maintained or geographically sorted |

The programme-level principle is therefore:

> **Flower-colour variation is structured in both evolutionary time and geographic space, but the form of that structure is context dependent rather than governed by one universal scale or map.**

In the time arm, “local” means phylogenetic proximity or lineage-conditioned state space. In the space arm, “local” means geographic neighbourhood or within-species spatial configuration.

The parallel is biological and conceptual, not statistical.

## Why the time-space pairing matters

The pairing changes the overarching question from “what causes flower colour?” to:

> **How does phenotypic variation retain structure while being reorganized across two fundamental coordinates: evolutionary divergence and geographic separation?**

That exposes a general distinction between **structure** and **template**.

A trait can be non-randomly organized without all lineages sharing the same evolutionary resolution, and within-species variation can be non-randomly organized without all species sharing the same geographic boundary.

This suggests a broader candidate principle:

> **Phenotypic organization can be recurrent without being universally templated.**

The current evidence supports that statement separately in time and space. It does not yet establish one common mechanism linking the two.

## The next genuinely integrative test

The clean next synthesis is not another retrospective moderator search.

A future harmonized study should freeze a lineage property before outcomes are opened and ask whether it predicts both:

1. **faster or slower loss of flower-colour memory through evolutionary divergence**, and
2. **stronger or weaker contemporary geographic turnover or spatial sorting within species**.

Possible biological predictors include pollinator turnover, environmental heterogeneity, mating system, dispersal/gene flow and developmental accessibility, but none is currently established.

That prospective test would convert the present sister-paper symmetry into a direct spatiotemporal ecological hypothesis.

## Terminology

Use **flower-colour variation** as the umbrella term across the programme.

Reserve **flower-colour polymorphism** for documented within-population coexistence of discrete colour variants.

Use **temporal memory** for lineage-conditioned excess similarity through relative evolutionary divergence.

Use **hidden memory** only for additional fine-state lineage organization after coarse phenotype membership is held fixed.

## Claim boundaries

Do not claim:

- that the 51-clade source is an exhaustive sample of flowering plants;
- that one phenotype resolution is universally optimal;
- that hidden memory is universal across all phenotype representations;
- that one ecological mechanism causes temporal memory decay;
- that the same mechanism causes both CHUN temporal structure and FCP spatial structure;
- that temporal memory predicts FCP spatial sorting in the current separate datasets;
- that `chun` and `fcp` estimate the same parameter or constitute one pooled analysis;
- that post-v0.3 hierarchical-memory results are already part of frozen Evolution Letters v0.3.

## Governance

- Frozen Evolution Letters v0.3 science remains unchanged.
- Post-v0.3 hierarchical-memory work remains an extension.
- Camellia Paper 1 science remains unchanged.
- FCP science remains unchanged.
- This document updates programme-level framing only.
