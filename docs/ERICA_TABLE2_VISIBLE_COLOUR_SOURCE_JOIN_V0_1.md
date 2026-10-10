# Erica 2019 Table 2 → published seven-gene qPCR identity join (2026-10-10)

**Source-only outcome:** 30/30 original qPCR taxon/morph measurement labels can be joined to the flower-colour classes explicitly printed in Le Maitre et al. 2019 Table 2. **No phylogenetic-memory inference and no six-compound biochemistry replication.**

## Verified input identities

- 2019 *Frontiers in Plant Science* paper, DOI `10.3389/fpls.2019.01565`, source Table 2 (colour, gene expression, anthocyanin production, putative causes).
- Original XLSX from dataset DOI `10.25413/sun.9980498`, Figshare file ID 18004067, source archived by GitHub Actions original run `38046569468`.
- The quantitative matrix has 630/630 numeric fold changes for seven measured pathway genes over 30 original taxon/morph labels × three floral developmental stages. The 90 intentionally blank normalization-reference fold-change entries (`PTB1_REF`) are not pathway data failures.
- New authored source transcript `data/erica_table2_visible_colour_qpcr_taxon_crosswalk_v0_1.json` is explicitly human-transcribed from the published table and **not** a newly measured pigment table. Source wording and qPCR spellings remain separate columns; synonym/typo assumptions are not silently applied to tree-tip matching.

## Complete source identity result

The published table has **30 measurement rows**: red 15, pink 7, white 6, yellow 2. Three colour morphs (red/pink/white) from one original lineage, `Erica_plukenetii_plukenetii`, must not count as three independent branches. After collapsing that lineage there are 28 source lineage labels in total; setting its polymorphic observation aside leaves 27 single-colour lineage labels:

| Visible state | Original measurement rows | Single-colour lineage labels | Theoretical unordered pairs if all 27 lineages were sampled in a tree |
|---|---:|---:|---:|
| Red | 15 | 14 | 91 |
| Pink | 7 | 6 | 15 |
| White | 6 | 5 | 10 |
| Yellow | 2 | 2 | 1 |
| **Total** | **30** | **27** | **117** |

**The 117 are combinatorial candidate pairs, not verified matched tree pairs or independent replicates.** There is no demonstrated observed number of pairs until the exact measured labels are joined to directly sequenced molecular tips on a branch-length phylogeny.

Distinct source spellings are deliberately left visible, including qPCR `Erica_cerenthoides` vs Table2 `cerinthoides`, qPCR `Erica_hematocodon` vs Table2 `haematocodon`, qPCR `Erica_sparmanii` vs Table2 `sparmannii`, and qPCR `Erica_verticiliata` vs Table2 `verticillata`. These are **source-to-source label crosswalks, not a voucher-backed assertion of accepted taxonomy**.

The letters A–J in the paper denote ten published close-relative comparison groups and **must not be taken as 10 reconstructed independent evolutionary events**. It is not legitimate to use all 30 raw measurements as 30 unrelated species or collapse the three developmental stages into independent ancestral-change events.

## Reproduction

A new source-only executable `scripts/audit_erica_table2_visible_colour_crosswalk_v0_1.py` retrieves the original expression workbook keys and rejects any missing or extra source identifier. The frozen row count, seven-gene numeric coverage, phenotypically polymorphic species, and crosswalk cardinality are all fail-closed.

The hosted replay [GitHub Actions 38058694895](https://github.com/zuizui0223/chun/actions/runs/38058694895) confirmed `PASS_TABLE2_VISIBLE_COLOUR_QPCR_KEYS_ONLY_TREE_AND_CHEMICAL_STATES_HOLD` and all four unit tests. Its source audit output is an archived JSON receipt; the original XLSX source is unchanged.

## Additional attempted tree source recovery

The later, distinct 2024 Pirie et al. Supplementary Material 7 (DOI `10.3897/phytokeys.244.124565.suppl7`) was independently identified under canonical Zenodo preservation **record 12730704**. The hosted Zenodo API request **timed out** (run [38058479382](https://github.com/zuizui0223/chun/actions/runs/38058479382)); neither metadata nor raw ZIP bytes were admitted. This is `HOLD_ZENODO_2024_TREE_SOURCE_NOT_ADMITTED`. The previous 2016 TreeBASE S18291 and 2024 PMC/publisher direct-download routes also remain unrecovered. No rerooting, tree replacement, missing-species imputation, or inferred patristic distance was performed.

## Ecological inference boundary

The newly joined source supports **which red, pink, white, and yellow states had gene-expression measurements**. This is a prerequisite for asking if lineages sharing an external visible phenotype retain finer pathway-expression phylogenetic organisation. However, **visible-colour identity is not exact anthocyanidin identity**; the source paper itself reports pink/red flowers with similar observed biochemical profiles and several different molecular routes for white/yellow changes. Its Table 2 gene-expression and qualitative product assessments cannot be treated as a six-bit or quantitative HPLC/UPLC species-by-pigment matrix comparable to Petunieae.

For a new **visible-state-conditioned** Erica prediction, freeze the revised biological estimand explicitly as *different* from the Petunieae exact-chemical-state condition, and require a matched **observed (non-imputed) tip** with branch lengths for the 27 source lineages before any P value is computed. A raw tree that includes fewer observed taxa changes the pair denominator and may cause structural HOLD.

**Submission decision unchanged:** Petunieae remains one retrospective 47-tip source. The original AJB Paper 1 and Evolution Letters v0.3 submission paths remain frozen, and the integrated mechanism→memory claim is not promoted on the strength of this source join.
