# Micro-accessibility to macroevolution audit — 2026-08-26

## Question

Does micro-accessibility predict macroevolutionary flower-colour transitions in *Camellia*?

## Verdict

**Not yet.** The project has frozen a non-circular micro predictor and established a robust macro pattern, but current public hard-state data do not identify a robust set of accepted-species transition branches on which to test prediction.

## What is demonstrated

### 1. A micro-only accessibility predictor exists

`docs/MICRO_ACCESSIBILITY_SCORE_V0_1_RESULT.md` defines `n_independent_micro_clusters` without using genus-scale transition branches, extant section concentration or macro colour-state abundance. At module level, anthocyanin-downstream has the broadest current recurrence, followed by flavonol and regulatory modules. FLS and ANS have the highest current explicit node recurrence.

This is an evidence-recurrence ranking. It is not a mutation rate, natural transition probability or fitted macro predictor.

### 2. Molecular implementation is flexible

The authoritative Paper 1 registry retains two complementary sequence-aware results:

- FLS includes a resolved same-lineage recurrence mode;
- DFR implements the same pathway module through different paralog subclasses in independent evidence clusters.

The identifiable micro claim is therefore stronger at module level than at universal exact-gene level.

### 3. Macro flower colour is locally conserved

After accepted-taxonomy normalization, wild-colour auditing and independent FastTree versus IQ-TREE/UFBoot topology sensitivity, the nearest same-colour relative is closer than expected under count-preserving random placement. The UFBoot result remains significant under both strict and dominant trait scenarios.

This is a root-independent local phylogenetic pattern. It does not identify transition direction or cause.

### 4. Accessibility does not imply macro lability

Flexible molecular routes coexist with topology-robust local colour conservatism. This supports the distinction:

`micro accessibility -> macro realization -> persistence`

The data establish that these layers should not be collapsed. They do not yet estimate the arrows between them.

## Why the prediction test stops

The accepted-species colour-history analysis yields zero transition branches shared by strict and dominant wild-colour encodings. Consequently there is no defensible response set for testing whether high-ranked micro nodes or modules are enriched on macro transition branches.

Running a branch-enrichment, climate or pollination-causation model on the current hard-state data would add model precision without restoring event identifiability.

## Claim ceiling

Supported:

- a preregisterable, micro-only accessibility ranking;
- same-lineage recurrence and paralog substitution as distinct implementation modes;
- topology-robust local wild-colour conservatism;
- a cross-scale mismatch between molecular flexibility and macro lability;
- an explicit public-data identifiability stop.

Not supported:

- preferential reuse of high-accessibility nodes/modules on natural macro transitions;
- transition or mutation probabilities;
- branch-specific molecular, climatic or pollinator causation;
- a universal accessibility hierarchy across all *Camellia* lineages.

## Reopening gate

The direct prediction test requires all of the following:

1. population-resolved wild pigment states rather than one hard hue per species;
2. accepted-species nuclear histories with topology/reticulation sensitivity;
3. transition branches stable across predeclared trait encodings;
4. a common ortholog/paralog map for macro candidates;
5. enrichment against the already frozen micro-only recurrence score, without post-hoc reweighting.

Until that gate passes, the correct conclusion is **molecularly accessible yet macroevolutionarily constrained**, not “micro-accessibility predicts macroevolutionary transition.”
