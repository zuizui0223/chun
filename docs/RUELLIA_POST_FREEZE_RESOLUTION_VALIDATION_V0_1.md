# Ruellia post-freeze resolution stress test — v0.1

## Role

Ruellia was not used to construct the intermediate pathway-region rule frozen on `main`. The rule had already been merged before the detailed Ruellia source mechanism distribution was extracted. However, Ruellia was not named and preregistered as the next target before source-result inspection, so this is **not** called a prospective validation.

Status:

`EXTERNAL_AFTER_RULE_FREEZE_NOT_TARGET_PREREGISTERED`

Primary source: Zhuang & Manzitto-Tripp 2022, DOI `10.1186/s12862-021-01955-x`.

## Source observation frame

The paper contains a 10-species Ruellia panel with petal transcriptomes, anthocyanidin HPLC, reflectance information and a species phylogeny:

- 4 purple-flowered species;
- 3 red-flowered species;
- 3 yellow-flowered species;
- no petal anthocyanins detected in the three yellow species.

The source authors explicitly did **not** perform formal flower-colour ancestral-state reconstruction because ten terminals are sparse relative to the genus. They described four potential transitions suggested by the 10-tip tree. Therefore this analysis does not promote those transitions to robust independent historical-event counts.

## Frozen prediction being stressed

The previously merged tier synthesis suggested:

1. hue/hydroxylation changes repeatedly localize to branching machinery;
2. pigment loss/depletion often localizes downstream or to pigment-output regulation, but Petunieae raw amount remains unresolved;
3. exact genes and complete implementations are less repeatable than pathway regions.

Ruellia is useful because the same source contains both red/purple hue contrasts and yellow anthocyanin-loss states.

## Hue result — PASS at pathway-region resolution

### Purple -> red context

The source identifies two mechanistic manifestations involving the F3'5'H branch in red taxa within a source-inferred purple-to-red context:

- a premature-stop coding loss of F3'5'H in *R. fulgida*;
- extremely low / unrecovered F3'5'H consistent with regulatory loss in *R. brevifolia*.

These are not counted as two independent macroevolutionary origins. They demonstrate that the source-inferred hue shift is mechanistically centered on the branching/hydroxylation node.

### Red -> purple context

The source interprets the red-to-purple contrast involving *R. elegans* and *R. hirsuto-glandulosa* as putative reactivation/restoration of the F3'5'H branch in petals.

Thus the Ruellia hue component is:

`SUPPORT_BRANCHING_HYDROXYLATION`

After adding Ruellia as an external system-level stress test, hue/branching support becomes **5/5 systems** across the admitted M1/M2/external regimes.

## Yellow depletion result — MIXED counterexample to an output-side-only rule

The three yellow species show a broader expression pattern:

- F3H downregulated in *R. bourgaei* and *R. speciosa*;
- ANS downregulated in all three yellow species;
- the source argues that coordinated downregulation may be more consistent with mutations in shared regulatory genes than with independent structural losses at every locus.

This spans:

- `EARLY_CORE` — F3H;
- `LATE_OUTPUT` — ANS;
- `REGULATORY` — inferred shared regulatory control.

Therefore Ruellia is a genuine mixed-region case and **falsifies the strict formulation that pigment loss/depletion must remain on the downstream/output side**.

The updated six-system depletion tally is:

- downstream/output/regulatory support under the previous classification: **4/6**;
- unresolved: **1/6** — Petunieae raw amount;
- mixed early+late+regulatory counterexample: **1/6** — Ruellia.

These are system tallies, not a pooled effect size.

## Revised biological interpretation

The external stress test sharpens rather than merely confirms the cross-radiation rule:

> **Hue/hydroxylation changes show unusually stable localization to pathway-branching machinery across radiations, whereas pigment loss/depletion is mechanistically broader: often downstream/regulatory, but capable of coordinated early + late pathway suppression.**

This makes the resolution-dependence claim more specific:

- hue axis -> narrow pathway-region predictability;
- loss/depletion axis -> broader module/regulatory predictability, lower exact-region specificity;
- complete molecular implementation -> heterogeneous.

## Boundaries

- Ruellia is not a prospective target-selection test.
- Potential source transitions are not promoted to robust event counts.
- Two red taxa are not counted as two independent purple-to-red events.
- Yellow species are not assumed to represent three independent losses.
- The source provides a stress test of pathway-region localization, not a common cross-clade transition-rate estimator.
- Camellia Paper 1 remains unchanged.
