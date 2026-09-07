# Epimedium: actual source ingestion and organ-state audit v0.1

## Status

This is an executed source-data analysis, not a source-availability score or a planned ingestion contract. It does not reopen Camellia Paper 1.

Source: Zhang, C., Meng, R., Meng, Y., Guo, B.-L., Liu, Q.-R. & Nie, Z.-L. (2023). *Parallel evolution, atavism, and extensive introgression explain the radiation of Epimedium sect. Diphyllon (Berberidaceae) in southern East Asia*. Frontiers in Plant Science 14:1234148. DOI: https://doi.org/10.3389/fpls.2023.1234148. The original source is distributed under CC BY; the unchanged source workbook and derived CSV exports retain this attribution.

The supplement was actually retrieved using Europe PMC's documented `fullTextXML` and `supplementaryFiles` endpoints for PMC10616310. Article DOI and license were checked. The original `Table_1.xlsx` has 161,106 bytes and SHA256 `057a0aaa603cfa4d9683a2eac75e747cb14bd1294e541feb82483fe6bc160e45`.

## What now exists

- All 11 original worksheets have positional CSV exports; source cells and merged ranges are preserved.
- S4 contains exactly **699 measurement rows**, grouped into **41 named source taxa and one unidentified group**, with **53 taxon/locality/voucher strata**.
- The organ-aware long table contains **1,398 rows**: each source measurement contributes one inner-sepal and one petal/spur record.
- A separate XML-based check reconciles **every exported cell** in S1, S2, S4 and S9 against the pinned workbook, not only row counts or a registry flag.

Source names are normalized only by genus expansion and whitespace. This is not a claim that all names have passed a modern accepted-taxonomy audit. Locality/voucher strata are source groups, not proven independent populations or evolutionary events.

## Executed test: can one organ substitute for the other?

The named-taxon analysis assigns one equal weight per source taxon, rather than 699 independent evolutionary replicates. S4 contains four nominal inner-sepal colour categories, five spur categories and seven joint combinations.

| Sepal source code | Spur source code | Named taxa | All source taxa | Measurement rows |
|---|---|---:|---:|---:|
| 0 | 0 | 2 | 2 | 31 |
| 0 | 1 | 6 | 6 | 106 |
| 1 | 1 | 10 | 10 | 196 |
| 2 | 1 | 9 | 9 | 147 |
| 2 | 2 | 3 | 3 | 56 |
| 2 | 4 | 3 | 4 | 37 |
| 3 | 3 | 8 | 8 | 126 |

These are source-variable-specific nominal codes, not an assumed universal colour scale. A numerical code is **not translated to WHITE/RED/YELLOW/PURPLE/BROWN without an explicit codebook**. The analysis is invariant to independently renaming the codes in either organ.

The mapping is not one-to-one: sepal category 0 accompanies two spur categories, and sepal category 2 accompanies three. Conversely, spur category 1 accompanies three sepal categories. Thus **neither single-organ state is sufficient to recover the joint floral display state in this sampled table**.

Equal-taxon descriptive information measures are:

- H(sepal, spur) = **2.607109 bits**;
- H(spur | sepal) = **0.659865 bits**;
- H(sepal | spur) = **0.947269 bits**;
- mutual information = **0.999975 bits**.

Retaining only sepal or only spur removes, respectively, 25.31% or 36.33% of the empirical joint-state entropy. These are descriptive information losses under this coding and equal-taxon weighting, not biological effect sizes, estimates of accessible phenotype space, or selection coefficients. Including the unidentified group retains seven combinations and the same failure of single-organ sufficiency.

No evolutionary P value, transition rate, ancestral state, independent gain/loss count or ecological cause is estimated. The 7 of 20 combinatorially possible code pairs does not demonstrate that the other pairs are biologically inaccessible.

## Important finding about polymorphism

Colour codes are constant within **all 42 source taxa and all 53 source strata**. This does not establish natural monomorphism. The table may reflect the sampled material and/or taxon-level categorical coding; its rows do not provide a comprehensive morph-frequency survey.

This distinction matters because the existing project provenance audit records geographic colour variation in *E. acuminatum* and *E. leptorrhizum* (DOI https://doi.org/10.3897/phytokeys.118.30268). Their constant S4 codes must not erase that external evidence. The atlas's temporal–spatial bridge still requires population-resolved morph observations.

## Crosswalk: molecular accessions, morphology and phylogenetic summaries

The eight-species molecular panel comes from Mi et al. (2023), DOI https://doi.org/10.3389/fpls.2023.1133616. Matching normalized species names—not claiming matched individual plants—gives:

| Source layer | Molecular-panel taxa represented |
|---|---:|
| S1 GBS sampling list | **7/8** |
| S4 reproductive measurements | **6/8** |
| S9 reproductive summary | **5/8** |

*E. epsteinii* is absent from all three source layers. *E. sagittatum* appears in S1 but not S4/S9. *E. lishihchenii* appears in S1/S4 but not S9. Missing records are not filled from the molecular paper's A+/A− labels.

S9 contains **34 ingroup rows plus one outgroup row**, whereas the article's Methods describe **35 ingroup species plus one outgroup**. This discrepancy is recorded, not silently padded with a guessed species. Of the 34 ingroup rows, 33 join S1 by exact ID and taxon. The remaining `E. shennongjiaense S26` is explicitly reconciled to `JS26`, supported by the unique same-taxon S1 entry; original and reconciled identifiers are retained. All **34/34** ingroup S9 colour-code pairs agree with S4.

The `E. elatum (outgroup)` row is not treated as the original sequenced `E. koreanum` tip. Methods 2.4–2.5 explicitly describe substituting *E. elatum* morphological traits when estimating ancestral states. This is an author-defined outgroup treatment that requires sensitivity analysis, not a new molecular crosswalk.

The exact 2011 molecular-plant-to-morphological-plant link remains unestablished, and no historical direction is assigned to the eight molecular accessions.

## Implication for the temporal programme

The useful result is now quantitative: **a single whole-flower label can discard organ-specific state structure before any time-axis reconstruction begins**. The cross-clade atlas should reconstruct joint or explicitly organ-specific states rather than assuming one scalar colour state per species. This supports a better measurement design; it is not proof of temporal modular evolution or a new claim that organs differ in colour.

## Reproduce offline

```sh
python scripts/analyze_epimedium_organ_states_v0_1.py \
  --source-dir data/atlas_epimedium_ingested_v0_1 \
  --out-dir build/epimedium_organ_audit
python -m unittest discover -s tests -p 'test_epimedium_organ_states_v0_1.py'
```

Network retrieval remains available separately:

```sh
python scripts/ingest_epimedium_source_v0_1.py --out-dir build/epimedium_source_refresh
```

The analysis pins the original workbook SHA256, rejects altered exports even when the raw workbook is unchanged, preserves unidentified taxa in a sensitivity analysis, and never converts constant taxon codes into evidence of absent population polymorphism.

## Remaining scientific boundary

Completed: actual binary ingestion, positional export, organ-coded descriptive analysis, molecular/morphological/sampling-list crosswalk, and deterministic reanalysis tests.

Not completed: explicit nominal-code-to-hue verification, current accepted taxonomy, the exact machine-readable tree and its complete tip set, resolution of the 34-versus-35 discrepancy, root/outgroup sensitivity, population morph-frequency recovery, and a matched historical molecular comparison. A cross-clade evolutionary model is not yet fitted.

Camellia science v0.2.2, framing v0.3.4 and AJB v1.0 remain untouched.
