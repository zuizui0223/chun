# C. perpetua competing seasonal mechanism models v0.1

## Why a second preregistration is needed

PR #139 fixed the sampling frame, but the existing ecology already shows very large seasonal reward and pollinator changes. Therefore a future winter-vs-summer petal molecular difference, by itself, would not identify a sensory mechanism.

The historical anchors are deliberately treated as motivation/baseline rather than as new independent evidence:

- nectar volume: winter/summer = **3.513**;
- full-bloom sucrose/(glucose+fructose): **7.109**;
- total nectar amino acids: **0.402**;
- fork-tailed sunbird visitation: **2.90**;
- *Apis cerana* visitation: **0.241**;
- *A. mellifera ligustica* visitation: **0.186**;
- bird/(two Apis) visitation ratio shifts approximately **13.76-fold** toward birds in winter.

Exact visitation-rate anchors are retained from the study precursor; the 2025 peer-reviewed article independently retains the same seasonal direction. They are not counted twice.

## Competing models

### M_REWARD_ONLY

Season changes nectar/reward and microclimate, which changes pollinator weighting and fitness, while the mature petal molecular/sensory state remains effectively stable.

Prediction: the historical reward/guild shift replicates, but the prespecified petal latent-state test does not.

### M_GENERAL_SEASONAL_PHYSIOLOGY

Petal biochemistry changes with season, but the change is not aligned with the bee-to-bird weighting shift and does not add predictive information beyond reward/microclimate.

Prediction: latent-state Gate A passes, while the bee-salience and sensory incremental-prediction gates fail.

### M_SENSORY_PLUS_REWARD

Season changes both reward and petal sensory state. The petal change contributes information about pollinator weighting beyond reward/microclimate, and effective service contributes to fitness.

This is the only outcome class allowed to support a seasonal sensory ecological-filter mechanism.

### M_BEHAVIOR_WITHOUT_FITNESS

Sensory state predicts pollinator weighting/effectiveness, but the added service signal does not improve plant-level fruit/seed prediction. This supports behavior/service association but not reproductive filtering.

## Primary latent-state gate

Do **not** transfer the signs of the June S1-S5 developmental trajectory into winter-vs-summer predictions. Developmental A/F/C/P slopes and seasonal full-bloom contrasts are different estimands.

For each of the 15 tagged plants, construct the winter-minus-summer vector for the four frozen CHUN module scores A/F/C/P at the same full-bloom stage.

Use a sign-invariant scale for each axis, `s_j = sqrt(mean(delta_ij^2))`, and the prespecified statistic:

`T = sum_j (mean(delta_j) / s_j)^2`.

Enumerate all **2^15 = 32,768** plant-level whole-vector sign flips. The exact two-sided multivariate P value is the fraction of sign assignments with `T_perm >= T_obs` (including the observed assignment). Axis-wise paired effects are secondary and Holm-adjusted across A/F/C/P.

A significant Gate A says only that mature petal latent state is seasonal; it does not establish pollinator mediation.

## Sensory directional gate

The actual winter shift is away from Apis visitation and toward *Aethopyga christinae*. Therefore one sensory direction is prespecified without assuming any A/F/C/P sign:

> **winter full-bloom flowers should have lower bee-facing chromatic salience than summer if petal sensory state contributes to the guild shift.**

Primary bee-salience endpoint:

- Apis/honeybee color-hexagon chromatic contrast between petal reflectance and a same-plant green-leaf background;
- standardized 300-650 nm acquisition and illumination;
- one plant-level value per season after within-plant flower averaging.

The primary directional test is paired winter-minus-summer < 0 using exact plant-level sign-flip inference. UV-band reflectance and fluorescence are secondary prespecified families and cannot replace a failed primary bee-salience test post hoc.

No directional bird-vision prediction is claimed without a defensible *Aethopyga christinae* receptor model.

## Incremental prediction gate: sensory beyond reward

The central causal discrimination is not whether spectra change, but whether sensory information helps explain pollinator weighting after reward/microclimate information is already available.

Outcome per plant-season:

`bird effective-service share = bird_service / (bird_service + bee_service)`

where service should use visitation multiplied by a defensible per-visit pollen-deposition/effectiveness estimate rather than visit counts alone whenever available.

Predeclared baseline predictors:

1. full-bloom nectar volume;
2. sucrose/(glucose+fructose);
3. mean observation-window temperature.

Sensory model = the same baseline plus the single primary Apis color-hexagon contrast.

Use **leave-one-plant-pair-out** prediction: both winter and summer observations from one plant are held out together. For each of 15 held-out plants, calculate mean prediction error across its two seasons for baseline and sensory models.

Gate G4 requires both:

- lower overall held-out RMSE for the sensory model;
- exact sign-flip/randomization support across the 15 plant-level error differences.

This prevents within-plant leakage and post-hoc spectral-variable fishing.

## Service-to-fitness gate

A sensory or visitation shift is not reproductive filtering unless service predicts plant-level reproduction.

Compare a prespecified season+reward baseline fitness model with the same model plus effective pollination service under leave-one-plant-pair-out validation. Fruit set and seed set remain separately reported endpoints; one cannot replace the other after results are known.

Gate G5 requires incremental out-of-sample prediction from effective service. If sensory/service gates pass but G5 fails, classify the result as M_BEHAVIOR_WITHOUT_FITNESS.

## Classification table

- **G0 replicated + G1 absent** -> M_REWARD_ONLY.
- **G1 present, G3/G4 absent** -> M_GENERAL_SEASONAL_PHYSIOLOGY.
- **G0 + G1 + G3 + G4 + G5** -> M_SENSORY_PLUS_REWARD.
- **G3/G4 present, G5 absent** -> M_BEHAVIOR_WITHOUT_FITNESS.
- mixed cases not matching these rules remain unresolved rather than being forced into the preferred mechanism.

## Additional measurements worth collecting but not allowed to redefine success

Record observation-window temperature, relative humidity, PAR/UV irradiance and flower age. These support sensitivity analyses and interpretation, but the primary success criterion is not reopened to whichever environmental variable looks strongest.

## Scientific consequence

This contract raises the bar intentionally. Because reward and pollinator weighting already move dramatically between seasons, a positive winter-vs-summer molecular result alone would be weak evidence. The sensory mechanism is promoted only when petal state changes in the same tagged plants, the prespecified bee-facing sensory direction is met, sensory information improves held-out pollinator-service prediction beyond reward/microclimate, and effective service improves reproductive prediction.

Even a full pass demonstrates an extant seasonal ecological-filter mechanism, not the cause of a particular historical accepted-species flower-colour transition.
