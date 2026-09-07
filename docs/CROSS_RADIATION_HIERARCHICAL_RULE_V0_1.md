# Cross-radiation hierarchical flower-colour rule v0.1

## Current result

Three external radiations now have source-to-tree flower-colour history reanalyses in this repository: Hydrangea sect. Cornidia, Linoideae and Angraecinae. Applying their frozen/authoritative summaries to a common decision layer gives two distinct conclusions.

1. **No universal WHITE transition direction is supported.** None of the three radiations passes a strong directional-asymmetry gate under its retained tree/source uncertainty.
2. **A finer hierarchical organization signal is replicated where a nested state representation is actually testable.** Linoideae retains hue-specific phylogenetic structure after conditioning on WHITE/nonwhite status; Angraecinae retains four-organ configuration structure after conditioning on primary GREEN/WHITE status. Both currently testable external radiations support this conditional fine-state pattern.

The supported result is therefore a replicated **candidate rule**, not a universal law:

> Coarse ancestral/display state constrains the evolutionary state space without fixing a universal transition direction; phylogenetic organization can persist at finer hue or organ levels after conditioning on the coarse colour class.

## Why this is not a directional WHITE-ancestor law

### Hydrangea sect. Cornidia

Independent source-to-tree reanalysis gives coloured-to-WHITE point rate ratios above 1, but the fixed-tree profile intervals include equal rates and AIC support is insufficient under the strong-direction criterion. Root WHITE probability is also model/prior dependent rather than robust.

### Linoideae

Under primary UNION coding, regular full and ITS point estimates lean in the opposite direction (WHITE->nonwhite), but ER/source sensitivities and profile behavior prevent a source-independent directional claim. A robust WHITE root is not admitted.

### Angraecinae

This is the strongest ancestry-direction separation. Across two independently executed three-tree reconstruction sets, the minimum root P(WHITE) across the retained primary analyses is **0.875**, so the pre-frozen robust-WHITE criterion passes. Yet the pre-frozen directional-rate criterion fails in both reconstruction sets.

Thus robust WHITE ancestry is **not sufficient** for a supported transition direction.

## Replicated conditional fine-state result

### Linoideae: hue within WHITE status

The conditional null keeps each tip's WHITE/nonwhite/ambiguous status fixed and exchanges complete hue-state vectors only within those classes. Across 54 correlated sensitivity settings, all tests have `p=0.0001`; observed/null minimum-change score ratios are **0.263-0.611**.

This does not mean 54 independent replications. It means one radiation retains the same qualitative fine-state organization across tree, source-coding and exclusion sensitivities.

### Angraecinae: organ configuration within GREEN/WHITE status

The analogous test fixes the primary sepal GREEN/WHITE class and exchanges complete sepal/petal/labellum/spur state vectors only within that class. Across two independently executed ML reconstruction sets x three tree variants, all six tests have `p=0.0001`; observed/null ratios are **0.513-0.549**.

The source trait matrix also shows why this state space matters: among 170 source rows that are GREEN/WHITE in all four organs, 46 (27.1%) are organ-discordant. A one-organ representation discards roughly 47-50% of the equal-row joint-state entropy.

## What Hydrangea contributes to this rule

Hydrangea is part of the three-radiation **directional** audit, but it is not counted as a third positive fine-state replication. The current Cornidia ingroup reanalysis is WHITE/RED only; the published PURPLE terminal observations used in earlier discussion belong to outgroups. Therefore there is no comparable nested hue-within-coarse-state ingroup test to run without inventing additional states.

This exclusion is intentional. The denominator for the fine-state replication claim is presently **2 testable radiations, 2 supporting**, not three.

## Relation to Camellia and Epimedium

Camellia remains the focal system but is not promoted as a third fine-state replication here. An exploratory WFO55 A/Y-within-nonwhite test was topology sensitive and low-powered under strict wild-colour coding, so it does not satisfy the same robustness standard.

Epimedium independently reinforces the measurement-grain lesson because ancestral visible colour is organ specific and molecular accessions cannot yet be mapped safely to independent historical events. It is useful triangulation, but it is not counted as an additional source-to-tree replication of the conditional fine-state test.

## New scientific position

The programme has therefore moved beyond the original broad idea that a WHITE-like ancestral radiation should preferentially gain colour. The stronger empirically bounded statement is:

- **ancestry and direction are separable**;
- **coarse WHITE/nonwhite state is often an insufficient evolutionary representation**;
- **repeatable phylogenetic organization can reside at finer state-space levels such as hue and floral-organ configuration**.

The result is more specific than generic phylogenetic conservatism because the null explicitly preserves the coarse colour class and asks whether additional organization remains in a nested finer state.

## Next falsification gate

Do not promote the candidate to a general flower-colour law until at least one additional independent radiation supplies a nested fine-state representation that can be tested with the same conditional-null logic. A useful third replication must be a new biological radiation; extra trees, alignments, source codings or reconstruction repeats from an existing radiation do not increase the replication count.

Mechanistic recurrence remains a separate layer. Gene/region/regulatory-module reuse should only be pooled after historical transition identity and phenotype-to-tree mapping are independently defensible.

## Reproducibility

`data/cross_radiation_hierarchical_rule_v0_1.json` is not hand-maintained evidence. `scripts/summarize_cross_radiation_hierarchical_rule_v0_1.py` reads the authoritative Hydrangea, Linoideae and Angraecinae summaries and regenerates the cross-radiation result. CI fails if the derived result drifts from the frozen cross-radiation JSON.

Paper 1 science and manuscript files are unchanged.
