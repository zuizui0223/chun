# Cross-radiation phenotype-axis → molecular-localization gate — v0.1

Frozen: 2026-09-11, **before extracting any new detailed molecular-localization outcomes beyond the already-known Iochrominae, Cape Erica, and prospectively frozen Petunieae bridge results.**

## Purpose

Test a narrower and more falsifiable generalization than the failed full two-axis Petunieae bridge:

> **Does the molecular location associated with flower-colour variation depend on which phenotype dimension is resolved? In particular, is hue/hydroxylation more reproducibly localized to pathway-branching machinery than pigment amount/intensity/presence?**

This is a retrospective cross-radiation synthesis with one prospective anchor (Petunieae hue). It is **not** a prospectively designed meta-analysis and must never be described as one.

## Existing anchors known before this gate

These three systems are prior evidence, not newly discovered outcomes:

1. **Iochrominae** — retrospective matched two-axis alignment under the v0.5 bridge definition.
2. **Cape Erica** — retrospective matched two-axis alignment under the same high-level definition.
3. **Petunieae** — first prospectively specified bridge test; frozen classification `PETUNIEAE_PROSPECTIVE_BRIDGE_MIXED`, with a strong hue→`BRANCHING_HUE` component and a non-supportive preregistered raw amount axis.

Their already-known outcomes may be entered exactly as frozen. They cannot be relabelled to improve the synthesis.

## Search/admission universe for additional systems

Additional systems must be recovered from **all** of the following, not selected because their result is convenient:

1. the existing `chun` cross-clade / mechanistic atlas and its cited primary sources;
2. backward and forward citation links from the admitted Iochrominae, Erica, and Petunieae sources;
3. fixed database/web queries combining flower colour/pigment terms with comparative molecular/genetic/transcriptomic terms and one of the phenotype-axis terms below.

A candidate is screened at the level of an independent evolutionary clade/system, not at the level of individual papers. Multiple papers on the same biological system are collapsed before analysis.

The initial candidate names already visible in programme notes or broad prior reading include **Phlox, Penstemon, Antirrhinum/Antirrhineae, Ruellia, and Ipomoea**. Naming a candidate here is not admission and does not prespecify its molecular category.

## Phenotype-axis classes — fixed before new extraction

### HUE
Admit only when the source directly distinguishes pigment composition, anthocyanidin/hydroxylation chemistry, spectral hue attributable to pigment composition, or a genetically/biochemically explicit hue shift. Pure human colour words without an independently resolved hue dimension are insufficient.

### AMOUNT_INTENSITY
Admit pigment presence/absence, total pigment abundance, quantitative intensity/saturation, or a directly defined depletion/gain axis. Pattern-only changes are excluded from the primary analysis unless the source separately quantifies pigment amount/intensity.

### OTHER_PATTERN
Pattern/spatial-placement phenotypes may be retained descriptively but are not part of the primary HUE versus AMOUNT_INTENSITY test.

If one system contains both HUE and AMOUNT_INTENSITY axes, retain both as separate axis rows tied to the same `system_id`.

## Molecular-localization classes — fixed before new extraction

Classify the best-supported molecular location for each admitted axis into exactly one primary category:

- `BRANCHING_HYDROXYLATION` — branch-choice / hydroxylation machinery such as F3'H, F3'5'H, branch-specific modification enzymes, or a source-defined homologous branch-choice module;
- `LATE_OUTPUT` — downstream anthocyanin/output machinery such as DFR, ANS/LDOX, UFGT/GST where the evidence is output-localized rather than branch-choice;
- `REGULATORY` — MYB/bHLH/WD40 or other source-demonstrated regulatory control without a uniquely localized structural branch target;
- `EARLY_CORE` — CHS/CHI/F3H or homologous shared early-core machinery;
- `DISPERSED_MULTIPLE` — independent evidence implicates multiple non-equivalent subspaces and no single localization is defensible;
- `UNRESOLVED` — evidence is insufficient to assign one of the above.

`BRANCHING_LOCALIZED = 1` only for `BRANCHING_HYDROXYLATION`; all other resolved categories are 0. `UNRESOLVED` is missing in the primary binary test, not 0.

## Evidence tiers — fixed

- **Tier A:** causal genetic/functional evidence, mapped causal locus with molecular identity, transgenic/knockout/complementation evidence, or directly demonstrated enzyme-function change.
- **Tier B:** matched comparative expression/biochemical/genetic association across the same admitted system with a source-supported molecular localization.
- **Tier C:** candidate-only narrative, single-species expression without comparative axis contrast, or review-level inference.

Primary synthesis uses Tier A+B only. Tier C is retained in the ledger but excluded from the primary statistic.

## Independence and collapse rules

1. Primary biological unit = `system_id × phenotype_axis_class`.
2. Nested papers from the same radiation/system do not count as independent replicates.
3. When several sources address the same axis in one system, use the highest evidence tier; ties are combined. Conflicting Tier-A/B sources force `DISPERSED_MULTIPLE` or `UNRESOLVED`, not selective source choice.
4. A clade can contribute both HUE and AMOUNT_INTENSITY rows, but dependence is recorded explicitly.
5. No visible hue may be used to infer an unmeasured molecular state.

## Primary estimand

Primary effect:

`P(BRANCHING_LOCALIZED | HUE) - P(BRANCHING_LOCALIZED | AMOUNT_INTENSITY)`

reported as raw proportions, risk difference, and odds ratio where defined.

Because some systems contribute both axes and the number of independent radiations is expected to be small, no asymptotic mixed-model P value is primary.

### Primary exact test

For systems with **both** eligible HUE and AMOUNT_INTENSITY rows, use the paired discordance/sign test on `BRANCHING_LOCALIZED`. Report the exact one-sided probability for the prespecified direction HUE > AMOUNT_INTENSITY and the two-sided value.

### Broader secondary test

Across all independent system-axis rows, report Fisher's exact test for HUE versus AMOUNT_INTENSITY × BRANCHING_LOCALIZED, explicitly treating it as a secondary approximation because paired systems contribute two rows.

### Required robustness

- leave-one-system-out proportions and effect direction;
- Tier-A-only sensitivity;
- matched-two-axis-systems-only result;
- prospective-anchor-excluded result;
- retrospective-only versus Petunieae prospective component shown separately;
- `UNRESOLVED` rows never converted to negatives.

## Predeclared interpretation classes

### `AXIS_LOCALIZATION_SUPPORTED`
Requires all of:

1. at least 5 independent systems with Tier A/B evidence overall;
2. at least 3 independent HUE systems and 3 AMOUNT_INTENSITY systems;
3. at least 3 systems contain both axes;
4. HUE branching-localized proportion exceeds AMOUNT_INTENSITY by >=0.35;
5. the effect direction remains HUE > AMOUNT_INTENSITY in every leave-one-system-out analysis;
6. at least one prospective component supports the HUE→branching prediction without post hoc relabelling.

The exact paired P value is reported but is **not** required to cross 0.05 because the system count is expected to be small; magnitude, independence, and leave-one-system-out stability are the predeclared admission criteria.

### `AXIS_LOCALIZATION_MIXED`
Coverage items 1–3 pass, but effect size <0.35, leave-one-system-out direction is unstable, or evidence differs materially by tier.

### `AXIS_LOCALIZATION_HOLD`
Coverage items 1–3 do not pass.

### `AXIS_LOCALIZATION_CONTRADICTED`
Coverage is adequate and AMOUNT_INTENSITY is at least as branching-localized as HUE, or the HUE-specific branching localization fails under the required robustness checks.

## Evolution journal escalation gate

This synthesis may trigger a new *Evolution* manuscript/editorial gate only if:

- classification = `AXIS_LOCALIZATION_SUPPORTED`;
- Petunieae remains exactly MIXED at the full two-axis bridge level and only its preregistered hue component is counted as prospective support;
- the result is presented as **dimension-specific molecular localization**, not a universal whole-phenotype mapping law;
- at least one leave-one-system-out analysis excluding each retrospective anchor retains the direction;
- prior-art audit confirms that this exact cross-radiation axis-specific localization comparison is not already established.

Even if supported, do **not** silently rewrite the frozen Camellia AJB Paper 1. Build a separate general-evolution manuscript architecture first and compare it prospectively against the frozen AJB route.

## Non-negotiable boundaries

- No outcome-driven system admission.
- No post hoc transformation may upgrade the frozen Petunieae amount result.
- No paper-level pseudoreplication within a clade.
- No universal causal-gene claim.
- No common ecological-driver claim from this analysis.
- No pooling of HUE and AMOUNT_INTENSITY into a single coarse “colour” state.
- Paper 1 science remains unchanged until a separate editorial gate explicitly authorizes a new manuscript.

Current state at freeze:

`AXIS_SPECIFIC_GENERALIZATION_GATE_FROZEN_BEFORE_NEW_DETAILED_EXTRACTION`
