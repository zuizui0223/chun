# Tea pigment orthology / paralog crosswalk result

## Purpose

This analysis asks how far the micro-accessibility evidence can be resolved from enzyme-family names to sequence-supported loci **before** any macroevolutionary transition branch is inspected.

The result keeps three levels separate:

1. source-paper annotation and experimental result;
2. `chun` public-database/sequence crosswalk result;
3. hypotheses that still require full-length orthology, gene trees or synteny.

## 1. TPIA2 public route recovered

The public TPIA2 interfaces were audited rather than guessed.

Priority source IDs were submitted to the Gene ID Convert endpoint across all source namespaces exposed by the site. Seven of ten IDs resolved **only** in the Yunkang10 namespace; the three non-resolving IDs were all `CSNG...` de novo transcript IDs from the source study rather than genome IDs.

Resolved Yunkang10 source rows:

- `CSA003949`;
- `CSA006950`;
- `CSA008358`;
- `CSA011508`;
- `CSA011986`;
- `CSA018523`;
- `CSA019984`.

For all seven rows, Yunkang10, Shuchazao v1 and Shuchazao v2 CDS/transcript sequences were recovered through the public Batch Retrieve endpoint. The sequence workflow recovered `7 loci × 3 genomes × 2 sequence types = 42/42` FASTA records.

## 2. TPIA ID rows are strongly sequence-supported but gene models can differ

Across Yunkang10, SCZ v1 and SCZ v2, the seven converted rows have very high identity over overlapping CDS sequence.

Examples:

- `CSA003949 -> TEA024758 -> CSS0011557`: minimum pairwise nongap identity `0.9932`;
- `CSA006950 -> TEA010328 -> CSS0007745`: `0.9911`;
- `CSA008358 -> TEA016601 -> CSS0045924`: `0.9941`;
- `CSA011508 -> TEA010322 -> CSS0010687`: `0.9978`;
- `CSA018523 -> TEA027582 -> CSS0009063`: `1.0000` over overlapping CDS.

This supports the database crosswalk rows at sequence level.

However, gene models are not always coextensive. For example `CSA019984` is 522 bp in the Yunkang10 CDS export versus 1197 bp in both SCZ exports. Its overlapping sequence is `0.9981` identical, but full-alignment identity is only `0.435` because the Yunkang10 model is much shorter.

**Conclusion:** TPIA row correspondence is strongly supported; do not equate it automatically with identical complete gene models.

## 3. Same enzyme symbol can hide strongly separated paralogs

### FLS

The two `C. sinensis` source FLS loci are clearly distinct sequences:

- `CSA006950` versus `CSA008358` CDS nongap identity is ~`0.82-0.83` across Yunkang10/SCZ versions.

This matters because they also have different developmental directions in the white/pink source dataset:

- `CSA008358` is pink-directed at the early informative stage;
- `CSA006950` is white-directed at later stages.

Thus part of the apparent `FLS direction changes through development` pattern can arise from **different FLS paralogs becoming the informative locus at different stages**, not necessarily one FLS gene reversing direction.

### LAR

`CSA018523` and `CSA019984` are also distinct LAR-family rows, with CDS nongap identity ~`0.72-0.79` depending on genome version.

Again, an enzyme-family symbol is not a unique evolutionary node.

## 4. CnFLS provenance correction and the CnFLS2-like tea paralog

A temporary sequence screen using unverified `XP_...` accessions as `CnFLS1/2/3` was rejected after NCBI identity checks showed those accessions were not the claimed `C. nitidissima` FLS paralogs. The invalid screen and workflow were removed before merge.

The analysis was rebuilt from the Feng 2024 primary supplement itself.

The authors' Supplementary Fig. 8 groups source transcripts as:

- CnFLS1: `F01.PB53224`, `F01.PB58793`, `F01.PB6032`;
- CnFLS2: `F01.PB57785`, `F01.PB107898`, `F01.PB59604`, `F01.PB41677`, `F01.PB49622`, `F01.PB8395`, `F01.PB39893`;
- CnFLS3: `F01.PB4564`, `F01.PB102531`, `F01.PB53935`;
- CnFLS4: `F01.PB10952`, `F01.PB4098`, `F01.PB29531`.

Supplementary Table 4 provides a qRT-PCR primer pair for the author-classified `CnFLS2` transcript `F01.PB8395`.

That primer pair was tested against the two sequence-resolved tea FLS source paralogs and the published complete `C. nitidissima` CnFLS1 cDNA `JF343560.1`.

Result:

- `CSA008358 -> CSS0045924`: **0 forward mismatches + 0 reverse mismatches**, paired hit, predicted amplicon `246 bp`;
- `CSA006950 -> CSS0007745`: forward mismatch 5, reverse mismatch 4, no paired decisive hit;
- CnFLS1 `JF343560.1`: forward mismatch 5, reverse mismatch 3, no paired decisive hit.

### chun inference

The strongest current paralog hypothesis is therefore:

> **the early-stage pink-directed tea FLS locus `CSA008358/CSS0045924` is CnFLS2-like in the exact qRT-PCR amplicon, whereas the later white-directed `CSA006950/CSS0007745` is a distinct FLS paralog.**

This provides a concrete mechanistic explanation for the previously observed stage-dependent FLS sign pattern: some of that heterogeneity can reflect **paralog substitution**.

This is not yet a formal orthology assignment because the public supplement does not provide a full-length `F01.PB8395` sequence in the current recovered package. Formal `CnFLS2 <-> CSS0045924` naming still requires full-length sequence plus gene-tree/synteny evidence.

## 5. DFR: source locus is not the canonical tea DFRa

The source `DFR` locus `CSA003949` resolves through TPIA2 to `TEA024758`.

Primary tea DFR-family work identifies `TEA024758` as the **CsDFRb2** subclass and distinguishes it from canonical experimentally characterized `CsDFRa = TEA032730`.

Therefore the source white/pink expression result must be narrowed:

> `CSA003949` is DFR-family / CsDFRb2-subclass evidence, not evidence that canonical `CsDFRa` is the changing source locus.

This refinement reduces false exact-node reuse while preserving anthocyanin-module accessibility.

## 6. CSA011508: resolve toward ANS/LDOX, not LAR

The Zhou processed table labels `CSA011508` inconsistently as `LAR`, `FLAR` or `LAR` in different stage sheets.

The original source supplement/main text, however, explicitly uses `CSA011508` as `LDOX1` and provides a qRT-PCR assay. TPIA2 maps the locus to `TEA010322 / CSS0010687`, and independent primary tea studies identify `CSS0010687` as an ANS/CsANS1/CsANSa-type locus.

**Decision:** preserve the source annotation conflict as provenance, but classify `CSA011508` under the **ANS/LDOX family**, not strict LAR evidence.

This raises the C. sinensis ANS family evidence from a generic symbol to one sequence-supported source locus, while exact cross-species ANS paralog reuse remains unresolved.

## 7. CSNG de novo unigenes do not simply map to known genome candidates

The source study calls `Csng38209` and `Csng45659` new unigenes annotated as DFR. It also reports `Csng5035`/`Csng05035` as LAR-like.

Public qRT-PCR primers were recovered for:

- `Csng45659 / DFR`;
- `Csng5035 / LAR-like`.

Predeclared candidate panels were constructed independently of the primer result:

- seven established tea DFR-family candidates for `Csng45659`;
- four source-listed genome LAR candidates for `Csng5035`.

The primer pairs were tested across candidate CDS, transcript and exon exports.

Result:

- `Csng45659`: **no amplicon-compatible candidate** across the seven DFR candidates;
- `Csng5035`: **no amplicon-compatible candidate** across the four LAR candidates.

This does **not** show that the CSNG unigenes are novel genes. It only rejects a simple mapping to those predeclared known candidate loci. Full de novo transcript/assembly sequence is still required for strict node assignment.

## 8. Consequence for the micro-accessibility ranking

Current family-level recurrence remains:

- FLS: 3 independent micro clusters;
- ANS: 3;
- DFR: 2;
- ANR: 2.

Sequence anchoring has improved:

- FLS: source transcript groups and a strong CnFLS2-like local amplicon hypothesis;
- ANS: `CSA011508 -> CSS0010687` sequence-supported ANS/LDOX family anchor;
- DFR: `CSA003949 -> CsDFRb2` subclass anchor;
- named `CjMYB114` and `CjbHLH1` remain exact one-cluster sequence anchors.

But the decisive held-out gate remains unchanged:

> **zero features currently have the same fully sequence-resolved strict ortholog/paralog demonstrated in two or more independent micro clusters.**

Thus family/module recurrence is not converted into exact-gene recurrence.

## 9. H_MICRO_MACRO_REUSE test order

### First test — ready once a safe nuclear history is admitted

Test **module/state-vector reuse**:

- anthocyanin downstream;
- flavonol;
- PA;
- carotenoid;
- regulatory module;
- direction of quantitative state-vector displacement.

### Second nested test — still held out

Test strict gene/paralog reuse only after full-length sequence/gene-tree/synteny mapping makes the same node comparable across independent micro systems.

## Claim boundary

Supported now:

- sequence-level provenance for seven legacy CSA source loci across three tea genome versions;
- clear within-family FLS and LAR paralog separation;
- `CSA003949` is CsDFRb2-subclass rather than canonical CsDFRa;
- `CSA011508` is best classified as ANS/LDOX despite later table-label conflict;
- `CSA008358/CSS0045924` is a unique exact local amplicon-compatible candidate for the source CnFLS2 qRT-PCR target among the tested tea FLS paralogs and CnFLS1 reference;
- CSNG45659 and CSNG5035 do not simply map to the predeclared known family candidates.

Not supported now:

- formal full-length `CnFLS2 <-> CSA008358/CSS0045924` orthology;
- strict cross-species repeated exact-node reuse;
- a universal exact-gene accessibility hierarchy;
- any macroevolutionary or ecological selection inference from these sequence crosswalks.
