# Paper core after the accessibility audit

## Central question

Where does predictability break between short-timescale floral pigment feasibility and long-term evolutionary realization in *Camellia*?

The paper no longer treats `accessibility` as one undifferentiated quantity. It separates four empirically distinct layers:

1. **demonstrated feasibility** — a state change can occur within genotype, development, bud sport, or a close cultivar system;
2. **mechanistic recurrence** — independent systems reuse the same multivariate A/F/C/P transition package;
3. **macroevolutionary realization** — a state is distributed across historical lineage backgrounds more or less broadly than expected from its extant species count;
4. **persistence/filtering** — ecology, mating system, lineage history, introgression or other processes affect establishment, retention or loss after a feasible state is generated.

## H1 — short-timescale feasibility is recurrent

### Current status: supported as an existence-level statement

Multiple within-genotype, developmental and close-cultivar systems demonstrate that substantial visible colour changes can be generated without deep phylogenetic divergence or wholesale pathway deletion.

### Boundary

The literature does not provide a standardized denominator of perturbations, so it does not estimate a natural generation probability or a variational-bias distribution.

## H2 — the same multivariate molecular transition package is repeatedly reused

### Current status: not supported by the literature-coded dependence-aware test

- biological-system sensitivity: recurrence score 0.220, permutation P approximately 0.084;
- dependence-cluster primary test: recurrence score 0.200, P = 1.0.

Thus the current evidence cannot support a claim that one common A/F/C/P package repeatedly evolves.

### Why the test may be under-resolved

The published mechanistic matrix resolves axes unevenly:

- A: 8/10 systems;
- F: 4/10;
- C: 1/10;
- P: 3/10.

The system-level A-axis ascertainment enrichment has permutation P approximately 0.0081 and weakens after dependence collapse.

### Falsification test

Candidate-free public RNA-seq reanalysis quantifies the same predefined A/F/C/P modules in all admitted systems. H2 is strengthened only if recurrence emerges after missing-axis rescue and dependence collapse.

## H3 — feasible states are broadly realized in macroevolution

### Current status: rejected in its simple form

Using the count-controlled Fan 2026 traditional-section proxy:

- A section-breadth realization gap approximately 0.582, lower-tail P approximately 0.000020;
- Y gap approximately 0.503, P approximately 0.00130;
- W gap approximately 0.036, P approximately 0.496.

A and Y are much more concentrated across historical section backgrounds than expected from their species counts, while W is not.

Therefore:

`demonstrably feasible -> broadly realized`

is insufficient.

### Boundary

This does not identify whether the missing process is reduced gain hazard, differential persistence/loss, radiation history, introgression or ecology.

## H4 — ecology acts primarily as a conditional persistence/service filter rather than a hue generator

### Current status: supported at reproductive-service level, not at branch-causal level

The ecological meta-analysis supports large and repeatable reproductive-service effects and climate/season mediation, while rejecting deterministic coarse-hue rules such as universal `red -> bird`.

The strongest current causal chain is therefore:

`molecular feasibility -> latent pigment/spectral/reward phenotype -> flowering-window environment + pollinator availability/effectiveness -> reproductive success -> persistence`.

### Boundary

Accepted-species branch-specific colour-transition causes remain unidentifiable. Ecology cannot yet be assigned as the cause of individual macroevolutionary colour changes.

## Primary novelty claim that survives current tests

The paper should not claim that developmental accessibility shapes macroevolution in general; that idea has strong precedent.

The current defensible novelty is:

> **In a conserved floral metabolic network, demonstrated short-timescale feasibility, observed mechanistic recurrence, literature ascertainment and long-term macroevolutionary realization are not interchangeable quantities and can be empirically separated.**

The first separation is already observed: literature-coded multivariate recurrence collapses after dependence control, while macro realization is strongly restricted for A and Y despite demonstrated short-timescale feasibility.

## Decisive next result

The candidate-free RNA-seq layer determines whether the H2 failure is biological or observational:

- **recurrence appears after uniform quantification:** published candidate selection obscured a real shared multivariate transition structure;
- **recurrence remains null:** short-timescale colour lability is genuinely mechanistically heterogeneous across independent systems;
- **anthocyanin remains dominant after uniform quantification:** A-axis recurrence survives the ascertainment correction;
- **F/C/P become equally recurrent:** the published anthocyanin-centric narrative was partly an observation-process artifact.

The Joy Kendrick red/pink within-genotype pilot is the first real-data test of this layer. Its expected direction is deliberately not encoded as a CI pass condition.
