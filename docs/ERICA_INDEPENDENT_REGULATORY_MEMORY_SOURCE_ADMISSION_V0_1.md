# Independent Cape Erica molecular-memory source admission — 2026-10-10

**Classification: EXPRESSION_SOURCE_PASS / PIGMENT–TREE–TIP_JOIN_HOLD / NO INDEPENDENT MEMORY REPLICATION.**

This is a source-admission audit stacked on integrated Draft PR #414, not a change to the frozen American Journal of Botany *Camellia* submission or Evolution Letters v0.3. The source is independent of the Wheeler 2023 47-tip Petunieae phylogeny, but **having an independent expression data matrix alone is not the same as demonstrating an independent evolutionary-memory effect**.

## Verified measured source

Le Maitre, Pirie and Bellstedt (2019), DOI **10.3389/fpls.2019.01565**, provides an open repository link to *RT-qPCR expression data of the Erica sp. anthocyanin synthesis gene pathway* (Le Maitre & Bellstedt dataset DOI **10.25413/sun.9980498**; source Figshare file ID **18004067**).

Hosted GitHub Actions retrieved **real XLSX bytes** from the manuscript-linked source URL and validated the ZIP-based OOXML structure. The workbook has four tabs: `Metadata` (26 source XML rows) and `Matrix non-normalized`, `Matrix normalized`, `Fold Change` (721 XML rows each including header).

All three matrix tabs have matching ordered original `ID_REF` keys. Parsing **720** measured IDs yields:

| Source unit | Original coverage |
|---|---:|
| Original taxon/morph measurement labels | 30 |
| Flower developmental stages per label | 3 (juvenile, intermediate, adult) |
| Anthocyanin pathway genes with numeric fold-change | 7 |
| Numeric taxon-label × stage × pathway-gene measurements | **630 / 630, no missing values** |
| PTB1_REF normalization-control IDs | **90** |
| PTB1_REF self-referenced fold-change entries | **90 intentionally blank** |

Frozen gene list: `ANS`, `CHI`, `CHS`, `DFR`, `F3'H`, `F3H`, `UDP3-O-GST`. The eighth `PTB1_REF` is a normalization control, **not a seventh/eighth evolutionary response gene**. The measured 30 taxon-label strings include separate **red/pink/white morph entries under `Erica_plukenetii_plukenetii`**. Those three morphs are one named subspecific lineage with separate measurements, **not three independently evolving phylogeny tips**. The author's article reports approximately 28 species/subspecies; do not equate that number mechanically with the 30 quantitative labels.

The exact measured label spellings include `Erica_cerenthoides`, `Erica_hematocodon`, `Erica_sparmanii`, `Erica_verticiliata`. Orthographic repair and phylogeny-tip synonym mapping remain **unverified**; nothing is silently renamed.

**Reproducibility:** `scripts/preflight_erica_qpcr_xlsx_source_v0_1.py`, `scripts/audit_erica_qpcr_source_keys_v0_1.py`, and their eight focused tests. Hosted source-key audit PASS: [GitHub Actions #38046569468](https://github.com/zuizui0223/chun/actions/runs/38046569468). The job artifact retains the original downloaded XLSX and the source-only schema receipt.

## Required species-tree source and tested retrievals

The Pirie et al. (2016) study (DOI **10.1186/s12862-016-0764-3**) identifies TreeBASE **S18291** as the source for sequence matrices and trees. We specifically tested three raw machine-readable tree routes (NEXUS, NeXML and publisher-referenced PURL). All three **timed out** in a hosted GitHub Actions job. This is a **transport/source HOLD**, not a biological disconfirmation.

- Source-only audit: `scripts/preflight_erica_treebase_s18291_source_v0_1.py`, tests and workflow.
- Replay: [#38046791269](https://github.com/zuizui0223/chun/actions/runs/38046791269).
- Result: `HOLD_TREEBASE_SOURCE_TREE_UNRECOVERED`.
- No original tree bytes, tip names, patristic distance matrix, branch lengths or temporal estimate admitted.

A **distinct later phylogeny** exists in Pirie et al. (2024), *PhytoKeys*, DOI **10.3897/phytokeys.244.124565**, supplementary 7 DOI **10.3897/phytokeys.244.124565.suppl7**. Its stated contents are cpDNA, nrDNA and combined trees, including later datasets; some downstream complete-species trees include **phylogenetically imputed taxa**, which must never substitute for independently sequenced tips in an ancestry/memory test. The following external source download routes were checked separately as **alternatives only**, not replacements for the 2016 source:

- PMC usual `/articles/PMC11255470/bin/<supp7 filename>` → HTTP 404.
- PMC `/articles/instance/11255470/bin/<supp7 filename>` → HTTP 200 but content is not ZIP.
- Publisher guessed `/article/124565/download/suppl7` → HTTP 404.

All three fail structural byte admission. The guessed publisher path and PMC routes are transport probes, **not citations establishing download links**. Later-source raw archive was not obtained, no tree was chosen, and status is `HOLD_LATER_PHYLOGENY_SOURCE_BYTES_UNRECOVERED`. Code: `scripts/preflight_erica_2024_tree_bundle_v0_1.py`; tests and workflow.

## Additional biological source gate: matching *pigment states*

Le Maitre et al. (2019) Table 2 and accompanying UPLC-MS/MS findings report visible colour and qualitative pathway/anthocyanin production information, but this newly recovered quantitative workbook contains **gene expression, not a source-verified per-tip six-anthocyanidin abundance or presence table**. Therefore the precise Petunieae within-*exact measured biochemical state* estimand cannot yet be applied to this source without **an independently sourced species/morph-specific pigment schema**, a non-imputed branch-length species tree, and a frozen voucher/tip taxon crosswalk.

The complete 30-label/three-age data should **not** be treated as 90 evolutionary tips, 630 independent observations, or 30 independent species. No selection of the juvenile/intermediate/adult sampling stage may be made after seeing an evolutionary-memory test outcome.

## Minimal legitimate next inference gate

1. **Tree admission:** recover a documented full branch-length machine-readable molecular tree (preferably original 2016 S18291), pin exact SHA256, disclose topology source and all imputed tips, retain only direct observed taxa.
2. **Taxon join:** freeze a measurable crosswalk between the approximately 28 independent *Erica* source taxa, the 30 raw morph labels, and the sequenced tree tips. Do not count the three *E. plukenetii* colour morph rows as separate historical origins.
3. **Phenotype admission:** recover a machine-readable per-taxon pigment-identity profile or explicitly predeclare a **different** visible-colour phenotype estimand. Table 2 qualitative pigment production must never masquerade as Petunieae's exact biochemical six-bit state.
4. **Outcome freeze then calculation:** freeze stage, gene panel, pair-support gate, null exchangeability, taxon sampling unit and hypothesis direction **before** running any new same-tree expression/phenotype phylogenetic statistic. Underinsufficient within-state pair support yields structural HOLD, not a negative biology result.

**Scientific publication judgment:** Independent *Erica* expression availability strengthens feasibility; it provides **zero** new admitted independent regulatory-memory replications. Keep both frozen journal submission routes and integration PR #414 governance intact. Do not convert source success or access failures into evidence for or against a universal flower-colour molecular memory principle.
