# Visible-colour predictive provenance sensitivity v0.1

## Purpose

The primary out-of-sample validation uses the provenance-clean Tuberculatae values. This sensitivity asks whether the negative predictive result was itself created by that correction.

The exact same A/W prediction procedure is repeated under three frozen range-tail scenarios:

1. original country-only values, retaining the suspect shared extreme coordinates;
2. minimal removal of the two shared extreme coordinates;
3. strict Tuberculatae section-envelope filtering.

For each scenario, four climate metrics are tested under both leave-one-species-out and leave-one-section-out validation.

Total comparisons:

`3 provenance scenarios x 2 holdout modes x 4 metrics = 24`.

## Result

> **Visible colour improves held-out RMSE in 0/24 comparisons.**

Geometric mean colour/null RMSE ratios across the four metrics are:

| provenance scenario | species holdout | section holdout |
|---|---:|---:|
| original country-only | 1.0180 | 1.0344 |
| minimal extreme-coordinate removal | 1.0160 | 1.0320 |
| strict section envelope | 1.0160 | 1.0321 |

All ratios are >1, so the A/W colour predictor is slightly worse than the intercept-only null in every scenario/mode combination.

## Interpretation

The direct annual-climate null is therefore **not an artefact of deleting the suspicious Tuberculatae cold-tail records**. Even when those records are retained, coarse flower colour does not improve prediction of held-out species or held-out historical sections.

This closes an important alternative explanation for the negative climate result:

`provenance correction -> apparent colour/climate null`

is not supported.

The stronger current result is:

> **Across provenance assumptions, coarse visible A/W state has no out-of-sample annual-climate predictive gain in the current Camellia matrix.**

The claim remains specific to annual species-level climate summaries. It does not test flowering-window weather or climate-mediated pollinator reliability.
