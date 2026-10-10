# Cape Erica 2025 phylogenomic source verdict — exact record is a target panel, not a species tree

**Status:** `PASS_EXACT_SOURCE_INVENTORY_NOT_AN_ERICA_SPECIES_TREE_SOURCE`. This is a **source-classification success**, **not** a biological hypothesis FAIL.

The connected public GitHub Actions execution [38061210098](https://github.com/zuizui0223/chun/actions/runs/38061210098) verified the original Figshare article (DOI `10.25375/uct.27134208`, article ID `27134208`) cited by Musker, Nürk & Pirie (2025), *PhytoKeys* 251:87–118, DOI `10.3897/phytokeys.251.136373`. Five focused tests passed.

## Source contents actually verified

| Figshare file ID | Original filename | Size bytes | Interpretation |
|---|---|---:|---|
| 49503738 | `ALL_Erica303_combined_HybPiper.fasta` | 2,303,729 | Marker-reference sequences |
| 49503729 | `ALL_Erica303_genomic_HybPiper.fasta` | 1,022,367 | Marker-reference sequences |
| 49503735 | `ALL_Erica303_transcripts_HybPiper.fasta` | 1,280,870 | Marker-reference sequences |
| 49503732 | `Readme.txt` | 2,044 | Describes those input sequence files |

The original `Readme.txt` was downloaded and matched the Figshare-provided MD5. It explains that the files are arranged for HybPiper target-capture workflows: they comprise reference targets from *Erica grandiflora*, *E. cinerea* and multiple *Rhododendron* transcriptomes. These **are not the study's terminal 30 *Erica* species phylogeny**. The source record contains neither a Newick/NEXUS tree nor any completed 30-tip species-tree object. Claiming a source-verified phylogenetic tree from a list of FASTA marker targets would be incorrect.

This verdict applies **to the four files of this specific identified Figshare record**. The original 2025 study published comparative trees, but the extracted data location for those exact completed tree objects was **not found in this record or its README**. This is not proof the trees are unpublished elsewhere.

## Effect on the ongoing analysis

The independently recovered Le Maitre et al. (2019) Cape *Erica* qPCR dataset (630 numeric values: 27 single-colour taxa candidates + one segregating three-morph subspecific lineage, all 3 floral stages and all 7 pathway genes) and the **30/30 source hue–expression ID crosswalk** remain intact. Table 2 visible-state pairs have an upper combinatorial bound of 117 among 27 single-colour candidates, not a verified number of sequenced phylogeny pairs. Neither the 2025 source FASTA sequences nor their associated paper's 30 sampled taxa can fill this tree/tree-tip match simply by article title.

The frozen new `Erica` question uses 7 genes × 3 floral stages among separate species sharing the same *visible* flower colour, and is categorically different from the exact *six-anthocyanidin-presence* state match in retrospective Petunieae. 2019 Table 2 qualitative chemistry cannot be promoted to quantitative HPLC. The 2016 original TreeBASE `S18291`, 2024 `S30617`/supplement 7 and this 2025 candidate are **distinct data sources** and cannot be silently interchanged.

A complete directly sampled branch-length tree is **still missing**. The current check does not compute a molecular-memory Spearman statistic, its within-colour permutation null, or any new biological result.

## Next finite source criterion

Only continue with a **specific, verified provenance record containing an actual inferred branch-length species tree and its tip list**. If present, require non-imputed sequenced-tip identity and manually justified taxon spelling/voucher mapping; then apply the already frozen support rule: at least 20 shared tips, 40 within-state pairs, and at least two colour states with three or more tips. If any of these fail, report `HOLD_SOURCE_SUPPORT` rather than lowering thresholds after exposure.

**Publication conclusion:** The 2025 paper provides useful context about low resolution of the rapid Cape *Erica* radiation, not an admitted independent mechanism-memory replicate. The frozen Camellia AJB and Evolution Letters v0.3 submission routes remain unchanged; the integrated proposal remains a Draft.
