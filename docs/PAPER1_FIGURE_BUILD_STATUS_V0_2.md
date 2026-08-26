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

Builder:

- `scripts/build_paper1_fig2_molecular_v0_2.py`.

CI:

- `.github/workflows/paper1-fig2-molecular-v0-2.yml`.

Outputs are generated as SVG and 300-dpi PNG artifacts. The builder is intentionally presentation-only: it cannot infer directions, fill missing axes, select favourable signs, or apply significance filtering.

### Panel contract

- **Fig. 2A:** five candidate-free A/F/C/P systems, retaining the single unresolved `CSIN_WHITE_PINK:P` cell.
- **Fig. 2B:** anthocyanin-gain literature versus candidate-free identified sets.
- **Fig. 2C:** yellow-development literature versus candidate-free identified sets.

The figure therefore visualizes the closed molecular claim:

> Whole A/F/C/P package recurrence is not retained under standardized measurement in either canonical transition class, while modular reuse remains transition-class dependent.

## Remaining figure work

1. Fig. 1: observation-to-realization conceptual framework.
2. Fig. 3: accepted-taxonomy and wild-colour evidence attrition.
3. Fig. 4: accepted-species nuclear topology concordance.
4. Fig. 5: local same-colour phylogenetic conservatism and demoted macro claims.
5. Fig. 6: pattern identifiable without robust event identity, plus cross-scale synthesis.
6. Supplement Fig. S1: copy/paralog-level molecular implementation details.
7. Supplement Fig. S2: ecological screen boundaries.

The next main figure should be Fig. 5, because it is the empirical macro counterpart to Fig. 2 and is already governed by authoritative result IDs `P02`/`P03`.
