# Iochrominae original Dryad tree recovery — 19 November 2026

## Completed

**This is actual original-source byte recovery, not another archive-link inventory.** The verified CC0 GitHub Actions source [run #43895705048](https://github.com/zuizui0223/chun/actions/runs/43895705048) uploaded original Dryad archive artifact ID **14239795231**. The nested ZIP files were retrieved and inspected using Python `zipfile`, `csv` and Biopython `Phylo.parse(..., "nexus")`.

| Authoritative source | Original file | Parsed result |
|---|---|---|
| Smith & Goldberg 2015, Dryad `10.5061/dryad.0732g` | `ModeandTempoFlColor.zip/IochBeast100.nex` | **100 BEAST posterior trees; 42 tips per tree** |
| Same source | `ioch_data.csv` | **33 source-coded binary flower-colour records**; **not** HPLC/qPCR |
| Smith & Kriebel 2018, Dryad `10.5061/dryad.5jn7b` | `Smith_and_Kriebel_2018.zip/phylogenies/MCC_tree.nex` | **1 MCC tree; 44 tips** |
| Same source | `phylogenies/126_trees.nex` | **126 trees; 44 tips each** |
| Same source | `data/data.csv` | **36 source floral-shape/pollinator/colour rows**, colour counts purple 19, yellow 7, orange 5, white 3, red 2 |

Exact source file SHA256 and original provider archive SHA256 are saved in [`results/iochrominae_recovered_original_trees_20261119.json`](../results/iochrominae_recovered_original_trees_20261119.json). The deposited 2015 archive has SHA256 `2a7a92f600b0d92f874d636e90f5e2fcc3314876a7c4affc21b51e3c81701e5b`; its `IochBeast100.nex` SHA256 is `c2690a2b27d712684baab36be251e016904b98f60dd95156917a77a5a866c671`.

## Source integrity and biological inference

The original **2015** BEAST tree posterior is now recovered, directly from the original Dryad deposit. However, it is **not yet established which individual posterior tree or summary tree Larter et al. 2018 used**, and the 2018 flower-shape MCC tree is from a **separate publication** with **44** tips, not the same 42-tip 2015 posterior. The 2018 shape study provides a real floral colour/pollinator comparison opportunity but no original 2018 Larter HPLC or seven-gene qPCR species matrix.

The original Larter et al. 2018 MBE paper's publisher supplemental PDF and numeric HPLC/qPCR table remain blocked by HTTP 403 in the CI environment. Therefore the programme has recovered an original historical phylogenetic source, **not yet a second complete 2018 pigment × expression × phylogeny panel**. The previously established Petunieae gene-to-product result and the independent-radiation admission count of one are unchanged.

## Next source-bound action

Determine whether Larter et al. 2018 explicitly identifies the original Smith & Goldberg 2015 posterior and the relevant tree summary. Retrieve the original 2018 species-level quantitative HPLC and qPCR tables, verify their provider bytes and species IDs, then join to the verified tree tip names using an explicit source name mapping. No reconstructed plot-bar values, inferred species matches or post hoc substitute phylogenies should be treated as original measurements.

Camellia AJB Paper 1 and frozen EL v0.3 are untouched. Integrated PR #414 remains Draft.
