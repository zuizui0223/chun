# Observation-corrected mechanistic recurrence — primary comparison gate

## Why the earlier recurrence statistic is demoted

The exploratory dependence-collapsed recurrence analysis was useful for exposing missing A/F/C/P information, but it mixed different biological transition classes and retained each study's recorded source-to-target direction. In particular, the *C. reticulata* developmental fading contrast is recorded pink -> white whereas other red/pink contrasts are mostly less-red -> more-red. Exact-signature recurrence is not biologically interpretable if such orientations are mixed.

Therefore the former pooled all-colour recurrence identified set (`0.20–0.36`) remains a provenance/sensitivity result, not the primary recurrence statistic.

## Frozen canonical frame

Before inspecting candidate-free RNA-seq outputs, every edge is assigned to one of two currently supported classes and a fixed orientation:

1. `anthocyanin_gain`: canonical target = **more red/pink**;
2. `yellow_development`: canonical target = **later/more yellow**.

The orientation table is `data/micro_transition_canonical_orientation_v0_1.csv`. A recorded edge may be reversed only by that pre-frozen table; expression results cannot choose the orientation.

## Literature-only identified sets under the corrected frame

Using the existing literature-coded A/F/C/P registry and exhaustive completion of every unresolved cell by `{up, down, same}`:

### Anthocyanin gain

Three dependence clusters: `CJAPONICA`, `CRETICULATA`, `CSIN_WHITE_PINK`.

After canonical orientation their currently resolved signatures are:

- `CJAPONICA`: `A=up`, F/C/P unresolved;
- `CRETICULATA`: `A=up`, `P=down`, F/C unresolved;
- `CSIN_WHITE_PINK`: `A=up`, `F=down`, C/P unresolved.

There are seven unresolved cluster × axis cells and 2,187 exact completions.

- exact-signature recurrence identified set: **0.3333–1.0**;
- pairwise axis-concordance identified set: **0.25–1.0**.

### Yellow development

Two dependence clusters: `CNITIDISSIMA`, `CPERPETUA`.

- `CNITIDISSIMA`: `A=down, F=up, C=up, P=down` after combining the two published developmental systems;
- `CPERPETUA`: `F=up`, A/C/P unresolved.

There are three unresolved cells and 27 exact completions.

- exact-signature recurrence identified set: **0.5–1.0**;
- pairwise axis-concordance identified set: **0.25–1.0**.

These intervals are intentionally broad. The literature alone does not identify how strongly the full multivariate mechanism recurs once transition orientation and biological class are handled correctly.

## Primary candidate-free test

The new primary question is not whether candidate-free results reproduce the paper authors' highlighted genes. It is:

> **How much does the identified set for class-specific mechanistic recurrence contract or shift when the same public biological systems are remeasured with one frozen, candidate-independent A/F/C/P protocol?**

`scripts/analyze_observation_corrected_recurrence_v0_1.py` compares the two observation regimes on the **same dependence-cluster set**. Candidate-free measurements never inherit literature values for unmeasured cells.

For each class it reports:

- exact-signature recurrence bounds;
- pairwise A/F/C/P directional-concordance bounds;
- agreement/conflict in cells independently resolved by both regimes;
- reduction in identified-set width on the common cluster set.

Candidate-free input must be tidy rows with:

`measurement_id, dependence_cluster, transition_class, axis, direction, status, source`

where `direction` is already expressed in the frozen canonical orientation and can only be `up`, `down`, or `same` when `status=resolved`.

## Claim rule

A narrower candidate-free interval is evidence that standardized measurement resolves literature missingness. A shift in the interval or conflicts with published cells is evidence that the literature observation process changes the apparent mechanistic recurrence. Neither result by itself proves mutation-level causal reuse or branch-specific macroevolutionary causation.

This gate is deliberately outcome-agnostic: confirmation, attenuation, and reversal of published recurrence are all admissible results.
