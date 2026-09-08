# Antirrhineae pre-result fine-state gate v0.1

## Purpose

Test the merged cross-radiation hierarchical-state-space candidate in a third independent biological radiation without changing the success criterion after seeing the result.

Source bundle: Ellis & Field 2016 research data, DOI `10.15479/AT:ISTA:34`.

## Source-native states

The source readme defines `face_phenotype` as:

- `0` = unpigmented;
- `1` = anthocyanin-pigmented;
- `2` = yellow;
- `3` = double-pigmented.

The current source CSVs contain states 0/1/2. State 3 is retained in the parser but is not invented where absent.

## Nested state representation

Coarse state:

- `UNPIGMENTED`: source state 0;
- `PIGMENTED`: source states 1/2/3.

Fine state:

- exact source `face_phenotype` state.

The conditional null preserves every tip's coarse `UNPIGMENTED/PIGMENTED` class and exchanges exact fine states only within that class. With the current 0/1/2 data this specifically asks whether anthocyanin versus yellow pigmentation remains phylogenetically organized after conditioning on pigment presence itself.

No phenotype is inferred from colour names, and taxon-code reconciliation is exact-match-only in v0.1.

## Two source-native datasets

Primary gate: `mm_face_phenotypes.csv` + `monomorphic_snapdragons.tree`, excluding source-declared flower-colour-polymorphic taxa.

Sensitivity gate: `face_phenotypes.csv` + `polymorphic_snapdragons.tree`, retaining the source's polymorphic sampling design.

Each NEXUS contains 1,000 posterior trees. The analysis uses 20 deterministic, evenly spaced trees from each posterior ensemble, including the first and last stored trees. Sensitivity trees are not counted as independent biological replications.

## Statistic

For every selected tree:

1. prune to exact phenotype/tree tip joins;
2. calculate the Sankoff minimum-change score for the exact fine state using unit cost between distinct states;
3. generate 9,999 conditional permutations of exact fine states within fixed coarse-state classes;
4. calculate the lower-tail permutation p-value and `observed / null mean` score ratio.

The score is a phylogenetic-organization statistic, not a count of independent origins.

## Frozen support gate

Antirrhineae is admitted as a **third independent replication** of the hierarchical fine-state candidate only if all conditions hold:

1. the monomorphic primary dataset has at least 140 exact joined tips and both anthocyanin and yellow have at least 20 tips;
2. at least 18/20 monomorphic posterior-tree tests have `p <= 0.01` and `observed/null < 1`;
3. at least 18/20 polymorphic posterior-tree sensitivity tests also have `p <= 0.01` and `observed/null < 1`;
4. no result depends on recoding an unmatched taxon, collapsing yellow with anthocyanin, or treating posterior trees as biological replicates;
5. the current ISTA payload checksum drift remains explicitly recorded rather than overwritten by the historical published MD5.

If this gate fails, Antirrhineae is a failed/indeterminate third replication under this test. Thresholds will not be weakened post hoc.

## Claim boundary

A positive result would support nested pigment-state phylogenetic organization conditional on coarse pigment presence. It would not establish a universal transition direction, ancestral WHITE state, ecological cause, molecular mechanism, or dated transition rate.

Paper 1 remains unchanged.