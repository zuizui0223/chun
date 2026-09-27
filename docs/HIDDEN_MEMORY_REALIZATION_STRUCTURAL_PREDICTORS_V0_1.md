# Structural predictors of hidden-memory realization — v0.1

## Question

The cross-radiation programme now separates **opportunity** from **realization**.

Opportunity means that a coarse phenotype actually collapses multiple fine states. But could the positive hidden-memory pattern simply be a combinatorial artifact of how much collapsing occurs?

The primary hypothesis was fixed before this calculation:

> Larger fine-to-coarse pair-collision gain should predict a larger permutation-centered within-coarse hidden-memory effect.

## Primary result: failed, with the opposite sign

Across the 21 already-fixed opportunity clades:

- Spearman rho = **−0.2571**
- 99,999-permutation two-sided **P = 0.26023**
- bootstrap 95% interval = **−0.5932 to +0.1455**
- bootstrap median rho = **−0.2531**
- only **10.4%** of bootstrap rhos were positive

Leave-one-clade-out robustness is especially clear:

- all **21/21** leave-one-out correlations remain negative;
- range = **−0.3624 to −0.2000**.

The preregistered positive collision-gain prediction is therefore not supported.

## Secondary structural descriptors

These were explicitly descriptive and cannot rescue the primary test.

- entropy loss: rho = **−0.0805**, P = 0.729
- number of collapsed fine states: rho = **+0.3920**, P = 0.0789
- fine-state count: rho = **+0.3920**, P = 0.0789
- log10 retained tips: rho = **+0.3597**, P = 0.109

The positive state-count/tip trends are not promoted. No new primary predictor is selected after seeing them.

## Evolutionary implication

This removes an important trivial explanation.

The recurrent within-coarse signal is **not stronger simply because coarse coding creates more pairwise fine-state collisions**.

So the hierarchy now has three distinct pieces:

1. **opportunity** — finer states exist within a coarse phenotype;
2. **informativeness** — the test has enough null resolution to adjudicate a benchmark-sized effect;
3. **realization** — those fine states are actually arranged on the phylogeny in a lineage-structured way.

The first is state-space geometry. The third is not reducible to the first.

That makes hidden memory more biologically interesting: among-radiation variation in realization must involve historical transition dynamics, lineage-specific constraints, ecology, or some other biological structure beyond simple phenotype compression.

This analysis does **not** identify which of those mechanisms is responsible.

## Boundaries

This is post-outcome exploratory work.

No environmental variable was searched. No clade was removed based on outcome. Secondary predictors cannot replace the failed primary hypothesis. No ecological or molecular cause is claimed.

Frozen Evolution Letters v0.3 and Camellia Paper 1 remain unchanged.
