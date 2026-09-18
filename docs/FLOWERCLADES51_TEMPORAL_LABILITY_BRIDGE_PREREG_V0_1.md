# Flower-clades-51 temporal-lability bridge preregistration — v0.1

## Biological question

The current CHUN cross-radiation analysis measures how strongly same flower-colour states are retained among phylogenetically close species at coarse, intermediate, and fine phenotypic resolutions. That quantity is not itself a transition-rate estimate. The source Flower-clades-51 study, however, used stochastic character mapping to estimate flower-colour transitions through evolutionary history.

This bridge asks whether **clade-level flower-colour evolutionary lability predicts which phenotypic resolution retains phylogenetic structure**.

Conceptually:

```
flower-colour turnover through evolutionary history
        ↓
persistence/erosion of same-state identity
        ↓
coarse / intermediate / fine resolution profile
```

This is intended to reconnect the cross-radiation programme to the original biological question of flower-colour variation through evolutionary history, rather than treating phenotype representation as an isolated coding problem.

## Exposure boundary

This is not a prospective test. CHUN already knows the 28 completed standardized resolution-profile outcomes and the source paper's aggregate conclusion that flower and fruit transition counts differ among clades. However, before this freeze CHUN has **not extracted the clade-specific flower-colour transition-count values** used as the predictor here.

Therefore this analysis is labeled `RETROSPECTIVE_BIOLOGICAL_MODERATOR_BRIDGE`.

## Frozen predictor

Primary predictor:

`source_stochastic_map_mean_flower_transition_count`

The value must come from an exact clade-level value reported in Sinnott-Armstrong et al. (2026), Appendix S2, or an exact machine-readable companion object traceable to that appendix.

Rules:

- no replacement by a newly re-estimated stochastic map under different trees or settings;
- no switching to fruit transitions, colour diversity, sampling fraction, or another predictor after seeing results;
- no manual plot digitization unless a separate protocol is frozen before digitized values are inspected;
- unresolved or ambiguous values become `HOLD_SOURCE_LABILITY_VALUE_UNRESOLVED`.

The primary transform is `log1p`, followed by z-scoring within the training frame.

## Frozen outcomes

The two independent CHUN resolution-profile contrasts are:

1. `AUC_intermediate - AUC_coarse`;
2. `AUC_fine - AUC_intermediate`.

The derived `AUC_fine - AUC_coarse` contrast is diagnostic only.

## Frozen model and qualification

Fit one predictor plus intercept separately to each independent contrast.

Qualification requires leave-one-clade-out RMSE to improve over the intercept-only baseline for **both** independent contrasts.

A directional sign is not required for qualification. The biological question is whether temporal lability has reproducible out-of-sample explanatory value for the full resolution profile; a sign chosen after outcome inspection would not be admissible.

No larger multivariable model is allowed in v0.1.

## Interpretation boundary

A passing result would support the retrospective statement that evolutionary flower-colour turnover is associated with which phenotypic resolution preserves phylogenetic same-state structure. It would not by itself establish causation or constitute a prospective prediction.

A failed result would show that the source paper's clade-level temporal lability metric is insufficient to explain the resolution-profile heterogeneity under this frozen one-predictor test.

Only after the result is frozen may a separate held-out radiation be used for a genuinely prospective biological prediction.

Camellia Paper 1 remains unchanged.
