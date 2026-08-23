# Paper 1 ecological integration v0.1

## Why Paper 1 is reopened

The previous submission candidate correctly established molecular implementation flexibility, accepted-species wild-colour auditing, and local nearest-same-colour phylogenetic conservatism. It was too conservative, however, in treating ecological causes as wholly untestable from public data.

Ecological-driver meta-analysis v2 now separates two inferential levels:

1. **mechanism/service level** — public experiments and field gradients can quantify how strongly pollinator availability, pollen delivery and flowering-window environment affect reproduction;
2. **accepted-species event level** — current hard-state colour data still do not identify individual transition branches robust enough to assign those ecological effects as the historical cause of specific colour transitions.

Paper 1 should therefore include the ecological synthesis while retaining the branch-causation boundary.

## Revised central story

1. Similar floral pigment states are molecularly accessible through more than one implementation mode, including same-lineage reuse and paralog substitution.
2. Wild flower colour is not freely labile at macroevolutionary scale: nearest-same-colour local phylogenetic conservatism survives taxonomy, polymorphism and nuclear-topology sensitivity.
3. A universal direct `visible red/A -> cold niche` model is not supported, and visible hue is not a deterministic pollinator-functional state.
4. Ecological experiments nevertheless show strong reproductive filtering. Across three independent A/Y/W *Camellia* species, bird access increases fruit set 2.29–6.35-fold (geometric-mean RR 3.53; leave-one-out 2.64–4.39).
5. Within *C. oleifera*, independent bird-access and honey-bee-introduction experiments give a geometric-mean fruit-set RR of 2.42, while five registered pollinator-reliability gradient effects across independent studies/years all point in the expected direction.
6. Climate/season mediation is documented in five studies across four taxa, including altered phenology, pollinator visitation, pollen deposition, reward and pollination benefit.
7. Direct abiotic floral-pigment experiments are much thinner: one admitted cold+dark floral experiment is confounded and cannot support a comparable meta-analysis.
8. Accepted-species transition branches remain unidentifiable across strict and dominant wild-colour scenarios, so service-level ecological support must not be promoted to historical branch-specific causation.

The resulting model is:

`molecular accessibility -> latent pigment/spectral/reward state -> flowering-window environment + pollinator availability/effectiveness -> reproductive success -> evolutionary persistence`

The evidence is strongest for molecular accessibility, local macro pattern, and the ecological service/reliability middle of this chain. Historical alignment of those ecological effects with individual colour-transition events remains unresolved.

## Frozen quantitative ecological results

### Cross-species pollinator-service magnitude

- *C. japonica* (A): RR 6.35
- *C. petelotii* (Y): RR 3.04
- *C. oleifera* (W): RR 2.29
- equal-weight geometric mean RR: **3.53**
- leave-one-out range: **2.64–4.39**
- formal inverse-variance random-effects pooling: **not performed**, because defensible sampling variances remain unavailable for all three independent primary effects.

### *C. oleifera* within-species replication

- bird access vs exclusion: RR **2.29**
- independent *Apis cerana* cage introduction vs no-bee cage: RR **2.56**
- geometric mean across the two independent studies: **2.42**
- secondary open-field contrast in the honey-bee study: RR **4.31**, retained as same-study sensitivity rather than a third independent effect.

### Pollinator reliability gradients

Five registered effects all have the direction predicted by service limitation:

- Xie et al. 2013: pollen limitation decreases with legitimate *Andrena* visit density;
- Li et al. 2021: wild-bee abundance positively predicts fruit set in 2018 and 2019;
- Li et al. 2021: fruit set decreases with distance from a wild-bee nesting aggregation in 2018 and 2019.

The coefficients are not pooled because their scales and response definitions differ.

### Pollen limitation

*C. pubipetala* supplemental vs open fruit set:

- RR **3.50**
- SE(lnRR) **0.586**
- approximate 95% RR interval **1.11–11.03**

*C. petelotii* instead shows no detectable pollen-supplementation effect despite a large bird-exclusion effect. This is evidence that pollinator contribution and realized pollen limitation are related but not interchangeable.

### Climate / season mediation

Five studies across four taxa are admitted as explicit mediation evidence:

- *C. hainanica*: cooler transplant delayed anthesis 45 d, pollinator visits -92%, pollen deposition -57%, natural fruit set 0 while hand cross still produced fruit;
- *C. perpetua*: winter/summer nectar RR 3.51 and sucrose:hexose RR 7.11 with stronger winter bird/reproductive weighting;
- *C. petelotii*: bee visitation decreases in cloudy/rainy weather;
- *C. oleifera*: natural pollination has a higher flowering-temperature threshold than artificial pollination in long-term observations, and honey-bee benefits vary among years/weather.

These outcomes remain a structured triangulation rather than one pooled effect size.

### Direct abiotic floral pigment

Only one admitted flower-specific manipulation is currently available. In *C. japonica*, anthocyanin declined after 6 and 8 weeks of 7 C dark storage, but temperature and darkness are confounded. Leaf-only tea studies are excluded from the floral effect family.

## Manuscript edits required

### Abstract

Add the ecological synthesis explicitly. Do not say ecological causes are simply untestable. State instead that pollinator-service/reliability and climate/season mediation are quantitatively supported at the mechanism/service level, whereas assignment to individual accepted-species colour-transition branches is not identifiable.

### Introduction

The fourth question should become two nested questions:

- which ecological processes show repeatable quantitative effects on reproductive performance?
- can those processes be assigned to individual macroevolutionary colour-transition events?

### Methods

Replace the current purely categorical pollination-screening paragraph with an ecological-driver synthesis section that:

- keeps response families separate;
- uses lnRR for commensurable fruit-set contrasts;
- distinguishes independent species from repeated studies within one species;
- reconstructs binomial lnRR variance only when raw event counts are available;
- treats heterogeneous regression coefficients and climate/season effects as structured triangulation rather than pooled effects;
- excludes leaf-only pigment experiments from floral-pigment pooling.

### Results

Add one primary ecological subsection after macro colour conservatism:

**Ecological filtering has large reproductive effects but is not hue specific.**

Headline values are cross-species RR 3.53, *C. oleifera* replicated RR 2.42, 5/5 reliability gradients in the expected direction, and four taxa with climate/season mediation evidence.

### Discussion

Revise the previous `PUBLIC-DATA BOUNDARY` argument. The boundary is now narrower:

- public data **can** test ecological service/reliability mechanisms quantitatively;
- public data **cannot yet** robustly connect those mechanisms to particular accepted-species colour-transition branches.

This strengthens, rather than removes, the empirical handoff: population-level studies are needed to connect sensory/pigment states, pollinator service, weather, fitness and paralog-specific expression within naturally variable lineages.

## Figure plan

Retain Fig 1–5. Revise Fig 6:

- **Fig 6A — cross-species pollinator-service magnitude:** three A/Y/W fruit-set RRs and geometric mean 3.53;
- **Fig 6B — ecological triangulation:** *C. oleifera* repeated service experiments + reliability gradients + climate/season-mediated systems;
- **Fig 6C — causal boundary:** mechanism/service level supported; accepted-species branch-specific causation remains unidentifiable; direct abiotic floral-pigment evidence remains under-replicated.

Move the old detailed strict/dominant event-count panel to Supporting Information while retaining the zero-shared-event statement in Fig 6C and the text.

## Submission status

The previous AJB bundle remains a reproducible provisional snapshot, not the final Paper 1 submission. Final submission packaging should resume only after this ecological integration is propagated through the manuscript, figure registry, Supplement and claim-drift gates.
