# Paper 1 figure build status v0.2

## Status

**All main-text figures Fig. 1–6 now have reproducible build contracts.**

The governing hierarchy remains `data/paper1_authoritative_results_v0_2.csv` and `data/paper1_main_figure_manifest_v0_2.csv`. Figure builders are presentation-only and must not reintroduce superseded analyses, impute missing molecular states, or add branch-causal inference.

## Fig. 1 — observation-to-realization framework

Inputs:
- `data/paper1_fig1_framework_v0_2.csv`;
- `data/paper1_fig1_observation_contract_v0_2.csv`.

Builder / CI:
- `scripts/build_paper1_fig1_framework_v0_2.py`;
- `.github/workflows/paper1-fig1-framework-v0-2.yml`.

Contract: feasibility -> observation regime -> identified recurrence -> macro realization -> event-identifiability boundary -> persistence/filtering context. Panel B makes the nonuniform literature A/F/C/P observation regime explicit and contrasts it with the frozen five-system candidate-free protocol.

## Fig. 2 — molecular recurrence

Inputs:
- `data/paper1_fig2_candidate_free_signature_v0_2.csv`;
- `data/paper1_fig2_recurrence_intervals_v0_2.csv`;
- `data/paper1_fig2_direct_overlap_v0_2.csv`.

Builder / CI:
- `scripts/build_paper1_fig2_molecular_v0_2.py`;
- `.github/workflows/paper1-fig2-molecular-v0-2.yml`.

Claim: whole A/F/C/P package recurrence is not retained under standardized measurement in either canonical class, while modular reuse remains transition-class dependent.

## Fig. 3 — evidence attrition

Builder / CI:
- `scripts/build_paper1_fig3_fig4_audits_v0_2.py`;
- `.github/workflows/paper1-fig3-fig4-audits-v0-2.yml`.

Contract: 93 legacy tips -> 55 WFO accepted species; 35 provisional hard colour states -> strict 24 / dominant sensitivity 30, with 11 strict demotions.

## Fig. 4 — nuclear topology concordance

Built in the Fig. 3/4 audit builder. Contract: 50 nontrivial splits per topology, 46 shared, RF difference 8, normalized RF 0.08, split Jaccard 0.8519. Downstream trait patterns remain checked on both topologies.

## Fig. 5 — macroevolutionary realization pattern

Inputs:
- `data/paper1_fig5_nearest_same_v0_2.csv`;
- `data/paper1_fig5_robustness_status_v0_2.csv`.

Builder / CI:
- `scripts/build_paper1_fig5_macro_v0_2.py`;
- `.github/workflows/paper1-fig5-macro-v0-2.yml`.

Claim: accepted wild flower colours retain reproducible local phylogenetic structure under both topologies and both wild-colour codings. Global MPD and A-specific clustering remain sensitivity-dependent and are not promoted.

## Fig. 6 — pattern without event identity

Inputs:
- `data/paper1_fig6_event_gate_v0_2.csv`;
- `data/paper1_fig6_synthesis_v0_2.csv`.

Builder / CI:
- `scripts/build_paper1_fig6_identifiability_v0_2.py`;
- `.github/workflows/paper1-fig6-identifiability-v0-2.yml`.

Contract: strict robust branches=0, dominant sensitivity=1, strict×dominant shared=0. This is the explicit stop rule for branch-specific molecular/ecological causation.

## Remaining work

1. Run/verify the new figure CI jobs and inspect generated artifacts.
2. Build Supplement Fig. S1 (copy/paralog implementation) and Fig. S2 (ecological boundary) only after main figures pass.
3. Reconcile the branch with the one newer `main` commit (#93 ecological-driver integration); current PR mergeability must be rechecked afterward.
4. Final manuscript/figure cross-check against the authoritative result registry.
5. Keep PR #95 draft until those cleanup gates pass.
