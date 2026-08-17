# Quantitative Camellia pigment-state-vector meta result

## Question

After the dependence-aware literature synthesis established recurrent regulatory/pathway-flux lability, can public processed quantitative data show whether flower-colour variation is adequately represented by one scalar `anthocyanin versus competing branch` axis?

## Independence and assay rule

Four independent quantitative systems are currently admitted:

1. `CSIN_WHITE_PINK` — *C. sinensis* white ZJW versus pink BTP, reported expression across five matched developmental stages;
2. `CRETICULATA` — *C. reticulata* red HHYC / pink XJ / white TZM, reported expression plus metabolite data;
3. `CJAPONICA` — *C. japonica* white-to-crimson cultivar gradient, reported metabolite data;
4. `OIL_CAMELLIA_MULTI` — author-defined W/P/CP/R colour materials, reported metabolite data. The source has conflicting taxon-name mappings, so only colour-material labels are admitted.

Expression and metabolite effect magnitudes are **not pooled as commensurate effect sizes**. The cross-system unit is the independence cluster and the direction of pre-defined relative allocation contrasts.

## Result 1 — anthocyanin versus flavonol separation recurs across four systems

All four quantitative systems show a positive redder-state shift in `anthocyanin - flavonol` allocation.

- *C. sinensis*: positive in 5/5 developmental stages after the S6 sample-label provenance correction;
- *C. reticulata*: red-white relative allocation difference `+4.5854 log2`;
- *C. japonica*: crimson-white relative allocation difference `+5.0828 log2`;
- oil-Camellia W/P/CP/R materials: red-white relative allocation difference `+6.4196 log2`.

Across the four independence clusters:

- positive = `4/4`;
- exact two-sided sign test `P = 0.125`;
- Beta(1,1) directional-concordance mean = `0.8333`;
- 95% interval = `0.4782–0.9949`;
- `P(direction > 0.5) = 0.96875`.

This is a replicated preliminary quantitative pattern, but `n=4` is not sufficient to call the direction universal or estimate its natural evolutionary frequency.

## Result 2 — proanthocyanidin allocation is not a universal opposite branch

The PA axis behaves differently from FLS/flavonol.

- *C. sinensis*: LAR is pink-directed in 10/10 gene-stage observations; `anthocyanin - PA` is positive in only 3/5 stages and is developmentally mixed overall;
- *C. reticulata*: total PA is slightly white-enriched while anthocyanin is strongly red-enriched;
- *C. japonica*: PA declines moderately toward crimson while anthocyanin rises strongly;
- oil-Camellia colour materials: PA itself **increases** from white to red (`+0.876 log2`), although anthocyanin increases more strongly.

Thus PA can move with anthocyanin in some systems and against it in others. It cannot be merged with FLS into one generic `competing branch` scalar.

## Result 3 — accessibility is node/paralog-specific as well as module-specific

The complete *C. reticulata* 61,277-gene table shows substantial directional heterogeneity among broad KEGG homolog families. For example, DFR-like and ANS-like homologs include both red- and white-directed paralogs, while the source-highlighted late UFGT set gives a much cleaner state association:

- 4/4 highlighted UFGT loci are red > white;
- 3/4 are red > pink > white;
- four-locus red-white module Hedges `g = 2.236` within that study.

Therefore a pathway-level label is too broad for `H_MICRO_MACRO_REUSE`. The relevant hierarchy is:

`node/paralog accessibility -> module-state displacement -> biochemical/spectral phenotype`.

## Provenance finding — processed supplements need their own data audit

The *C. sinensis* supplement contains a reproducible sample-label conflict:

- Table S8/S9 and article mapping: ZJW = white, BTP = pink;
- Table S6 printed headers are reversed relative to those sources;
- 16/16 overlapping gene-stage FPKM triplets match only after swapping the S6 BTP/ZJW labels;
- direct match = 0/16, swapped match = 16/16.

The quantitative workflow therefore applies an explicit provenance gate before using S6. This is an example of why public processed tables should not be pooled without cross-table metadata verification.

## New model requirement — H_PATHWAY_STATE_VECTOR

The minimum supported biochemical representation is now:

`P = [anthocyanin, flavonol, proanthocyanidin, carotenoid, ...]`.

Each component should preserve node/paralog identity where possible. Human-visible W/A/Y is an observation generated from this state together with optical and sensory factors, not the mechanistic state itself.

## Connection to the macro programme

This result strengthens the **generation** side of the project:

- regulatory/flux lability is robust at the literature-meta level;
- quantitative processed data show recurrent anthocyanin/flavonol state-vector separation in four independent systems;
- node/paralog heterogeneity means macro reuse must be tested on independently reconstructed transition branches rather than inferred from pathway-wide expression or extant state abundance.

It does **not** identify:

- how many independent macro gains occurred;
- whether generation or persistence causes A/Y lineage concentration;
- whether a state-vector component is the ecological selection target;
- whether any Camellia branch is a true adaptive reactivation.

Those remain branch-history and matched ecological/fitness questions.

## Claim ceiling

The strongest defensible statement is:

> Public quantitative Camellia flower-colour datasets independently support a multidimensional pigment-allocation architecture, with a recurrent redder-state shift of anthocyanin relative to flavonol in the four currently recoverable quantitative systems, while proanthocyanidin allocation and individual paralogs remain heterogeneous.

Do not convert `4/4` into a natural mechanism-frequency estimate or a universal evolutionary law.
