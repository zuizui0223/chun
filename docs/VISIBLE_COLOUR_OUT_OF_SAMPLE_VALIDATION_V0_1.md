# Visible-colour out-of-sample climate validation v0.1

## Question

The previous climate screens are in-sample model comparisons or permutation tests. This validation asks a harder predictive question using only `chun`'s committed species matrix:

> **Does knowing whether a held-out Camellia species is A or W improve prediction of its annual climatic niche?**

If a direct coarse-colour climatic mechanism is important at genus scale, visible A/W state should have at least some out-of-sample predictive value.

## Data and provenance gate

Input is `data/fan2026_chelsa_species_compact_v0_1.csv`.

Before validation:

1. the fuzzy duplicate `Camellia kissi` is removed when exact `C. kissii` is present;
2. the two Tuberculatae cold-tail rows are replaced by the frozen `minimal_remove_two_shared_extreme_coordinates` values in `data/camellia_coldtail_provenance_sensitivity_v0_1.csv`;
3. only A and W are retained.

Final validation matrix:

- **48 species**;
- A = **14**;
- W = **34**.

The four metrics were fixed before the prediction comparison:

- BIO1 median;
- BIO6 median;
- BIO6 q05;
- BIO1 IQR.

## Model comparison

For each held-out species, two predictions are made using only the training rows:

- `null`: training-set mean climate value;
- `colour`: training-set mean for the held-out species' A/W state.

Thus the colour model is given the simplest possible opportunity to improve prediction. No section, phylogenetic branch, pollinator variable or post-hoc interaction is added.

## Test 1 — leave-one-species-out

Every species is hidden once and predicted from the other 47.

| metric | null RMSE | colour RMSE | colour/null |
|---|---:|---:|---:|
| BIO1 median | 2.0219 | 2.0601 | 1.0189 |
| BIO6 median | 2.7668 | 2.8040 | 1.0134 |
| BIO6 q05 | 4.3802 | 4.4189 | 1.0088 |
| BIO1 IQR | 1.2019 | 1.2293 | 1.0227 |

**Colour improves RMSE: 0/4 metrics.**

The geometric mean colour/null RMSE ratio is approximately **1.016**. In other words, adding coarse A/W colour makes held-out prediction slightly worse overall rather than better.

## Test 2 — leave-one-section-out

The stronger test removes an entire traditional section at a time. The held-out species therefore come from a historical/taxonomic background absent from training. The colour model must generalize across sections rather than exploit within-section composition.

| metric | null RMSE | colour RMSE | colour/null |
|---|---:|---:|---:|
| BIO1 median | 2.0429 | 2.0785 | 1.0174 |
| BIO6 median | 2.7577 | 2.8936 | 1.0493 |
| BIO6 q05 | 4.4314 | 4.5934 | 1.0365 |
| BIO1 IQR | 1.2052 | 1.2353 | 1.0250 |

**Colour improves RMSE: 0/4 metrics.**

The geometric mean colour/null RMSE ratio is approximately **1.032**. Coarse flower colour therefore generalizes even less well when prediction is forced across historical section boundaries.

## Interpretation

This is a stronger negative result than another A-vs-W mean comparison.

The direct coarse model predicts:

`A/W visible state -> annual climate information`

but the held-out tests show:

`A/W visible state -> no predictive gain over the training mean`.

That result appears under both single-species holdout and whole-section holdout and after the known cold-tail provenance artefact is removed.

The current conclusion is therefore:

> **Human-visible A/W state is not a useful out-of-sample predictor of annual thermal niche in the current Camellia species matrix.**

This does not imply climate is irrelevant to flower evolution. It specifically rejects the coarse direct route as the best current explanation. Flowering-window climate can still act upstream by changing pollinator availability, reward economics or phenology.

## Connection to the ecological-cause model

The predictive null sharpens the competing causal interpretation:

- direct annual climate -> visible colour: fails in-sample, history-blocked and out-of-sample tests;
- visible colour -> fixed pollination syndrome: fails because same hue contains different pollinator functions;
- flowering-window environment -> pollinator conditions -> reproductive success: repeatedly supported;
- latent spectral state -> pollinator choice: replicated but still the leave-one-study-out weak link.

Thus the next empirical investment should not be more annual-climate occurrence points. The highest-value test remains a wild Camellia system connecting measured biochemical/spectral state to pollinator effectiveness and fruit/seed fitness.

## Claim ceiling

This validation is predictive, not a historical branch-causation test. It does not prove pollinator selection caused any accepted-species colour transition, and it does not replace the nuclear-tree event-identity gate.
