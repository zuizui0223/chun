# UV-pollinator ecology layer quality screen v0.1

## Candidate source

Oliveira et al. 2026, *Plant Biology*, DOI `10.1111/plb.70138`, reports a broad comparative dataset of floral spectral reflectance, hue and dominant bee/bird pollination for 245 angiosperm species. This is conceptually attractive for the cross-clade atlas because it directly supports the distinction between coarse human-visible hue and pollinator-facing sensory phenotype.

## Why this layer is not yet admitted

The article text contains internally incompatible count statements that cannot all describe one 245-species terminal dataset.

### Declared dataset size

- abstract / Methods: 245 species;
- Supporting Information description of Table S1: 245 species;
- Methods: 180 genera and 71 families.

### Results counts

White-red analysis set:

- red = 94;
- white = 74;
- other = 124;
- arithmetic total = **292**.

Yellow analysis set:

- yellow = 46;
- other = 246;
- arithmetic total = **292**.

UV binary summary:

- UV− = 197;
- UV+ = 93;
- arithmetic total = **290**.

Fig. 2 caption separately states that the 245 species span **205 genera and 76 families**, conflicting with the Methods values of 180 genera and 71 families.

These discrepancies could reflect duplicated records, different analysis subsets, a manuscript-version mismatch, or simple reporting errors. The current screen does not assume which explanation is correct.

## Biological relevance retained

The conceptual result remains useful as prior evidence:

- hue and UV state are evolutionarily labile;
- red bee- and bird-pollinated flowers differ in fitted UV optima;
- white and yellow categories show different evolutionary parameter patterns;
- therefore visible hue alone is not a sufficient ecological state representation.

However, the dataset is **not** used as an atlas row source or pooled ecological layer until its terminal rows are reconciled.

## Required reconciliation gate

Admission requires the actual Table S1 rows to be ingested and audited for:

1. exact unique species count;
2. duplicate species or multiple floral-structure records;
3. exact genus/family counts under the table taxonomy;
4. hue-category sums;
5. UV+/UV− classification counts;
6. pollinator-category missingness and exclusivity;
7. attractant-structure field (`P`, `SP`, `B`, `ST`) so organ identity can be preserved rather than collapsed to generic flower colour.

Only after those checks explain the published count discrepancies can this layer move from `HOLD` to `ADMIT`.

## Current verdict

`ECOLOGY_TIER_ADMISSION = HOLD_COUNT_RECONCILIATION_REQUIRED`

This is a data-quality hold, not a rejection of the biological study.

## Boundary

Post-Paper-1 only. This screen does not change Camellia Paper 1 science, AJB v1.0, or any historical branch claim.
