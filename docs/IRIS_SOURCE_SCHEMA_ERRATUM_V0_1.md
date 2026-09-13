# Iris source-schema erratum — v0.1

## Status

**FROZEN AFTER ROW-LEVEL SOURCE INGESTION, BEFORE ANY CHUN IRIS AUC OR RESOLUTION-ORDERING STATISTIC.**

This erratum overlays `data/intermediate_resolution_rule_prereg_v0_1.json`. The original preregistration is not rewritten.

## What was found

The preregistration froze six loci as:

`matK, trnL, trnK, NADPH, rbcL, ITS`

After PR #234 opened the already-frozen accession source, the exact source header was observed as:

`organism, matK, trnL, ndhF, trnK, rbcL, ITS`

The source therefore contains **ndhF** and contains no locus column named `NADPH`.

## Correction

For all subsequent trait-blind phylogeny reconstruction, the preregistered token `NADPH` is interpreted as a source-schema transcription error and replaced by **`ndhF`**.

The effective locus list is therefore:

`matK, trnL, ndhF, trnK, rbcL, ITS`

No seventh locus is added and no source locus is dropped because of trait values or later phylogenetic results.

## Why this is not an outcome-driven protocol change

The mismatch is visible in the accession-file header before any of the frozen outcome statistics are computed. At this point CHUN has inspected row-level trait categories, but has still computed:

- no coarse AUC;
- no intermediate AUC;
- no fine AUC;
- no intermediate-minus-coarse delta;
- no intermediate-minus-fine delta;
- no PASS/MIXED/FAIL classification.

Run `34729493048` is the row-ingestion receipt that first exposed the exact accession structure while explicitly asserting `auc_computed=false` and `decision_computed=false`.

## Everything else remains frozen

This erratum does **not** change:

- coarse/intermediate/fine state definitions;
- exclusion of multi-hue or multi-major-pigment primary rows;
- the >=5-tip fine-state rule;
- the common eligible-tip frame;
- no-imputation rule;
- MAFFT alignment settings;
- trimAl settings;
- partitioned IQ-TREE2 + ModelFinder + 1000 ultrafast bootstrap plan;
- source outgroup/rooting rule;
- source-specified *Iris darwasica* exclusion;
- pairwise same-state AUC definition;
- 9,999 joint permutations;
- seed `20260913`;
- PASS/MIXED/FAIL thresholds;
- prohibition on sensitivity analyses upgrading the primary decision.

## Governance

Any further source-schema inconsistency discovered before AUC execution must be frozen in a new explicit erratum before the statistic is computed. Once the AUC run begins, protocol changes that could alter the primary result are forbidden.

Camellia Paper 1 remains unchanged.
