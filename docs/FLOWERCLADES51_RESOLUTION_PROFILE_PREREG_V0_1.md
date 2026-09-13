# Flower-clades-51 resolution-profile preregistration — v0.1

## Goal

Increase exact same-estimand replication for the radiation-level resolution-profile programme using the standardized 51-clade flower-colour dataset of Sinnott-Armstrong et al. (2026; article DOI `10.1002/ajb2.70146`, Dryad DOI `10.5061/dryad.r4xgxd2sc`).

This is a **training expansion**, not the next held-out test. The future held-out radiation remains external to this batch.

## Why this source

The published dataset reports 51 angiosperm clades, 2960 species, one flower-colour variable scored into the same eight human-perceived categories across clades, and 51 phylogenies. This creates a much stronger path to same-estimand replication than continuing to hunt one favorable radiation at a time.

Before this freeze, CHUN has used only source metadata: publication identity, file names, reported clade/species counts, the published eight-category vocabulary, and the existence of clade phylogenies. CHUN has **not** ingested species-level `flower_color` values or calculated any clade resolution profile.

## Frozen nested visible-colour hierarchy

No pigment chemistry is inferred from visible hue. The hierarchy stays entirely on the source human-perceived colour axis.

| Fine source state | Intermediate | Coarse |
|---|---|---|
| black/dark | DARK | NONWHITE |
| blue/purple | COOL | NONWHITE |
| green | COOL | NONWHITE |
| orange | WARM | NONWHITE |
| pink | WARM | NONWHITE |
| red | WARM | NONWHITE |
| white | WHITE | WHITE |
| yellow | WARM | NONWHITE |

The warm/cool grouping is fixed before row values are opened and is not allowed to change after clade frequencies are seen. `fruit_color` is outside this analysis.

## Outcome-blind preflight first

The first post-freeze acquisition step may read only:

- dataset version/file metadata and hashes;
- `clade` and `species` identifiers;
- tree filenames, tip labels, branch lengths and tip counts.

It may not read or emit `flower_color` or `fruit_color` values. That preflight must freeze clade↔tree mapping, identifier normalization, duplicate handling and join diagnostics before outcomes are opened.

## Exact profile estimand

For each eligible clade, use the same estimator already frozen for the Gesnerioideae attempt and executed in Iris:

1. one common retained-tip frame for coarse/intermediate/fine;
2. drop missing flower colour;
3. drop fine states represented by fewer than 5 matched tips, then use the same remaining tips at every resolution;
4. require at least 20 common tips and at least two states at each resolution;
5. use negative patristic distance to predict whether each pair shares the same state;
6. calculate ROC AUC for coarse, intermediate and fine;
7. jointly permute complete three-level state triplets across retained tips 9,999 times (`seed=20260913` per clade).

Per-clade terminal classes remain exactly:

- `PROFILE_SIGNALLED_COARSE`;
- `PROFILE_SIGNALLED_INTERMEDIATE`;
- `PROFILE_SIGNALLED_FINE`;
- `PROFILE_SIGNALLED_TIED`;
- `PROFILE_NO_PHYLOGENETIC_SIGNAL`.

A unique winner requires AUC > 0.5 with one-sided signal P <= 0.05 and winner-vs-runner-up joint-permutation P <= 0.05. No sensitivity analysis can upgrade a terminal class.

Clades failing crosswalk/state replication are `HOLD_*` and do not count as profile outcomes.

## Training boundary

One clade = one biological radiation-level replication unit. The common publication and common colour-scoring protocol create source-level dependence and must be reported; no individual species is treated as an independent radiation.

The frozen moderator minimum remains 5 completed exact same-estimand radiations. This preregistration does not fit any moderator. Only after the batch outcomes exist may Issue #245 be revisited under its existing one-predictor / leave-one-radiation-out rule.

## Claim boundary

This batch tests whether resolution profiles vary among radiations under one standardized visible-colour ontology. It does not test pigment chemistry, molecular mechanisms, pollinator causation, or a universal intermediate-resolution optimum. Iris already falsified that universal optimum.

Camellia Paper 1 remains unchanged and closed.
