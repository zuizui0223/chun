# Micro-accessibility score v0.1 result

## Purpose

This result creates the predictor needed for a non-circular future test of `H_MICRO_MACRO_REUSE`.

The score is constructed **only from micro/developmental evidence**. It excludes Fan genus-scale transition evidence, extant section concentration, macro colour-state abundance, and future nuclear stochastic maps.

## Why this is not a transition probability

Studies differ in which genes, paralogs and biochemical modules they assayed. Therefore the true denominator of observation opportunities is unknown for many features.

A naive quantity such as `positive studies / all studies` would mix biological accessibility with assay design and publication selection.

The v0.1 product is therefore an **evidence recurrence profile**. For each node/module it retains separately:

- independent micro evidence-cluster count;
- comparison-scale breadth;
- public-raw support;
- functional-validation support;
- observed direction labels;
- orthology/paralog uncertainty.

The primary pre-specified predictor for the later macro enrichment test is `n_independent_micro_clusters`. Other fields are evidence-quality modifiers, not hidden weights chosen after seeing macro results.

## Module-level result

Current micro-only recurrence ranking:

1. **anthocyanin downstream** — 4 independent clusters / 4 scale classes / 3 public-raw clusters / 1 functionally anchored cluster;
2. **flavonol** — 3 clusters / 2 scales / 3 public-raw / 1 functional;
3. **regulatory** — 3 clusters / 3 scales / 2 public-raw / 1 functional;
4. **proanthocyanidin** — 2 clusters / 2 scales / 2 public-raw / no direct module-level functional validation in the current ledger;
5. **carotenoid** — 2 clusters / 2 scales / 1 public-raw / no node-resolved functional validation in the current ledger.

The strongest present inference is therefore **module recurrence**, not a single universal red-colour switch.

## Node-level result

Current explicit node/family evidence:

- **FLS** — 3 independent clusters, 2 scale classes, 3 public-raw clusters, one functionally validated paralog system (`CnFLS2`);
- **ANS** — 3 clusters, 3 scales, one public-raw cluster, one functional CrANS system; exact cross-species paralog mapping remains incomplete;
- **DFR** — 2 clusters, 2 scales, one public-raw and one functionally anchored system;
- **ANR** — 2 clusters, 2 scales, both public-raw, but directions differ across systems/stages;
- CHS, F3H, F3'H, LAR and UFGT currently have one explicit independent micro cluster each in the strict ledger;
- MYB114 and bHLH1 each have one named functional C. japonica system, while broader MYB evidence exists at family/module resolution.

## Important interpretation

### 1. Module accessibility is currently more identifiable than exact node accessibility

The evidence is much cleaner at biochemical-module resolution than at exact gene/paralog resolution. This is not merely missing sample size: source studies often use broad enzyme-family annotations, different reference assemblies, or multiple paralogs with opposing developmental directions.

### 2. FLS and ANS are the current highest-recurrence explicit nodes, but their meaning differs

- FLS is repeatedly implicated across three independent systems, but its **direction is stage/paralog dependent** in C. sinensis. The signal is lability, not a universal `FLS = white/yellow` direction.
- ANS is implicated across three systems, including a functional CrANS experiment, but cross-species orthology/paralog identity still needs harmonization.

### 3. DFR has especially clean mechanistic anchoring despite fewer independent clusters

DFR is repeated in two independent systems and has direct MYB114/bHLH1 promoter-level functional evidence in C. japonica. It should therefore remain a high-priority node even though the unweighted recurrence count is lower than FLS/ANS.

### 4. A ranking is not a mutation-rate estimate

`n_independent_micro_clusters` says how broadly a feature is independently implicated in the current micro evidence base. It does not estimate the probability that a mutation occurs, the probability that a species-level transition fixes, or the natural fraction of Camellia colour evolution using that feature.

## Connection to the quantitative state-vector result

PR #13 established that a useful minimum biochemical representation requires separable anthocyanin, flavonol, PA and carotenoid dimensions and that visible A/red is a lossy state label.

The present result adds the micro predictor layer:

`micro node/paralog evidence -> module accessibility -> state-vector displacement`

The later macro test is deliberately held out:

`micro accessibility predictor` **vs** `independently reconstructed macro transition branches`.

## Decisive H_MICRO_MACRO_REUSE test

Once provenance-safe nuclear histories are admitted:

1. identify independent colour/pigment transition branches without using the micro score;
2. annotate macro-transition candidate genes/modules under a common ortholog map;
3. test whether features with higher pre-defined `n_independent_micro_clusters` are enriched on transition branches relative to matched pigment-network background features;
4. separately test whether independent branches move along similar module state-vector directions;
5. repeat across topology/reticulation uncertainty.

A positive result would support accessibility-biased macroevolution. A null result would show that short-scale mechanistic lability does not necessarily predict long-term evolutionary reuse.

## Next public-data bottleneck

The next bottleneck is **ortholog/paralog harmonization**, not more qualitative literature counting.

Priority families/nodes:

- FLS/CnFLS2 and other FLS paralogs;
- ANS/LDOX;
- DFR;
- UFGT family;
- ANR/LAR;
- named regulatory factors such as MYB114/bHLH1 versus broader MYB/bHLH family annotations.

This can still be advanced with public sequence/processed-expression data before new field sampling.

## Claim boundary

Supported now:

- a non-circular, micro-only evidence ranking can be defined;
- anthocyanin-downstream is the broadest recurrent current module;
- flavonol and regulatory modules are independently recurrent;
- FLS and ANS have the broadest current explicit node recurrence;
- exact node-level accessibility is less identifiable than module accessibility because of paralog/annotation uncertainty.

Not supported now:

- natural transition/mutation probabilities;
- preferential macro reuse;
- a universal node hierarchy across Camellia;
- ecological selection on any high-ranked node/module.
