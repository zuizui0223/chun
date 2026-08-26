# Micro-to-macro evolutionary accessibility test — v0.1

## Main question

Do floral pigment-state changes that are mechanistically reachable on short timescales recur disproportionately in long-term *Camellia* evolution?

## Motivation

The current project already supports two separate observations:

1. visible colour can change through regulation and pathway-flux redistribution without requiring wholesale structural-gene loss in several within-genotype, developmental and cultivar systems;
2. ecological effects are strongest at the reproductive-service / reliability layer rather than as a universal mapping from coarse visible hue to a pollinator guild or abiotic regime.

The missing test is whether short-timescale mechanistic accessibility predicts the structure of macroevolutionary transitions.

## Primary hypothesis

For mechanistic pigment states i and j, short-timescale accessibility A_ij predicts macroevolutionary transition weight Q_ij:

`Q_ij ~ beta0 + beta1 * A_ij`

with `beta1 > 0` under the accessibility hypothesis.

A positive result supports biased evolutionary accessibility, not identity of causal mutations. A null result is also informative: developmental / horticultural lability would not predict long-term transition structure.

## State representation

Do not use a single ordered white-pink-red-yellow trait. Represent states on pathway axes:

- `A`: anthocyanin deployment;
- `F`: flavonol deployment;
- `C`: carotenoid deployment;
- `P`: proanthocyanidin / procyanidin diversion;
- optional `S`: spectral/UV state where defensible;
- optional `R`: reward state where defensible.

Each axis is initially coded as `low`, `intermediate`, `high`, or `unknown`. Visible colour is retained only as an observation label.

## Evidence layers

### Layer M1 — observed micro-accessibility

Eligible contrasts:

- within-genotype petal sectors;
- bud sports / somatic colour variants;
- developmental colour transitions within a genotype;
- within-species cultivar series when ancestry is sufficiently close and the contrast is not interpreted as an independent macroevolutionary origin;
- unified reanalysis of public petal RNA-seq where pathway-module state changes can be derived without relying on the source paper's nominated candidate genes.

Each biological system contributes at most one independent accessibility edge per state pair and direction. Correlated outcomes from the same system are not independent replicates.

### Layer M2 — macroevolutionary transition distribution

Target input is an admitted nuclear-phylogeny state reconstruction over accepted wild taxa. Transition counts must be propagated across tree and model uncertainty rather than frozen as one integer.

Until branch-level accepted-species transitions are identifiable, this layer remains a gated input rather than being imputed from cultivar evidence.

### Layer E — ecological filtering

Ecological evidence enters only after accessibility is defined. Candidate comparison:

- generation-only: `macro transition ~ accessibility`;
- generation + filtering: `macro transition/persistence ~ accessibility + ecological service/reliability predictors`.

Current ecological meta-analysis supports service/reliability filtering but not branch-specific causal attribution.

## Primary statistics

1. Build a directed micro-accessibility graph from independence-collapsed edges.
2. Compute weighted edge support, node degree, betweenness, transition entropy and reachability.
3. Test micro-macro edge congruence once macro transition weights are available.
4. Use degree-preserving directed graph permutations as the primary structural null so that apparent congruence is not explained only by a high-degree hub state.
5. Report an effect size for observed-minus-null congruence and its permutation distribution.
6. Run leave-one-biological-system-out sensitivity.

## White-state hub test

The specific `white as gateway` hypothesis is secondary to the general accessibility test.

Test whether low-anthocyanin states have higher betweenness / reachability than expected under degree-preserving nulls. Do not equate visible white with a single molecular state; multiple low-A states may exist.

## Candidate-free public-RNA-seq validation

To reduce candidate-gene publication bias:

1. quantify a predefined ortholog panel across admitted petal RNA-seq datasets;
2. calculate pathway module scores without using source-paper candidate selection;
3. derive within-study standardized state contrasts;
4. compare these independently derived states with the literature-coded accessibility edges.

This reanalysis is a validation layer, not a reason to pool incompatible raw expression scales directly.

## Hold-out prediction

Where data density permits, reserve at least one lineage / dataset from model construction. Predict its accessible state or transition direction before admitting it to the evaluation set.

## Failure modes and interpretation

- **Micro-macro congruence positive:** short-timescale mechanistic accessibility predicts evolutionary reuse.
- **Congruence null:** local developmental/regulatory lability is not sufficient to predict long-term evolution.
- **Accessibility positive, ecology adds little:** pathway architecture dominates observed transition structure.
- **Accessibility + ecology improves prediction:** supports a generation-and-filtering model.

## Immediate implementation gate

Before any macro claim:

1. freeze a machine-readable micro-accessibility edge registry;
2. record evidence type, independence unit and direction for every edge;
3. implement deterministic graph summaries and degree-preserving null machinery;
4. keep macro transition inputs explicitly missing until an admitted nuclear-tree reconstruction exists;
5. add CI assertions preventing visible-colour labels from being treated as mechanistic states.
