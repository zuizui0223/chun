# WFO53 UFBoot accepted-species topology sensitivity

## Question

Does the accepted-species nuclear topology used for macro flower-colour pattern tests depend strongly on the approximate FastTree gene-tree pipeline?

## Frozen inputs

- 339 runtime91 gene trees inferred with IQ-TREE LG+G4 + 1000 UFBoot (run 32439653098);
- WFO Plant List 2026-06 multi-individual mapping from PR #46;
- FastTree/ASTRAL accepted-species sensitivity tree from PR #48.

The runtime91 UFBoot gene-tree set contains 91 legacy individuals. After filtering the WFO mapping to those observed individuals, they collapse to 53 accepted Camellia species. `C. japonica`, accepted `C. petelotii`, and `Polyspora speciosa` are absent from this runtime91 UFBoot set, so the topology comparison is unrooted and restricted to the common 53 species.

## Result

Both accepted-species trees contain 50 nontrivial splits on the common 53-tip set.

- shared nontrivial splits: **46/50**;
- reciprocal split recall: **0.92**;
- split Jaccard: **0.8519**;
- Robinson–Foulds symmetric difference: **8**;
- normalized RF over the total split count: **0.08**.

## Interpretation

The accepted-species backbone is highly concordant between the approximate FastTree gene-tree pipeline and the much stronger IQ-TREE/UFBoot gene-tree ensemble. Four nontrivial splits differ on the common 53-species set, so downstream trait patterns should still be rechecked directly on the UFBoot topology rather than assumed identical.

This is a phylogeny-only sensitivity. Flower colour, climate, pollinator information and other ecological predictors were absent from inference and comparison.

## Next gate

Retest strict and dominant wild-colour phylogenetic conservatism on the WFO53 UFBoot-ASTRAL topology. If colour-wide conservatism survives both topology and trait scenarios, it is a defensible pattern-level macro result even though accepted-species branch transitions are not robust enough for causal branch tests.
