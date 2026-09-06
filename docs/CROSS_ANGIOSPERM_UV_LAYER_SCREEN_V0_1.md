# Cross-angiosperm UV / pollinator layer screen — v0.1

## Candidate dataset

Oliveira et al. 2026 (`10.1111/plb.70138`) is potentially valuable for the ecological tier of the atlas because it combines:

- floral hue;
- UV reflectance;
- the visually conspicuous floral attractant organ;
- pollinator class (bee or bird);
- phylogenetic comparative models across a broad angiosperm sample.

It is especially relevant to the atlas claim that `human-visible hue != complete ecological phenotype`.

## Why it is not admitted yet

The article narrative contains sample-frame statements that cannot currently be reconciled from text alone.

### Primary sample-size statements

- Abstract: 245 species.
- Methods: 245 species, 180 genera, 71 families.
- Figure 2 caption: 245 species, 205 genera, 76 families.
- Supporting Table S1 description: list of 245 plant species.

The species count is repeatedly stated as 245, but genus/family counts differ.

### Hue-category abundance statement

The Methods lists:

- cyan 2;
- green 3;
- black 3;
- blue 24;
- pink 46;
- yellow 47;
- white 75;
- red 94.

These counts sum to **294**, not 245.

### Results subsets

The white-red set is reported as:

- red 94;
- white 74;
- other 124;

which sums to **292**.

The yellow set is reported as:

- yellow 46;
- other 246;

which also sums to **292**.

The UV binary counts are:

- UV− 197;
- UV+ 93;

which sum to **290**.

These discrepancies may reflect different filtering stages, missing values, a stale narrative denominator, or version/text errors. The atlas does **not** choose among those explanations without inspecting the row-level supplement.

## Arbitration source

The article states that all supporting datasets are in Supporting Information and identifies:

`PLB-28-201-s001.docx` — 88.4 KB

Table S1 is described as the 245-species list and contains:

- botanical classification;
- attractant structure;
- geographic distribution;
- visitor/pollination categories;
- hue category;
- UV reflection value;
- pollinator references.

That file is therefore the only admissible source for the atlas row count and category denominators.

## Compatibility with the atlas

The dataset has a major design advantage: attractant structures are already typed as petal, sepal, bract or stamen. This matches the atlas rule that colour must be attached to a display organ rather than reduced to one whole-flower hue.

If admitted, the normalized unit will be:

`taxon × attractant organ × visible hue × UV state/value × pollination system × provenance`.

The source's single dominant bee/bird pollinator category remains a coarse ecological label and must not overwrite more detailed within-clade pollinator evidence where available.

## Admission gate

Current status:

**HOLD — TABLE S1 BINARY RECONCILIATION REQUIRED**

Promote only after:

1. `PLB-28-201-s001.docx` is ingested and checksummed;
2. the actual row count and unique taxon count are calculated;
3. hue-category counts are recomputed from rows;
4. UV+/UV− counts and missingness are recomputed;
5. genus/family counts are recomputed;
6. duplicated species or multiple-attractant-organ rows, if present, are identified explicitly;
7. the 245/290/292/294 narrative discrepancy is explained by the row structure rather than guessed.

## Scientific role if admitted

This dataset would not test white-ancestor diversification. It would enter the **ecological filtering / sensory phenotype tier** as an angiosperm-wide control demonstrating that UV and visible hue evolve jointly with pollinator context and that hue categories alone do not define a unique sensory regime.

Paper 1 remains unchanged and closed.
