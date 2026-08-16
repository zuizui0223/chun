# Idea: molecular accessibility as a predictor of niche evolution

## Starting result from chun

This idea is generated from two preliminary patterns observed in the repository rather than from a literature future-work statement.

1. **Micro/mechanistic recurrence:** across independent *Camellia* systems, redder states repeatedly increase anthocyanin deployment and the same limited regulatory/flux nodes are labile across development, petal sectors, bud sports, cultivars and species.
2. **Macro/environment recurrence:** independently published comparative datasets, recoded under one framework in `data/macro_flower_colour_environment_synthesis_v0_1.csv`, repeatedly associate floral pigmentation or colour diversification with cold/high-altitude/high-UV environments.

The combined problem is whether molecularly easy pigment changes only create visible variation, or whether they bias the environmental directions available to macroevolution.

## Core hypothesis

> **The probability and direction of climatic niche evolution depend partly on the mechanistic accessibility of pigment-network states.**

An accessible anthocyanin-rich state may increase persistence or establishment in cold/high-UV environments; alternatively, environmental shifts may occur first and recruit pigmentation secondarily.

The primary target is therefore **temporal ordering and rate change**, not a cross-sectional red-vs-temperature correlation.

## Model landscape: what already exists

The project must not claim that state-dependent niche models are absent.

Existing relevant model classes include:

- **BM** — unconstrained diffusion baseline;
- **OU** — mean reversion toward one or more optima;
- **EB** — declining evolutionary rate through time;
- **BBM (Bounded Brownian Motion)** — Brownian diffusion between hard reflective bounds;
- **multirate BM / multi-regime OU** — different rates or optima in different regimes;
- **MuSSCRat** — joint discrete-state-dependent continuous-trait rate evolution with background rate variation;
- **hOUwie and related joint discrete/continuous models** — jointly model hidden/discrete regimes and continuous trait evolution rather than treating a stochastic map as fixed;
- **SURFACE / shift-detection OU approaches** — infer convergent adaptive regimes or optimum shifts;
- **Pagel lambda/kappa/delta and white-noise transformations** — sensitivity to phylogenetic dependence and tempo.

Thus the methodological gap for `chun` is narrower.

## The gap relevant to chun

Existing state-dependent methods can ask whether a discrete state changes a continuous-trait evolutionary rate or optimum. What they do not natively provide as one biological model is the specific chain discovered here:

`measured molecular accessibility -> probability of pigment-state transition -> direction/timing of multidimensional climatic niche movement -> ecological persistence`

with all of the following simultaneously represented:

1. **continuous mechanistic accessibility**, rather than only a categorical colour regime;
2. **directional lead-lag**, distinguishing pigment-first from niche-first histories;
3. **multidimensional niche movement**, including centroid, cold-tail limit, breadth, seasonality and UV exposure;
4. **geographic opportunity/bounds**, distinguishing a true adaptive optimum from hard limits on climates actually available to the lineage;
5. **reticulation/introgression sensitivity**, important in *Camellia*;
6. **micro-to-macro node reuse**, linking developmental/cultivar accessibility to species-level evolutionary transitions.

The immediate goal is not necessarily to invent a new stochastic process. First test whether combinations/extensions of existing joint models plus event-centred statistics are sufficient. A new model is justified only if these fail to express the causal contrast.

## Main evolutionary hypotheses

### H1 — pigment-enabled cold/UV expansion
Anthocyanin-rich transitions occur before or with movement toward colder/high-UV niches more often than expected under null histories.

### H2 — stress-induced follower
Cold/high-UV niche movement comes first; pigment deployment follows. Present-day correlation is real but the causal direction is reversed.

### H3 — historical sorting
Colour-climate association disappears after ancestral range, clade and geographic opportunity are controlled.

### H4 — dual-function co-option
Pigment chemistry predicts climate better than human-visible hue because the same flavonoid network contributes to abiotic protection and signalling.

### H5 — accessibility × filter
Mechanistically easy states are generated more often, but only a subset persists depending on climate and pollinator environment. This predicts an interaction between a micro-accessibility score and ecological opportunity.

## Decisive analyses

### 1. Species niche matrix
Join admitted nuclear-tree taxa to cleaned native GBIF occurrences and CHELSA/WorldClim climate. Preserve niche tails and breadth rather than only species means.

### 2. Baseline niche-process comparison
Compare BM, OU, EB, BBM and rate-shift models. Treat model fit as phenomenology, not proof of adaptation.

### 3. State-dependent rate/optimum analysis
Fit state-dependent BM/OU and joint discrete-continuous models to ask whether anthocyanin/pigment states alter climatic niche rate or optimum.

### 4. Event-centred lead-lag analysis
Across stochastic histories, quantify whether W->A pigment transitions precede, coincide with or follow cold-side niche shifts.

### 5. Mechanistic-accessibility regression
Replace colour category with a quantitative micro-accessibility score derived from RNA-seq/meta-mechanistic recurrence and ask whether that score predicts macro transition reuse and climatic shift magnitude.

### 6. Geography-bounded sensitivity
Compare OU-like attraction with BBM-like environmental bounds and explicit available-climate backgrounds. This distinguishes adaptive attraction from simply occupying the climatic space that geography makes available.

## Current claim ceiling

The current data justify the hypothesis that anthocyanin/pigment accessibility **may** be linked to cold/high-UV niche expansion. They do not yet demonstrate that floral anthocyanin caused cold adaptation in *Camellia*.

A convincing result requires the same direction across multiple nuclear trees, state histories and niche summaries, with pigment-first histories outperforming geography-only and niche-first alternatives.
