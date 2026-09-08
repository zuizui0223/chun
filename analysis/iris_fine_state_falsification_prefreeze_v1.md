# Iris fine-state falsification — prospective pre-freeze v1

Freeze status: **FROZEN BEFORE COMPUTATION OF THE CONDITIONAL FINE-STATE ENDPOINT**.

## Question

Does the surviving cross-radiation result — residual phylogenetic organization at fine flower-colour resolution after conditioning on an a priori coarse biological state — replicate in an independent fourth radiation?

Test unit: **Iris**.

Primary source: Roguz K. et al. (2020), *All the Colors of the Rainbow: Diversification of Flower Color and Intraspecific Color Variation in the Genus Iris*, Frontiers in Plant Science 11:569811, DOI `10.3389/fpls.2020.569811`.

The article reports flower-colour data for all 227 phylogeny taxa and excludes `Iris darwasica` from downstream analysis for a pre-existing topology conflict, leaving 226 analysis taxa. Source retrieval was frozen and audited before any new phylogenetic signal calculation. Europe PMC `supplementaryFiles` returned the publisher supplement `Table_1.xlsx` (SHA-256 `183ef5231c48e782b0ea69a7aa5605d40c892dd91d9d9b2d259ed7b65d230072`). Its `Source of data` sheet contains exactly **226 non-empty, unique species rows**, with zero colour missingness and no `Iris darwasica` row; rows 228–996 are formatting-only empties. Therefore no additional trait row is removed for the published exclusion.

## Frozen fine alphabet and parser

Use the seven visible colour categories defined by the source, without rebinning after looking at the result:

`MAROON, ORANGE, PINK, PURPLE, RED, YELLOW, WHITE`.

The publisher workbook codes these as:

- `mar` → `MAROON`;
- `ora` → `ORANGE`;
- `pin` → `PINK`;
- `pur` → `PURPLE`;
- `red` → `RED`;
- `yel` → `YELLOW`;
- `whi` → `WHITE`.

Multi-colour source cells are split only on the publisher delimiter `&`; the complete resulting set is retained. Blue/violet observations remain `PURPLE` because that is the source coding. Polymorphic and bi-coloured taxa are never forced to one colour. Any non-empty colour token outside the seven frozen codes is a schema error and causes `HOLD_SCHEMA`, not a post-hoc recoding.

The publisher `Pigment` column is retained only as a quality-control field. The primary coarse status is derived from the complete frozen colour vector using the source authors' published pigment grouping below, exactly as specified before source-table inspection; individual `Pigment` cells are not allowed to override a fine-state colour vector after the fact.

## Frozen primary coarse grouping

Use the source authors' own pigment grouping, not a partition selected by this audit:

- `ANTHOCYANIN`: MAROON, PINK, PURPLE, RED;
- `CAROTENOID`: ORANGE, YELLOW;
- `NO_MAJOR_PIGMENT`: WHITE.

For a taxon with multiple allowed fine states, define its coarse status as the **set** of coarse groups implied by its complete fine-state vector. During conditional permutation, exchange whole fine-state vectors only among tips that have the identical allowed coarse-group set. This preserves coarse pigment status, polymorphism/bicolour ambiguity structure, fine-state frequencies, and uncertainty counts.

## Frozen topology and taxon-matching rule

No machine-readable final Newick tree is supplied in the recovered Roguz et al. supplement; `Supplementary Material 3` is a PDF discussion/subtree document. Therefore the predeclared OpenTree fallback is the primary topology.

Taxon matching is fixed before signal computation:

1. Use each source `Species` string as the immutable source identifier.
2. Construct the TNRS query as the canonical Iris name: genus plus specific epithet, retaining an immediately following explicit infraspecific rank (`subsp.`, `ssp.`, `var.`, `f.`) and its epithet when present; author strings are discarded deterministically.
3. Publisher hybrid markers are formatting/nomenclatural markers rather than epithet characters for this query. Both attached `Irisx<epithet>` / `Iris×<epithet>` and separated `Iris x <epithet>` / `Iris × <epithet>` forms are normalized to the same genus-plus-epithet TNRS query `Iris <epithet>`, while the original source string remains the immutable identifier. This rule was added after the source-only parser encountered `Irisxgermanica L.` and **before any colour-signal endpoint was computed**.
4. Query OpenTree TNRS with `do_approximate_matching=false` and `include_suppressed=false`.
5. Admit only one unambiguous exact TNRS match (`score >= 0.999999`, not approximate).
6. Require a one-to-one source-taxon ↔ OTT-id mapping. If multiple source rows collapse onto the same OTT id, all members of that collision are marked topology-unresolved and excluded before scoring; none is chosen using colour information.
7. Build one induced subtree from the admitted unique OTT ids with `label_format=id`; rename tips back to their immutable source identifiers before attaching traits.

Sankoff scoring uses topology only, so branch lengths are irrelevant. Any alternative source topology discovered later is sensitivity-only and cannot replace the frozen primary topology because of the observed colour result.

## Frozen admission gate

Proceed only if all are true:

1. at least 80% of the 226 source analysis taxa (>=181) are represented one-to-one in the OpenTree tree–trait intersection;
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

A `PRIMARY_FAIL` is **not automatically a cross-radiation refutation**. It becomes `REFUTATION` only if the admission gate passes and all predeclared, admissible trait sensitivities also fail to recover stable support. If a required robustness check cannot be adjudicated, retain `ADVERSE_BUT_NOT_REFUTATION` rather than upgrading the result.

## Frozen sensitivities

1. **Single-coarse only**: remove taxa whose allowed fine-state vector spans more than one coarse pigment class; retain within-class colour polymorphism when it remains inside one coarse class. Repeat the same conditional test.
2. **WHITE/non-WHITE coarse sensitivity**: repeat the same conditional test with coarse allowed sets defined only by WHITE presence versus non-WHITE presence, matching the binary-conditioning style used in Linoideae.
3. **Topology sensitivity**: run only if a machine-readable final source topology is later recovered independently of the endpoint; otherwise record `NOT_AVAILABLE`, not a failed biological sensitivity.

Classification after sensitivities:

- primary support with no material contradictory admitted sensitivity => `SUPPORTIVE_ALIGNMENT`;
- primary fail and all admitted trait sensitivities fail => `REFUTATION` of the current 3/3 recurrence generalization by a matched fourth radiation;
- material disagreement among primary/admitted sensitivities => `MIXED`;
- primary adverse but robustness cannot be adjudicated => `ADVERSE_BUT_NOT_REFUTATION`;
- inadequate primary coverage or unavailable matched traits/topology => `HOLD`.

## Prohibited post-hoc moves

After the first endpoint is computed, do not:

- redefine the seven colours;
- move colours among primary pigment groups;
- pick a different coarse partition because it gives a smaller p-value;
- remove taxa based on influence on the statistic;
- replace the support threshold;
- relax exact TNRS matching because the primary result is inconvenient;
- count multiple trees or sensitivity variants as independent radiations.

This pre-freeze is the decision record for Issue #213.
