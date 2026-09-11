# Petunieae prospective cross-level gate — v0.1

## Status

**PRE-RESULT GATE — frozen before opening or inventorying the OSF data files at `https://osf.io/zg9cu/`.**

The Wheeler et al. 2023 article (`10.1098/rspb.2023.0275`) and its broad published conclusion are prior art and were known before this gate. What is prospective here is the repository's own reanalysis/admission decision from the processed OSF files under the already-merged v0.5 cross-level definition.

## Question

Does Petunieae satisfy the same high-level cross-level definition retained after Iochrominae and Cape Erica?

`VISIBLE_PHENOTYPE_AXIS_TO_MOLECULAR_SUBSPACE_WITHIN_ONE_RADIATION`

The two phenotype axes are fixed as:

1. **pigment amount / depletion axis** — total floral anthocyanin mass fraction;
2. **anthocyanidin hue / hydroxylation axis** — anthocyanin composition from mono-, di- and tri-hydroxylated anthocyanidins, evaluated only where anthocyanin is detected.

## Molecular subspaces — frozen before OSF inspection

Gene-expression variables are grouped by pathway position, not by the result:

- `EARLY_CORE`: CHS, CHI, F3H;
- `BRANCHING_HUE`: F3'H, F3'5'H, MT;
- `LATE_OUTPUT`: DFR, ANS;
- `REGULATORY`: AN1, AN11, JAF13, MYB27, SG6-MYBs.

Aliases/paralog-combined names may be reconciled only when the published methods explicitly define the equivalence. Missing genes remain missing; genes will not be moved between subspaces after inspection.

FLS/MYB-FL/MYB12 and flavonol amounts are retained as a trade-off/sensitivity layer, not used to define a PASS for the two-axis bridge.

## Planned source-derived variables

From the processed source files, without reading flower photographs or manually selecting taxa by outcome:

- `anthocyanin_total` = sum of measured anthocyanidin mass fractions;
- `hydroxylation_index` = abundance-weighted hydroxylation state among anthocyanidins: 1 for pelargonidin-derived, 2 for cyanidin/peonidin-derived, 3 for delphinidin/petunidin/malvidin-derived compounds;
- one standardized expression score per frozen molecular subspace, using PC1 of the available member genes after log1p expression transformation.

A subspace must contain >=2 observed member genes to be tested. If fewer than three of the four frozen subspaces are testable, the result is HOLD.

## Phylogenetic comparison

Where the processed source supplies a branch-length species tree that can be joined one-to-one to the phenotype/expression taxa, each phenotype axis is related separately to each molecular-subspace PC1 with a one-predictor Brownian phylogenetic GLS model. The intercept-only model is retained as the null. All subspaces therefore enter with the same one-predictor dimensionality.

If a usable source tree cannot be joined, ordinary species-level regressions may be reported only as a diagnostic; the prospective bridge gate becomes HOLD rather than silently dropping phylogenetic control.

## Pre-frozen PASS / MIXED / HOLD gate

`PETUNIEAE_PROSPECTIVE_BRIDGE_PASS` requires all of the following:

1. >=30 taxa have matched pigment and gene-expression observations and a one-to-one tree join;
2. both phenotype axes have >=20 valid taxa;
3. >=3 frozen molecular subspaces are testable for both axes;
4. for the **hue/hydroxylation axis**, `BRANCHING_HUE` is the best subspace by AICc and exceeds the next-best subspace by >=2 AICc units;
5. for the **amount/depletion axis**, the best subspace is `LATE_OUTPUT` or `REGULATORY`, exceeds the next-best subspace by >=2 AICc units, and is not `BRANCHING_HUE`;
6. the two axes therefore select different best molecular subspaces under the same frozen analysis.

`PETUNIEAE_PROSPECTIVE_BRIDGE_MIXED` is assigned when source coverage passes items 1–3 but only one phenotype axis satisfies its subspace-specific criterion, or the expected best subspaces are recovered without the >=2 AICc separation.

`PETUNIEAE_PROSPECTIVE_BRIDGE_HOLD` is assigned when source/taxon/tree coverage is insufficient to execute the frozen test.

`PETUNIEAE_PROSPECTIVE_BRIDGE_FAIL` is assigned when coverage is sufficient but the two axes do not show the pre-specified molecular-subspace separation (for example the same non-expected subspace dominates both axes).

No threshold or gene grouping will be changed after OSF inspection.

## Claim boundary

A PASS would be one **prospectively specified source-data reanalysis** supporting the high-level phenotype-axis→molecular-subspace pattern in a third radiation. It would not make the prior Iochrominae/Erica alignments prospective, would not establish universal causal genes, and would not establish a common ecological driver or transition direction.

Paper 1 remains unchanged.
