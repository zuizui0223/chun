# Hierarchy specificity control — pre-result gate v0.1

## Question

The merged v0.2 result shows that fine flower-colour state remains phylogenetically organized after conditioning on a biologically motivated coarse state in three independent radiations.

That result has a serious alternative explanation:

> fine colour states may simply have phylogenetic signal, so almost any coarse partition could leave significant residual structure.

This control is frozen before examining any alternative-partition result. It asks whether the selected biological coarse boundary captures an unusually large share of the fine-state phylogenetic organization relative to **all non-trivial two-way partitions of the same fine-state alphabet**.

The existing 3/3 conditional-signal result is not erased by this control. What changes is the interpretation of the word **constraint**.

## Common statistic

For a fixed tree, fine-state observations and source coding:

1. `S_obs` = observed Sankoff minimum-change score of the fine state.
2. `U` = mean score under 999 unconditional exchanges of whole fine-state observation vectors among tips.
3. For each candidate coarse bipartition `P`, `C_P` = mean score under 999 exchanges of whole fine-state vectors **only within the coarse classes induced by P**.
4. Define the coarse-capture fraction

`capture(P) = (U - C_P) / (U - S_obs)`.

Interpretation:

- `capture > 0`: conditioning on P preserves some of the fine-state phylogenetic organization that is destroyed by the unconditional null;
- `capture = 0`: P explains none of that organization;
- `capture < 0`: P is less aligned with the observed organization than an unconditional shuffle;
- values are not clipped at 0 or 1.

Because the same `S_obs` and `U` are used for every partition within a sensitivity setting, partitions are ranked by decreasing `capture` without pooling incomparable effect sizes across radiations.

Alternative-partition controls use 999 permutations (`seed=20260907`). The original positive residual-signal tests remain the higher-precision 9,999-permutation analyses already frozen in the source reanalyses.

## Exhaustive partition spaces

Complementary labels define the same two-way conditioning, so complements are counted once.

### Linoideae

Fine alphabet: `WHITE, YELLOW, BLUE, PURPLE, RED, PINK`.

All **31** unique non-trivial bipartitions are enumerated. The biological partition is `WHITE | all non-WHITE hues`.

For ambiguous allowed-state vectors, each tip is classified as:

- entirely on side A;
- entirely on side B;
- crossing both sides (ambiguous).

Whole allowed-state vectors are shuffled only within those classes, exactly generalizing the existing WHITE/non-WHITE/ambiguous conditional null.

Sensitivity scope is the existing conditional-hue design: three frozen trees x three source codings (`FIGURE2`, `FIGURES5`, `UNION`) x three deterministic one-source-binomial draws x crop included/excluded = **54 settings**.

### Angraecinae

Fine alphabet is the five observed exact four-organ GREEN/WHITE patterns in the frozen 169-tip analysis.

All **15** unique non-trivial bipartitions of those five patterns are enumerated. The biological partition is the primary sepal/petal GREEN | WHITE projection. Sepal and petal are identical among the fully-binary tips; labellum and spur remain part of the fine pattern.

Sensitivity scope: both retained ML reconstruction sets x three frozen trees = **6 settings**.

### Antirrhineae

Fine alphabet currently observed in the source tables: `0=unpigmented, 1=anthocyanin, 2=yellow`.

All **3** unique non-trivial bipartitions are enumerated. The biological partition is `0 | {1,2}` = unpigmented | pigmented.

Sensitivity scope: the same 20 deterministic posterior trees in the monomorphic primary dataset and the same 20 in the polymorphic sensitivity dataset = **40 settings**.

The historical ISTA checksum drift remains part of the source contract.

## Per-radiation rank summary

Within every sensitivity setting:

- rank 1 = partition with the largest `capture`;
- percentile = `(rank - 1) / (N_partitions - 1)`;
- lower percentile means stronger alignment of the coarse partition with the fine-state organization.

For the biological partition, record the full rank/percentile distribution and median capture fraction across sensitivity settings.

A radiation is classified **BIOLOGICAL_PARTITION_ENRICHED** if:

1. median biological-partition percentile <= 0.25; and
2. median biological-partition capture fraction > 0.

It is classified **BIOLOGICAL_PARTITION_NOT_ENRICHED** if:

1. median percentile >= 0.50; or
2. median capture fraction <= 0.

Otherwise it is **INTERMEDIATE_PARTITION_SPECIFICITY**.

These thresholds are frozen before results and will not be relaxed.

## Cross-radiation interpretation gate

- **BOUNDARY_SPECIFICITY_SUPPORTED_ACROSS_SYSTEMS**: at least 2/3 radiations are `BIOLOGICAL_PARTITION_ENRICHED` and none is `BIOLOGICAL_PARTITION_NOT_ENRICHED`.
- **GENERIC_FINE_STATE_ORGANIZATION_MORE_LIKELY**: at least 2/3 are `BIOLOGICAL_PARTITION_NOT_ENRICHED`.
- Otherwise: **MIXED_BOUNDARY_SPECIFICITY**.

Claim consequences:

- If boundary specificity is supported, the v0.2 wording that biologically defined coarse state **constrains** the nested state space is strengthened.
- If mixed, retain the 3/3 empirical statement that fine-state organization survives biologically motivated conditioning, but soften the stronger coarse-constraint interpretation.
- If generic, drop the claim that the selected coarse boundaries are a common constraining layer; retain only the 3/3 fine-state phylogenetic-organization result.

## Boundaries

This is a specificity/control analysis, not a new biological replication. Partition tests within a radiation are not independent clades. No ecological cause, molecular mechanism, transition-rate direction or universal law is inferred.

Paper 1 remains unchanged.