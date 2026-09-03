# C. perpetua intervention causal closure v0.1

## Why intervention is needed

The current paired seasonal design can test whether natural winter/summer variation in petal state predicts pollinator weighting beyond season and reward. That remains observational with respect to the sensory cue and pollinator service.

To demonstrate an extant ecological-filter mechanism more directly, add two orthogonal interventions in the same 15 tagged GBG plants:

1. **sensory intervention:** alter the bee-facing optical cue while holding handling/reward as constant as possible, then measure bee response;
2. **pollinator-access intervention:** alter access by bird/insect pollinators, then measure fruit/seed outcome.

These experiments are independent of historical branch reconstruction.

## A. Sensory intervention — G4X

Use flowers separate from the 30-bud reproductive cohort.

Per plant per season:

- 6 active spectral-manipulation flowers;
- 6 vehicle/sham flowers.

Across 15 plants × 2 seasons this gives 180 active and 180 sham flowers while the **plant remains the inferential unit**.

### Intervention specification

Do not freeze a chemical/material after seeing pollinator outcomes. Before field use, choose one optical manipulation that:

- changes the single prespecified Apis color-hexagon petal-vs-leaf contrast in the intended direction;
- leaves 400–650 nm human-visible reflectance within a separately frozen equivalence tolerance except for the intended receptor-space change;
- uses an identical vehicle/handling sham;
- leaves nectar amount/composition and flower temperature within frozen equivalence tolerances;
- if the material contacts petals, document/validate that treatment does not create an obvious odor/headspace artefact before behavioral inference.

If these manipulation checks fail, G4X cannot be interpreted even if pollinator behavior differs.

### Behavioral/service endpoint

Bag trial flowers until testing. Record:

- first legitimate Apis approach/contact;
- latency and visitor identity;
- stigma pollen deposition after a standardized single legitimate visit whenever feasible.

Primary G4X outcome should privilege **single-visit pollen deposition/effectiveness** over visit count if the sample is sufficient.

For each tagged plant, average the active-minus-sham response across its valid trial flowers. Use exact plant-level sign-flip inference. The prespecified direction is active manipulation -> lower bee response if the manipulation reduces bee-facing contrast.

G4X requires both the optical manipulation check and the behavioral/effectiveness contrast.

## B. Pollinator-access intervention — G5X

Reuse the published scale of 30 marked buds per plant in each season.

Randomize similar buds within each plant to:

- **open: 8**;
- **bird exclusion: 8**;
- **full animal exclusion: 7**;
- **hand cross-pollination: 7**.

Total = 30 buds per plant per season.

Randomization occurs within plant and season; treatment labels are assigned before fruit outcome is known.

### Treatment validation

Bird-exclusion structures must be demonstrated by camera/visitor logs to:

- exclude *Aethopyga christinae*;
- retain realistic bee access.

If bee visitation is substantially suppressed by the bird-exclusion structure, the bird contrast is invalid rather than silently reinterpreted.

Full-exclusion bags provide the autonomous baseline. Hand-cross flowers receive standardized outcross pollen and are rebagged.

### Prespecified causal contrasts

Define plant-level seed-set contrasts first; fruit set is reported as a parallel endpoint.

**Bird contribution in winter**

`B_winter = seed_set(open,winter) - seed_set(bird_exclusion,winter)`

Prediction: `B_winter > 0`.

**Seasonal change in bird contribution**

`Delta_B = B_winter - B_summer`

Prediction: `Delta_B > 0` because the existing ecology is more bird-weighted in winter.

**Insect contribution in summer**

`I_summer = seed_set(bird_exclusion,summer) - seed_set(full_exclusion,summer)`

Prediction: `I_summer > 0` because bee visitation is much greater in summer.

Test each contrast by exact plant-level sign flipping across the 15 tagged plants; correct the three core G5X seed-set tests as one prespecified family. Fruit-set directions must be reported and cannot replace failed seed-set gates post hoc.

**Pollen limitation context**

`hand_cross - open` is reported in each season. It is useful for interpreting ceiling effects and pollen limitation but is not required to promote the sensory mechanism.

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
