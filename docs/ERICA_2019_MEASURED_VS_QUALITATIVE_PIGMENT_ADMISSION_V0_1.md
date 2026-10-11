# Erica 2019 Table 2 chemical-data admission: measured UPLC result ≠ quantified matched pigment matrix

**Date:** 2026-10-11  
**Status:** `QUALITATIVE_UPLC_TABLE2_AVAILABLE_EXACT_SIX_COMPOUND_PROFILE_NOT_ADMITTED`

## Immediate source verdict

Le Maitre, Pirie & Bellstedt (2019), DOI `10.3389/fpls.2019.01565`, report real floral UPLC-MS/MS results across 30 source measurement/morph rows (Table 2, Fig. 4, Supplementary Fig. 2). The original article’s **Data Availability Statement** specifically links the RT-qPCR expression workbook, which is recovered and quantitatively verified in CHUN; the UPLC supplementary object indexed by PMC is **a 3.3 MB PDF figure**. A source-verifiable machine-readable **species × quantified anthocyanidin compound** table or raw UPLC peak-area file is **not identified** in those listed objects. This statement does **not** establish that no further author/private analytical files exist.

The original 30-row Table 2 has categorical "Anthocyanin production" descriptors; these have been stored in `data/erica_2019_table2_qualitative_chemistry_source_v0_1.json` with original qPCR measurement keys. These descriptors are **published qualitative conclusions based on experiments**, not independently measured numerical chemical profiles. Do not silently equate their category `NORMAL_ANTHOCYANIN` with exact equality of multiple measured pigments.

Published article, Table 2: https://pmc.ncbi.nlm.nih.gov/articles/PMC6892755/  
Source expression DOI: `10.25413/sun.9980498`.

## The 22-taxon Erica result is even more biochemically under-resolved than the hue table suggests

The original 2019 flower-colour source and the already frozen 22-taxon Erica exploratory negative result were joined **without rerunning its expression correlations**.

| Original visible-colour class | 22-taxon labels | Original Table 2 coarse chemical-product category |
|---|---:|---|
| Red | 12 | 12 "normal anthocyanin" |
| Pink | 6 | 6 "normal anthocyanin" |
| White | 2 | 1 blocked after DFR; 1 largely no intermediates other than quercetins |
| Yellow | 2 | 2 pelargonidin-hexose rather than cyanidin |

- Among the same-visible-colour **83 unordered taxon pairs**, **82** share the same **coarse source chemical-product descriptor** (66 red-red + 15 pink-pink + 1 yellow-yellow); the lone white-white pair has **different pathway-level chemistry** in Table 2.
- Beyond same visible hue, **72 additional red-versus-pink pairs** also share the paper's "normal anthocyanin" descriptor. They are deliberately **excluded from the already frozen same-visible-hue Erica test**. Do not add them after observing its P=0.4988.
- The original authors explicitly report that red-vs-pink flowered taxa could not be separated on a *qualitative* anthocyanin basis using their UPLC-MS/MS or gene expression readouts, although optical intensity, pH, metal associations, epidermis or other pigments may explain colour variation. This is the **authors’ existing biological interpretation**, not a newly discovered mechanism.

**The word "normal" does not imply identical cyanidin/delphinidin/pelargonidin profiles or peak concentrations.** The white and yellow Table 2 records encode strong pathway differences; some qualitatively normal taxa could still differ in fine pigment chemistry. There is therefore **no source-supported way to transform 2019 Table 2 into the Petunieae six-bit measured anthocyanidin chemical identity**. Using the source PDF chromatogram graphics as if they were original raw numerical peak areas or silently selecting peaks would violate source admission.

## Scientific interpretation and publication

The new Erica exploration already returned **combined-tree Spearman rho +0.0414969984, 9,999 within-visible-hue taxon-vector permutation P=0.4988** for 22 name-matched taxa and 21 fixed gene-by-flower-development traits. That decision remains **NOT_SUPPORTED_EXPLORATORY_TAXON_NAME_LEVEL**.

The biochemical source check provides a concrete reason **not to equate** this with Petunieae's **rho +0.511199 / P=0.0002** within **identical measured anthocyanidin-presence profiles**, nor conclude that taxa with visually similar flowers share or lack one universal molecular-memory rate. It does not "rescue" Erica. It also does not prove the true phylogenetic molecular effect differs between the radiations.

Ecological context is interesting but not causally tested: bird-versus-insect pollination may respond to hue, intensity, flower morphology and reflectance, while chemically coarse UPLC categories cannot directly quantify pollinator-visible signals or fitness. Original paper mentions potential pollinator shifts; those ecological causal links were not independently measured in this audit.

The next scientifically commensurable evidence needs **actual per-species quantitative or six-anthocyanidin matched chemical measurement** on the same original sequenced taxa in a second radiation—not new work on generic hue thresholds or post-outcome rebinning. An original-source peak table and documented specimen crosswalk would change the **source feasibility** gate, not retroactively turn this negative exploratory Erica result into prospective positive evidence.

## Audited files and frozen constraints

- `data/erica_2019_table2_qualitative_chemistry_source_v0_1.json`
- `scripts/audit_erica_2019_qualitative_chemistry_coverage_v0_1.py`
- `results/erica_2019_qualitative_chemistry_availability_v0_1/result_v0_1.json`
- `tests/test_erica_2019_qualitative_chemistry_coverage_v0_1.py`
- `.github/workflows/erica-2019-qualitative-chemistry-v0-1.yml`

No new P value, predictor, transformation, gene feature, taxon, source-tree tip, biochemical profile, phylogenetic signal or independent replication was generated. The frozen AJB Camellia and Evolution Letters v0.3 submission materials remain unchanged. The integrated temporal proposal stays Draft.
