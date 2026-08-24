# Paper core after accessibility, ascertainment and nuclear-realization audits

## Central question

Where does predictability break between short-timescale floral pigment feasibility, recurrent molecular mechanism, and long-term evolutionary realization in *Camellia*?

The paper separates four empirically distinct layers:

1. **demonstrated feasibility** — a state change can occur within genotype, development, bud sport, or a close cultivar system;
2. **mechanistic recurrence** — independent systems reuse the same multivariate A/F/C/P transition package;
3. **macroevolutionary realization pattern** — states are locally clustered or broadly distributed across accepted-species nuclear history;
4. **persistence/filtering** — ecology, mating system, lineage history, introgression or other processes affect establishment, retention or loss after a feasible state is generated.

The observation process is treated explicitly because published systems resolve pigment axes unevenly.

## H1 — substantial flower-colour changes are demonstrably feasible on short timescales

### Current status: supported as an existence-level statement

Multiple within-genotype, developmental and close-cultivar systems demonstrate that substantial visible colour changes can be generated without deep phylogenetic divergence or wholesale pathway deletion.

### Boundary

The literature does not provide a standardized denominator of perturbations, so it does not estimate a natural generation probability or a variational-bias distribution.

## H2 — independent systems repeatedly reuse the same multivariate molecular transition package

### Current status: not point-identified from the published mechanistic matrix

Observed literature-coded results:

- biological-system sensitivity: recurrence score 0.220, permutation P approximately 0.084;
- dependence-collapsed literal-signature result: recurrence score 0.200, P = 1.0.

However, dependence collapse leaves **10 unresolved A/F/C/P cluster-axis cells**. Exact completion over `up/down/same` yields 59,049 admissible completion patterns and a recurrence identified set of **0.20–0.36**.

Therefore the correct result is not `recurrence absent`; it is:

> **the published literature does not currently point-identify dependence-aware multivariate mechanistic recurrence.**

### Observation-process diagnosis

The published mechanistic matrix resolves axes unevenly at biological-system level:

- A: 8/10 systems;
- F: 4/10;
- C: 1/10;
- P: 3/10.

Conditional on the exact number of resolved axes in every system, exact enumeration of 5,308,416 axis-symmetric assignments gives:

- exact P for A-axis enrichment = **0.0083618164**;
- exact P for any axis imbalance at least as large as observed = **0.0239483869**.

After collapsing to five dependence clusters, A enrichment weakens to P = **0.140625**.

Thus repeated study of a few anthocyanin-focused systems contributes strongly to the apparent system-level narrative.

### Identification experiment

Candidate-free public RNA-seq reanalysis applies one predefined branch-specific A/F/C/P observation protocol to the same public raw datasets. It is designed to reduce within-system candidate-axis ascertainment and shrink the missing-axis identified set without outcome-directed imputation.

H2 is strengthened only if recurrent signatures emerge after this standardized observation protocol and dependence collapse.

## H3 — all demonstrably feasible states share the same macroevolutionary realization pattern

### Current status: rejected at the root-independent nuclear pattern level

The primary macro evidence is no longer traditional-section concentration. It is accepted-species wild-colour clustering on two public nuclear topology pipelines:

1. WFO55 FastTree gene trees -> ASTRAL;
2. WFO53 IQ-TREE LG+G4 + 1000 UFBoot gene trees -> ASTRAL-IV.

Both use 100,000 count-preserving label permutations and unrooted topology distances.

### Global local-conservatism result

Nearest-same-state phylogenetic distance is shorter than null under both trait scenarios and both topologies:

- FastTree strict P = **0.00212**;
- FastTree dominant P < **1e-5**;
- UFBoot strict P = **0.00116**;
- UFBoot dominant P = **0.0000800**.

Thus a reproducible local phylogenetic pattern exists even though individual transitions are not robustly identifiable.

### State-specific result

- **Y:** clustered under strict and dominant coding on both nuclear topologies; this is the strongest state-specific macro pattern.
- **A:** clustered on both topologies only under dominant-colour sensitivity; strict A is a singleton and cannot be tested.
- **W:** not individually clustered under either trait scenario on either topology.

Therefore A/W/Y can all be demonstrably generated on short timescales, yet they do not share one accepted-species nuclear realization pattern.

### Pattern-versus-event boundary

Accepted-species branch-transition analysis gives:

- strict wild scenario: zero strong robust branches;
- dominant scenario: one W->A candidate branch;
- strict × dominant cross-scenario gate: **zero robust accepted-species transitions**.

The macro result is therefore a **pattern without identifiable events**. No branch-specific molecular, climate or pollinator cause is assigned.

### Supplementary sensitivity

The Fan 2026 traditional-section count-controlled result remains supplementary only:

- A breadth gap approximately 0.582;
- Y approximately 0.503;
- W approximately 0.036.

It is not used as a substitute for the nuclear topology result.

## H4 — ecology acts primarily as a conditional reproductive-service/persistence filter rather than a deterministic hue generator

### Current status: supported at reproductive-service level, not at branch-causal level

The ecological meta-analysis supports large and repeatable reproductive-service effects and climate/season mediation, while rejecting deterministic coarse-hue rules such as universal `red -> bird`.

The strongest current causal chain is:

`molecular feasibility -> latent pigment/spectral/reward phenotype -> flowering-window environment + pollinator availability/effectiveness -> reproductive success -> persistence`.

### Boundary

Accepted-species branch-specific colour-transition causes remain unidentifiable. Ecology cannot yet be assigned as the cause of individual macroevolutionary colour changes.

## Primary novelty claim that survives current prior-art audit

Do not claim novelty for any of the following in isolation:

- developmental or mutational bias can shape macroevolution;
- flower-colour pathways constrain transitions;
- spontaneous variation differs from fixed substitutions;
- candidate-gene literature is biased;
- public flower-colour RNA-seq can be reanalysed.

All have substantial precedent.

The current strongest novelty target is the integrated identification framework:

> **In a conserved floral metabolic network, demonstrated feasibility, multivariate mechanistic recurrence, the literature observation process, and root-independent macroevolutionary realization are separately measured rather than treated as one `accessibility` quantity. Missing mechanistic axes are partially identified rather than outcome-imputed, and the observation process is then standardized with a frozen multi-pigment raw-RNA-seq protocol to test how the identified mechanistic state space changes.**

This is paired with a second distinction:

> **a macroevolutionary pattern can be robustly identifiable even when the individual historical events and their causes are not.**

The current nuclear tree already supplies that pattern-without-events result.

## Decisive next result

The candidate-free RNA-seq layer determines whether the H2 identification failure is mostly observational or biological:

- **identified set contracts toward repeated signatures:** heterogeneous candidate measurement obscured real mechanistic convergence;
- **identified set contracts toward distinct signatures:** short-timescale colour lability is genuinely mechanistically heterogeneous;
- **A remains disproportionately recurrent after uniform A/F/C/P quantification:** anthocyanin dominance survives ascertainment correction;
- **F/C/P become comparably recurrent:** the published anthocyanin-centric narrative was partly an observation-process artifact.

The Joy Kendrick red/pink within-genotype pilot is the first real-data test of this observation-standardization layer. Its expected biological direction is deliberately not encoded as a CI pass condition.
