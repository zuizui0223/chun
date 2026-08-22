# Paper 1 Main Figure Freeze v0.1

## Build

Green workflow run: `32558022436` (`Paper 1 main figure build`, run #2).

Artifact: `paper1-main-figures-v0-1`.

The artifact contains SVG + PNG for all six main figures plus `figure_build_summary.json`.

## Visual QA

The first build exposed text/arrow overlap in Figs 1–3 and an ambiguous `discordant = 4` label in Fig 4. The second build fixes those layout issues and clarifies Fig 4 as `4 unique splits per tree`, consistent with RF symmetric difference = 8.

Figs 5–6 passed the first visual review without scientific-layout changes.

## Frozen figure set

1. `Fig1_hypothesis_trajectory` — literature alternatives → micro re-analysis → accepted-species macro pattern → public-data boundary.
2. `Fig2_micro_implementation_modes` — FLS same-lineage recurrence; DFR paralog substitution; ANS/ANR copy-aware heterogeneity.
3. `Fig3_taxonomy_trait_audit` — 93 legacy tips → 55 accepted species; 35 provisional hard states → strict 24 / dominant 30.
4. `Fig4_nuclear_topology_sensitivity` — 46/50 shared nontrivial splits; four unique splits per tree; normalized RF = 0.08.
5. `Fig5_colour_conservatism_robustness` — local nearest-same-colour signal remains under both topology pipelines, while global MPD does not survive UFBoot sensitivity.
6. `Fig6_public_data_boundary` — strict robust branches 0, dominant 1, shared strict × dominant 0; empirical measurement handoff.

## Reproducibility

Figures are generated deterministically from:

- `data/paper1_authoritative_results_v0_1.csv`;
- `data/paper1_figure_numeric_inputs_v0_1.csv`;
- `scripts/build_paper1_main_figures.py`.

The builder aborts if a numeric figure input references a `superseded` or `exclude` result in the authoritative Paper 1 registry.

## Scientific boundary

This figure freeze adds no new analysis. It only visualizes results already admitted by the authoritative registry. Layout edits must not change numeric inputs, result dependencies, or claim boundaries without reopening the relevant registry result.
