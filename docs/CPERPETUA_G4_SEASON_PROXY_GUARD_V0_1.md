# C. perpetua G4 season-proxy guard v0.1

## Problem

The first future-data runner compared a reward/microclimate baseline against the same model plus the prespecified Apis color-hexagon contrast. Because both pollinator weighting and floral sensory state may change strongly between winter and summer, a sensory variable could appear predictive simply because it acts as another season label.

That is not enough to support sensory-mediated filtering.

## Fix

G4 now compares:

`bird effective-service share ~ season + nectar volume + sucrose ratio + temperature`

against:

`bird effective-service share ~ season + nectar volume + sucrose ratio + temperature + bee color-hexagon contrast`.

Prediction remains leave-one-plant-pair-out: both summer and winter observations from one tagged plant are held out together.

Thus bee-facing sensory state earns G4 credit only for information **beyond explicit season and the frozen reward/microclimate baseline**.

## Adversarial synthetic test

A fourth deterministic smoke scenario, `season_proxy`, was added.

It deliberately contains:

- a strong winter-summer A/F/C/P shift;
- a strong winter decrease in bee color-hexagon contrast, so G3 passes;
- a strong winter shift toward bird service;
- no incremental relationship between bee contrast and bird share after the season effect is known.

Independent deterministic recalculation with the corrected baseline gives approximately:

- season-adjusted baseline RMSE: **0.00929**;
- + bee-contrast RMSE: **0.01058**;
- mean plant-level squared-error improvement: negative;
- exact G4 directional P = **1.0**.

Therefore G3 can be positive while G4 is negative, and the synthetic case is forbidden from being classified as `M_SENSORY_PLUS_REWARD`.

For comparison, the synthetic `sensory_plus_reward` case retains clear incremental information after season adjustment (G4 exact P approximately `3.05e-5`).

## Interpretation

This closes an important causal loophole:

> a winter sensory shift that merely co-occurs with winter cannot be used as evidence that sensory state helps explain the pollinator-guild shift.

The sensory mechanism requires within-design predictive information beyond season, reward and temperature.

This remains an extant seasonal causal-discrimination test. It does not identify the cause of a historical accepted-species flower-colour transition.
