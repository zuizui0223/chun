# Ruellia51 opportunity-conditional held-out prediction — v0.1

## Why this test

The exploratory Flower-clades-51 extensions changed the question.

The retrospective result is not that fine resolution universally wins. Instead:

1. overall **memory amplitude** varies strongly among radiations;
2. coarse–fine **scale tilt** is a smaller, largely independent axis;
3. a hierarchy must contain fine distinctions hidden inside coarse states before nonzero tilt is even possible;
4. among 21 visible-color clades with that structural opportunity, 15 showed positive fine-minus-coarse tilt.

That last observation is hypothesis-generating because it was derived after the visible-color outcomes were open.

*Ruellia* provides a genuinely held-out test because its row-level HPLC presence patterns, state frequencies and CHUN profile AUCs remain unopened.

## Existing hierarchy is unchanged

This prediction inherits the already-frozen *Ruellia* HPLC hierarchy:

- coarse: any anthocyanidin present versus none;
- intermediate: PEL/CYA/DEL branch-presence pattern;
- fine: exact six-anthocyanidin presence pattern.

No representation is changed to fit the new hypothesis.

The existing common-frame rule, rare-state threshold, estimator, 9,999 joint permutations and seed also remain unchanged.

## Sequential outcome opening

If the authoritative phylogeny/source gate is cleared:

1. freeze tree bytes/hash, tip crosswalk and species representative rule;
2. open the HPLC rows under the existing preregistration;
3. construct the already-frozen common retained-tip frame;
4. record only the retained state counts needed to determine whether fine→coarse compression opportunity exists;
5. **before computing any AUC**, classify the system as opportunity or no-opportunity;
6. then run the frozen AUC/permutation estimator.

This separates the structural condition from its phylogenetic realization.

## Conditional prediction

### No opportunity

If the retained fine and coarse partitions contain the same number of states, their partitions are identical under the deterministic nesting.

Prediction:

`AUC_fine - AUC_coarse = 0`

This is a structural identity and does **not** count as a biological success.

### Opportunity present

If:

`fine_state_count > coarse_state_count`

then the held-out biological prediction is:

[
AUC_{fine} > AUC_{coarse}.
]

PASS requires both:

- observed `AUC_fine - AUC_coarse > 0`;
- one-sided joint-permutation P <= 0.05.

The primary label is then:

`PROSPECTIVE_OPPORTUNITY_REALIZED_FINE_TILT`.

If opportunity exists but this criterion is not met, the prospective prediction FAILS. No intermediate contrast or alternate recoding can rescue it.

## Why this is stronger than the earlier universal-resolution prediction

The old prediction asked:

> Which resolution should win everywhere?

The new prediction asks:

> When a hierarchy actually hides fine biological distinctions inside a coarse state, are those hidden distinctions phylogenetically organized in an independent radiation?

The hierarchy supplies **opportunity**. Evolutionary history determines **realization**.

This is directly testable in a held-out biochemical system.

## Current blocker

The HPLC source is fixed and remains outcome-unopened. The blocker is still the authoritative phylogeny used by Watts et al.:

`03-Ruellia_phylo.timed.tre`.

The published 2021 *Ruellia* chronogram is not an authorized substitute because the 2026 analysis states that its tree was pruned from the 2023 187-species ddRAD maximum-likelihood phylogeny.

No HPLC outcome is opened until that provenance gate is cleared.

## Claim boundary

A PASS would provide one independent prospective cross-representation validation of the opportunity→fine-tilt prediction.

It would not establish a universal fine-resolution law, would not revive the rejected intermediate optimum, and would not modify frozen EL v0.3.

Camellia Paper 1 remains unchanged.
