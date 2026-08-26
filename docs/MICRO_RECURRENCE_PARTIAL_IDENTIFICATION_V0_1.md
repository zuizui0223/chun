# Micro mechanistic recurrence — missing-axis partial identification v0.1

## Why this analysis is needed

The dependence-aware literature matrix has only five broader clusters and many unresolved A/F/C/P axes. Treating `unknown` as a fifth biological state artificially makes cluster signatures look unique. Filling unknown axes with the expected direction would be outcome-directed imputation.

The correct question is therefore not initially `what is the recurrence score?` but:

> **What range of recurrence is compatible with everything currently observed, before candidate-free raw-data resolution?**

## Exact completion space

After dependence collapse, the current signatures are:

- `CJAPONICA`: `up | unknown | unknown | unknown`;
- `CNITIDISSIMA`: `down | up | up | down`;
- `CPERPETUA`: `unknown | up | unknown | unknown`;
- `CRETICULATA`: `mixed | unknown | unknown | mixed`;
- `CSIN_WHITE_PINK`: `up | down | unknown | unknown`.

There are **10 unresolved cluster-axis cells**.

For partial identification, every `unknown` is allowed to be `up`, `down`, or `same`. Observed `mixed` entries remain fixed as mixed because they represent disagreement among known system-level directions, not absence of measurement.

This yields exactly:

`3^10 = 59,049`

admissible completions.

## Identified set for multivariate recurrence

For five dependence clusters, a Simpson concentration score of 0.20 corresponds to all five completed signatures being unique.

Across all 59,049 exact completions:

- minimum recurrence = **0.20**;
- maximum recurrence = **0.36**;
- 54,027 completions give **0.20**;
- 4,941 completions give **0.28**;
- 81 completions give **0.36**.

Thus the current literature does **not point-identify** multivariate mechanistic recurrence. Both complete uniqueness and repeated cluster signatures are compatible with the observed evidence.

The fraction of the combinatorial completion space above the all-unique floor is approximately **0.08505**. This number is not a biological probability: the enumeration does not assume that up/down/same are equally likely in evolution. It is only a diagnostic of how much the conclusion depends on unresolved measurement axes.

## Consequence for the earlier P = 1 recurrence result

The dependence-collapsed point analysis that retains literal `unknown` labels gives recurrence 0.20 and P = 1.0. That remains a valid statement about the **observed literature-coded signatures**, but it must not be interpreted as proof that the true complete mechanistic signatures are all different.

The stronger conclusion is:

> **The published evidence currently fails to identify whether independent Camellia systems converge on the same multivariate pigment transition package.**

This is more informative than either claiming convergence or claiming heterogeneity.

## Why this strengthens the candidate-free design

Candidate-free RNA-seq is now an explicit identification strategy, not simply an additional dataset.

Every newly resolved A/F/C/P cluster-axis cell removes outcome-directed ambiguity from the completion set. The reanalysis therefore asks whether the current identified set collapses toward:

- recurrent shared signatures;
- persistent mechanistic heterogeneity;
- or a mixture in which only selected axes such as anthocyanin converge.

## Novelty boundary

Flower-colour studies have long distinguished mutation spectra from fixed substitutions and developmental constraint from selection. The new contribution cannot be that separation alone.

The methodological contribution targeted here is narrower:

1. quantify the observation/ascertainment imbalance in a multi-pigment literature matrix;
2. avoid filling unmeasured pathway axes with visible-colour assumptions;
3. report a partial-identification bound for mechanistic recurrence;
4. intervene on the observation process by re-quantifying the same public raw datasets with one predefined multi-axis module panel;
5. measure how much the identified set contracts after the observation protocol is standardized.

This directly separates uncertainty caused by biology from uncertainty caused by what the literature chose to measure.
