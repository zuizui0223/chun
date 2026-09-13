# Gesnerioideae resolution-profile schema decision — v0.1

## Decision

**`HOLD_SCHEMA_SOURCE_AXES_NOT_NESTED`**

The fifth-radiation Gesnerioideae profile test stops before row-level outcome ingestion and before any AUC/permutation calculation.

This is the exact stop rule frozen in `data/gesnerioideae_resolution_profile_prereg_v0_1.json`:

> `HOLD_SCHEMA if three nested levels cannot be instantiated without outcome-dependent recoding`

## What was frozen before this decision

PR #249 preregistered three intended state resolutions:

1. coarse — anthocyanin pigmentation present vs absent;
2. intermediate — source-defined major anthocyanin/anthocyanidin biochemical class;
3. fine — source-defined visible hue/reflectance class.

PR #253 then acquired only source-object/workbook schema. Hosted run `34738455036` passed without opening row-level source outcomes. The schema receipt identifies:

- source DOI `10.3389/fpls.2020.604389` / PMCID `PMC7767864`;
- current PMC article prefix `PMC7767864.1/`;
- `Table_1.xlsx`, SHA256 `a84abf67da0afb8c0bafd4c1251dbcbb6dc48eb286dca788e6e88ce0176ccbc8`;
- worksheet `FINAL SAMPLE LIST` (183 rows × 33 columns).

## Why the nesting fails before row-level inspection

The source paper defines two different biological axes:

- pigment chemistry: `HYD90`, `DEO90`, `DEO+HYD`, `NONE`;
- visible/reflectance colour: nine source colour groups.

The coarse presence/absence level can be obtained as a coarsening of the four chemistry groups (`NONE` vs the three anthocyanin-present classes).

The fine visible/reflectance classes, however, are not refinements of those chemistry classes. The published aggregate results already demonstrate cross-cutting membership:

- the source orange/red colour groups contain DEO90, DEO+HYD **and** HYD90 samples;
- the other colour groups (white, cream, yellow, purple, pink and green) contain mostly HYD90 and NONE, plus smaller DEO90 and DEO+HYD fractions.

Therefore a fine visible state cannot be assigned to one intermediate pigment class by a semantics-only many-to-one mapping. Likewise a pigment class spans multiple visible states.

This is a **source-architecture incompatibility**, not a CHUN outcome.

## Why no rescue is allowed

The following would violate the preregistration:

- defining new reflectance thresholds after opening source rows;
- collapsing pigment classes using realized frequencies;
- choosing a hue-to-pigment mapping that improves phylogenetic AUC;
- replacing the frozen fine visible/reflectance axis with exact anthocyanidin composition after seeing the schema conflict.

Any of those changes could define a useful future estimator, but it would be a **new preregistered estimand**, not the frozen Gesnerioideae fifth-radiation test.

## Outcome firewall

At this decision:

- CHUN row-level trait values used for the target test: **no**;
- coarse/intermediate/fine AUC: **not computed**;
- resolution winner: **not computed**;
- 9,999-permutation result: **not computed**.

No `results/gesnerioideae_resolution_profile_v0_1/` directory is permitted to exist under this decision.

## Cross-radiation consequence

Gesnerioideae does **not** enter the same-estimand resolution-profile outcome set and does not increase the training count for the quantitative moderator rule.

This is not evidence that Gesnerioideae lacks phylogenetic colour structure. It means only that this source cannot test the already-frozen three-level nested representation without changing the estimand after source-schema inspection.

## Scientific consequence for the larger programme

The Iris prospective FAIL already rejected a universal `coarse < intermediate > fine` optimum. The Gesnerioideae HOLD adds a second, different boundary: some rich flower-colour datasets do not even admit one common nested resolution ladder because visible colour and biochemical composition are cross-cutting phenotype dimensions.

That strengthens the current programme architecture:

> **flower-colour predictability should be analysed by explicit phenotype dimension and state representation, rather than by assuming that visible hue, pigment chemistry and pigment quantity form one universal hierarchy.**

Camellia Paper 1 remains unchanged and closed.
