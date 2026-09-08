# Iris fine-state falsification — prospective pre-freeze v1

Freeze status: **FROZEN BEFORE COMPUTATION OF THE CONDITIONAL FINE-STATE ENDPOINT**.

## Question

Does the surviving cross-radiation result — residual phylogenetic organization at fine flower-colour resolution after conditioning on an a priori coarse biological state — replicate in an independent fourth radiation?

Test unit: **Iris**.

Primary source: Roguz K. et al. (2020), *All the Colors of the Rainbow: Diversification of Flower Color and Intraspecific Color Variation in the Genus Iris*, Frontiers in Plant Science 11:569811, DOI `10.3389/fpls.2020.569811`.

The source reports flower-colour data for all 227 phylogeny taxa and excludes `Iris darwasica` from downstream analysis for a pre-existing topology conflict, leaving 226 analysis taxa. That exclusion is adopted here before signal computation.

## Frozen fine alphabet

Use the seven visible colour categories defined by the source, without rebinning after looking at the result:

`MAROON, ORANGE, PINK, PURPLE, RED, YELLOW, WHITE`.

Blue/violet observations remain `PURPLE` because that is the source coding. Polymorphic and bi-coloured taxa retain their complete source-reported allowed fine-state set rather than being forced to one colour.

## Frozen primary coarse grouping

Use the source authors' own pigment grouping, not a partition selected by this audit:

- `ANTHOCYANIN`: MAROON, PINK, PURPLE, RED;
- `CAROTENOID`: ORANGE, YELLOW;
- `NO_MAJOR_PIGMENT`: WHITE.

For a taxon with multiple allowed fine states, define its coarse status as the **set** of coarse groups implied by its complete fine-state vector. During conditional permutation, exchange whole fine-state vectors only among tips that have the identical allowed coarse-group set. This preserves coarse pigment status, polymorphism/bicolour ambiguity structure, fine-state frequencies, and uncertainty counts.

## Frozen topology rule

Primary topology priority:

1. machine-readable final Iris ML topology from the Roguz et al. source package, if retrievable without reconstructing choices;
2. if no machine-readable final topology is supplied, use an OpenTree induced Iris subtree on the frozen included taxa as the designated fallback. Sankoff scoring uses topology only, so branch-length differences are irrelevant to the primary statistic.

Do not choose between alternative topologies based on the flower-colour result. If both become available, the non-primary topology is a frozen sensitivity analysis.

## Frozen admission gate

Proceed only if all are true:

1. at least 80% of the 226 source analysis taxa are represented in the tree–trait intersection;
2. every admitted tip has at least one source-coded fine colour;
3. at least one coarse class contains >=3 distinct fine states and >=30 admitted tips;
4. no taxon is excluded because of its contribution to the signal statistic.

If these fail, classify `HOLD_OBSERVATION_REGIME`, not a biological counterexample.

## Frozen statistic and null

Statistic: unordered Sankoff/Fitch minimum number of changes for the seven-state allowed-state vectors on the admitted topology.

Null: 9,999 conditional permutations. Each permutation exchanges entire allowed fine-state vectors **only within identical frozen coarse-status sets**. The observed assignment is permutation zero.

Seed: `20260908`.

Primary outputs:

- `observed_minimum_changes`;
- `null_mean` and null quantiles;
- `observed_over_null_mean`;
- lower-tail permutation p-value `p_lower = (1 + count(null <= observed)) / 10000`.

## Frozen primary decision

- `SUPPORTIVE_ALIGNMENT`: `p_lower <= 0.01` **and** `observed_over_null_mean < 1`.
- `PRIMARY_FAIL`: either condition is not met.

A `PRIMARY_FAIL` is **not automatically a cross-radiation refutation**. It becomes `REFUTATION` only if the admission gate passes and all predeclared sensitivity analyses also fail to recover stable support.

## Frozen sensitivities

1. **Monomorphic/single-coarse only**: remove taxa whose allowed fine-state vector spans more than one coarse pigment class; retain within-class colour polymorphism when it remains inside one coarse class.
2. **WHITE/non-WHITE coarse sensitivity**: repeat the same conditional test with coarse allowed sets defined only by WHITE presence versus non-WHITE presence, matching the binary-conditioning style used in Linoideae.
3. **Topology sensitivity**: if both the source ML topology and OpenTree fallback are available, repeat on the alternate topology.

Classification after sensitivities:

- primary support and no decisive contradictory sensitivity => `SUPPORTIVE_ALIGNMENT`;
- primary fail and all admitted sensitivities fail => `REFUTATION` of the current 3/3 recurrence generalization by a matched fourth radiation;
- material disagreement among primary/sensitivities => `MIXED`;
- inadequate coverage or unavailable matched topology/traits => `HOLD`.

## Prohibited post-hoc moves

After the first endpoint is computed, do not:

- redefine the seven colours;
- move colours among primary pigment groups;
- pick a different coarse partition because it gives a smaller p-value;
- remove taxa based on influence on the statistic;
- replace the support threshold;
- count multiple trees or sensitivity variants as independent radiations.

This pre-freeze is the decision record for Issue #213.
