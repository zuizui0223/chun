# Flower-clades-51 relative-time flower-color persistence — v0.1

## Question

Does the cross-radiation result recover the original biological question of how flower-color variation persists through evolutionary depth, rather than only asking which character coding maximizes a phylogenetic AUC?

This analysis is a **retrospective derived analysis** of the already opened Flower-clades-51 data. It is not a new prospective replication and it does not alter the frozen Evolution Letters v0.2 science.

## Exact source identity

The analysis uses the same exact source bytes as the frozen 51-clade profile batch:

- Sinnott-Armstrong et al. 2026, DOI `10.1002/ajb2.70146`
- Dryad DOI `10.5061/dryad.r4xgxd2sc`
- `final_dataset.csv` SHA-256 `a253308785e4cbd0e361b3ca04cdfdae29c523eefa843375cebf8030ee0874af`
- `trees.zip` SHA-256 `ae5c82945e5bf9c29bcabc52d6029acd8d4f5be1fe9141fad95918eacb4f674d`

## Relative-time axis

All eligible source trees are effectively ultrametric at numerical precision. In the fine-color 32-clade frame, the maximum root-to-tip CV is `2.98e-11`.

For a pair of species we therefore define relative phylogenetic divergence depth as

`t = patristic distance / (2 * source-tree crown height)`.

On an ultrametric tree this ranges from recent divergence near 0 to crown-depth divergence near 1.

This is **not an absolute-time calibration**. No result is reported in Ma.

## Fine visible flower-color persistence

For the direct biological question, the primary descriptive frame uses the exact source flower-color categories only. It retains the existing rare-state rule (fine states need at least five tips), at least 20 retained tips, and at least two fine flower-color states. It does **not** require coarse or intermediate variation.

This yields 32 eligible clades and 19 HOLD clades.

For each clade, unordered species pairs are binned by relative divergence depth. Within each bin, the observed probability that two species share the exact flower-color state is centered on the exact without-replacement same-state probability implied by that clade's color frequencies:

`excess retention = (P[same color | t-bin] - P[same color under frequency baseline]) / (1 - baseline)`.

A negative clade-level slope means that excess same-color retention is concentrated among recent divergences and decays toward deeper divergences.

### Result

- negative persistence slopes: **23/32 clades**
- median slope: **-0.1897**
- one-sided Wilcoxon P = **0.00120**
- one-sided sign-test P = **0.0100**
- bootstrap 95% interval for median slope: **[-0.373, -0.090]**

The signed excess-retention area is positive in **23/32 clades**:

- median area = **0.0207**
- one-sided Wilcoxon P = **0.00467**
- one-sided sign-test P = **0.0100**

The near-minus-far contrast is positive in 19/32 clades (median 0.0882; Wilcoxon P = 0.0354), but its sign test does not clear 0.05. The slope and integrated area are therefore the stronger summaries.

The median binned curve is positive at shallower divergence depths and approaches or crosses the frequency baseline at deeper depths. The change of sign near roughly 0.7 of crown depth is descriptive only; it is not a fitted threshold or half-life.

## What this adds biologically

The positive result is:

> Exact visible flower-color states retain a detectable phylogenetic memory across angiosperm radiations, but that excess same-color retention is concentrated among relatively recent divergences and generally decays across deeper phylogenetic divergence.

This is a macroevolutionary persistence/lability statement about **interspecific flower-color states**. It is not a claim about within-population or within-species polymorphism persistence.

The source study itself analyzed flower- and fruit-color lability as transition processes. The present result asks a complementary question: how rapidly does the realized flower-color state cease to be more similar than expected from clade-level color frequencies as lineages diverge?

## Relation to the resolution result

The common 28-clade coarse/intermediate/fine frame still shows no universal persistence scale:

- persistence-area winner counts: coarse 13, intermediate 10, fine 5
- winner-count chi-square against equal frequencies: P = 0.174
- intermediate-minus-coarse area: P = 0.108
- fine-minus-intermediate area: P = 0.831
- fine-minus-coarse area: P = 0.412

Thus two statements can coexist:

1. flower-color state memory generally **decays with relative evolutionary depth**;
2. no single coarse/intermediate/fine representation is consistently the longest-lived or most informative across clades.

## Dependence on the existing AUC

This is not independent evidence from the existing same-state AUC. Both analyses reuse pairwise phylogenetic distances and state-sharing labels. For fine color on the common 28-clade frame, AUC and persistence slope are strongly related (Spearman rho = **-0.845**, P = **1.60e-8**).

The new contribution is therefore **shape and biological interpretation through relative divergence depth**, not an independent replication count.

## Claim boundary

Allowed:

- flower-color state similarity shows a general tendency to decay across relative phylogenetic depth;
- this temporal/depth profile is heterogeneous among clades;
- no universal phenotypic resolution has the longest persistence in the current standardized frame.

Not allowed:

- absolute persistence times in Ma;
- transition-rate estimates from this curve;
- causal pollinator/environmental explanations from this analysis alone;
- within-population polymorphism persistence;
- counting this derived analysis as an independent prospective confirmation.

Camellia Paper 1 remains unchanged.
