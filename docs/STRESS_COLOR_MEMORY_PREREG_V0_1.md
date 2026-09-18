# Stress-associated flower colors and evolutionary memory — preregistration v0.1

## Question

The temporal-memory analysis shows that exact flower-color similarity generally decays with relative evolutionary divergence. The next biological question is whether colors known to track stressful environments are especially labile across lineages.

Dellinger et al. (2026; DOI `10.1002/ajb2.70044`) reported that pink and red flowers increase in cold environments, while purple and yellow flowers are associated with dry and/or high-UV-B environments in the same broad 51-clade system.

We therefore freeze the following prediction before computing any color-specific memory curve:

> If stress-associated flower colors repeatedly evolve in response to similar abiotic conditions across separate lineages, pink/red/purple/yellow should retain weaker phylogenetic memory than white within the same clades.

## State-specific time-memory estimand

Use the exact source flower-color categories and exact source phylogenies.

Within each clade, first apply the existing fine-state filter: remove exact flower-color states represented by fewer than five tips, then require at least 20 retained tips.

For a focal color with at least five focal and five nonfocal retained tips:

1. treat every focal-color species as a focal lineage;
2. pair it with every other retained species;
3. define relative divergence depth as patristic distance divided by twice crown height on an effectively ultrametric source tree;
4. divide directed focal-partner pairs into ten equal-count time bins;
5. calculate the probability that the partner has the same focal color;
6. center on the exact random-partner baseline `(k-1)/(n-1)`;
7. scale to excess retention and integrate the curve.

The signed area is the focal color's memory score within that clade.

## Frozen ecological contrast

Stress-associated colors are fixed as:

- pink
- red
- purple
- yellow

White is the reference color.

For every clade containing white and at least one eligible stress color, average the memory area across eligible stress colors and subtract the white memory area.

Primary contrast:

`stress mean area - white area`

Prediction: negative.

At least 10 paired clades are required. The primary test is a one-sided paired Wilcoxon signed-rank test. PASS requires both a negative median contrast and P <= 0.05.

Individual-color contrasts and sign/leave-one-out diagnostics are secondary only.

## Interpretation boundary

A PASS would be consistent with repeated ecological convergence of stress-associated colors eroding their phylogenetic memory relative to white. It would not establish abiotic selection causally, because the environment-color associations are imported from the published macroecological study rather than re-estimated here.

A FAIL would reject this simple convergence prediction, not the published environment-color associations.

Camellia Paper 1 and frozen EL v0.2 remain unchanged.
