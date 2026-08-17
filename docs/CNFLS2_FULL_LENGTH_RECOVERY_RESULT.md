# CnFLS2 full-length recovery result

## Purpose

Resolve whether the early pink-directed tea FLS locus `CSA008358` and the author-classified *Camellia nitidissima* `CnFLS2` source transcript belong to the same paralog lineage, without using any macro flower-colour transition result.

This is a pre-macro orthology gate for `H_MICRO_MACRO_REUSE`.

## 1. What comes directly from the source literature

Feng et al. 2024 classify the PacBio transcript `F01.PB8395` in the `CnFLS2` group and use it as the qRT-PCR target for `CnFLS2`. Their supplementary table reports the primer pair:

- forward: `AGCAATCACCACCGTCAAAGG`;
- reverse: `CTCTTAGACTCAGCATCCTTAGC`.

The source paper and supplement do not expose the full `F01.PB8395` sequence. Therefore the literature alone does not identify its current genome locus or its strict cross-species ortholog.

NCBI RunInfo independently connects the F01 PacBio transcriptome to the unique long-read run `SRR22729450` in BioProject `PRJNA909942`.

## 2. What chun recovered from public data

### 2.1 Whole-transcriptome primer gate

The published CnFLS2 primer pair was scanned against all **42,697** transcripts in the public *C. nitidissima* GWH RNA annotation.

Exactly one transcript passed the declared gate, and it was an exact pair match:

- transcript: `GWHTFILD005297.1`;
- gene: `GWHGFILD004416.1` / original annotation `Cpet02g11620`;
- coding length: **1,020 bp**;
- forward-primer mismatches: **0**;
- reverse-primer mismatches: **0**;
- predicted amplicon: **246 bp**;
- sequence SHA256: `7b5f8498cab54679d219c0decc567ad76bdcb15ce5968c13352ce46bb2328735`.

No other annotated GWH transcript matched both primers within two mismatches per primer.

### 2.2 Full coding-sequence comparison

The candidate was compared against coding-sequence references rather than intron-bearing transcript exports.

| reference | identity | aligned bp | mismatches | gap opens | query coverage |
|---|---:|---:|---:|---:|---:|
| tea `CSA008358` | **98.824%** | **1,020** | **12** | **0** | **100%** |
| published `CnFLS1` (`JF343560.1`) | 81.631% | 1,018 | 178 | 3 | 99% |
| tea `CSA006950` | 81.139% | 1,018 | 183 | 3 | 99% |

The identity margin between `CSA008358` and the next closest tested reference is **17.193 percentage points**.

An exploratory coding-sequence tree also pairs `GWHTFILD005297.1` with `CSA008358`, while `CSA006950` groups with the published CnFLS1 reference in the four-sequence panel. This small tree is diagnostic only and is not treated as a formal family-wide gene tree.

## 3. New chun inference

The combined primer and full-length evidence supports the following inference:

> The early pink-directed tea locus `CSA008358` and the *C. nitidissima* candidate `GWHTFILD005297.1` are likely counterparts in the CnFLS2-like paralog lineage, whereas the later white-directed tea locus `CSA006950` belongs to a distinct FLS paralog lineage.

This provides a concrete explanation for the stage-dependent FLS direction in the white/pink *C. sinensis* system:

> part of the apparent FLS sign switch can arise from **paralog substitution through development**, rather than one FLS locus reversing its response.

This hypothesis was generated from the chun quantitative meta-analysis plus the public sequence crosswalk. It is not merely a remaining question copied from the source papers.

## 4. Connection to the existing meta-analysis

The earlier meta-analysis established that the flavonol/FLS module is repeatedly labile but that FLS direction is stage- and paralog-dependent.

The present result resolves part of that heterogeneity:

- `CSA008358`: early pink-directed and CnFLS2-like;
- `CSA006950`: later white-directed and sequence-distinct;
- therefore a symbol-level `FLS up/down` score compresses two different biological nodes.

This strengthens the hierarchical state-vector model:

`paralog identity -> module deployment -> pigment state vector -> visible/sensory phenotype`.

It also refines `H_MICRO_MACRO_REUSE`:

1. module/state-vector reuse remains the valid first macro test;
2. strict node reuse must be tested inside resolved paralog lineages;
3. macro convergence may use the same module through either the same paralog or different paralogs.

## 5. What is still not identified

The current result does **not** yet prove all of the following:

- that `GWHTFILD005297.1` is literally the source assembly record `F01.PB8395`;
- formal CnFLS2–`CSA008358` orthology across a broadly sampled FLS family;
- conserved synteny between the two loci;
- repeated strict-node reuse on independent macro flower-colour branches.

The remaining public-data gates are:

1. recover source-read or consensus support from `SRR22729450`;
2. add broader Camellia FLS-family sequences and infer a proper gene tree;
3. compare locus neighbourhood/synteny where assemblies permit;
4. only then use the resolved paralog class in the held-out macro enrichment test.

## Claim boundary

**Supported now:** a unique exact GWH primer-compatible candidate and a strong sequence-supported same-paralog/orthology hypothesis linking `GWHTFILD005297.1` to tea `CSA008358`.

**Not supported now:** exact source-transcript naming, formal orthology, macro reuse, or ecological selection pressure.
