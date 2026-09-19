# Petunieae hierarchical hidden biochemical memory — retrospective result v0.1

## Question

The Flower-clades-51 extension showed that fine visible-color states often remain phylogenetically organized **inside** coarse flower-color states.

Petunieae provides a cross-representation check using a biochemical hierarchy:

- coarse — any of six anthocyanidins present versus none;
- fine — exact six-compound presence pattern.

This analysis applies the same conditional AUC logic to the exact audited Petunieae source and the already-frozen 47-tip frame.

It is retrospective and is **not** an additional prospective replication.

## Estimator

Among unordered taxon pairs sharing the same frozen coarse anthocyanidin-presence state:

1. score the pair by negative patristic distance;
2. label whether the pair also shares the same six-compound fine state;
3. compute ROC AUC;
4. permute fine labels within each coarse group while preserving fine-state counts;
5. repeat 9,999 times, seed 20260920.

Because the conditional null is shaped by the fixed coarse groups and fine-state frequencies, its AUC is not assumed to equal 0.5.

The primary effect is:

[
Delta AUC_{hidden}
=
AUC_{observed}
-
E(AUC_{within-coarse null}).
]

## Frozen frame

The exact source hashes match the existing Petunieae profile:

- HPLC/expression table SHA256: `5843d4cd4eb253046f97349fa6bd285ca77e43e7a9c3aaa0e78fae3e8e391edd`;
- dated tree SHA256: `95b4a688d3d71417b712b37a2b04cdc22a9431be3172d6509def4435f5fd8614`.

After excluding source outgroup `BROW` and applying the pre-existing rare-fine-state rule, **47 tips** remain.

Coarse states:

- anthocyanidin absent: 6;
- anthocyanidin present: 41.

Six retained fine compound states have supports 6, 6, 6, 10, 6 and 13.

## Result

- observed conditional AUC = **0.70180**;
- within-coarse null mean AUC = **0.51385**;
- permutation-centered effect = **+0.18794 AUC**;
- null 95% interval = **0.47978–0.57087**;
- one-sided permutation **P = 0.0001**.

Thus fine biochemical composition carries substantial phylogenetic organization after coarse anthocyanidin presence/absence has already been fixed.

## Cross-representation meaning

This result aligns with the visible-color Flower-clades-51 result under the same conceptual estimand:

- visible-color batch: hidden fine-memory effect is positive in **18/21** opportunity clades, median **+0.0270 AUC**;
- Petunieae biochemical hierarchy: centered hidden-memory effect **+0.1879 AUC**, P = **0.0001**.

The magnitude should not be compared as though these were exchangeable replicates: Petunieae is one radiation and the Flower-clades batch shares one standardized ontology/source.

The relevant concordance is qualitative and structural:

> fine phenotype identity can retain phylogenetic organization inside a coarser state in both visible-color and biochemical representations.

## Why this is more informative than “fine wins”

The existing Petunieae unconditional profile already showed a fine winner:

- coarse/intermediate AUC = 0.5189;
- fine AUC = 0.6996.

The new analysis identifies **where that extra information lives**.

It is not merely that the fine coding has more categories. The fine compound identities are non-randomly arranged phylogenetically **within the coarse anthocyanidin-presence state space** relative to a count-preserving within-coarse null.

This is the hierarchical-memory quantity that the global winner statistic only indirectly reflected.

## Boundary

Petunieae source values had already been inspected and its unconditional profile was already known before this extension. Therefore this result is retrospective.

It does not count as a new independent Petunieae replication and cannot establish a universal biochemical law.

The prospectively frozen Ruellia test remains the held-out cross-representation test if its authoritative tree provenance can be cleared.

Frozen Evolution Letters v0.3 and Camellia Paper 1 remain unchanged.
