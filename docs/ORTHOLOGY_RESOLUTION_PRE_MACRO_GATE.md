# Orthology resolution pre-macro gate

## Question

The micro-accessibility score v0.1 showed repeated evidence for FLS, ANS, DFR and ANR families. This document asks a stricter question before any macro transition result is inspected:

> **Do those repeated gene symbols already represent the same sequence-resolved ortholog/paralog across independent Camellia systems?**

## Result

No.

At the current public-data resolution, **zero node features have the same sequence-resolved strict node demonstrated in two or more independent micro evidence clusters**.

This creates an important distinction:

- **module/family recurrence is already supported**;
- **exact ortholog reuse is not yet demonstrated**.

## Feature-level audit

### FLS

Family-level recurrence: **3 independent clusters** (`CSIN_WHITE_PINK`, `CNITIDISSIMA`, `CPERPETUA`).

Resolution differs sharply among systems:

- `C. sinensis`: `CSA008358` and `CSA006950` are different FLS-labelled source loci and even move in different developmental directions;
- `C. nitidissima`: named sequence anchors exist. `CnFLS1 = LOC114301642 / XP_028071684 / MW010918.1`; `CnFLS2 = LOC114321369 / XP_028092149 / MW010919.1`, with `Cn03G0014790` crosswalking to the CnFLS2 protein anchor;
- `C. perpetua`: current evidence identifies FLS as a yellow-development hub but no frozen sequence/locus anchor is yet available.

Thus FLS is recurrent as a **module/family**, but `FLS=3` is an upper bound on exact node recurrence.

### ANS

Family-level recurrence: **3 clusters** (`CSIN_WHITE_PINK`, `CRETICULATA`, `CSASANQUA`).

- `C. sinensis`: current frozen evidence reports ANS involvement without a sequence-resolved source locus;
- `C. reticulata`: multiple K05277/ANS-like homologs are present and show mixed directions; a named `CrANS` functional result anchors the family biologically but is not yet crosswalked to a cross-species sequence ortholog;
- `C. sasanqua`: current evidence remains family-level.

Therefore ANS recurrence is real at family/module resolution but not yet an exact cross-species node recurrence.

### DFR

Family-level recurrence: **2 clusters** (`CSIN_WHITE_PINK`, `CJAPONICA`).

- `C. sinensis`: at least three DFR-labelled source loci are recovered (`CSA003949`, `CSNG45659`, `CSNG38209`);
- `C. japonica`: `CjDFR` is a functional target of `CjMYB114-CjbHLH1`, but the current registry does not freeze a sequence accession/source locus for CjDFR.

The functional mechanism is strong, but the exact DFR orthology across the two systems remains unresolved.

### ANR

Family-level recurrence: **2 clusters** (`CSIN_WHITE_PINK`, `CRETICULATA`).

- `C. sinensis`: source locus `CSA011986`;
- `C. reticulata`: five K08695/ANR-like homologs are recovered and show mixed directions.

The repeated family is not a resolved strict node.

### UFGT and LAR

Each currently has only one strict micro independence cluster in the v0.1 recurrence ledger. Within those systems multiple source paralogs exist, so neither is currently eligible as a recurrent exact-node predictor.

### Named regulators

`CjMYB114 = PP033112.1` and `CjbHLH1 = MZ614498.1` are sequence-resolved named functional regulators. However, each occurs in only one independent biological cluster. They are **strictly resolved but not recurrent**.

## Important quarantine

`C. sinensis` source locus `CSA011508` is reported as `LAR`, `FLAR`, and `LAR` across S8 stage sheets, while KEGG/Swiss-Prot annotation points to K05277 / leucoanthocyanidin dioxygenase / ANS-like function.

It remains `annotation_conflict_quarantined` and is excluded from strict LAR or ANS recurrence.

## Consequence for H_MICRO_MACRO_REUSE

The hypothesis must be split into two nested tests.

### Test 1 — module/vector reuse: ready first

Use the already non-circular micro predictors:

- anthocyanin-downstream accessibility;
- flavonol accessibility;
- PA accessibility;
- carotenoid accessibility;
- regulatory-module accessibility;
- quantitative state-vector displacement directions.

Once independent nuclear transition branches are available, test whether macro transitions disproportionately move along micro-accessible **module/vector directions**.

### Test 2 — strict node reuse: not ready yet

Before asking whether the *same gene* is reused, perform sequence-resolved orthology/paralogy mapping across the micro systems. A strict node enters the macro enrichment test only when the same resolved ortholog/paralog identity can be compared across independent systems.

## New research implication

This result prevents a common but consequential shortcut:

> repeated annotation name ≠ repeated evolutionary node.

The current evidence supports **network/module accessibility** more strongly than exact-gene reuse. Therefore the strongest near-term form of accessibility-biased macroevolution is a prediction about **repeated module/state-vector displacement**, not yet a prediction that the identical FLS/ANS/DFR ortholog is repeatedly selected.

## Next public-data task

Resolve sequence-level orthology for priority families:

1. FLS/CnFLS1-3 and source-local FLS loci;
2. ANS/LDOX/K05277 family;
3. DFR paralogs;
4. ANR/LAR;
5. UFGT family;
6. named MYB/bHLH regulators where homologous sequence data exist.

Use public sequences/reference annotations where possible. Preserve one-to-many mappings rather than forcing reciprocal one-to-one orthology in duplicated families.

## Claim boundary

Supported:

- family/module recurrence of FLS, ANS, DFR and ANR;
- named within-species sequence anchors for some nodes/paralogs;
- exact cross-species node recurrence is **currently unestablished**;
- module/vector-level macro reuse is the valid first held-out test.

Not supported:

- that FLS=3 or ANS=3 means the same ortholog evolved three times;
- a universal exact-gene accessibility ranking;
- preferential macro node reuse before sequence-level mapping;
- any ecological selection inference from the family recurrence ranking.
