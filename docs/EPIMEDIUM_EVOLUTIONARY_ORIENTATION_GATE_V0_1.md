# Epimedium evolutionary-orientation gate v0.1

## Why this gate exists

The eight-species molecular study (`10.3389/fpls.2023.1133616`) labels four sampled accessions as anthocyanin-positive (A+) and four as anthocyanin-negative (A-) and discusses convergent loss of floral anthocyanin. That molecular comparison is valuable, but `A-` is not itself an observed historical loss event.

The later sect. *Diphyllon* phylogenomic/morphological study (`10.3389/fpls.2023.1234148`) reconstructs white as the plesiomorphic inner-sepal state and yellow as the ancestral petal/spur state, with repeated transitions to purple/red and other colours. Therefore the evolutionary direction of the eight molecular accessions cannot be inherited from the words `loss` or `non-pigmentation` in the molecular paper.

## Current result

**Historical event direction is unresolved for every one of the eight molecular accessions.**

Do not count four A- species as four independent losses. Do not count four A+ species as four independent gains. First reconstruct organ-specific state history on the same taxon/tree layer used by the atlas.

## Accession-level versus species-level state

The molecular study used wild-derived accessions grown in a common garden. The A+/A- measurement therefore applies directly to those sampled accessions/tissues.

This distinction matters because at least some sampled species are not fixed for one visible colour across their ranges:

- *E. acuminatum* has documented geographic variation from yellow to purple;
- *E. leptorrhizum* has documented geographic flower-colour variation;
- *E. sagittatum* flowers combine white inner sepals with yellow petals and show broad taxonomic/geographic complexity.

Accordingly, molecular A+/A- is never promoted to a fixed species-level state before the 699-individual reproductive dataset is ingested.

## Conservative dependence groups

Before event direction is reconstructed, the eight molecular accessions are grouped only to prevent pseudo-replication.

- `FRANCHETII_COMPLEX`: *E. franchetii*, *E. lishihchenii*, *E. zhushanense*. Published taxonomic work treats these taxa as one species-complex problem, and some treatments subordinate *E. lishihchenii* under *E. franchetii*. The group contains both A- and A+ sampled accessions, so it cannot be represented as one simple loss event.
- `SAGITTATUM_COMPLEX`: *E. sagittatum*. This is a separate, explicitly recognized taxonomic complex with strong geographic structure.
- `WUSHANENSE_COMPLEX`: *E. wushanense*. This has its own species-complex history.
- `ACUMINATUM`, `LEPTORRHIZUM`, `EPSTEINII`: retained separately, but current geographic/taxonomic variation is preserved rather than majority-collapsed.

A plastome result clustering *E. sagittatum* with *E. lishihchenii* is treated as a topology sensitivity, not as permission to redefine the taxonomic dependence groups. Sect. *Diphyllon* has extensive documented introgression and topology conflict, so no single plastid adjacency can define the event structure.

## Molecular pattern already visible without assigning event direction

The common qPCR/HPLC observation regime itself is informative:

- ANS is reduced in all four sampled A- accessions;
- DFR is reduced in most A- accessions but not *E. lishihchenii*;
- FLS/DFR balance differs among A- accessions;
- different CHS copies are reduced in *E. franchetii* and *E. wushanense*;
- functional assays in *E. sagittatum* retain catalytic activity for tested pathway enzymes.

Thus the molecular evidence already suggests **hierarchical recurrence**: a strongly repeated downstream ANS component with more heterogeneous upstream/competing-branch implementation. This is a mechanistic pattern, not yet an estimate of independent evolutionary recurrence.

## Decisive next gate

The second-anchor analysis proceeds only after all of the following:

1. ingest Supplementary Table S4 from `10.3389/fpls.2023.1234148` at individual level;
2. preserve inner-sepal and petal/spur colour separately;
3. map the eight molecular taxa/accessions onto the accepted taxon and nuclear-tree sensitivity layer;
4. reconstruct organ-specific visible/pigment state without forcing A- = loss or A+ = gain;
5. collapse event comparisons across taxonomic/topological dependence;
6. require at least three defensibly independent, directionally oriented molecular transitions before estimating recurrence.

Until then:

`EPIMEDIUM_SECOND_MECHANISTIC_ANCHOR = PROMISING_BUT_EVENT_ORIENTATION_BLOCKED`

This work is post-Paper-1 and does not change Camellia science v0.2.2 or AJB v1.0.
