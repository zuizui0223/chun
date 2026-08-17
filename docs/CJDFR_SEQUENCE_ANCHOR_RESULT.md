# CjDFR sequence-anchor analysis

## Current question

Issue #19 asks whether repeated Camellia pigment-module changes reuse the
same exact node or are implemented by different paralog lineages.

The FLS case is already sequence-resolved. The next independent test is DFR:

> Is the public *Camellia japonica* CjDFR sequence in the same tea DFR
> subclass as the *C. sinensis* white/pink source locus `CSA003949`, or does
> the same anthocyanin-downstream module recur through a different DFR
> paralog?

## Frozen public inputs

- `AB524885.1`: partial petal CjDFR cDNA cloned from *C. japonica*.
- `AB018685.1`: canonical, experimentally active tea `CsDFRa`
  (`TEA032730`).
- `XM_028251603.1`, `XM_028243762.1`, `XM_028243764.1`,
  `XM_028268820.1`, `XM_028230958.1`: the five additional tea DFR-family
  candidates evaluated in the primary family study.
- `XM_028243762.1 = CsDFRb2 = TEA024758`: the TPIA2-resolved counterpart of
  the meta-analysis source locus `CSA003949`.

The workflow downloads versioned GenBank records, stores sequence checksums,
extracts annotated CDS/proteins, compares the partial CjDFR against all six
tea candidates, and audits published CjDFR primer pairs.

## Decision rule

The lineage call is `strong` only when:

1. one tea candidate is the top protein match;
2. the partial query is covered across at least 95%;
3. the best protein-identity margin is at least 0.10 over the runner-up; and
4. nucleotide evidence does not contradict the protein call where a
   significant nucleotide alignment is recovered.

The DFR paralog-substitution hypothesis is advanced only if the public CjDFR
best match and `CSA003949/CsDFRb2` are different DFR subclasses.

## Claim boundary

This analysis can resolve the sequence lineage of public `AB524885.1` and
its difference from the source-resolved tea locus. It cannot, by pairwise
similarity alone, establish duplication age, species-tree orthology,
equivalent enzymatic function, macroevolutionary enrichment, or identity of
every later paper's generic `CjDFR` target with `AB524885.1`.

The 2024 CjMYB114–CjbHLH1 promoter assay remains family-level functional
evidence until its CjDFR target sequence or exact promoter/primer coordinates
are publicly linked.
