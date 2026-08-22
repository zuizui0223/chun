# CjDFR sequence-anchor analysis

## Question

Issue #19 asks whether repeated Camellia pigment-module changes reuse the
same exact node or are implemented by different paralog lineages.

The DFR test asks:

> Is the public *Camellia japonica* CjDFR sequence in the same tea DFR
> subclass as the *C. sinensis* white/pink source locus `CSA003949`, or does
> the same anthocyanin-downstream module recur through a different DFR
> paralog lineage?

## Frozen public inputs

- `AB524885.1`: 605-bp partial petal CjDFR CDS from *C. japonica*.
- `AB018685.1`: canonical tea `CsDFRa` (`TEA032730`).
- `XM_028251603.1`, `XM_028243762.1`, `XM_028243764.1`,
  `XM_028268820.1`, `XM_028230958.1`: the five additional tea DFR-family
  candidates admitted from the primary family study.
- `XM_028243762.1 = CsDFRb2 = TEA024758`: the TPIA2-resolved counterpart of
  the white/pink meta-analysis source locus `CSA003949`.

The workflow downloads versioned GenBank records, stores CDS/protein
checksums, compares CjDFR against all six tea candidates, and audits published
CjDFR primer pairs against the public sequence.

## Reproducible result

`AB524885.1` is unambiguously **canonical-CsDFRa-like** within the admitted
tea DFR comparison set.

| rank | tea reference | protein identity | protein query coverage | nucleotide identity | nucleotide query coverage |
|---:|---|---:|---:|---:|---:|
| 1 | `CsDFRa / AB018685.1 / TEA032730` | 99.005% | 100% | 99.008% | 100% |
| 2 | `CsDFRb3 / XM_028243764.1` | 55.000% | 99.005% | 69.549% | 42.975% |
| 3 | `CsDFRb2 / XM_028243762.1 / CSA003949` | 53.883% | 100% | no significant local hit | — |
| 4 | `CsDFRb1 / XM_028251603.1` | 51.244% | 100% | no significant local hit | — |
| 5 | `CsDFRc / XM_028268820.1` | 38.462% | 98.508% | no significant local hit | — |
| — | `CsDFRd / XM_028230958.1` | no significant local hit | — | no significant local hit | — |

The top-versus-runner-up identity margin is **44.005 percentage points at
protein level** and **29.459 percentage points at nucleotide level**. The
predeclared strong-call thresholds are therefore passed with full query
coverage.

## Assay-to-sequence linkage

Two independent published CjDFR primer pairs map exactly to `AB524885.1`:

1. the Tateishi 2010 forward and reverse primers each have one exact hit and
   delimit 412 bp within the public partial sequence;
2. the Berruti et al. 2015 qPCR primers each have one exact hit and reproduce the
   reported **167-bp** amplicon exactly. The historical computational assay ID
   `LARCHER2015_CJDFR_QPCR` is retained only for provenance.

Thus the 2010 cloned CjDFR and the 2015 qPCR target are sequence-linked to the
same public partial CDS. The 2024 CjMYB114–CjbHLH1 promoter target remains
family-level functional evidence because no exact target sequence or promoter
coordinates are frozen in the current public registry.

## Biological interpretation

The two independently admitted DFR micro clusters now contain different
sequence-resolved subclasses:

- `CJAPONICA`: `AB524885.1`, strongly `CsDFRa`-like;
- `CSIN_WHITE_PINK`: `CSA003949`, resolved as `CsDFRb2`, alongside two
  still-unresolved de novo DFR-annotated unigenes.

This is a direct **cross-cluster DFR paralog-subclass contrast**. It supports
the prediction of `H_PARALOG_SUBSTITUTION`: recurrence of the same
anthocyanin-downstream module need not mean recurrence of the same exact DFR
node.

It does not make the strict-node predictor positive. The resolved labels are
different, so strict same-node recurrence remains zero while both DFR
clusters are now sequence anchored.

## Frozen outputs

- `data/cjdfr_sequence_manifest_v0_1.csv`
- `data/cjdfr_pairwise_dfr_family_v0_1.csv`
- `data/cjdfr_assay_linkage_v0_1.csv`
- `data/cjdfr_sequence_anchor_summary_v0_1.json`

The workflow diffs regenerated outputs against these files. Any accession,
sequence, ranking, primer-linkage, or decision drift therefore fails CI.

## Claim boundary

Supported:

- sequence-lineage classification of public CjDFR `AB524885.1`;
- comparison against all six admitted tea DFR candidates;
- distinction between public CjDFR/CsDFRa-like and source-resolved
  `CSA003949/CsDFRb2`;
- exact linkage of the 2010 and 2015 CjDFR assays to `AB524885.1`;
- a second direct candidate case, after FLS, in which module-level recurrence
  spans different paralog lineages.

Not supported:

- identity of every later generic `CjDFR` target with `AB524885.1`;
- assignment of `CSNG45659` or `CSNG38209` to a known tea DFR paralog;
- duplication age or formal species-tree orthology from pairwise similarity;
- equivalent biochemical function of all DFR-like copies;
- frequency of paralog substitution across Camellia;
- macro-transition enrichment, ecological adaptation, or selection.
