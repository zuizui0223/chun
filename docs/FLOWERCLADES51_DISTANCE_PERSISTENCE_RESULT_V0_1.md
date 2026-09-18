# Flower-clades-51 relative-time persistence spike — v0.1

## Question

Does the original time-axis idea survive after the cross-radiation resolution result?

Rather than asking only whether negative patristic distance discriminates same-state pairs (AUC), this retrospective extension asks how same-state retention changes continuously as phylogenetic separation increases.

The analysis reuses the exact frozen Flower-clades-51 source objects and the already-frozen common-frame hierarchy. Exact source SHA-256 digests match the prior batch receipt.

## Time-axis boundary

All 28 clades that pass the existing common-frame gate are numerically ultrametric:

- median root-to-tip CV: `2.14e-16`;
- maximum root-to-tip CV: `2.98e-11`;
- 28/28 have root-to-tip CV <= `1e-8`.

Therefore normalized within-clade patristic separation can be read as **relative divergence depth/time**. It is not calibrated absolute time and no Ma-scale claim is made.

## Estimand

For each clade and each frozen phenotype resolution:

1. retain exactly the same common tip frame used by the resolution-profile analysis;
2. calculate every unordered pair's patristic separation and same-state indicator;
3. normalize pairwise distance by that clade's maximum distance;
4. split pairs into ten equal-count distance bins;
5. calculate same-state probability within each bin;
6. subtract the exact without-replacement same-state probability implied by that clade's state frequencies, then scale by the available range above baseline.

This yields an excess-retention curve. The primary descriptive contrast is excess retention in the nearest bin minus the farthest bin. Cross-clade inference treats **clade**, not species pair, as the replication unit.

## Result: flower color has phylogenetic memory across relative time

The near-minus-far excess-retention contrast is positive in:

| resolution | positive clades | median contrast | one-sided sign P | Wilcoxon P |
|---|---:|---:|---:|---:|
| coarse | 20/28 | 0.172 | 0.0178 | 0.0102 |
| intermediate | 21/28 | 0.152 | 0.00627 | 0.00411 |
| fine | 19/28 | 0.151 | 0.0436 | 0.00354 |

The fitted binned decay slope is also negative in 19/28 coarse, 21/28 intermediate and 20/28 fine clades.

Thus the positive result is not that one phenotype resolution universally wins. It is that **flower-color state sharing generally decays with relative evolutionary separation**: flower color retains phylogenetic memory through relative evolutionary time.

## Result: the temporal memory has no privileged resolution

Paired clade-level comparisons of near-minus-far persistence give no detectable difference among the three representation levels:

- coarse vs intermediate: Wilcoxon two-sided P = `0.528`;
- coarse vs fine: P = `0.689`;
- intermediate vs fine: P = `0.722`.

The time-axis result therefore complements, rather than replaces, the existing resolution-profile result:

> Flower-color similarity generally decays with evolutionary divergence, but there is no universal phenotypic resolution at which that temporal memory is strongest.

This is biologically stronger than a pure character-coding claim. It separates two questions:

- **memory existence:** does flower-color state persist over evolutionary separation? — broadly yes across the standardized clade batch;
- **memory representation:** at which phenotype resolution is that persistence most visible? — heterogeneous among clades, with no universal privileged scale.

## Interpretation boundary

This is a retrospective analysis of an already-opened dataset. It does not identify the ecological cause of persistence or turnover, does not treat pairwise species comparisons as independent replicates, and does not estimate absolute persistence duration in millions of years.

The next biological target is therefore not another generic coding demonstration. It is to explain why the **decay profile of flower-color memory** differs among clades, using predeclared ecological moderators such as pollination regime or environmental heterogeneity.

Camellia Paper 1 and the frozen Evolution Letters v0.2 science remain unchanged by this spike.
