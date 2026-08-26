# Paper 1 figure build status v0.2

## Current main goal

Convert the frozen v0.2 result hierarchy into reproducible manuscript figures without reintroducing superseded analyses or hand-copied values.

## Fig. 2 — molecular recurrence

**IMPLEMENTED as a reproducible build contract.**

Source of truth:
- unified frozen actual-results run `32929846096`;
- `docs/CANDIDATE_FREE_ACTUAL_RECURRENCE_RESULT_V0_1.md`;
- `docs/YELLOW_TWO_CLUSTER_RECURRENCE_RESULT_V0_1.md`;
- `data/paper1_authoritative_results_v0_2.csv`;
- `data/paper1_main_figure_manifest_v0_2.csv`.

Frozen presentation inputs:
- `data/paper1_fig2_candidate_free_signature_v0_2.csv`;
- `data/paper1_fig2_recurrence_intervals_v0_2.csv`;
- `data/paper1_fig2_direct_overlap_v0_2.csv`.

Builder / CI:
- `scripts/build_paper1_fig2_molecular_v0_2.py`;
- `.github/workflows/paper1-fig2-molecular-v0-2.yml`.

Panel contract:
- Fig. 2A: five candidate-free A/F/C/P systems, retaining unresolved `CSIN_WHITE_PINK:P`.
- Fig. 2B: anthocyanin-gain literature vs candidate-free identified sets.
- Fig. 2C: yellow-development literature vs candidate-free identified sets.

Claim: whole-package recurrence is not retained in either canonical class, while modular reuse is transition-class dependent.

## Fig. 3 — evidence attrition

**IMPLEMENTED as a reproducible build contract.**

Frozen values are read directly from `data/paper1_figure_numeric_inputs_v0_1.csv` and guarded against result IDs `T01_WFO_ACCEPTED_TAXONOMY` and `T02_WILD_COLOUR_AUDIT`.

Panel contract:
- Fig. 3A: 93 legacy Camellia tips -> 55 WFO 2026-06 accepted species.
- Fig. 3B: 35 provisional hard colour states -> strict 24 / dominant-sensitivity 30; 11 provisional hard labels are demoted in strict analysis.

Builder / CI:
- `scripts/build_paper1_fig3_fig4_audits_v0_2.py`;
- `.github/workflows/paper1-fig3-fig4-audits-v0-2.yml`.

## Fig. 4 — nuclear topology concordance

**IMPLEMENTED in the same audit builder as Fig. 3.**

Frozen values:
- 50 nontrivial splits per accepted-species topology;
- 46 shared;
- RF difference 8;
- normalized RF 0.08;
- split Jaccard 0.8519.

Claim boundary: the topologies are highly concordant but not identical, so downstream trait patterns are checked on both.

## Fig. 5 — macroevolutionary realization pattern

**IMPLEMENTED as a reproducible build contract.**

Source of truth:
- `docs/NUCLEAR_COLOUR_REALIZATION_ROBUSTNESS_V0_1.md`;
- result IDs `P02`, `P03`, `P04`, `P05`;
- `data/paper1_figure_numeric_inputs_v0_1.csv`.

Frozen presentation inputs:
- `data/paper1_fig5_nearest_same_v0_2.csv`;
- `data/paper1_fig5_robustness_status_v0_2.csv`.

Builder / CI:
- `scripts/build_paper1_fig5_macro_v0_2.py`;
- `.github/workflows/paper1-fig5-macro-v0-2.yml`.

Panel contract:
- Fig. 5A: observed vs count-preserving-null mean nearest-same-colour edge distance under FastTree/UFBoot × strict/dominant coding. All four observed distances are lower than their matched null means.
- Fig. 5B: robustness map showing global MPD is topology-sensitive and A-specific clustering is coding-sensitive.

Claim: accepted wild flower colours retain reproducible local phylogenetic structure even though broader compression and A-specific structure are sensitivity-dependent.

## Remaining figure work

1. Fig. 1: observation-to-realization conceptual framework.
2. Fig. 6: pattern identifiable without robust event identity, plus cross-scale synthesis.
3. Supplement Fig. S1: copy/paralog-level molecular implementation details.
4. Supplement Fig. S2: ecological screen boundaries.

The empirical main-result panels Fig. 2–5 are now represented by reproducible build contracts. Next priority is Fig. 6 because it closes the identification argument; Fig. 1 should then be drawn as the final conceptual summary after the empirical panels are fixed.
