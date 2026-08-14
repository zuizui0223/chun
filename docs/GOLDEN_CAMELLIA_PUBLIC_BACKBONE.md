# Public golden-*Camellia* backbone

## Why this exists

The two strongest 2026 broad *Camellia* colour studies are not currently reproducible from open raw population data: their data-availability statements are request-based. The project therefore separates:

1. **published colour-history evidence** from those 2026 studies; and
2. **open sequence evidence** that can be reanalysed independently now.

The most useful open yellow-lineage bridge is Xie et al. (2025; DOI `10.1038/s41598-024-83004-3`), which deposited one leaf transcriptome for each of 20 named golden-*Camellia* accessions/species. The exact paper Table 1 mapping is frozen in `data/golden_camellia_20_transcriptomes_v0_1.csv`.

## Why the dataset is valuable

The 20 accessions include:

- a Northeast Vietnam yellow accession (*C. insularis*; `SRR27212634`);
- Guangxi acid-soil and limestone lineages;
- *C. longruiensis* (`SRR27212615`), which connects an open leaf transcriptome to the separate published 2026 WRKY23→FLS yellow-flavonol mechanism;
- *C. flavida*, *C. chrysanthoides* and multiple names subsequently placed inside or close to those species complexes.

Because the material is **leaf RNA-seq**, this dataset can support:

- nuclear phylotranscriptomic reconstruction;
- coding-sequence presence and orthology tests;
- FLS/DFR/ANS and regulator-family sequence comparisons where expressed;
- testing whether candidate yellow lineages retain broadly similar pigment-pathway coding machinery.

It cannot directly support petal-specific pathway expression.

## Taxonomic-independence gate

The 20 published names must not be interpreted as 20 independent evolutionary units.

Liu et al. (2025; DOI `10.1186/s12870-025-07067-8`) re-examined golden *Camellia* species concepts using nuclear ITS and complete chloroplast genomes. Their results document extensive hybridization and chloroplast capture and tentatively recognize about 23 Chinese golden-flower species. For the public 20-transcriptome set, several consequences are immediate:

- *C. longgangensis* → treated as a synonym of *C. flavida*;
- *C. longruiensis* → treated as a synonym of *C. flavida*;
- *C. longzhouensis* → not a clean independent lineage; linked to the *C. chrysanthoides* complex and proposed as a possible hybrid involving *C. chrysanthoides* and *C. ptilosperma* / *C. flavida*;
- *C. limonia* and several other names show conflicting/repeated placements in the taxonomic datasets;
- *C. terminalis* and *C. tunghinensis* receive explicit support for species-level status in that revision.

Therefore the project uses three separate quantities:

1. `published_name_count` — number of labels in the transcriptome paper;
2. `taxonomically_independent_lineage_count` — only units passing the taxonomic gate;
3. `sequence_sample_count` — all sequence samples retained for within-complex and reticulation analyses.

Only quantity 2 may enter a count of independent colour transitions.

## Reticulation rule

A plastid tree is not permitted to define the main yellow-state transition history when nuclear/plastid conflict is present. Chloroplast genomes remain useful for tracing maternal/geographic history, but they cannot substitute for a nuclear species-history model in a reticulate group.

The public 20-transcriptome data therefore have priority over plastid-only placement for a first independent nuclear backbone. ITS/plastid results are used to flag species complexes, hybrids and possible chloroplast capture, not to force one fully bifurcating history.

## Immediate analysis sequence

### Gate G1 — live archive verification

`Golden Camellia public backbone` GitHub Actions resolves all 20 SRR accessions against live NCBI SRA and freezes:

- Run;
- BioProject;
- BioSample;
- archive ScientificName;
- library layout/source;
- sequence yield and hashes where provided.

A missing or substituted SRR fails the gate.

### Gate G2 — taxonomic reconciliation

For every sequence sample, store:

- transcriptome-paper name;
- accepted/working name;
- taxonomic status (`independent`, `species_complex`, `synonym`, `hybrid_candidate`, `unresolved`);
- nuclear evidence;
- plastid evidence;
- voucher/type-locality compatibility where available.

No state-transition count is run before G2.

### Analysis G3 — open nuclear backbone

Reconstruct the 20-sample nuclear topology from single-copy orthologs or independently reproduce the published phylotranscriptomic topology. The original divergence-time estimates are not a target for confirmation because the paper itself reports failure of the molecular-clock assumption and treats the time estimates as tentative.

### Analysis G4 — pigment-pathway coding architecture

Screen expressed coding sequences for:

- `FLS` family, including homology to *C. nitidissima* CnFLS/CnFLS1 (`JF343560.1`) and T2T-genome FLS paralogs;
- `DFR`;
- `ANS/LDOX`;
- `CHS`, `CHI`, `F3H`, `F3'H/F3'5'H`;
- `UFGT` where expressed;
- candidate MYB/bHLH/WD40 regulators;
- candidate WRKY regulators, especially the mechanistically implicated WRKY23 class.

Presence in leaf transcriptomes can support retention of coding capacity. Absence from leaf RNA-seq is **not gene loss**.

### Analysis G5 — connect mechanism to history

Combine:

- public yellow-lineage coding architecture;
- public *C. nitidissima* S1–S5 flower RNA-seq (`SRP112181`);
- public *C. nitidissima* T2T genome;
- published functional evidence for CnFLS1/CnFLS2 and WRKY23→FLS;
- published 2026 broad colour-history results as an external, non-reproduced evidence layer.

The goal is to ask whether different yellow lineages share the same biochemical/regulatory deployment or only the same visible phenotype.

## What this changes conceptually

The Southeast Asian yellow comparison is no longer:

> how many yellow *Camellia* species are there, and how many times did yellow arise?

It becomes:

> how many **taxonomically independent and molecularly distinguishable lineages** deploy yellow pigmentation, which pigment branches do they use, and did those deployments arise by retention, repeated recruitment, hybrid transfer, or regulatory switching?

This makes the yellow comparison directly commensurable with the East Asian *Cirsium* question, where a coloured descendant is not called a reactivation until both history and latent pathway retention are demonstrated.