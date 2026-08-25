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

The primary question is:

> **How much does the identified set for class-specific mechanistic recurrence contract or shift when the same public biological systems are remeasured with one frozen, candidate-independent A/F/C/P protocol?**

`scripts/analyze_observation_corrected_recurrence_v0_1.py` compares the two observation regimes on the **same dependence-cluster set**. Candidate-free measurements never inherit literature values for unmeasured cells.

For each class it reports:

- exact-signature recurrence bounds;
- pairwise A/F/C/P directional-concordance bounds;
- agreement/conflict in cells independently resolved by both regimes;
- reduction in identified-set width on the common cluster set.

Candidate-free input is tidy rows with:

`measurement_id, dependence_cluster, transition_class, axis, direction, status, source`

where `direction` is already expressed in the frozen canonical orientation and can only be `up`, `down`, or `same` when `status=resolved`.

## Gate closure — actual frozen result

**Status: CLOSED for the first >=2-cluster anthocyanin-gain test.**

Frozen raw-result runs:

- Joy Kendrick `CJAPONICA`: `32803242153`;
- *C. sinensis* `CSIN_WHITE_PINK`: `32817229591`;
- *C. nitidissima* `CNITIDISSIMA`: `32803242174`;
- integrated recurrence: `32820995797`.

The common `anthocyanin_gain` cluster set is `CJAPONICA + CSIN_WHITE_PINK`.

### Literature regime on the same two clusters

- unresolved cluster × axis cells: 5;
- exact completions: 243;
- exact-signature recurrence: **0.5–1.0**;
- pairwise concordance: **0.25–1.0**;
- pairwise identified-set width: **0.75**.

### Candidate-free regime on the same two clusters

- unresolved cluster × axis cells: 1;
- exact completions: 3;
- exact-signature recurrence: **0.5 exactly**;
- pairwise concordance: **0.25–0.5**;
- pairwise identified-set width: **0.25**;
- width reduction: **0.50**.

Thus standardized observation both **contracts** and **shifts** the admissible recurrence region: complete multivariate concordance is no longer supported on the common two-cluster set.

### Independently resolved cell agreement

Across three comparable resolved cells:

- agreement: **1/3**;
- conflict: **2/3**.

Both conflicts are the A axis:

- `CJAPONICA`: literature `up`, candidate-free `down`;
- `CSIN_WHITE_PINK`: literature `up`, candidate-free `down`.

The *C. sinensis* result is especially strong at the frozen module level: A is down in 5/5 prespecified stages with mean Hedges' g **-2.8595**.

### Yellow-development control

`CNITIDISSIMA` remains a single candidate-free yellow cluster, so class-level recurrence contraction is not testable yet. However, literature and candidate-free directions agree **4/4** for A/F/C/P on that cluster.

This rejects a simple interpretation that the standardized pipeline mechanically reverses published directions. Observation effects are system/class dependent.

## Claim rule after closure

The first real standardized two-cluster test supports:

> **Published anthocyanin-gain mechanistic recurrence is materially observation-regime dependent. A frozen pathway-wide candidate-free remeasurement reduces the identified recurrence space and reverses the published A-axis direction in both independently remeasured common clusters.**

It does **not** support the stronger claims that anthocyanin is irrelevant, all candidate-gene studies are wrong, mutation-level reuse has been disproved, or branch-specific macroevolutionary causes are identified.

The authoritative numerical record is `docs/CANDIDATE_FREE_ACTUAL_RECURRENCE_RESULT_V0_1.md`.
