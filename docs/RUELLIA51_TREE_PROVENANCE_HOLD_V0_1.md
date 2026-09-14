# Ruellia51 authoritative-tree provenance hold — v0.1

## Terminal state

`HOLD_AUTHORITATIVE_2023_TREE_BYTES_OR_EXACT_RECONSTRUCTION_SOURCE_UNAVAILABLE_OUTCOMES_UNOPENED`

This is a source/provenance hold, not a biological negative result.

## What the source actually uses

The Watts et al. flower-colour analysis reads:

`color data/color data/phylogeny/03-Ruellia_phylo.timed.tre`

The author code computes cophenetic distances from this tree and maps its tip labels directly through `antho_db$phylo_ID` before replacing them with species labels. Thus tree topology, branch lengths and the exact `phylo_ID` tip set are part of the profile estimator input.

The source article states that the phylogenetic framework was obtained by pruning a ddRADseq maximum-likelihood phylogeny of 187 Ruellia species from Manzitto-Tripp & Daniel (2023; DOI `10.1002/tax.13001`). That study used RAxML and archives its RADseq reads under NCBI BioProject `PRJNA948660`.

## What was searched

Before opening CHUN HPLC outcomes we checked:

- both Figshare versions of the Watts et al. dataset;
- the current author GitHub repository and every one of its six historical commits;
- the 2023 TAXON article and indexed supplementary/web surfaces;
- NCBI BioProject `PRJNA948660`;
- targeted public web/GitHub searches for the DOI, RAxML outputs and final-tree filenames.

The public sequence archive exposes raw reads, but no authoritative final Newick/RAxML tree object was located in these surfaces.

## Why the 2021 chronogram is not substituted

Dryad DOI `10.5061/dryad.qnk98sfff` contains `Ruellia_chronogram.tre` (file id `529362`, 8,201 bytes, SHA-256 `2644cf014c2e4434bee8d496fce729802efef322a1b97c2fb8773d5f5ce72cb6`). Its public automated route is also presently blocked by the Dryad validation interstitial/API authentication gate.

More importantly, even if those bytes were recovered, the 2026 source explicitly identifies its comparative phylogeny as a prune of the 2023 187-species ddRAD ML phylogeny. The 2021 chronogram therefore cannot be promoted to the primary tree from filename or organism similarity alone.

## Identifier-only source correction

The exact Figshare `raw_data.csv` was inspected only through identifier columns. It contains:

- 197 source rows;
- 123 unique species;
- 139 rows with nonmissing `phylo_ID`;
- 58 rows with missing `phylo_ID`;
- 93 species with at least one nonmissing `phylo_ID`;
- 122 unique nonmissing `phylo_ID` values.

A literal `NA` in `phylo_ID` is treated as missing. No nonmissing `phylo_ID` maps to more than one species, but some species have multiple `phylo_ID` values. This confirms that a tree-tip/species representative rule cannot be frozen correctly until the authoritative tree tips and order are available.

The preregistration's `reported_species = 51` was therefore an incorrect source-metadata statement, not a realised-outcome result. It is corrected in `data/ruellia51_source_scope_erratum_v0_1.json`; the original preregistration remains unchanged for auditability.

## Why we do not reconstruct a tree from raw reads here

A new RAxML reconstruction from `PRJNA948660` would be a new analysis object, not recovery of the exact tree consumed by the source. Because the CHUN statistic uses patristic distance, even reasonable differences in filtering, topology, rooting or branch-length estimation can alter AUCs. Reconstructing after the programme exists would therefore require its own separately frozen tree-estimand contract.

## Outcome firewall

At this hold:

- six HPLC numeric values: unopened;
- compound-presence states: uncomputed;
- branch-presence states: uncomputed;
- state frequencies: uncomputed;
- AUCs and permutations: uncomputed;
- profile winner: uncomputed.

## Release condition

Resume only if one of the following becomes available before HPLC outcome opening:

1. exact `03-Ruellia_phylo.timed.tre` bytes or an author-supplied hash;
2. an authoritative 2023 final ML tree object plus an outcome-independent deterministic pruning/timing recipe demonstrably reproducing the Watts tree.

Then freeze the tree hash, branch lengths, `phylo_ID` crosswalk and species-level representative rule before running the preregistered profile estimator.
