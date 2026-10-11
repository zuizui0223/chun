# Erica taxon-name-level developmental gene expression vs voucher-averaged ancestry (2026-10-11)

**Status: `NOT_SUPPORTED_EXPLORATORY_TAXON_NAME_LEVEL`.** New, retrospective exploratory estimand; **does not supersede** the original predeclared 2016-tree direct-tip Erica analysis, which remains `HOLD_SOURCE_IDENTITY_SUPPORT`.

## Why this separate test exists

The original 2019 Cape *Erica* source contains 7 anthocyanin-pathway gene fold-change measurements at juvenile, intermediate, and adult corolla stages (630 numeric observations over 30 original taxon/morph source labels). Excluding the polymorphic three-morph *E. plukenetii* subspecies leaves 27 single-visible-colour taxon labels, of which 22 have at least one named DNA voucher on the 2025 Hoekstra et al. published molecular trees.

Original original-source provenance:
- 2019 expression/colour paper: `10.3389/fpls.2019.01565`; original qPCR dataset: `10.25413/sun.9980498` (archived unmodified from GitHub Actions `38046569468`).
- 2025 IQ-TREE source: `10.3897/phytokeys.257.139457.suppl3`; original `oo_1344866.zip` MD5 `d4363c6e604784b58c91d8a1d824a1f1` (archived unmodified from Actions `38062290346`).
- Seven source-reported subspecies names in the **original 2019 Methods** were used to constrain compatible 2025 DNA accession tips **before** testing the new expression outcome. See `data/erica_2019_published_subspecies_2025_tree_prefix_contract_v0_1.json`.

The original strict `Erica` phenotype/gene exact-tip design had only **14 candidate taxa and 31 possible same-hue pairs**, fewer than required 20 taxa / 40 pairs. Eight other taxa still had multiple accession candidates that sometimes represent divergent subspecific histories. Rather than arbitrarily picking tips, this *different exploratory study* averages all patristic distances in the cross-product of **every** source-compatible pair of 2025 DNA accessions for each named 2019 taxon pair, using uniform voucher weights. This is a source-name-level macroevolutionary distance proxy, not proof that the particular 2019 floral qPCR plant was sampled in the 2025 DNA tree.

## Fixed-before-this-new-statistic estimator

See `data/erica_voucher_averaged_developmental_memory_design_v0_1.json`.

- Source taxa: **22 named taxon labels** (12 red, 6 pink, 2 white, 2 yellow).
- Inference frames: **83** distinct-taxon unordered pairs sharing an **exact same visible hue** (not identical anthocyanidin chemistry).
- Expression: seven original pathway-gene Fold Change axes × juvenile/intermediate/adult = **21** original gene–age features. Transform each source nonnegative fold value by `log1p`, standardize each feature across the 22 taxa, and compute equal-feature-weight RMS between taxon expression vectors.
- Primary molecular tree: original Hoekstra 2025 **combined** IQ-TREE source. Predictor is the arithmetic mean of all candidate accession-pair branch distances between the two named taxa. Tree branch lengths are **not dated millions of years**.
- Statistic: within-colour Spearman `rho` of molecular distance vs 21-feature expression distance. **Whole taxon expression vectors** are shuffled within each of the four frozen hue classes (9,999 independent permutations, seed 20261011); 83 pairs are not independent experimental replicates.
- Required exploratory positive result: observed rho greater than permutation-null mean **and** upper-tail P at or below .05; no stage, gene, colour, accession, or tree partition selection after the result.

## Actual result

GitHub Actions source replay in `PR #422` completed all four focused tests and calculated the following from the unmodified original inputs:

| Original IQ-TREE partition | Within-hue rho | Role |
|---|---:|---|
| Combined | **+0.041497** | Frozen main exploratory test |
| Nuclear | +0.064250 | Descriptive sensitivity, not another independent replicate |
| Plastid | +0.194429 | Descriptive sensitivity, not another independent replicate |

For the frozen combined-tree test, 9,999 within-hue species-vector permutations gave a null-mean rho **+0.046626**, an observed-minus-null effect **−0.005129**, and **one-sided P = 0.4988**. The prerequired positive conditional association was therefore **not supported**. The source-exposed leave-one-taxon descriptive analysis yielded 19/22 positive rho values, but the lower bound became negative (−0.02855) and this does **not** replace the primary decision or justify post hoc taxon removal.

**No rescue or optimization was attempted.** Only the complete 7-by-3 feature matrix, frozen source taxon/hue classes and combined partition decide the test. Nuclear/plastid rho values do not have promoted confirmatory P values.

## Biological conclusion and what remains unidentified

Within *Erica* taxa sharing the **same coarse visible flower hue**, gene-expression distances over flower developmental stages did **not** show the predeclared positive association with the taxon-name/voucher-averaged molecular tree distances. This is informative because unlike the prior source transport/source-unit HOLD, there is a *real measured new exploratory outcome*. It challenges a naive universal strong visible-colour-conditional developmental-gene-memory claim at this source resolution.

However, it is **not** a demonstrated absence of molecular regulatory phylogenetic signal in *Erica*:
- The 2019 qPCR flowers and the 2025 DNA specimens were not identical vouchers or necessarily matched populations; several taxon labels remain taxonomically broad and their voucher sets nonmonophyletic.
- Original RT-qPCR `2^-ΔΔCt` values normalized using PTB1 may still differ in calibration/primer performance and flower developmental comparability; the published source does not provide an unmeasured cross-taxon batch-effects control.
- The direct ancestral 2016 tree is unavailable. The 2025 source includes multiple partition-specific trees; they are *correlated reconstructions of one radiation*.
- Red vs pink hue cannot be assumed to differentiate fine chemical states, and the 2019 UPLC-MS/MS Table 2 does not match the Petunieae exact six-compound binary chemical identity.
- The positive retrospective **Petunieae** result after pigment adjustment (`rho +0.5112`, P .0002) and the failed frozen nearest-two donor prediction are unchanged. **Petunieae vs Erica rho values do not estimate one common effect and cannot be compared as if they were independent same-estimand measurements.**

The sharp biological follow-up is to test **whether hierarchical memory lives at the pigment-species-biochemistry level, at the developmental-gene trajectory level, or is contingent on the evolutionary context** under a future *matched same-tier* multi-radiation source design. Ecological causes involving pollinators, selection, and fitness remain **untested**.

## Submission governance

- **Do not merge into frozen first-submission governance** on the strength of an exploratory null.
- The previously frozen direct Erica observed-tip design remains on HOLD.
- Keep original *Camellia* AJB Paper 1 and Evolution Letters v0.3 scientific artefacts byte-identical.
- Integrated CHUN temporal proposal and this novel cross-radiation comparison remain **Draft**.
