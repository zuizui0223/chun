# White-baseline atlas source ingestion — v0.2

## Current result

The cross-clade atlas now distinguishes **published conclusion availability** from **reconstructable source-data availability**. This is essential because the planned study will re-estimate trait histories under one common protocol rather than copy ancestral-state conclusions from papers.

The source manifest is `data/white_baseline_source_ingestion_v0_2.csv`.

## Four priority systems

### 1. Antirrhineae — READY

Ellis & Field provide a dedicated open research-data object (`10.15479/AT:ISTA:34`) containing flower-colour data and phylogeny files under CC0. This is the cleanest first ingestion target.

Expected use:
- recover all taxon-level anthocyanin/yellow phenotype codes;
- retain polymorphic states rather than collapse them;
- recover the published phylogeny/NEXUS;
- normalize names to current taxonomy;
- rerun transition models under the common atlas model set.

### 2. Epimedium sect. Diphyllon — READY WITH EXTRACTION

The 2023 phylogenomic study (`10.3389/fpls.2023.1234148`) explicitly assembled reproductive morphometric data for 41 species plus one unknown taxon and 699 individuals. Inner-sepal colour is coded as white/yellow/red/purple and spur colour as white/yellow/red/purple/brown. Supplementary files are open.

The companion molecular study (`10.3389/fpls.2023.1133616`) supplies eight-species anthocyanidin and pathway-gene expression/function evidence.

Expected use:
- extract species-level colour states from the reproductive-trait supplement;
- preserve separate inner-sepal and spur colour axes before any combined visible-state coding;
- map eight molecular species onto the macro tree without assuming that pigmentation loss/gain direction is identical across floral organs.

### 3. Linoideae — REBUILD REQUIRED

The 2022 paper (`10.3390/plants11121579`) reports colour coding for 112 species and provides accessions, dated phylogenies and ancestral-state figures. However, the supplementary package does not expose a standalone 112-tip terminal colour table.

Therefore this clade will contribute genuinely original data curation:
- rebuild the terminal colour matrix taxon-by-taxon from the same floristic/herbarium sources where possible;
- record provenance per taxon;
- compare the rebuilt matrix with the published tip colours/ancestral reconstruction as a QC target;
- never digitize an ambiguous colour from a figure when a primary textual source can be recovered.

### 4. Hydrangea sect. Cornidia — REBUILD REQUIRED

The 2021 paper (`10.3389/fpls.2021.661522`) provides taxon sampling, voucher/accession data, alignments and gene trees. Flower colour is reconstructed in the paper, but no standalone terminal colour matrix is exposed in the supplement.

Expected use:
- rebuild wild flower-colour states from field records, taxonomic descriptions and article evidence;
- retain white/red/purple and polymorphic/uncertain states explicitly;
- re-estimate transition rates instead of importing the published rate matrix;
- use this system as the primary falsification test against a one-way white-to-colour narrative.

## Source-quality finding

The first four clades already span three distinct data regimes:

1. `READY_MACHINE_READABLE` — Antirrhineae;
2. `READY_WITH_EXTRACTION` — Epimedium;
3. `REBUILD_REQUIRED` — Linoideae and Hydrangea-Cornidia.

This heterogeneity is not a nuisance to hide. It becomes part of the atlas observation process and must be recorded explicitly, analogous to the observation-regime logic in Camellia Paper 1.

## Original-data contribution

For Linoideae and Hydrangea-Cornidia, the harmonized terminal trait matrix will not be a copied published table because no such machine-readable table is currently exposed. The atlas must reconstruct these states with row-level provenance and uncertainty flags. That derived dataset is a substantive original research product.

For Antirrhineae and Epimedium, originality comes from re-coding existing open observations into the same cross-clade ontology and re-estimating trait histories under identical transition-model and uncertainty rules.

## v0.3 gate

Proceed to actual pooled macro modelling only after:

- Antirrhineae matrix/tree is ingested and reproduced;
- Epimedium species-level inner-sepal/spur colour matrix is extracted;
- at least one of Linoideae or Hydrangea-Cornidia has a newly rebuilt terminal matrix with >=80% of the published phylogenetic tips assigned or explicitly unresolved;
- all admitted clades pass the same taxonomy/provenance validator;
- coloured-ancestor control Iochrominae is prepared as the first molecular benchmark.

Until these conditions are met, `macro_literature_admission = PASS` but `pooled_analysis = BLOCKED`.
