# White-baseline cross-clade flower-colour atlas — Phase 1 v0.1

## Status

Post-Paper-1 programme development only. This document does not modify `chun` Paper 1 science v0.2.2, framing v0.3.4 or AJB v1.0.

The first literature-admission screen is complete enough to justify a real cross-clade atlas. The harmonized row-level registry is `data/white_baseline_cross_clade_atlas_v0_1.csv`.

## Question

> Across clades with a defensible white-like or low-visible-pigment ancestral state, are repeated derived colour states generated through common functional molecular modules, and is the set of molecularly accessible states broader than the states that persist over macroevolutionary time?

The atlas is not a vote-counting review. The intended original contribution is a rebuilt comparative measurement layer: ancestral-state uncertainty, visible-colour coding, transition classes, current polymorphism and molecular functional modules are harmonized under one protocol.

## Phase-1 screen

### White-like / low-pigment candidates

1. **Camellia — anchor.** Independent genus-scale reconstruction supports white as the ancestral visible state (`10.1111/pbi.70442`). It already has the strongest public molecular and ecological layer and remains the calibration system, not the sole target.

2. **Epimedium sect. Diphyllon — strongest second mechanistic anchor.** Inner-sepal colour is reconstructed as white plesiomorphic, followed by repeated diversification to yellow, red, pink and purple (`10.3389/fpls.2023.1234148`). An independent eight-species study quantified anthocyanidins and expression/function of anthocyanin-pathway genes, finding convergent regulatory reduction of DFR/ANS in multiple loss-of-pigmentation species (`10.3389/fpls.2023.1133616`). This is the best immediate external test of whether `Camellia`-style hierarchical repeatability generalizes.

3. **Linoideae / Linum s.l. — strongest dated macro anchor.** A 112-species reconstruction supports a yellow-white deep ancestral state, with purple arising earlier and blue/red/pink later (`10.3390/plants11121579`). The macro history is unusually useful; the limiting layer is wild cross-species floral molecular data.

4. **Hydrangea sect. Cornidia — transition-rich macro replication.** White is reconstructed as ancestral, but subsequent dynamics are not a simple one-way white-to-colour radiation. Stochastic reconstructions estimate many transitions, with red-to-white more frequent than white-to-red (`10.3389/fpls.2021.661522`). This is a critical falsification case: a white ancestor does not automatically imply persistent directional pigment gain.

5. **Polygonatum / sect. Verticillata — promising bridge to current colour variation.** Recent colour-focused work reconstructs a white ancestral state for the diversified Verticillata context and identifies white as ancestral among sampled *P. kingianum* colour phenotypes (`10.1186/s12870-025-07147-9`). A strong phylogenomic backbone exists (`10.1016/j.ympev.2022.107431`), but the colour reconstruction needs an independent re-analysis before promotion because the newest study has limited colour-phenotype sampling.

6. **Angraecinae / Angraecum — low-complexity control.** White is symplesiomorphic and green evolved repeatedly (`10.1371/journal.pone.0163194`). It is useful as a binary control for gain/loss asymmetry, not as a full rainbow-radiation system.

7. **Nicotiana — complex-node control.** Some internal ancestral nodes are reconstructed as white and spectral colour states arose repeatedly (`10.1093/aob/mcv048`), but hybridization and polyploidy are central. It should not be labelled a simple white-root radiation; instead it tests whether reticulation changes the accessibility-realization relationship.

### Coloured-ancestor / non-white controls

- **Iochrominae** — ancestral delphinidin/blue context with four independent pigment losses and a 28-species pigment + seven-gene expression dataset (`10.1093/molbev/msy117`). Best positive molecular-convergence control.
- **Antirrhineae** — transition/polymorphism control rather than a white-root admission system. The 369-species colour survey and 169-taxon phylogeny already connect extant polymorphism to long-term transition structure (`10.1093/aob/mcw043`).
- **Iris** — highly labile coloured-ancestor system with extensive intraspecific colour variation (`10.3389/fpls.2020.569811`).
- **Mimulus / Erythranthe** — incipient-transition control. Two independently evolved yellow morphs within ancestrally red hummingbird-pollinated species have pigment, transcriptomic/genomic and bumblebee-response data in parallel (`10.1038/s41467-025-57639-3`).

## First substantive result from the screen

The atlas should **not** preregister a universal `white ancestor -> repeated colour gains` directional conclusion.

There are already two competing empirical patterns:

- broad comparative work has found gain/loss asymmetries that can favour anthocyanin gains in some clades;
- within Hydrangea sect. Cornidia, a white ancestral state coexists with later transition dynamics dominated by returns to white.

Therefore the valid question is whether ancestral baseline changes the **distribution of transition rates and molecular routes**, not whether gains must dominate.

This makes the cross-clade study stronger: the white-baseline hypothesis is falsifiable rather than built into taxon selection.

## Common molecular ontology

Literal `A/F/C/P` cannot be forced across all clades because yellow pigmentation may be carotenoid-, aurone-, chalcone- or other flavonoid-based. The cross-clade layer will use hierarchical functional modules:

1. `ANTHOCYANIN_DEPLOYMENT` — production and floral deployment of anthocyanins;
2. `COPIGMENT_FLAVONOL` — flavonol/copigment branch and precursor competition;
3. `YELLOW_PIGMENT` — typed subtype (`CAROTENOID`, `AURONE`, `CHALCONE_FLAVONOID`, `OTHER`);
4. `SHARED_FLUX_DIVERSION` — proanthocyanidin or clade-appropriate competing sink;
5. `REGULATORY_STATE` — transcriptional activation/suppression versus structural loss where evidence permits;
6. `SENSORY_STATE` — UV/visible/fluorescence coordinates where available.

Camellia A/F/C/P maps into this ontology but does not define it.

## Admission verdict

The **macro literature-admission gate is provisionally passed**: at least three independent white-like ancestral clades and at least two coloured/non-white controls have explicit phylogenetic colour reconstructions.

This is not yet the pooled-analysis gate. Before modelling, each admitted clade must pass raw-source ingestion:

- recover the original terminal colour matrix or rebuild it taxon-by-taxon;
- obtain a current/pinned phylogeny and record topology uncertainty;
- reproduce the ancestral-state result under a common model set (ER/SYM/ARD where identifiable, plus stochastic mapping or posterior sensitivity);
- distinguish wild states, cultivars and within-species polymorphism;
- record missing tips rather than imputing colour;
- count transition direction from posterior histories rather than one maximum-likelihood painted tree where possible.

## Priority order for actual ingestion

1. **Epimedium** — highest information gain because both macro parallelism and multi-species molecular mechanism already exist.
2. **Antirrhineae** — open colour matrix/phylogeny and direct temporal-spatial bridge; Issue #150 controls its admission.
3. **Linoideae** — large, dated macro matrix; tests timing of colour acquisition.
4. **Hydrangea sect. Cornidia** — strongest falsification case for simple directional gain.
5. **Iochrominae** — coloured-ancestor positive molecular control.
6. **Polygonatum** — promote only after independent colour-state reconstruction is reproduced.

## What counts as original data here

The original data product is the harmonized comparative measurement itself. Public source observations are re-coded under one trait ontology and one uncertainty protocol, phylogenetic histories are re-estimated rather than copied as conclusions, and molecular evidence is mapped to common functional modules. This is a new derived dataset and a new comparative test even though the raw sequences and taxonomic observations are public.

## Next executable gate

Build `v0.2` by ingesting the source matrices for the first four systems (Epimedium, Antirrhineae, Linoideae, Hydrangea-Cornidia). Promotion requires at least three clades with reproducible terminal colour coding and transition posteriors; molecular pooling remains separate until at least three independent clades have auditable functional-module measurements.
