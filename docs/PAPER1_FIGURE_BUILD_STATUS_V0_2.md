# Paper 1 figure build status v0.2

## Current main goal

Convert the frozen v0.2 result hierarchy into reproducible manuscript figures without reintroducing superseded analyses or hand-copied values.

## Fig. 2 — molecular recurrence

**IMPLEMENTED as a reproducible build contract.**

Source of truth:

- unified frozen actual-results run: `32929846096`;
- authoritative interpretation: `docs/CANDIDATE_FREE_ACTUAL_RECURRENCE_RESULT_V0_1.md`;
- yellow matched-estimator result: `docs/YELLOW_TWO_CLUSTER_RECURRENCE_RESULT_V0_1.md`;
- manuscript hierarchy: `data/paper1_authoritative_results_v0_2.csv`;
- panel role: `data/paper1_main_figure_manifest_v0_2.csv`.

Frozen presentation-layer inputs:

- `data/paper1_fig2_candidate_free_signature_v0_2.csv`;
- `data/paper1_fig2_recurrence_intervals_v0_2.csv`;
- `data/paper1_fig2_direct_overlap_v0_2.csv`.

Builder / CI:

- `scripts/build_paper1_fig2_molecular_v0_2.py`;
- `.github/workflows/paper1-fig2-molecular-v0-2.yml`.

Outputs are generated as SVG and 300-dpi PNG artifacts. The builder is intentionally presentation-only: it cannot infer directions, fill missing axes, select favourable signs, or apply significance filtering.

### Panel contract

- **Fig. 2A:** five candidate-free A/F/C/P systems, retaining the single unresolved `CSIN_WHITE_PINK:P` cell.
- **Fig. 2B:** anthocyanin-gain literature versus candidate-free identified sets.
- **Fig. 2C:** yellow-development literature versus candidate-free identified sets.

The figure visualizes the closed molecular claim:

> Whole A/F/C/P package recurrence is not retained under standardized measurement in either canonical transition class, while modular reuse remains transition-class dependent.

## Fig. 5 — macroevolutionary realization pattern

**IMPLEMENTED as a reproducible build contract.**

Source of truth:

- `docs/NUCLEAR_COLOUR_REALIZATION_ROBUSTNESS_V0_1.md`;
- authoritative result IDs `P02_LOCAL_COLOUR_CONSERV_FASTTREE`, `P03_LOCAL_COLOUR_CONSERV_UFBOOT`, `P04_GLOBAL_MPD_TOPOLOGY_SENSITIVE`, and `P05_A_SPECIFIC_PERMISSIVITY_NOT_STRICT`;
- legacy numeric audit table `data/paper1_figure_numeric_inputs_v0_1.csv`.

Frozen presentation-layer inputs:

- `data/paper1_fig5_nearest_same_v0_2.csv`;
- `data/paper1_fig5_robustness_status_v0_2.csv`.

Builder / CI:

- `scripts/build_paper1_fig5_macro_v0_2.py`;
- `.github/workflows/paper1-fig5-macro-v0-2.yml`.

### Panel contract

- **Fig. 5A:** observed versus count-preserving-null mean nearest-same-colour edge distance under FastTree/UFBoot × strict/dominant wild-colour coding. All four observed distances are lower than their matched null means.
- **Fig. 5B:** robustness map showing that global MPD is topology-sensitive and A-specific clustering is coding-sensitive; neither is promoted over the robust nearest-same-colour result.

The figure visualizes the macro claim:

> Accepted wild flower colours retain reproducible local phylogenetic structure even though broader compression and A-specific structure are sensitivity-dependent.

The builder is unrooted-pattern presentation only. It cannot infer ancestral states, individual transitions, or ecological causes.

## Remaining figure work

1. Fig. 1: observation-to-realization conceptual framework.
2. Fig. 3: accepted-taxonomy and wild-colour evidence attrition.
3. Fig. 4: accepted-species nuclear topology concordance.
4. Fig. 6: pattern identifiable without robust event identity, plus cross-scale synthesis.
5. Supplement Fig. S1: copy/paralog-level molecular implementation details.
6. Supplement Fig. S2: ecological screen boundaries.

Next priority is Fig. 3 + Fig. 4 because both are lightweight audit figures already fully frozen by `T01`, `T02`, and `P01`. Fig. 6 should follow only after those evidence-audit panels are fixed.
