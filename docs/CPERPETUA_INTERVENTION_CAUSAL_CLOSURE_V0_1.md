# C. perpetua intervention causal closure v0.1

## Why intervention is needed

The current paired seasonal design can test whether natural winter/summer variation in petal state predicts pollinator weighting beyond season and reward. That remains observational with respect to the sensory cue and pollinator service.

To demonstrate an extant ecological-filter mechanism more directly, add two orthogonal interventions in the same 15 tagged GBG plants:

1. **sensory intervention:** alter the bee-facing optical cue while holding handling/reward as constant as possible, then measure bee response;
2. **pollinator-access intervention:** alter access by bird/insect pollinators, then measure fruit/seed outcome.

These experiments are independent of historical branch reconstruction.

## Independence and randomization frame

Two inferential frames must not be conflated.

- For the **natural winter/summer observational comparison**, the tagged plant remains the biological independence unit.
- For **G4X/G5X interventions**, treatment is randomized to individual flowers/buds *within each plant × season block*. The randomized flower/bud is therefore the experimental unit for the treatment effect, while plant × season is the blocking unit and the 15 plants define the biological generalization frame.

Using the randomized flower-level outcomes is not pseudoreplication: the treatment labels themselves are assigned at that level. Primary intervention P values are randomization-based and preserve the exact treatment counts within every plant-season block. Plant-level treatment contrasts and heterogeneity are always reported alongside the blocked estimate.

This distinction prevents two opposite errors: pretending observational flowers are independent replicates, or discarding valid randomized flower-level information by collapsing every intervention to only 15 numbers.

## A. Sensory intervention — G4X

Use flowers separate from the 30-bud reproductive cohort.

Per plant per season:

- 6 active spectral-manipulation flowers;
- 6 vehicle/sham flowers.

Across 15 plants × 2 seasons this gives 180 active and 180 sham flowers.

Treatment labels are randomized among the 12 comparable trial flowers separately within each plant-season block.

### Intervention specification

Do not freeze a chemical/material after seeing pollinator outcomes. Before field use, choose one optical manipulation that:

- changes the single prespecified Apis color-hexagon petal-vs-leaf contrast in the intended direction;
- leaves 400–650 nm human-visible reflectance within a separately frozen equivalence tolerance except for the intended receptor-space change;
- uses an identical vehicle/handling sham;
- leaves nectar amount/composition and flower temperature within frozen equivalence tolerances;
- if the material contacts petals, document/validate that treatment does not create an obvious odor/headspace artefact before behavioral inference.

If these manipulation checks fail, G4X cannot be interpreted even if pollinator behavior differs.

### Behavioral/service endpoint and inference

Bag trial flowers until testing. Record:

- first legitimate Apis approach/contact;
- latency and visitor identity;
- stigma pollen deposition after a standardized legitimate-visit/trial protocol whenever feasible.

The endpoint definition and exposure window must be frozen before treatment labels are linked to outcomes. Pollen-deposition/effectiveness is preferred over visit count when the protocol yields a complete comparable outcome; behavioral response remains fully reported.

Primary G4X inference uses treatment-label randomization **within every plant-season block**, preserving 6 active / 6 sham assignments. The test statistic is an equally block-weighted active-minus-sham contrast so one high-visit plant or season cannot dominate merely because it contributes more observations. Exact enumeration over all blocks is infeasible, so use a deterministic Monte Carlo randomization distribution with a frozen seed and at least 100,000 joint within-block reassignments.

Report in parallel:

- pooled blocked treatment effect;
- each plant-season treatment contrast;
- each plant's season-specific and across-season effect summaries.

The prespecified direction is active manipulation -> lower bee response if the active manipulation reduces bee-facing contrast.

G4X requires both the optical manipulation check and the behavioral/effectiveness contrast.

## B. Pollinator-access intervention — G5X

Reuse the published scale of 30 marked buds per plant in each season.

Randomize comparable buds **within each plant × season** to:

- **open: 8**;
- **bird exclusion: 8**;
- **full animal exclusion: 7**;
- **hand cross-pollination: 7**.

Total = 30 buds per plant per season.

Treatment labels are assigned before fruit outcome is known. The randomized bud is the treatment unit; the plant-season block absorbs shared plant quality and seasonal background.

### Treatment validation

Bird-exclusion structures must be demonstrated by camera/visitor logs to:

- exclude *Aethopyga christinae*;
- retain realistic bee access.

If bee visitation is substantially suppressed by the bird-exclusion structure, the bird contrast is invalid rather than silently reinterpreted.

Full-exclusion bags provide the autonomous baseline. Hand-cross flowers receive standardized outcross pollen and are rebagged.

### Prespecified causal contrasts

Seed set is the primary reproductive endpoint; fruit set is reported as a parallel endpoint and cannot replace a failed seed-set gate post hoc.

For pairwise intervention gates, inference is restricted to the relevant arms and treatment labels are permuted only among those buds **within each plant-season**, preserving the observed arm sizes.

**Bird contribution in winter**

`B_winter = mean_block[seed_set(open,winter) - seed_set(bird_exclusion,winter)]`

Prediction: `B_winter > 0`.

For each winter plant, permute the 8 open / 8 bird-exclusion labels among its 16 eligible buds. The primary test statistic is the equally plant-weighted average contrast. Use deterministic joint blocked randomization with at least 100,000 draws; also report all 15 plant-specific contrasts.

**Seasonal change in bird contribution**

`Delta_B = mean_block[B_winter] - mean_block[B_summer]`

Prediction: `Delta_B > 0` because the existing ecology is more bird-weighted in winter.

For the interaction randomization distribution, independently reshuffle the 8/8 open/exclusion labels within **every plant-season block** and recompute the winter-minus-summer treatment-contrast difference. Season labels themselves are not permuted because season was not randomized.

**Insect contribution in summer**

`I_summer = mean_block[seed_set(bird_exclusion,summer) - seed_set(full_exclusion,summer)]`

Prediction: `I_summer > 0` because bee visitation is much greater in summer.

Within each summer plant, permute 8 bird-exclusion / 7 full-exclusion labels among the 15 eligible buds, preserving 8/7 allocation.

The three core G5X seed-set tests form one prespecified multiplicity family. Fruit-set directions are always reported and cannot substitute for failed seed-set gates.

**Pollen limitation context**

`hand_cross - open` is reported in each season using the same within-block randomization logic. It is useful for interpreting ceiling effects and pollen limitation but is not required to promote the sensory mechanism.

## Why blocked randomization is preferable to plant-only collapse

The initial intervention draft proposed collapsing every treatment arm to a plant-level proportion and applying a 15-plant sign-flip test. That is conservative but wastes treatment randomization information. Design simulations showed that moderate bird-access differences can be detectable with 8 vs 8 flowers, while a seasonal difference-in-differences can remain weak after collapsing to only 15 paired contrasts.

Because G4X/G5X labels are randomized at the flower/bud level, conditional randomization within plant-season blocks provides design-based causal inference without assuming that flowers are observationally independent. It therefore preserves the randomized information while protecting against plant-level confounding.

The 15 plant-specific effects remain essential for effect heterogeneity, biological generalization and sensitivity analysis; the blocked randomized-flower P value is not permission to generalize beyond the sampled GBG population without those summaries.

## Experimental causal hierarchy

The strongest extant seasonal conclusion requires:

1. natural seasonal latent-state shift (G2);
2. natural winter decrease in bee-facing salience (G3);
3. season-adjusted natural sensory incremental prediction (G4);
4. **sensory manipulation -> bee response/effectiveness (G4X)**;
5. **pollinator-access manipulation -> reproductive outcome (G5X)**.

If G4X fails, natural G3/G4 associations cannot be upgraded to sensory causation.

If G5X fails, pollinator service cannot be upgraded to reproductive filtering even if behavior changes.

A full G4X+G5X pass would provide a much stronger same-population mechanism chain than distributed literature triangulation, but it still tests an extant seasonal filter rather than a particular historical accepted-species flower-colour transition.

## Claim boundary

No specific optical material, effect size, or winter molecular result is assumed here. The intervention itself must pass manipulation checks before causal interpretation.
