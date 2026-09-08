# Antirrhineae conditional fine-state result v0.1

## Result

The pre-frozen third-replication gate is **PASS**.

This analysis uses the source-native Ellis & Field flower-colour coding:

- 0 = unpigmented;
- 1 = anthocyanin-pigmented;
- 2 = yellow;
- 3 = double-pigmented.

The current source tables contain states 0/1/2. No absent state was invented.

The coarse conditioning variable is pigment presence (`0` versus `1/2/3`). The fine state is the exact source pigment class. The null therefore keeps every tip pigmented or unpigmented while shuffling anthocyanin versus yellow identity among pigmented tips.

## Primary monomorphic dataset

Source files: `mm_face_phenotypes.csv` + `monomorphic_snapdragons.tree`.

- 1,000 posterior trees in the source NEXUS;
- 152 exact phenotype/tree tip joins after fail-closed matching;
- 21 unpigmented, 68 anthocyanin, 63 yellow;
- 20 deterministic posterior-tree tests, each with 9,999 conditional permutations;
- **20/20** tests satisfy `p <= 0.01` and `observed/null < 1`;
- p range: **0.0001–0.0084**;
- observed/null range: **0.792–0.863**.

The frozen primary requirement was at least 18/20 supporting tests, with at least 140 exact tips and at least 20 anthocyanin and 20 yellow tips. All requirements pass.

## Polymorphic sensitivity dataset

Source files: `face_phenotypes.csv` + `polymorphic_snapdragons.tree`.

- 1,000 posterior trees;
- 179 exact phenotype/tree tip joins;
- 29 unpigmented, 83 anthocyanin, 67 yellow;
- **19/20** tests satisfy `p <= 0.01` and `observed/null < 1`;
- p range: **0.0002–0.0207**;
- observed/null range: **0.828–0.902**.

One selected posterior tree (`tree_index=420`) has `p=0.0207`; it is retained rather than discarded. The frozen sensitivity requirement was at least 18/20, so the result passes without post-hoc threshold changes.

## Source-integrity boundary

The currently served ISTA bundle is identical across two official ISTA hosts (4,468,543 bytes; SHA256 `5f25dc400d91ce913d1057aa9c5d7fac13addaf2a479f3af629f8393a90876dd`) but does not match the historical MD5 displayed by the record (`950f85b80427d357bfeff09608ba02e9`). This discrepancy remains explicitly recorded as `CURRENT_ISTA_MIRRORS_IDENTICAL_PUBLISHED_MD5_DRIFT`.

The analysis uses this current mirrored-identical payload for content audit; it does not rewrite or pretend to satisfy the historical checksum.

## Cross-radiation consequence

Antirrhineae is admitted as a **third independent nested fine-state replication** of the hierarchical state-space candidate:

1. Linoideae: hue organization remains after conditioning on WHITE/nonwhite status;
2. Angraecinae: four-organ configuration remains organized after conditioning on primary GREEN/WHITE status;
3. Antirrhineae: anthocyanin versus yellow pigment identity remains organized after conditioning on pigment presence.

Therefore the replicated candidate advances from **2/2 testable external radiations to 3/3**.

This does not make it a universal law. Posterior trees are correlated uncertainty samples within one Antirrhineae radiation, not independent biological replications. The result does not identify ancestral WHITE, a common transition direction, ecological cause, molecular mechanism, or dated transition rate.

Paper 1 remains unchanged.