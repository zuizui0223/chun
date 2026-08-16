# Camellia flower-colour transition phylogeny gate

## Purpose

The flower-colour meta-analysis now has a repeated mechanistic signal. The next question is historical:

> **How many times did Camellia move into and out of white, anthocyanin-rich red/pink and yellow phenotypes?**

This document prevents a transition-count analysis from being run on a convenient but biologically inappropriate single tree.

## 1. Published primary reference: Fan et al. 2026

Fan et al. (`10.1111/pbi.70442`) analysed 237 accessions representing 129 species using 4,182,517 nuclear SNPs. The published study:

- recovers seven major clades;
- places white-flowered *C. pilosperma* in a unique basal position;
- reports white, yellow and red phenotypes in early-diverging Clade 1;
- reconstructs white as the most likely ancestral **visible** flower colour using both maximum parsimony and maximum likelihood;
- notes multiple potential red-white transitions;
- provides the complete 237-accession IQ-TREE topology as Supporting Figure S1 and the colour ASR as Figure S4.

However, the data-availability statement says that the underlying data are available on request. The public supporting files provide figures, not a machine-readable Newick/branch-length tree and raw SNP matrix suitable for a reproducible stochastic-mapping analysis.

### Admission rule

The Fan 237 result can be used as:

- a published reference topology/state reconstruction;
- a qualitative source for candidate transition branches;
- a benchmark against independent public nuclear trees.

It cannot be silently converted into an exact branch-length tree or treated as a locally reproduced origin-count analysis.

## 2. Fully public independent nuclear backbone: Wu et al. 2022

Wu et al. (`10.1111/tpj.15799`) generated transcriptomes for 116 Camellia plants covering almost all sections plus *Polyspora speciosa* and reconstructed the genus from 405 high-quality low-copy nuclear core genes. Raw reads are deposited under `PRJNA665925`.

This is currently the highest-value **fully public** alternative backbone for the colour-transition project because it is:

- nuclear rather than plastid;
- genus-scale;
- based on hundreds of low-copy genes;
- independently sampled from the Fan 237 resequencing study;
- reconstructable from public sequence reads.

`data/camellia_phylogeny_public_seeds_v0_1.csv` and the `Camellia public nuclear backbone manifest` workflow resolve this BioProject before any tree reconstruction is admitted.

### Limitation

Flower colour was not the primary phenotype in Wu et al. The phylogeny and the colour-state evidence must therefore be joined only after an authority-backed taxon/state table is frozen. Horticultural cultivar colours must not be projected onto wild species without evidence.

## 3. Additional nuclear topology sets

The colour-history analysis should not rely on one reconstruction because Camellia is a rapid and partly reticulate radiation.

### Zan et al. 2023 — 87 species

- 95 transcriptomes / 87 species;
- 1,481 low-copy nuclear genes;
- multiple concatenation/coalescent gene subsets;
- extensive conflict among major clades and evidence for reticulate evolution.

Role: test whether inferred colour gains/losses are stable to reticulation-sensitive alternative topologies.

### Zhang et al. 2023 — 55 species

- 60 transcriptomes / 55 species;
- 1,617 low-copy nuclear genes;
- coalescent species trees and explicit gene-tree-discordance/polytomy analyses;
- rapid diversification highlighted as a major source of conflict.

Role: sensitivity to a separately assembled low-copy nuclear data set.

### Yan et al. 2024 — Angiosperms353

- 44 Camellia species embedded in 68 Theaceae representatives;
- 348 recovered nuclear target loci;
- coalescent and concatenation analyses;
- substantial gene-tree heterogeneity; ILS explains part of the discordance.

Role: independent marker technology and robust outgroup-rooting sensitivity.

The public/deposition routes for these three datasets still need to be frozen in `chun`; they remain literature topology sets until that provenance gate is completed.

## 4. Why plastid-only transition counts are inadmissible

Multiple Camellia studies report cytonuclear discordance, introgression/hybridisation and/or chloroplast capture. Therefore:

- a plastid tree may be visualised as a maternal-history sensitivity;
- a plastid tree cannot be the sole backbone used to claim the number of flower-colour origins;
- disagreement between nuclear and plastid colour histories is itself a result that can motivate introgressive colour recruitment.

## 5. Visible-state analysis

The first M3 analysis uses only evidence-backed visible states:

- `W`: white / near-white;
- `A`: pink/red/crimson/purple-red anthocyanin-like visible class;
- `Y`: yellow;
- `M`: mixed/sectorial or documented stable polymorphism;
- `U`: unresolved.

Do not force morphs or polymorphic taxa into one deterministic state. State uncertainty should be carried into sensitivity analyses.

### Models

At minimum compare:

1. ER — equal transition rates;
2. SYM — symmetric pairwise rates;
3. ARD — all rates different;
4. constrained/penalised direct `A <-> Y` models;
5. hidden-state alternatives if simple Mk models fit poorly.

### Required outputs

Across admitted nuclear tree sets report distributions rather than one event count:

- `P(N_A_gains = k)`;
- `P(N_W_gains = k)`;
- `P(N_Y_gains = k)`;
- expected numbers of A→W, W→A, W→Y, Y→W and A↔Y transitions;
- probability that apparent A↔Y changes pass through W;
- root-state probability under alternative priors/models;
- branch-level candidate regain/reactivation probabilities.

## 6. Mechanistic-state analysis

The visible-state analysis is not the final evolutionary model. Once pigment chemistry and common expression-module scores are available, repeat reconstruction in a mechanistic state space such as:

- anthocyanin deployment (`A`);
- flavonol deployment (`F`);
- carotenoid deployment (`C`);
- proanthocyanidin/procyanidin diversion (`P`) where supported.

A visible yellow state may be `F-high`, `C-high`, or both. A white state may retain substantial flavonoid deployment. Therefore the number of visible-colour origins and the number of biochemical-mechanism origins are separate quantities.

## 7. Reactivation claim gate

A branch may be called a true floral-pigment **reactivation** only when all are satisfied:

1. a supported nuclear history contains active → suppressed/absent → active states;
2. the intervening white/low-pigment state retains the relevant pathway machinery;
3. the descendant active state reuses retained machinery rather than requiring independent structural reconstruction;
4. the inference remains plausible across the admitted tree/model uncertainty.

Otherwise use `retention`, `recruitment/gain`, or `candidate regain`.

## 8. Current major gap and resolution path

The main historical bottleneck is no longer a lack of nuclear Camellia data. It is the **join between phylogeny and defensible flower-colour states**.

The resolution path is:

1. resolve and freeze `PRJNA665925` run/taxon metadata;
2. reconstruct/publicly import the 405-locus nuclear backbone;
3. build a species-level colour evidence table from taxonomic treatments, figures, pigment studies and documented polymorphism;
4. compare its topology with Fan 237 and the additional nuclear studies;
5. only then run stochastic mapping and transition-model comparison.

This produces an independent public-data answer to the central question without pretending the Fan 237 raw SNP data are public.

## Claim boundary

Supported now:

> Multiple independent nuclear phylogenomic studies show that Camellia is a rapid radiation with substantial gene-tree/topology conflict, while the broadest current published flower-colour reconstruction favours a white visible ancestor and notes repeated colour transitions.

Not yet supported:

- an exact number of white, red/pink or yellow gains;
- a universal `white -> red -> yellow` or `yellow -> white -> red` sequence;
- a branch-specific true reactivation without molecular-retention evidence;
- a transition count derived from a single plastid topology.
