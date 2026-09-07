# Linoideae source-text terminal recovery v0.1

## Status

First auditable species-level terminal recovery from the primary Linoideae flower-colour study. This is a partial source-text layer, not a replacement for the published 112-species terminal matrix and not an atlas ancestral-state reconstruction.

Primary source: Villalvazo-Hernández et al. 2022, DOI `10.3390/plants11121579`.

The source states that flower colours were recorded for 112 Linoideae species from herbarium data, systematic/taxonomic studies, regional floras and a database, with each terminal coded as yellow, blue, white, purple, red or pink.

## Explicitly recovered current terminals

The primary text explicitly states that red is present only in two current species:

- `Linum decumbens` — RED
- `Linum grandiflorum` — RED

It separately identifies pink emergence in the Eurasian species:

- `Linum viscosum` — PINK
- `Linum pubescens` — PINK

These four rows are therefore admitted as source-text explicit terminal states.

## Admission boundary

All four rows retain:

- `phylogeny_tip = UNRESOLVED_TO_EXACT_TREE_TIP`;
- `include_macro = 0`;
- unresolved polymorphism status.

The source's Figure 2 is reported to carry current flower colour at every tip, but this v0.1 layer does not infer the remaining 108 terminal states from prose, clade colour affinity, or genus-level statements. The full matrix/figure must be recovered or independently rebuilt before common-model ASR.

## Executed result

The validator freezes:

- 4 unique source-backed taxa;
- RED = 2;
- PINK = 2;
- published terminal matrix size = 112;
- current direct text recovery = 4/112 = 0.03571428571428571;
- macro-ready rows = 0;
- atlas ASR = NOT_RUN.

## Why this matters for the cross-clade programme

Linoideae is a second macro-scale white/yellow-white baseline candidate distinct from Hydrangea. The source reconstruction favours yellow-white at the Linoideae root and reports multiple independent origins of pink and white in subclade II. Recovering its terminal matrix under the same provenance rules is therefore a direct route to a second common-model transition posterior.

The present 4-row layer is deliberately insufficient for inference but removes ambiguity about how source-text terminal evidence enters the atlas and provides a testable ingestion target for the remaining 108 published terminal states.

## Next gate

Recover the current colour attached to all tips in Figure 2 or an equivalent machine-readable source; reconcile exact tree labels; preserve unknown/polymorphic states where source evidence conflicts; require >=80% attempted-tip provenance coverage; then fit the same ER/SYM/ARD model family used for Hydrangea and other admitted systems.

Paper 1 remains unchanged.
