# Schistanthe state-support gate — v0.1

## State

`SCHISTANTHE_STATE_SUPPORT_PASS_OPPORTUNITY_CONFIRMED_AUC_UNOPENED`

The identifier-only crosswalk was frozen first:

- 130 trait rows;
- 147 tree tips;
- 129 exact matches;
- one unmatched trait identifier excluded without synonym/fuzzy repair.

Only after that freeze was the target `Flower_Color` column opened for **state-support counts**, not phylogenetic analysis.

## Frozen state counts

Fine exact source states:

- red = 63
- white = 36
- yellow = 30

No missing, ambiguous, or composite labels occur on the 129-tip exact-match frame.

Coarse deterministic states:

- NONWHITE = 93
- WHITE = 36

All fine states exceed the pre-frozen minimum support of five.

Therefore:

`fine_state_count = 3 > coarse_state_count = 2`

and genuine fine→coarse representation opportunity is confirmed.

## Prospective test now opened

The previously frozen held-out test may now be run exactly once:

- restrict to pairs sharing the same coarse state;
- score with negative patristic distance;
- outcome = same exact fine state;
- conditional ROC AUC;
- permute fine labels within coarse states;
- 9,999 permutations;
- seed 20260920;
- PASS only if observed AUC exceeds the permutation mean and one-sided P <= 0.05.

At this freeze point, observed AUC and null distribution remain unopened.

This Schistanthe validation is independent of Flower-clades-51 and is not allowed to alter the pre-frozen Ruellia-specific v0.7 promotion rule.
