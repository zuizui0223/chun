# CnFLS2 full-length recovery and same-paralog result

## Purpose

Resolve whether the early pink-directed tea FLS locus `CSA008358` and the author-classified *Camellia nitidissima* `CnFLS2` source transcript belong to the same paralog lineage, without using any macro flower-colour transition result.

This is a pre-macro orthology gate for `H_MICRO_MACRO_REUSE`.

## 1. What comes directly from the source literature

Feng et al. 2024 classify the PacBio transcript `F01.PB8395` in the `CnFLS2` group and use it as the qRT-PCR target for `CnFLS2`. Their supplementary table reports the primer pair:

- forward: `AGCAATCACCACCGTCAAAGG`;
- reverse: `CTCTTAGACTCAGCATCCTTAGC`.

The source paper and supplement do not expose the full `F01.PB8395` sequence. Therefore the literature alone does not identify its current genome locus or strict cross-species counterpart.

NCBI RunInfo independently connects the F01 PacBio transcriptome to the unique long-read run `SRR22729450` in BioProject `PRJNA909942`.

## 2. What chun recovered from public data

### 2.1 Whole-transcriptome primer gate

The published CnFLS2 primer pair was scanned against all **42,697** transcripts in the public *C. nitidissima* GWH RNA annotation.

Exactly one transcript passed the declared gate, and it was an exact pair match:

- transcript: `GWHTFILD005297.1`;
- gene: `GWHGFILD004416.1` / original annotation `Cpet02g11620`;
- protein: `GWHPFILD005297.1`;
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

### 2.3 Exact Longjing43 crosswalk

TPIA2 maps the tea source locus through the following exact chain:

`CSA008358 / CSS0045924 -> GWHTACFB016172 -> GWHGACFB016172 / GWHPACFB016172`

in the public Longjing43 assembly `GWHACFB00000000`.

This avoids substituting a merely similar tea locus from a different assembly. The local-context analysis therefore compares the source-linked tea locus directly with `GWHTFILD005297.1`.

### 2.4 Protein-family placement

A 40-terminal exploratory protein tree was built from the top 20 candidate homologs in each of the two public proteomes.

The target pair has:

- protein identity: **98.23%**;
- query coverage: **100%**;
- aligned length: **339 aa**;
- an exclusive sister relationship in the family tree;
- target-pair MRCA support: **0.977**;
- target-pair tree distance: **0.013553722**.

The nearest non-target sequence to both targets is the admitted *C. nitidissima* CnFLS1 anchor `GWHPFILD024733.1`, at substantially greater tree distance (`0.16175` from the *C. nitidissima* target and `0.15775` from the tea target).

### 2.5 Local synteny

Stable GWH accessions were normalized before comparing a 21-gene window centred on each target.

Results:

- the target genes are reciprocal best local protein hits;
- total local reciprocal-best anchors: **9**;
- non-target anchors: **8**;
- relative gene-order Spearman rho: **1.0**;
- orientation: **same**;
- longest same-orientation monotonic anchor chain: **8**;
- declared local-synteny gate: **passed**.

The target is therefore supported not only by sequence similarity but also by its position inside a strongly conserved local gene neighbourhood.

### 2.6 PacBio source-read validation

The admitted 1,020-bp candidate was queried directly against the F01 PacBio run `SRR22729450` using `blastn_vdb`, without converting the full archive.

Results:

- raw HSPs: **1,043**;
- unique read hits returned: **1,000**;
- reads admitted at identity >=80% and query coverage >=70%: **995**;
- full-length-like reads with query coverage >=95%: **583**;
- best single read: `SRR22729450.1253473.1`, **92.493%** identity and **100%** query coverage;
- consensus query coverage: **100%**;
- consensus identity to `GWHTFILD005297.1`: **99.705882%**;
- median coverage per covered query position: **944 reads**;
- minimum positional coverage: **393 reads**;
- all **43** primer positions covered;
- primer-consensus mismatches: **0**.

Thus the unique GWH candidate is not merely an annotation-based inference: its complete sequence is strongly represented in the source F01 PacBio reads, including the exact published qRT-PCR primer sites.

## 3. New chun inference

The combined source-primer, whole-annotation, full-CDS, PacBio-read, exact-crosswalk, protein-tree and local-synteny evidence supports:

> `GWHTFILD005297.1 / GWHPFILD005297.1` is the defensible public genome counterpart of the source `F01.PB8395` CnFLS2 target, and tea `CSA008358 / GWHPACFB016172` is its strongly supported same-paralog orthology counterpart.

Because the SRA archive stores raw reads rather than the source assembler's `F01.PB8395` record label, literal identifier equality cannot be read directly from SRA. The combined provenance chain nevertheless resolves the biological target operationally:

`F01.PB8395 source group + exact source primers + unique genome transcript + source-run read consensus`.

The later white-directed tea locus `CSA006950` is a separate FLS paralog.

This produces a concrete explanation for the stage-dependent FLS direction in the white/pink *C. sinensis* system:

> part of the apparent FLS sign switch can arise from **paralog substitution through development**, rather than one undifferentiated FLS locus reversing direction.

This hypothesis was generated from the chun quantitative meta-analysis plus public sequence and genome-context reanalysis. It is not merely a remaining question copied from the source papers.

## 4. Connection to the existing meta-analysis

The earlier meta-analysis established that the flavonol/FLS module is repeatedly labile but that FLS direction is stage- and paralog-dependent.

The present result resolves part of that heterogeneity:

- `CSA008358`: early pink-directed and strongly supported as the CnFLS2-like counterpart;
- `CSA006950`: later white-directed and sequence-distinct;
- symbol-level `FLS up/down` scores therefore compress different biological nodes.

This strengthens the hierarchical state-vector model:

`paralog identity -> module deployment -> pigment state vector -> visible/sensory phenotype`.

It also separates two macro hypotheses:

1. **module/state-vector reuse** remains the valid first held-out macro test;
2. **strict-node reuse** must be tested within resolved paralog lineages;
3. macro convergence may use the same module through either the same paralog or different paralogs.

The current result resolves one cross-species same-paralog pair and one source transcript counterpart. It does not yet show that this node was independently reused on multiple macro flower-colour branches.

## 5. Remaining research gate

The micro-level CnFLS2 identity problem is now substantially resolved. The remaining hard problem has moved to the macro level:

- reconstruct independent flower-colour and biochemical-vector transitions on an admitted nuclear tree;
- test whether the CnFLS2-like node or the broader flavonol module is repeatedly deployed on independent branches;
- distinguish same-paralog reuse from module convergence by different paralogs;
- only then relate repeated deployment to persistence, pollinator/sensory niche or conditional climate/light filtering.

Broader Camellia FLS sampling can refine the family tree, but it is no longer required merely to distinguish `CSA008358` from `CSA006950` in this micro system.

## Claim boundary

**Supported now:** a unique exact primer-compatible full-length candidate; strong F01 PacBio source-read support; a source-linked tea crosswalk; and strong sequence, tree and local-synteny support for the `GWHTFILD005297.1 <-> CSA008358` CnFLS2-like same-paralog orthology hypothesis.

**Operationally resolved:** the public genome counterpart of the source `F01.PB8395` CnFLS2 target, while preserving that the original assembled transcript label is absent from raw SRA records.

**Not supported now:** repeated strict-node reuse on independent macro branches; macro transition counts; or ecological selection pressure.
