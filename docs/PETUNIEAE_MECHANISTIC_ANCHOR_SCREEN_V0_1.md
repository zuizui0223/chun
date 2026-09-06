# Petunieae mechanistic-anchor screen — v0.1

## Decision

**Source admission: PASS_TO_EVENT_MAPPING.**

Petunieae is currently the strongest second mechanistic anchor for the cross-clade programme, not because it has a literal white ancestor, but because it provides a densely sampled **pale / low-visible-pigment ancestral state** followed by repeated derived pigmentation states under one coordinated molecular, biochemical and phylogenetic sampling programme.

It therefore fits the broader atlas hypothesis better than a forced `white ancestor` criterion:

`low-visible-pigment ancestral state -> repeated molecularly implemented colour intensification / hue shifts -> differential long-term realization`.

## Why this system is stronger than the current Epimedium molecular bridge

Wheeler et al. 2023 (`10.1098/rspb.2023.0275`) assembled a 60-taxon dataset (59 Petunieae + *Browallia americana*) with:

- an ASTRAL species tree from 3672 gene trees;
- developing-corolla RNA-seq, three biological replicates per species;
- public raw reads in SRA BioProject `PRJNA746328`;
- open transcriptome assemblies, scripts and processed files at `https://osf.io/zg9cu/`;
- HPLC measurements of six anthocyanidins and three flavonols;
- quantified expression of flavonoid structural genes and transcriptional regulators.

The molecular, chemical and phylogenetic layers were generated in the same coordinated programme and species identities are aligned across those layers. This removes the current Epimedium problem in which a garden accession phenotype cannot be crosswalked securely to a population/tree event.

## Ancestral baseline

The source stochastic-mapping analysis infers the Petunieae ancestor most likely belonged to a **pale-flowered, delphinidin-producing, high-flavonol phenotype** (reported probability ~0.7).

This is intentionally coded as:

`PALE_LOW_VISIBLE_PIGMENT`

not `WHITE`, `NO_PIGMENT`, or `MOLECULAR_ZERO`.

The result is conceptually useful because the ancestral phenotype already contains retained pigment machinery and flavonol production. Derived deep pigmentation can therefore be tested as regulatory/pathway redeployment from an existing biochemical state rather than de-novo invention.

## Repeated transitions

The source analysis estimates approximately four to five transitions from the pale phenotype to the intensely pigmented purple phenotype. It also identifies repeated changes along anthocyanin-intensity, flavonol-trade-off and hydroxylation axes.

This passes the **source-level recurrence admission** criterion, but it does not automatically pass the atlas historical-event gate.

Before estimating cross-clade molecular recurrence, the atlas must:

1. ingest the species-level tree, pigment and expression data under one fixed ontology;
2. recreate quantitative terminal states without choosing thresholds from reconstructed outcomes;
3. re-estimate transition/event identity under at least two defensible state resolutions;
4. require >=3 events to remain defensibly independent under those sensitivities;
5. only then compare molecular-module recurrence with Camellia.

## Functional-state mapping

Petunieae maps naturally onto the atlas ontology:

- `ANTHOCYANIN_DEPLOYMENT`: total anthocyanin amount / anthocyanin pathway expression;
- `COPIGMENT_FLAVONOL`: kaempferol, quercetin, myricetin and FLS-linked expression;
- `HUE_BRANCHING`: F3'H / F3'5'H and anthocyanidin hydroxylation state;
- `REGULATORY_STATE`: SG6 MYBs and other flavonoid regulators;
- `VISIBLE_STATE`: retained only as a secondary descriptor.

The source study itself finds a strong anthocyanin–flavonol trade-off, which is especially useful for testing whether the Camellia result generalizes from an A/F/C/P representation to a hierarchical functional-module representation.

## Novelty boundary

Petunieae is **not** a blank system. The source study already demonstrates pathway-structured accessibility and repeated expression-associated pigment evolution. The atlas contribution cannot be “discover that gene expression shapes Petunieae flower colour.”

The new cross-clade test is instead:

> When Camellia and Petunieae are re-expressed in one observation ontology, does the same hierarchy emerge—stronger recurrence at functional modules than at complete multivariate floral-pigment state, with accessible biochemical states broader than robustly realised historical states?

Thus Petunieae is primarily an **external validation / generalization anchor**, not a second case study whose known biology is repackaged as new.

## Current gate

- source/data admission: **PASS**;
- raw/processed ingestion: **NEXT**;
- atlas event identity: **PENDING**;
- second cross-clade mechanistic recurrence estimate: **BLOCKED until event remapping passes**.

Camellia Paper 1 remains scientifically closed and unchanged.
