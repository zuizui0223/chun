# C. perpetua latent-state gate power calibration v0.1

## Why this check was necessary

The paired design has 15 plants and an exact 4-axis A/F/C/P sign-flip omnibus test. Exact inference controls false positives, but exactness does **not** guarantee enough power to interpret a nonsignificant result as biological stability.

A deterministic simulation therefore attacks the planned null interpretation before data collection.

## Simulation

- paired plants: 15;
- axes: 4;
- whole-vector sign assignments: 32,768 (exhaustive);
- Gaussian paired differences with unit marginal variance and pairwise axis correlation 0.3;
- 500 simulations per cell, seed 20260903;
- shift magnitude is the Euclidean norm of the standardized four-axis mean vector;
- three shapes: distributed across all four axes (`dense`), two axes, or one axis;
- primary statistic is the preregistered sum of squared standardized mean differences.

This is design calibration, not a biological prior on the true C. perpetua shift.

## Deterministic reference result

Approximate rejection fractions from the frozen simulation:

| standardized multivariate shift | dense | two-axis | one-axis |
|---:|---:|---:|---:|
| 0.0 | 0.048 | 0.056 | 0.058 |
| 0.5 | 0.234 | 0.230 | 0.206 |
| 0.8 | 0.486 | 0.544 | 0.412 |
| 1.0 | 0.716 | 0.722 | 0.642 |
| 1.2 | 0.872 | 0.874 | 0.820 |

The null rejection rate stays near 0.05, so the randomization test is behaving as expected. The important result is power: a moderate standardized multivariate shift of 0.8 is detected in only roughly 41–54% of simulations, depending on how the change is distributed across modules.

## Correction to the interpretation contract

Therefore:

> **Gate A P >= 0.05 cannot be interpreted as 'petal latent state is stable'.**

Reward-only classification now requires a separate equivalence/SESOI gate that positively excludes a biologically meaningful seasonal shift. If Gate A is nonsignificant but equivalence is not established, the latent-state result is **unresolved**.

## How to define equivalence without post-hoc tuning

The equivalence bound must be frozen independently of the observed winter-summer mean difference. Preferred order:

1. estimate assay/within-plant repeatability from blinded same-season technical/flower subsamples;
2. define a biologically meaningful bound before unblinding season labels, using the repeatability distribution plus a prespecified minimum effect criterion;
3. run the equivalence analysis under that frozen bound;
4. report sensitivity to a small fixed set of wider/narrower bounds, never choose the bound that creates reward-only support.

If no defensible independent SESOI can be fixed, the study can test for seasonal change but **cannot conclude equivalence/stability from a null result**.

## Design consequence

The 15-plant frame remains valuable for detecting large shifts and for exact paired inference. Its limitation is now explicit: moderate latent-state shifts may be missed. This does not require abandoning the existing 15 plants, but it changes the claim boundary for negative results.
