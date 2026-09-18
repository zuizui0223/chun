# Abiotic heterogeneity as a flower-color memory moderator — preregistration v0.1

## Biological hypothesis

The 51-clade companion macroecological study shows that flower colors are associated with mean annual temperature, aridity, and UV-B across the same broad study system. We therefore test one ecological explanation for CHUN's between-clade memory heterogeneity:

> clades spanning more heterogeneous abiotic niches should retain weaker phylogenetic flower-color memory.

The logic is that repeated exposure to divergent abiotic regimes can increase opportunities for environment-associated color shifts, eroding state retention across evolutionary depth.

## Retrospective boundary

Flower-color memory outcomes are already known. This is therefore a retrospective moderator analysis, not a held-out prospective test. To reduce flexibility, the predictor and construction rule are frozen before CHUN downloads or inspects the PHAIDRA environmental files.

## Frozen predictor

Use only the public PHAIDRA collection linked by Dellinger et al. (2026), `o:2098641`.

For each matched species:

1. summarize retained occurrences by the median mean annual temperature, aridity, and UV-B;
2. z-score the three species-level environmental summaries across all matched species;
3. within each clade, calculate the coordinate-wise median environmental centroid;
4. define clade abiotic heterogeneity as the median Euclidean distance of species environmental centroids from that clade centroid.

Species are equally weighted at the clade stage regardless of occurrence count.

A clade is HOLD if fewer than 80% of the species in its CHUN fine-color memory frame match the environmental source.

## Frozen test

Primary outcome: fine visible flower-color signed excess-retention area.

Prediction: higher abiotic heterogeneity -> lower memory area.

Primary statistic: Spearman rho, expected negative, with 99,999 clade-label permutations (seed 20260918). PASS requires rho < 0 and one-sided P <= 0.05.

Temperature-, aridity-, and UV-B-specific dispersion are secondary diagnostics only and cannot rescue a failed composite test.

## Source gate

Before any environmental values are opened, CHUN will inventory PHAIDRA collection `o:2098641` through the public API and freeze member identifiers, filenames, MIME types and sizes. If the public source cannot be recovered, the analysis becomes HOLD. It will not substitute a fresh GBIF reconstruction in the same test.

Camellia Paper 1 and frozen EL v0.2 remain unchanged.
