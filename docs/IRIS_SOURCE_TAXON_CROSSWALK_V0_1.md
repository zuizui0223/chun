# Iris source taxon crosswalk — v0.1

## Status

**SOURCE-LABEL CROSSWALK FROZEN BEFORE TREE CONSTRUCTION AND BEFORE ANY IRIS AUC.**

The two frozen PMC source tables use slightly different labels for a small number of the same sampled taxonomic units. This crosswalk resolves only source-label identity. No flower-colour or pigment value is used to admit a mapping.

## Explicit mappings

Five mappings are required beyond the generic source-binomial join:

1. `Iris albertii Regel` -> `Iris_alberti`
2. `Iris albo-marginata R.C. Foster` -> `Iris_albomarginata`
3. `Iris linifoia (Regel) O. Fedtschenko` -> `Iris_linifolia`
4. `Iris mandschurica Maxim` -> `Iris_mandshurica`
5. `Iris spuria subsp. sogdiana Bunge` -> `Iris_sogdiana`

The first four are source orthography/typography variants. The fifth is an explicit infraspecific-to-accession source-label mapping needed because the trait table also contains a separate `Iris spuria subsp. spuria` row.

## Generic join

After removing the five explicitly reserved accession labels, all remaining source rows are joined by genus + species epithet. Rank suffixes and nomenclatural authors are ignored only for the join key. This permits source pairs such as a species-level trait label and a subspecies/variety accession label to identify the same sampled source unit without using trait outcomes.

## Required closure

The validator must establish:

- 226 trait rows;
- 226 distinct accession rows matched one-to-one;
- no missing, ambiguous or duplicate mapped accession row;
- exactly two accession rows remain outside the trait frame:
  - `Iris_cedretii` — tree-only, no trait row;
  - `Iris_darwasica` — source-specific exclusion, no trait row.

Thus the trait analysis can use at most 226 tips while the source phylogeny input contains the additional tree-only taxon before the frozen *I. darwasica* exclusion.

## Outcome firewall

The crosswalk validator reads only the `Species` column from the trait workbook. It does not read `Colour`, `Pigment`, or `Bic`, does not calculate patristic distances, and does not calculate coarse/intermediate/fine AUC or PASS/MIXED/FAIL.

Any later taxon remapping after AUC exposure is forbidden for the primary analysis unless a concrete source-identity error is documented as a new erratum and the original primary result is retained.

Camellia Paper 1 remains unchanged.
