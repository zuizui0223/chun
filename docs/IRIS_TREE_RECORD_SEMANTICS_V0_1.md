# Iris primary tree record semantics — v0.1

## Status

**FROZEN BEFORE TREE RECONSTRUCTION AND BEFORE ANY IRIS AUC.**

The frozen Iris accession table contains 131 accessions assigned to more than one marker column, overwhelmingly `matK` and `trnK`. GenBank inspection shows that many of these records span a trnK region containing the matK gene. The primary analysis therefore needed an explicit rule before the outcome statistic was opened.

## Source-method audit

The source study states that sequences were obtained with MatPhylobi. We audited the public MatPhylobi implementation at commit `a54443c475aecc8567d6981346ee53c0a126e0ca`.

For ordinary markers, MatPhylobi:

1. retrieves the GenBank record for the selected accession;
2. assigns `record.seq` as the sequence;
3. uses marker-specific BLAST searches to select candidate accessions;
4. does not use general-marker BLAST coordinates to slice the final sequence to an annotated feature before the marker matrix is written.

Therefore adding a new CHUN feature-extraction step after seeing the accession table would not reproduce the source tool's sequence semantics.

## Frozen primary rule

For the six effective loci after the earlier source-schema erratum:

`matK, trnL, ndhF, trnK, rbcL, ITS`

CHUN will download the **full GenBank record sequence** for each accession and place it into the marker partition named by the frozen source accession table.

If the same accession appears in two source marker columns, it remains represented in both source-assigned partitions in the primary analysis. This includes the common matK/trnK case.

This choice is not asserted to be biologically optimal. It is the closest auditable reconstruction of the source-tool semantics available from the frozen public source bundle.

## Taxa

- the 226 trait rows are mapped by `data/iris_source_taxon_crosswalk_v0_1.csv`;
- `Iris_cedretii` remains tree-only because no frozen trait row exists;
- `Iris_darwasica` is removed under the source-specific exclusion frozen before outcome analysis;
- the frozen public accession bundle contains no non-Iris outgroup accession rows.

The primary tree is consequently treated as unrooted. This does not alter the pairwise patristic distances used by the preregistered AUC statistic.

## Sensitivity only

After the primary result is frozen, CHUN may test a deduplicated matK/trnK representation or feature-specific extraction as a methodological sensitivity. Such analyses may weaken confidence but cannot upgrade a failed or mixed primary result.

## Outcome firewall

At this freeze point no CHUN Iris coarse/intermediate/fine AUC, resolution delta, permutation p value or PASS/MIXED/FAIL classification has been computed.

Camellia Paper 1 remains unchanged.
