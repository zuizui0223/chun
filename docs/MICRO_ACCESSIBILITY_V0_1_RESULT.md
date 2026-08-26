# Micro-accessibility v0.1 — dependence-aware null-model result

## Question

Do independent short-timescale *Camellia* systems repeatedly use the same multivariate pigment-pathway change package, beyond the marginal frequency of changes on A/F/C/P axes?

## Dependence structure

The expanded seed registry contains **10 biological systems** but only **5 broader dependence clusters** after grouping repeated studies from the same focal taxon/system:

- `CJAPONICA` — 3 systems;
- `CRETICULATA` — 3 systems;
- `CNITIDISSIMA` — 2 systems;
- `CSIN_WHITE_PINK` — 1 system;
- `CPERPETUA` — 1 system.

Repeated *C. japonica*, *C. reticulata* or *C. nitidissima* experiments are therefore retained as system-level sensitivities but not treated as independent macroevolutionary replicates.

## System-level recurrence sensitivity

Across all 10 biological systems, the observed mechanistic-signature recurrence score is **0.2200**.

A 10,000-permutation null independently shuffles A/F/C/P directional labels across systems while preserving each axis' marginal frequencies:

- observed recurrence = **0.2200**;
- null mean = **0.1531**;
- null SD = **0.0313**;
- z = **2.13**;
- upper-tail permutation P = **0.0840**.

This is suggestive only and ignores broader taxonomic dependence.

## Dependence-collapsed observed recurrence

Within each dependence cluster, an axis is coded as the common known direction when studies agree, `unknown` when no study resolves it, and `mixed` when known member studies conflict.

With literal `unknown` labels retained, all five observed cluster signatures differ:

- observed recurrence = **0.2000**;
- null mean = **0.2031**;
- null SD = **0.0155**;
- z = **-0.20**;
- upper-tail permutation P = **1.000**.

This means the **observed literature-coded signatures** do not show dependence-aware recurrence. It does **not** prove that the complete underlying mechanistic signatures are all different, because unmeasured axes remain unresolved.

The separate exact partial-identification analysis (`docs/MICRO_RECURRENCE_PARTIAL_IDENTIFICATION_V0_1.md`) shows that after allowing the 10 unresolved cluster-axis cells to take any `up/down/same` value, the recurrence identified set is **0.20–0.36**. Thus multivariate recurrence is currently not point-identified from the published evidence.

## Mechanistic-axis ascertainment bias

The literature-coded systems do not resolve all pigment axes equally often. Across the 10 systems, the number with a non-`unknown` call is:

- A / anthocyanin = **8**;
- F / flavonol = **4**;
- C / carotenoid = **1**;
- P / proanthocyanidin = **3**.

The ascertainment null conditions on the exact number of resolved axes in every biological system. Instead of Monte Carlo randomization, all **5,308,416** axis-symmetric assignments compatible with those row-wise coverage counts are enumerated exactly by dynamic programming.

Observed system-level imbalance:

- A coverage minus mean coverage of F/C/P = **5.3333**;
- exact conditional P for A enrichment = **0.0083618164**;
- observed max-minus-min coverage gap = **7**;
- exact conditional P for any axis imbalance at least this large = **0.0239483869**.

After collapsing repeated studies into five dependence clusters, coverage becomes A=4, F=3, C=1, P=2. There are only **576** exact axis-symmetric assignments under the corresponding cluster-level null:

- exact conditional P for A enrichment = **0.140625**;
- exact conditional P for an axis imbalance at least as large as observed = **0.416667**.

Therefore the anthocyanin-heavy literature matrix is not simply a property of ten exchangeable independent systems. A substantial part of the system-level signal is entangled with repeated mechanistic study of a few anthocyanin-focused focal taxa.

This does not erase the repeated directional association between redder states and anthocyanin deployment. It does mean that the current literature cannot establish that anthocyanin is uniquely recurrent relative to F/C/P without a standardized multi-axis observation protocol.

## Method correction before raw-data results

The primary candidate-free A module has been narrowed before inspection of the real RNA-seq pilot. It now measures **anthocyanin branch commitment** (`DFR`, `ANS/LDOX`, `UFGT/3GT`) rather than mixing shared flavonoid backbone genes into A.

`CHS`, `CHI`, `F3H` are retained as shared-backbone diagnostics, and `F3'H`/`F3'5'H` as hydroxylation/composition diagnostics, but neither group contributes to the primary A score. This prevents a general increase in flavonoid throughput from being misclassified as anthocyanin-specific allocation.

## Current inference

The strongest defensible conclusion is not `one molecular package repeatedly evolves` and not `all lineages use different mechanisms`.

It is:

> **The published Camellia flower-colour literature is insufficient to identify dependence-aware multivariate mechanistic recurrence because pathway axes are measured unevenly and many cluster-axis cells are missing.**

Candidate-free public RNA-seq is therefore an identification experiment: it applies one predefined branch-specific A/F/C/P observation protocol to already-public raw datasets, reduces missing-axis ambiguity without visible-colour imputation, and tests whether the identified set contracts toward recurrence or persistent heterogeneity.

## Next gate

Run the frozen candidate-free raw-data pipeline, beginning with the within-genotype *C. japonica* Joy Kendrick red/pink contrast, then propagate the same branch-specific module definitions across all five dependence clusters. Only after source/target biochemical states are sufficiently resolved should the mechanistic-state graph be activated.
