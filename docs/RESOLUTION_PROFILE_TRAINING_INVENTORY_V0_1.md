# Resolution-profile training inventory — v0.1

## Decision

**Do not fit a radiation-level quantitative moderator yet.**

The exact same-estimand training count is **1**, below the already frozen minimum of **5**.

## Exact estimand

A radiation enters quantitative moderator training only after completing the same profile test:

- one common eligible-tip frame;
- three genuinely nested coarse / intermediate / fine representations on one underlying phenotype axis;
- same-state versus different-state pair labels at each resolution;
- negative patristic distance as predictor;
- ROC AUC at all three resolutions;
- 9,999 joint permutations of the complete state triplet.

This definition excludes evidence that answers a different hierarchical question, even when that evidence is biologically supportive.

## Inventory

### Iris — training eligible

Iris is currently the only completed exact-estimand outcome.

Its preregistered universal-intermediate test ended in **FAIL** on 169 eligible tips:

- coarse AUC = 0.4617285166;
- intermediate AUC = 0.4543945669;
- fine AUC = 0.4870504419.

A failed prediction is still a valid training outcome because the estimand was executed as frozen.

### Gesnerioideae — not training eligible

The same profile estimand was preregistered, but the source failed the pre-outcome nesting audit:

`HOLD_SCHEMA_SOURCE_AXES_NOT_NESTED`

The source pigment-chemistry classes and visible/reflectance classes cross-cut, so no three-level nested ladder can be instantiated without changing the estimand after source-schema inspection. No AUC or resolution winner was computed.

### Linoideae / Angraecinae / Antirrhineae — scientifically relevant, not exchangeable

These three radiations support the separate conditional-hierarchy result:

> after fixing a coarse state, finer phenotype identity retains non-random phylogenetic organization.

That is not the same quantity as an unconditional three-resolution AUC profile. Importing these outcomes into moderator training would mix estimands and create a false sample size of four.

## Consequence for Issue #245

The proposed moderator programme is currently data-limited rather than model-limited:

- exact same-estimand outcomes available: **1**;
- frozen minimum before quantitative moderator fitting: **5**;
- current moderator fit: **forbidden**.

No regression, classification tree, one-predictor model or informal score should be fitted to the current outcome set.

## What should happen next

The next work should increase the same-estimand replication count, not tune a predictor to Iris.

Candidate admission should therefore prioritize sources that can be screened without target outcomes for:

1. three source-defined **nested** state resolutions on one phenotype axis;
2. adequate tip/state replication for one common frame;
3. a public branch-length tree or an outcome-blind reconstructable tree;
4. a fixed crosswalk and representation mapping before row-level target values are inspected.

Only after five completed exact-estimand radiations exist should the frozen moderator policy permit at most one predictor, with leave-one-radiation-out performance required to beat an intercept-only baseline.

## Failure modes kept separate

- **Iris:** valid prospective outcome, biological/statistical terminal FAIL of the universal intermediate-ordering prediction.
- **Gesnerioideae:** pre-outcome schema HOLD; not a biological negative and not a profile outcome.

That separation is essential. Counting a schema HOLD as a zero-signal radiation would bias the moderator dataset before it exists.

Camellia Paper 1 remains unchanged and closed.
