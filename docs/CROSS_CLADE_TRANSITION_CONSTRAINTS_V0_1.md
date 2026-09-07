# Cross-clade flower-colour transition constraints v0.1

## Status

Post-Paper-1 programme development. This layer converts the current cross-clade evidence into executable falsification constraints. It does **not** claim a pooled transition-rate estimate or a completed universal flower-colour law.

## Why this layer exists

The programme now contains real Epimedium source ingestion, a published Hydrangea stochastic-map QC benchmark, macroevolutionary reconstructions for several white-like systems, and an event-matched non-white Mimulus gain benchmark. Those evidence types are not yet commensurate enough for one pooled rate model, but they are sufficient to reject several over-simple formulations before further ingestion.

The machine-readable source is `data/cross_clade_transition_constraints_v0_1.csv`; `scripts/summarize_cross_clade_transition_constraints_v0_1.py` regenerates the frozen summary.

## Constraint result 1 — white ancestry does not impose one-way colour gain

Hydrangea sect. Cornidia is the decisive directionality falsification case. The published 1000-map ARD stochastic-mapping summary reports:

- RED -> WHITE = 18.011;
- PURPLE -> WHITE = 4.680;
- WHITE -> RED = 4.939;
- WHITE -> PURPLE = 1.773.

Therefore, for these four reported directions:

- coloured -> white = 22.691;
- white -> coloured = 6.712;
- return/gain ratio = 3.3806615017878427;
- share pointing toward white = 0.7717239737441758.

These are derived from the published map summary and are **not** an atlas re-estimate. They nevertheless reject a universal `white ancestor -> directional accumulation of colour` rule.

## Constraint result 2 — ancestral colour must be display-compartment specific

Epimedium cannot be encoded honestly by one ancestral whole-flower colour. The published reconstruction supports:

- inner sepals: ancestral/pleseomorphic WHITE;
- petals/spurs: ancestral/pleseomorphic YELLOW.

The same radiation therefore contains different ancestral colour states in different display compartments. Cross-clade models must preserve display organ/compartment rather than assign one scalar ancestral hue to the entire flower.

This matters directly for the white-baseline question: Epimedium is a valid white-like test for the inner-sepal display state, but not evidence for an ancestrally all-white flower.

## Constraint result 3 — regulatory-module reuse is not specific to white ancestry

The Chilean Mimulus benchmark contains three independently supported gains of petal-lobe anthocyanin from an ancestrally yellow context. All three are classified at the common ontology level as `PATHWAY_SPECIFIC_REGULATOR`, while exact genomic-region recurrence is lower (maximum 2/3) and exact-gene recurrence is not estimable under the frozen evidence.

Therefore strong module-level recurrence cannot be attributed specifically to a white-like ancestral state.

## Retained candidate rule

After those three constraints, the strongest rule still worth testing is:

> **Ancestral pigment/display state constrains the architecture of accessible transitions without fixing their direction, while evolutionary repeatability is stronger at some functional regulatory/pigment modules than at exact genes or complete implementations, and the relevant baseline is display-compartment specific.**

This is a retained cross-clade hypothesis, not yet a pooled causal estimate.

## What is newly established here

The new contribution of v0.1 is not another literature list. It is an executable decision layer that prevents three forms of claim drift:

1. a Hydrangea direction check must remain >1 for coloured-to-white / white-to-coloured under the frozen published QC numbers;
2. Epimedium inner-sepal and petal/spur ancestral states must remain different;
3. the non-white Mimulus control must retain its 3/3 module-level recurrence benchmark.

If any source coding changes, the summary must be regenerated and the affected cross-clade claim re-evaluated.

## Pooled-analysis gate

`pooled_common_rate_model_ready = false` in v0.1 because zero systems in this table yet have an atlas-generated `COMMON_REESTIMATED_TRANSITION_POSTERIOR` under a shared terminal-state/model protocol.

The next empirical gate is therefore not more broad candidate searching. It is to ingest and independently rebuild terminal states for Hydrangea sect. Cornidia or Linoideae, then estimate ER/SYM/ARD transition histories under the same protocol. Once at least three systems have common re-estimated transition posteriors, baseline effects on transition direction/rates can be tested quantitatively rather than by source-level constraints.

## Claim boundary

Supported by this layer:

- a universal white-to-colour directional rule is incompatible with the frozen Hydrangea published-map QC;
- a single whole-flower ancestral-colour code is invalid for Epimedium;
- high module-level regulatory recurrence is demonstrably possible from a non-white ancestral context.

Not supported by this layer:

- a pooled effect size of white-like ancestry;
- a universal gain/loss ratio across angiosperms;
- independent historical counts for Epimedium A- endpoints;
- an exact Camellia transition count;
- a causal ecological explanation for the retained rule.
