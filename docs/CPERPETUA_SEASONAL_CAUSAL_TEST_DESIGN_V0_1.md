# C. perpetua seasonal latent-state causal test design v0.1

## Current empirical position

The public-data work has now localized the strongest Camellia ecological test to one system.

- GBG seasonal ecology used 15 adult plants and found much higher winter nectar volume/sucrose weighting, bird visitation and reproductive success than in summer.
- the admitted C. perpetua molecular dataset is a June 2022 developmental flower series from the same institutional garden complex, not a winter-summer comparison;
- a second independent June flower transcriptome/chemistry study confirms that summer floral molecular material is available;
- the frozen open/public screen recovered no winter mature-flower molecular or spectral anchor.

The next experiment should therefore fill one missing state, not rebuild the whole ecology programme.

## Primary hypothesis

**H_CP_SEASONAL_LATENT_STATE**

> In the same GBG population, the winter flowering window differs from summer not only in nectar/pollinator conditions but also in the mature floral biochemical/sensory state. Those plant-level seasonal shifts covary with effective pollination and reproductive fitness.

This is an extant ecological-filter hypothesis. It is not a historical branch-causation test.

## Independence frame

Reuse the published GBG scale: **15 tagged adult plants**, followed in both winter and summer.

Plant, not flower, is the primary independence unit. Multiple flowers within a plant are subsamples used to stabilize the plant-level estimate.

The published ecology protocol marked 30 flower buds on each of 15 plants. The new measurements should be layered onto the same logic rather than treating hundreds of flowers as independent replicates.

## Primary measurements on all 15 paired plants

1. **A/F/C/P targeted petal state** at a standardized full-bloom stage, using the same annotation/module definition as CHUN candidate-free remeasurement.
2. **UV-visible reflectance and fluorescence**, with spectral coordinates/wavelength summaries predeclared before looking at pollinator outcomes.
3. **Pigment chemistry** covering anthocyanin, flavonol, carotenoid and flavan-3-ol/catechin classes.
4. **Nectar volume and composition** using standardized flower age and the previous bagging framework.
5. **Effective pollination**, not visit count alone: bird/bee visitation plus stigma pollen deposition or a defensible single-visit effectiveness measure.
6. **Fruit and seed output** linked back to the same tagged plant/marked flower cohort.

## Discovery layer

Use a prespecified subset of **6 tagged plants** for paired winter/summer full-bloom RNA-seq and widely targeted metabolomics (12 biological libraries/samples per platform before technical/QC replication).

This layer is for genome-wide interpretation and validation. The paper's primary success criterion must not depend on finding DE genes after the fact.

## Primary statistics

With 15 paired plants, exhaustive sign flipping contains **32,768** winter/summer sign assignments. The primary seasonal-state test can therefore use exact/randomization inference rather than relying on asymptotic P values.

### Gate A — does latent floral state shift with season?

- compute plant-paired winter-minus-summer effects for the predeclared A/F/C/P axes;
- test axes using exact sign-flip/randomization inference;
- control multiplicity across the four prespecified molecular axes;
- report all directions/effect sizes, including near-zero and contrary directions;
- spectra/chemistry are separate prespecified families; no post-hoc wavelength/metabolite winner selection.

The 15-pair frame has approximately 80% power for a paired standardized effect around **d = 0.78** at two-sided alpha 0.05 under conventional t-test planning. This is a planning reference, not the final inferential model.

### Gate B — is the shift ecologically connected?

A seasonal molecular/spectral difference alone is not enough. The ecological-filter claim is promoted only if the same tagged population also shows seasonal shifts in effective pollination and fitness, and plant-level latent-state changes are directionally/quantitatively connected to those endpoints.

A safe hierarchy is:

`season -> latent floral/reward state -> effective pollination -> fruit/seed fitness`

The first arrow can be tested experimentally/longitudinally with the paired design. Mediation language for later arrows should be proportional to the actual manipulation and covariance structure; season itself is not randomized.

## What would falsify the working mechanism?

The design is valuable even if negative.

- **No winter-summer A/F/C/P, chemistry or spectral shift:** weakens the hypothesis that the seasonal pollinator shift operates through floral pigment/sensory state; nectar/phenology-only mediation becomes more likely.
- **Latent-state shift without effective-pollination shift:** biochemical seasonality exists but is not linked to pollinator service in this test.
- **Pollinator/fitness shift without latent-state shift:** supports ecological filtering through reward/phenology or other traits rather than petal colour/spectral state.
- **All links shift together:** provides the first same-population Camellia mechanism/service chain strong enough to move beyond distributed literature triangulation.

## Claim boundary

Even a successful winter-summer experiment would demonstrate an extant seasonal ecological filter. It would still not prove that the same process caused a specific historical accepted-species flower-colour transition. The current macro event-identifiability ceiling remains a separate gate.
