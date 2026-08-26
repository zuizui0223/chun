# Paper 1 figure build status v0.2

## Current main goal

Convert the frozen v0.2 result hierarchy into reproducible manuscript figures without reintroducing superseded analyses or hand-copied values.

## Fig. 2 — molecular recurrence

**IMPLEMENTED as a reproducible build contract.**

Sources: unified run `32929846096`, `docs/CANDIDATE_FREE_ACTUAL_RECURRENCE_RESULT_V0_1.md`, `docs/YELLOW_TWO_CLUSTER_RECURRENCE_RESULT_V0_1.md`, `data/paper1_authoritative_results_v0_2.csv`.

Presentation inputs:
- `data/paper1_fig2_candidate_free_signature_v0_2.csv`;
- `data/paper1_fig2_recurrence_intervals_v0_2.csv`;
- `data/paper1_fig2_direct_overlap_v0_2.csv`.

Builder / CI:
- `scripts/build_paper1_fig2_molecular_v0_2.py`;
- `.github/workflows/paper1-fig2-molecular-v0-2.yml`.

Claim: whole A/F/C/P package recurrence is not retained under standardized measurement in either canonical class, while modular reuse remains transition-class dependent.

## Fig. 3 — evidence attrition

**IMPLEMENTED.** Frozen values are read directly from `data/paper1_figure_numeric_inputs_v0_1.csv` with result-ID guards.

- Fig. 3A: 93 legacy tips -> 55 WFO 2026-06 accepted species.
- Fig. 3B: 35 provisional hard colour states -> strict 24 / dominant sensitivity 30; 11 strict demotions.

Builder / CI:
- `scripts/build_paper1_fig3_fig4_audits_v0_2.py`;
- `.github/workflows/paper1-fig3-fig4-audits-v0-2.yml`.

## Fig. 4 — nuclear topology concordance

**IMPLEMENTED in the Fig. 3/4 audit builder.**

Frozen values: 50 nontrivial splits per topology; 46 shared; RF difference 8; normalized RF 0.08; split Jaccard 0.8519.

Claim boundary: topologies are highly concordant but not identical, so downstream trait patterns are checked on both.

## Fig. 5 — macroevolutionary realization pattern

**IMPLEMENTED.**

Presentation inputs:
- `data/paper1_fig5_nearest_same_v0_2.csv`;
- `data/paper1_fig5_robustness_status_v0_2.csv`.

Builder / CI:
- `scripts/build_paper1_fig5_macro_v0_2.py`;
- `.github/workflows/paper1-fig5-macro-v0-2.yml`.

- Fig. 5A: observed vs count-preserving-null mean nearest-same-colour edge distance under FastTree/UFBoot × strict/dominant coding; all four observed values are lower than their matched null means.
- Fig. 5B: global MPD is topology-sensitive and A-specific clustering is coding-sensitive, so neither replaces the robust nearest-same-colour result.

Claim: accepted wild flower colours retain reproducible local phylogenetic structure even though broader compression and A-specific structure are sensitivity-dependent.

## Fig. 6 — pattern without event identity

**IMPLEMENTED.**

Presentation inputs:
- `data/paper1_fig6_event_gate_v0_2.csv`;
- `data/paper1_fig6_synthesis_v0_2.csv`.

Builder / CI:
- `scripts/build_paper1_fig6_identifiability_v0_2.py`;
- `.github/workflows/paper1-fig6-identifiability-v0-2.yml`.

- Fig. 6A: strong accepted-species branch transitions are strict=0, dominant=1, strict×dominant shared=0.
- Fig. 6B: molecular whole-package failure/modular reuse -> robust local macro pattern -> event identity failure.

Claim boundary: the figure synthesizes frozen results only. Zero cross-scenario robust events is the stop rule for branch-specific molecular/ecological causation.

## Remaining figure work

1. Fig. 1: observation-to-realization conceptual framework.
2. Supplement Fig. S1: copy/paralog-level molecular implementation details.
3. Supplement Fig. S2: ecological screen boundaries.

Empirical main figures Fig. 2–6 now have reproducible build contracts. Fig. 1 should be the final conceptual figure so its arrows mirror the completed empirical result hierarchy rather than predetermine it.
