# Hierarchy specificity control — v0.1 result

## Question

The merged cross-radiation result showed fine-state phylogenetic organization in three independent systems after conditioning on a selected coarse state. This control asks a stricter question:

> Are the selected biological coarse boundaries themselves unusually informative compared with every alternative non-trivial bipartition of the same fine-state alphabet?

The alternative-partition space and interpretation thresholds were frozen before results in `HIERARCHY_SPECIFICITY_PRE_RESULT_GATE_V0_1.md`.

## Result

The answer is **no at the cross-system level**.

### Linoideae

Across 54 retained settings and all 31 bipartitions of the six-colour alphabet, the biological WHITE | non-WHITE partition is not enriched relative to alternatives.

- biological-partition rank percentile: min 0.667, median 0.900, max 1.000 (lower is better);
- capture fraction: min 0.011, median 0.088, max 0.213;
- top-quartile settings: 0/54;
- classification: `BIOLOGICAL_PARTITION_NOT_ENRICHED`.

The previously established conditional hue signal remains valid: hue organization persists after WHITE/non-WHITE is fixed. What fails is the stronger interpretation that WHITE/non-WHITE is a privileged coarse constraining boundary.

### Angraecinae

Across six retained tree-reconstruction settings and all 15 bipartitions of the five observed four-organ patterns:

- biological-partition rank percentile: min 0.071, median 0.464, max 0.500;
- capture fraction: min 0.507, median 0.521, max 0.545;
- top-quartile settings: 2/6;
- classification: `INTERMEDIATE_PARTITION_SPECIFICITY`.

The primary GREEN/WHITE boundary captures substantial structure, but it is not consistently the uniquely best partition.

### Antirrhineae

Across 40 posterior-tree settings and all three bipartitions of the source-native pigment alphabet 0/1/2, the biological unpigmented | pigmented partition is not enriched.

- biological-partition rank percentile: min 0.500, median 1.000, max 1.000;
- capture fraction: min -0.012, median 0.172, max 0.349;
- top-quartile settings: 0/40;
- classification: `BIOLOGICAL_PARTITION_NOT_ENRICHED`.

Anthocyanin-versus-yellow organization conditional on pigment presence remains supported, but pigment presence is not the privileged partition of the three source states.

## Cross-radiation consequence

The pre-frozen decision rule classifies the overall result as:

`GENERIC_FINE_STATE_ORGANIZATION_MORE_LIKELY`

Therefore the cross-system claim that the selected coarse boundaries form a shared constraining evolutionary layer is dropped.

What survives is stronger as a representation result but narrower biologically:

> **Flower-colour evolution is not collapsible to one privileged coarse state representation. Fine-state phylogenetic organization is reproducible across independent radiations, while the coarse boundary that best captures that organization is system dependent.**

This retains the 3/3 independent fine-state replication but rejects the stronger common-boundary interpretation.

## Boundaries

- The alternative partitions are mathematical controls, not necessarily biological hypotheses.
- `capture` measures how much of the fine-state organization gap is removed by conditioning on a partition; it is not an effect size for selection or adaptation.
- Sensitivity trees/settings are not independent biological replications.
- This analysis does not infer ecological causes, molecular mechanisms, dated rates, or a universal direction of flower-colour evolution.
- Camellia Paper 1 remains unchanged.
