# Orthology resolution pre-macro gate

## Current answer

Repeated Camellia pigment-module signals no longer collapse into one generic
“same gene reused” category. The public-data audit now resolves two distinct
implementation modes:

1. **same-paralog lineage recurrence** — the CnFLS2-like lineage is supported
   in two independent micro evidence clusters;
2. **different-paralog implementation of the same module** — both DFR
   clusters are sequence anchored, but one is CsDFRa-like and the other is
   CsDFRb2.

These are micro-level accessibility results. Neither result demonstrates
repeated deployment on independent macroevolutionary flower-colour branches.

## Current feature-level gate

| feature | family recurrence clusters | anchored clusters | recurrent strict-node clusters | present macro-test state |
|---|---:|---:|---:|---|
| FLS | 3 | 2 | 2 | strict CnFLS2-like predictor available; one family-only cluster remains |
| ANS/LDOX | 3 | 1 | 0 | family/module level only |
| DFR | 2 | 2 | 0 | family level with a resolved different-node contrast |
| ANR | 2 | 0 | 0 | family/module level only |
| LAR | 1 | 0 | 0 | not recurrent |
| UFGT | 1 | 0 | 0 | not recurrent |
| MYB114 | 1 | 1 | 0 | resolved but not recurrent |
| bHLH1 | 1 | 1 | 0 | resolved but not recurrent |

The machine-readable result is frozen in:

- `data/orthology_resolution_by_feature_v0_1.csv`;
- `data/micro_accessibility_node_score_harmonized_v0_1.csv`.

## FLS: same-paralog lineage recurrence

### Source target recovery

The author-classified *Camellia nitidissima* `F01.PB8395/CnFLS2` target is
operationally resolved to:

`GWHTFILD005297.1 / GWHGFILD004416.1 / GWHPFILD005297.1`.

The published primer pair selects one exact candidate among 42,697 public
transcripts. The source F01 PacBio run supplies:

- 995 admitted read hits;
- 583 full-length-like reads;
- 100% consensus query coverage;
- 99.705882% consensus identity;
- zero consensus mismatches across all primer positions.

### Tea counterpart

The source-linked tea locus is frozen through the exact chain:

`CSA008358 / CSS0045924 -> GWHTACFB016172 / GWHPACFB016172`.

Its relationship to the recovered CnFLS2 target is supported by:

- 98.824% identity across the complete 1,020-bp CDS;
- 98.23% protein identity across 339 aa;
- an exclusive sister pair in the admitted FLS family tree, support 0.977;
- reciprocal-best target matching in local gene context;
- eight additional non-target local reciprocal-best anchors;
- conserved local order (`rho = 1.0`) and orientation.

The two clusters therefore share the strict micro-lineage label
`CnFLS2_like_CSA008358`. The later white-directed tea locus `CSA006950` is a
separate FLS paralog and is not folded into that node.

The third FLS cluster, *C. perpetua*, remains family-only because its current
source evidence does not freeze a sequence or locus anchor.

## DFR: resolved different-paralog contrast

The public *C. japonica* partial CjDFR CDS `AB524885.1` was compared against
all six admitted tea DFR-family candidates.

Its best match is canonical tea `CsDFRa / AB018685.1 / TEA032730`:

- protein identity: 99.005%;
- protein query coverage: 100%;
- nucleotide identity: 99.008%;
- nucleotide query coverage: 100%.

The runner-up is CsDFRb3 at 55.0% protein identity. The sequence-resolved
white/pink tea source locus `CSA003949` is instead
`TEA024758 / XM_028243762.1 / CsDFRb2`, with 53.883% protein identity to the
partial CjDFR query and no significant nucleotide local hit under the frozen
gate.

Two published CjDFR assays link exactly to `AB524885.1`; the 2015 qPCR primer
pair reproduces its reported 167-bp amplicon.

Thus both recurrent DFR clusters are anchored, but to different labels:

- `CJAPONICA`: `CsDFRa_like_AB524885`;
- `CSIN_WHITE_PINK`: `CsDFRb2_for_CSA003949`.

DFR therefore enters the macro stage as a **module-level predictor with a
resolved paralog-substitution contrast**, while its strict same-node predictor
remains zero. The de novo tea unigenes `CSNG45659` and `CSNG38209`, and the
2024 generic CjDFR promoter target, remain outside exact subclass assignment.

## ANS/LDOX and remaining families

`CSA011508` is now retained as a sequence-anchored
`CSA011508_CsANS1_like` source locus through `TEA010322 / CSS0010687.1`.
The conflicting later S8 LAR/FLAR labels remain visible in provenance rather
than being allowed to overwrite the sequence/functional-class evidence.

The independent *C. reticulata* K05277 homolog set and the *C. sasanqua* ANS
signal remain unlinked to strict sequence labels, so ANS/LDOX is still a
family-level predictor.

ANR remains unresolved across two clusters. LAR and UFGT each currently have
only one admitted independence cluster, despite multiple within-system
paralogs. `CjMYB114` and `CjbHLH1` are exact named sequence anchors but occur
in one cluster each.

## Consequence for the hypothesis architecture

The held-out macro analysis must now compare three explicit alternatives:

1. **same-node reuse** — represented by the recurrent CnFLS2-like micro
   lineage;
2. **module convergence by paralog substitution** — represented by the
   CsDFRa-like versus CsDFRb2 DFR contrast;
3. **family recurrence with unresolved node identity** — currently ANS/LDOX
   and ANR.

This is stronger than a gene-symbol count because it can distinguish whether
a macro transition follows the same accessible molecular route, a different
route inside the same pathway module, or only a coarse family-level pattern.

## Next public-data analysis

The next resolution target is ANS/LDOX:

1. recover sequence or exact assay anchors for the *C. reticulata* K05277 set
   and named CrANS target;
2. resolve any public *C. sasanqua* ANS sequence or source-primer link;
3. compare both with `CSA011508_CsANS1_like` without forcing one-to-one
   orthology in a duplicated family.

After ANS/LDOX, proceed to ANR/LAR and then the UFGT family. Macro transition
enrichment remains quarantined until an admitted independent nuclear tree and
branch-level colour/state-vector reconstruction are available.

## Claim boundary

Supported now:

- recurrent FLS, ANS/LDOX, DFR and ANR families at micro level;
- one CnFLS2-like same-paralog lineage across two independent micro clusters;
- a DFR recurrence in which both clusters are anchored to different paralog
  subclasses;
- a reproducible distinction between strict-node, resolved-different-node and
  unresolved-family predictors.

Not supported now:

- repeated strict-node deployment on independent macro branches;
- frequency or universality of paralog substitution across Camellia;
- duplication age from pairwise similarity alone;
- biochemical equivalence of every family member;
- ecological adaptation, selection, persistence or pollinator causation.
