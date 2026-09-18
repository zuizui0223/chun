# Stress-associated flower colors and evolutionary memory — result v0.1

## Frozen prediction

Pink/red/purple/yellow were fixed as stress-associated colors from the published macroecological results of Dellinger et al. (2026). White was fixed as the reference.

If repeated adaptation to cold, drought or UV-B drives these colors to arise convergently in separate lineages, their focal-color evolutionary memory should be weaker than white within the same clades.

## Result: FAIL

Twenty-seven clades contained an eligible white state and at least one eligible stress-associated color on the frozen exact-color frame.

Primary contrast:

`mean stress-color memory area - white memory area`

Result:

- median contrast = **-0.00538**
- negative in **17/27** clades
- positive in 10/27
- one-sided paired Wilcoxon P = **0.0888**
- one-sided sign-test P = **0.1239**

The frozen PASS criterion is not met.

The negative median direction is stable under leave-one-clade-out removal (27/27 refits retain a negative median), but only 3/27 leave-one-out Wilcoxon tests fall below 0.05. This is directional consistency, not robust inferential support.

## Secondary colors do not rescue the primary test

- pink: n = 11, median stress-minus-white = -0.0223, P = 0.0615
- red: n = 8, median = -0.0168, P = 0.156
- purple: n = 3, median = -0.0709, P = 0.125
- yellow: n = 21, median = +0.00042, P = 0.446

Pink is the closest secondary pattern to the predicted direction, but the preregistration explicitly forbids using an individual color to rescue a failed aggregate primary test.

## Biological interpretation

The simple hypothesis that environmentally associated flower colors are generally more convergent and therefore carry weaker evolutionary memory than white is **not supported at the frozen threshold**.

This narrows the ecological story in an important way. The published environment-color associations are real spatial associations, but they do not automatically imply a universal loss of phylogenetic memory for the associated colors. Environmental effects may be color-specific, clade-specific, nonlinear, or conditional on pollinator and developmental context.

Together with the failed flower-fruit memory trade-off and the failed simple tree-geometry moderators, this result argues against one-factor explanations of between-clade flower-color memory.

Camellia Paper 1 and frozen EL v0.2 remain unchanged.
