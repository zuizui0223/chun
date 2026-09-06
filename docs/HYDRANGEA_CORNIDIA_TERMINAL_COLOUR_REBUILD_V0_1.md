# Hydrangea sect. Cornidia terminal flower-colour rebuild v0.1

## Purpose

Use *Hydrangea* sect. *Cornidia* as the first explicit falsification system for a simplistic `white ancestor -> repeated directional colour gain` narrative.

The published analysis (`10.3389/fpls.2021.661522`) reconstructs white as ancestral, but its stochastic mappings contain substantially more transitions back toward white than transitions from white to red/purple. The atlas will rebuild the terminal colour matrix and re-estimate this history under the common cross-clade protocol rather than importing the published ancestral nodes as data.

## Source character and organ context

The primary Methods define flower colour as purple, red or white and explicitly state that the colour refers to:

- sepals of enlarged marginal flowers; and
- petals of reduced flowers.

Therefore the row-level schema carries both `flower_type` and `display_organ`. If a source supports only the published combined species-level character but not the finer organ assignment, retain `SOURCE_TYPED_DISPLAY_PERIANTH`; do not infer SEPAL/PETAL from genus convention.

Allowed first-pass states:
- `WHITE`
- `RED`
- `PURPLE`
- `POLYMORPHIC`
- `UNKNOWN`

## Terminal-state rebuild

Priority evidence:
1. the study's field collections/photographic records where taxon-level state is recoverable;
2. herbarium/taxonomic descriptions cited or examined by the study;
3. independent species-level floristic/taxonomic descriptions;
4. article figure inspection as QC only when no textual source is available.

One row corresponds to one accepted taxon mapped to one target phylogeny tip. Historical names remain in `source_taxon_name`. Unresolved source disagreement is not majority-voted unless explicit biological polymorphism is documented.

## Published stochastic-map QC anchor

The source paper reports mean transition counts across 1000 stochastic maps:

- RED -> WHITE = 18.011 (95% HPD 12–23)
- PURPLE -> WHITE = 4.680 (1–7)
- WHITE -> RED = 4.939 (1–8)
- WHITE -> PURPLE = 1.773 (0–4)

The frozen project diagnostic therefore gives:

- coloured -> white = 22.691
- white -> coloured = 6.712
- return-to-white / gain-from-white ratio ≈ 3.38
- about 77.17% of these four directional changes point toward white.

These values are **not atlas estimates**. They are a published-map QC/falsification target. The rebuilt matrix may reproduce, weaken or reverse this asymmetry under the common model set.

## Why this matters

If a cross-clade study selected only white-ancestor radiations and assumed colour gains should dominate, Hydrangea would make the design circular. Instead, Hydrangea forces a stronger hypothesis:

> ancestral baseline may alter the topology/rates of accessible transitions, but it does not determine a one-way trajectory toward greater visible pigmentation.

This converts `white-like ancestor` from a narrative premise into a testable predictor.

## Coverage gate

Before any atlas ASR:
- >=80% of target phylogeny tips must have a provenance row, including explicit UNKNOWN rows after attempted recovery;
- display-organ context must be preserved or explicitly source-typed;
- no cultivar-only state may fill a wild terminal;
- taxonomy must be pinned;
- the published stochastic-map values remain comparison targets, not inputs to the new likelihood.

## Next analysis

After the terminal matrix passes the coverage gate, fit the same ER/SYM/ARD candidate models used for other clades where identifiable, propagate trait uncertainty, and derive posterior/stochastic-map summaries for:

- white -> coloured transitions;
- coloured -> white transitions;
- red <-> purple transitions if data permit;
- state occupancy / persistence through time.

Only then may Hydrangea enter the pooled ancestral-baseline comparison.

Paper 1 remains unchanged and closed.
