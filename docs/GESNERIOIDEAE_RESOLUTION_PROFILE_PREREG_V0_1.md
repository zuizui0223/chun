# Gesnerioideae resolution-profile prospective preregistration v0.1

## Status

**FROZEN BEFORE CHUN ROW-LEVEL GESNERIOIDEAE COLOUR / ANTHOCYANIN OUTCOME INGESTION.**

This analysis follows the terminal prospective Iris result (`FAIL`) and is designed to test whether cross-radiation resolution profiles are heterogeneous rather than to rescue the rejected universal `coarse < intermediate > fine` rule.

## Why Gesnerioideae

The candidate was named before this analysis in `EVOLUTION_SECOND_PROSPECTIVE_CANDIDATE_SCREEN_V0_1.md`. The screen records 180 samples representing 156 species with reflectance, detailed anthocyanin chemistry and a phylogenetic framework (source DOI `10.3389/fpls.2020.604389`). It failed the separate >=30-taxon matched molecular-bridge gate only because a radiation-wide expression/functional panel was not recovered.

That molecular HOLD is irrelevant to the present phenotype-resolution estimand. Gesnerioideae is selected because it supplies a large independent radiation with phenotype, biochemical and phylogenetic layers without having been used to construct the original CHUN intermediate-resolution rule.

## Exposure boundary

Allowed before freeze:

- source identity and DOI;
- reported sample/species count;
- existence of reflectance, anthocyanin chemistry and phylogenetic data;
- schema/column names and taxon identifiers needed for a trait-blind crosswalk;
- phylogeny reconstruction or acquisition that does not use flower-colour or pigment values.

Forbidden before freeze:

- CHUN inspection of row-level realized hue frequencies;
- CHUN inspection of row-level realized anthocyanin-class frequencies;
- any CHUN-computed coarse/intermediate/fine AUC;
- any CHUN-computed winner or PASS/MIXED/FAIL decision;
- threshold tuning using the realized Gesnerioideae outcome distribution.

Prospective label: `ANALYSIS_PROSPECTIVE_NOT_LITERATURE_BLINDED`.

## Primary estimand

Use one common eligible-tip frame for all three nested representations. For each representation, every unordered tip pair is labelled same-state vs different-state. Negative patristic distance predicts same-state membership; ROC AUC is the phylogenetic-predictability score.

The three levels are to be instantiated from source-defined variables without looking at the realized distribution:

1. **coarse** — chromatic anthocyanin pigmentation present vs absent / source-equivalent binary biochemical presence state;
2. **intermediate** — source-defined major anthocyanin / anthocyanidin biochemical class, collapsed only by a mapping frozen from chemical identity semantics rather than frequencies;
3. **fine** — source-defined visible hue / reflectance class, using source categories where available; if continuous reflectance is the only source representation, discretization boundaries must be frozen from an external colour-space convention before values are inspected and may not be optimized on the target data.

If the source schema does not permit these three levels without outcome-dependent recoding, the analysis is `HOLD_SCHEMA` and stops. It is not replaced by a favourable alternative hierarchy.

## Common-frame exclusions

Before outcome values are opened, the pipeline must freeze:

- taxon crosswalk and one-to-one mapping to the tree;
- treatment of duplicate samples / multiple accessions;
- treatment of polymorphic, mixed or ambiguous states;
- minimum state count: any fine state represented by <5 eligible tips is excluded from the common frame before all three AUCs are calculated;
- taxa missing any one of the three primary states are excluded from all three primary analyses.

No exclusion may be introduced because it improves the resolution ordering.

## Null and permutation contract

Use 9,999 joint taxon permutations with fixed seed `20260913`.

The complete `(coarse, intermediate, fine)` state triplet is permuted jointly across eligible tips, preserving marginal state frequencies and cross-resolution dependence while destroying phylogenetic association.

Primary outputs:

- `AUC_coarse`
- `AUC_intermediate`
- `AUC_fine`
- all three pairwise AUC differences
- one-sided empirical p-values for each representation above 0.5
- one-sided empirical p-values for each observed winner-vs-runner-up difference

## Primary decision rule

This fifth-radiation test no longer treats `intermediate` as the privileged expected winner.

Classify the observed profile as:

- `PROFILE_SIGNALLED_COARSE` — coarse AUC > 0.5 with p<=0.05 and coarse exceeds both other resolutions, with winner-vs-runner-up joint-permutation p<=0.05;
- `PROFILE_SIGNALLED_INTERMEDIATE` — intermediate satisfies the corresponding rule;
- `PROFILE_SIGNALLED_FINE` — fine satisfies the corresponding rule;
- `PROFILE_SIGNALLED_TIED` — at least one resolution has AUC>0.5 with p<=0.05 but no unique winner clears the 0.05 winner-vs-runner-up test;
- `PROFILE_NO_PHYLOGENETIC_SIGNAL` — no resolution has AUC>0.5 with p<=0.05.

No post-hoc sensitivity analysis may upgrade `PROFILE_SIGNALLED_TIED` or `PROFILE_NO_PHYLOGENETIC_SIGNAL` to a unique winner.

## Cross-radiation hypothesis being tested

The preregistered Iris result falsified the universal intermediate optimum. The new primary cross-radiation hypothesis is therefore deliberately weaker and directly falsifiable:

> **The identity of the resolution carrying the strongest phylogenetic signal is not invariant across angiosperm radiations.**

For this fifth system, any terminal profile is retained. A unique intermediate winner does not resurrect universality; a non-intermediate winner or no-signal/tied profile adds a second independent system inconsistent with a universal intermediate optimum.

## Moderator rule status

No multivariable radiation-level moderator is fit at this stage. The available biological replication count is too small and the discovery systems were not all measured with this exact AUC estimand. Fitting tree depth, reticulation, ontology type and pathway architecture simultaneously after the Iris outcome would be post-hoc overfitting.

Complexity cap before the next held-out system after Gesnerioideae:

- one biological row per radiation;
- only systems measured with the same primary AUC estimand enter quantitative moderator training;
- at least 5 same-estimand training radiations are required before fitting even a one-predictor moderator;
- maximum moderator complexity at n=5 is one prespecified predictor plus intercept;
- candidate predictor must be outcome-independent for the next held-out target;
- leave-one-radiation-out performance must beat an intercept-only / empirical-frequency baseline before any prospective moderator prediction is authorized.

Thus Gesnerioideae is primarily a **same-estimand profile replication and training expansion**, not a post-hoc moderator confirmation.

## Claim boundary

If Gesnerioideae produces a non-intermediate or tied/no-signal profile, CHUN may state that the pre-frozen intermediate optimum failed prospectively in Iris and did not become a stable cross-radiation winner in the next independent same-estimand profile test.

If Gesnerioideae produces a unique intermediate winner, CHUN may state only that resolution profiles are heterogeneous across the two prospective systems observed so far; Iris remains a terminal falsification of universality.

No outcome permits the words `universal`, `law`, or `optimal resolution for flower colour` without qualification.
