# Resolution-profile moderator qualification — v0.1

## Decision

`NO_MODERATOR_QUALIFIED_CURRENT_STANDARDIZED_TRAINING`

The Flower-clades-51 batch supplies 28 completed exact-estimand clades, so the numerical replication floor is no longer the limiting factor. The limiting factor is identifiability of a full three-resolution moderator.

## Training frame

All 28 completed clades share one source, one human-perceived visible-colour ontology, and one common scoring protocol. This is useful for standardized biological replication but does not provide representation-type variation. The prospective Iris result remains scientifically important but uses a mixed pigment/hue hierarchy and is not sufficient by itself to estimate a representation-type effect.

## Candidate predictors

Only quantities available before target outcome labels were considered:

- log tree-tip count;
- pairwise patristic-distance CV;
- branch-length CV;
- root-to-tip CV.

Complexity was capped at one predictor plus intercept.

## Qualification rule

A predictor must improve leave-one-clade-out RMSE relative to intercept-only prediction for both independent profile contrasts:

1. `AUC_intermediate - AUC_coarse`;
2. `AUC_fine - AUC_intermediate`.

This joint rule is required because improving only one contrast cannot predict a three-level winner.

## Result

No predictor passes the joint gate. All four also worsen LOO RMSE for the derived `AUC_fine - AUC_coarse` contrast.

The only partial improvement is `log_n_tips` for `fine - intermediate` (+2.53% LOO improvement), but the same predictor worsens `intermediate - coarse` by 3.11%, so it is not admitted as a resolution-profile moderator.

## Consequence

The programme does **not** fit a larger model, add correlated tree metrics, or use realized colour frequencies to rescue prediction. A new held-out resolution-profile outcome must remain unopened under Issue #245 until either:

- cross-representation exact-estimand training expands; or
- a separately preregistered outcome-independent moderator clears the joint LOO gate.

Thus the current strongest inference is not that tree geometry predicts the winning resolution, but that **resolution profiles vary substantially while the tested outcome-independent tree geometry does not yet explain that variation**.

Camellia Paper 1 is unchanged.
