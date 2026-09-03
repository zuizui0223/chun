# C. perpetua future seasonal data runner v0.1

## Purpose

PRs #139–#141 froze the sampling frame, competing mechanisms and null-result boundary before winter petal data exist. This runner removes the remaining analyst degrees of freedom: once the 15 paired GBG plants are measured, the data are placed into one fixed 30-row table and the primary gates are computed automatically.

It is intentionally fail-closed. Missing measurements, altered plant IDs, missing seasons, non-full-bloom rows, unfrozen SESOI bounds or invalid fitness proportions stop the analysis.

## Fixed input

`data/cperpetua_seasonal_input_template_v0_1.csv`

Exactly:
- 15 plant IDs, `P01`–`P15`;
- two rows per plant: `summer`, `winter`;
- standardized `full_bloom` stage;
- one plant-level estimate per field after any within-plant flower subsampling is aggregated.

Primary fields:
- CHUN module scores `A`, `F`, `C`, `P`;
- `bee_hex_contrast`: prespecified Apis/honeybee petal-vs-same-plant-leaf color-hexagon contrast;
- nectar volume, sucrose ratio, observation-window temperature;
- bird/bee visitation and independently defensible per-visit effectiveness;
- fruit set and seed set.

Required secondary fields are also always supplied and reported:
- UV 300–400 nm reflectance summary;
- fluorescence index;
- anthocyanin, flavonol, carotenoid and flavan-3-ol totals.

Secondary endpoints never replace a failed primary gate.

## Equivalence bounds

`data/cperpetua_equivalence_bound_template_v0_1.csv`

The five primary stability bounds are A/F/C/P plus BEE_HEX. Before the winter–summer labels are unblinded, replace `TBD` with a positive raw-unit bound and set `status=FROZEN_PRE_UNBLIND`.

Bounds must be justified from blinded same-season repeatability/pilot information plus a prespecified biological minimum. The runner will not accept a bound chosen after inspecting the seasonal mean.

For each primary axis, equivalence requires the paired 90% CI for winter-minus-summer mean difference to lie fully within ± the frozen bound. All five primary bounds must pass for G1.

## Automated gates

### G0 — seasonal ecology replication

Historical reward/guild direction is required to replicate in the new tagged plants:
- at least one of nectar volume or sucrose ratio increases winterward under Bonferroni-controlled paired exact testing;
- effective bird-service share increases winterward under paired exact testing.

### G2 / Gate A — mature-petal A/F/C/P seasonal shift

For each plant, form the four-axis winter-minus-summer vector. The runner uses the frozen statistic

`T = sum_j (mean(delta_j) / sqrt(mean(delta_ij^2)))^2`

and exhaustively enumerates all **32,768** whole-vector plant-level sign flips.

A nonsignificant result is not stability; G1 equivalence is separate.

### G3 — bee-facing sensory direction

Prespecified direction: winter `bee_hex_contrast` < summer. One-sided exact paired sign-flip test.

### G4 — sensory beyond reward/microclimate

Outcome: effective bird-service share.

Baseline predictors:
1. nectar volume;
2. sucrose ratio;
3. observation-window temperature.

Sensory model adds only the single frozen `bee_hex_contrast`.

Both seasons from one plant are held out together. G4 requires lower leave-one-plant-pair-out RMSE plus exact positive support across the 15 plant-level baseline-minus-sensory error differences.

### G5 — effective service to reproductive prediction

Baseline predictors:
- season indicator;
- nectar volume;
- sucrose ratio;
- temperature.

Service model adds total effective pollination service, with service calculated from visitation × per-visit effectiveness for birds and bees.

Fruit set and seed set are fitted separately but evaluated as one prespecified joint held-out error family so neither endpoint can be chosen post hoc. G5 requires lower joint leave-one-plant-pair-out RMSE plus exact positive support across plant-level error differences.

## Classification

- `M_SENSORY_PLUS_REWARD`: G0 + G2 + G3 + G4 + G5.
- `M_BEHAVIOR_WITHOUT_FITNESS`: G3 and/or G4, but G5 fails.
- `M_GENERAL_SEASONAL_PHYSIOLOGY`: G2 passes while G3 and G4 fail.
- `M_REWARD_ONLY`: G0 + G1 equivalence, with G3/G4 absent.
- `LATENT_STATE_UNRESOLVED`: Gate A nonsignificant and equivalence not established.
- everything else: `MIXED_UNRESOLVED`.

No classification identifies a historical accepted-species colour-transition cause.

## Execution

Real data:

```bash
python scripts/analyze_cperpetua_future_seasonal_data_v0_1.py \
  --data path/to/completed_30_row.csv \
  --bounds path/to/frozen_pre_unblind_bounds.csv \
  --out-dir build/cperpetua_future_real_v0_1

python scripts/summarize_cperpetua_secondary_endpoints_v0_1.py \
  --data path/to/completed_30_row.csv \
  --out-dir build/cperpetua_future_real_secondary_v0_1
```

Primary outputs:
- `summary.json`
- `gate_results.csv`
- `equivalence_results.csv`
- `fitness_endpoint_rmse.csv`

Secondary reporting:
- `secondary_seasonal_summary.csv`

## CI smoke tests

Hosted CI validates the empty official template and then generates three deterministic complete datasets:

1. `sensory_plus_reward` → must classify `M_SENSORY_PLUS_REWARD`;
2. `reward_only` → must classify `M_REWARD_ONLY` via equivalence, not mere nonsignificance;
3. `latent_unresolved` → Gate A nonsignificant but equivalence fails, so must classify `LATENT_STATE_UNRESOLVED`.

This specifically protects the distinction introduced by PR #141.
