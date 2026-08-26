# Paper 1 authoritative result registry

## Purpose

Paper 1 v0.2 is the current claim contract. The manuscript, Main Fig. 1–6, Supplementary figures, and repository summaries must follow the v0.2 result hierarchy rather than re-entering older accessibility, ancestral-state, ecological-causation, or legacy-tip framings.

The machine-readable contract is:

- `data/paper1_authoritative_results_v0_2.csv` — current Paper 1 results, including authoritative, sensitivity, and explicitly superseded claims;
- `data/paper1_main_figure_manifest_v0_2.csv` — Main Fig. 1–6 plus the permitted Supplementary figure dependencies;
- `scripts/validate_paper1_result_registry.py` — CI gate for result IDs, Main/Supp figure dependencies, excluded claims, and local source-reference existence;
- `.github/workflows/paper1-authoritative-registry.yml` — runs the v0.2 contract on every pull request.

The v0.1 registry and manifest remain provenance only.

## Current headline

> Repeated flower-colour change in *Camellia* does not imply recurrence of one invariant whole pigment-state package. Standardized A/F/C/P remeasurement removes literature-permitted complete whole-package recurrence in both canonical transition classes while retaining transition-class-dependent modular reuse. At macro scale, wild flower colour remains locally phylogenetically structured, but current public hard-state data do not identify individual accepted-species transition branches robustly enough for branch-specific causal attribution.

This is not a claim that molecular recurrence is absent, that candidate-gene studies are generally wrong, or that one ecological driver explains *Camellia* flower-colour evolution.

## Main molecular results

1. `M05_ANTHOCYANIN_OBSERVATION_REGIME` — across three independent anthocyanin-gain clusters, literature exact-signature recurrence spans 0.333–1.0 and pairwise concordance 0.25–1.0, whereas candidate-free remeasurement fixes exact-signature recurrence at 0.333 and narrows pairwise concordance to 0.333–0.5.
2. `M06_YELLOW_MODULAR_RECURRENCE` — the two yellow-development trajectories share A down / C up / P down and differ at F; candidate-free pairwise concordance is 0.75, not exact whole-signature recurrence.
3. `C03_WHOLE_PACKAGE_VS_MODULAR_RECURRENCE` — the integrated molecular conclusion is modular, transition-class-dependent repeatability rather than recurrence of one complete A/F/C/P package.

Sequence-aware FLS, DFR, ANS/LDOX, and ANR results remain authoritative supporting evidence in Supplement; they are not substitutes for the frozen candidate-free recurrence estimator.

## Main macro and identifiability results

1. `T01_WFO_ACCEPTED_TAXONOMY` — 93 historical nuclear tips collapse to 55 accepted *Camellia* species under the pinned WFO Plant List 2026-06 taxonomy.
2. `T02_WILD_COLOUR_AUDIT` — 35 provisional hard colour states reduce to a strict 24-species seed and a dominant-colour 30-species sensitivity.
3. `P01_NUCLEAR_TOPOLOGY_CONCORDANCE` — the two accepted-species nuclear pipelines share 46/50 nontrivial splits on 53 common species (normalized RF=0.08).
4. `P03_LOCAL_COLOUR_CONSERV_UFBOOT` — local nearest-same-colour conservatism survives the stronger UFBoot topology and wild-colour sensitivities.
5. `B01_NO_ROBUST_ACCEPTED_BRANCH_EVENTS` — strict and dominant colour codings share zero robust accepted-species transition branches.
6. `C02_PUBLIC_DATA_IDENTIFIABILITY_BOUNDARY` — pattern-level persistence is identifiable, but branch-specific ecological or molecular causation is not.

## Results retained as robustness or background

- FLS same-lineage recurrence and DFR paralog substitution;
- ANS/LDOX and ANR copy-specific directional heterogeneity;
- climate and pollination screens as persistence context rather than branch causes;
- FastTree local-colour conservatism as a topology sensitivity;
- global same-colour MPD and A-specific permissivity as explicitly demoted robustness results;
- accepted-species ancestral-state sensitivity, where W is favoured but W/Y uncertainty remains.

## `supersedes` semantics in v0.2

In v0.2, `supersedes` can mean that a newer result replaces an older result as the **primary estimator or framing** without making the older result scientifically false. A result is excluded from current claims only when it is explicitly marked:

`status = superseded` and `manuscript_role = exclude`.

This distinction allows, for example, sequence-aware FLS/DFR results to remain valid supporting evidence even though the candidate-free A/F/C/P recurrence analysis supersedes them as the primary molecular recurrence test.

## Superseded results that must not return to Main figures

- legacy A-specific lineage-permissivity headline;
- legacy/global same-colour MPD as if topology-independent;
- definitive or novel white-ancestor framing;
- three legacy 93-tip W→A branches as secure accepted-species events.

## Figure contract

- **Fig. 1** — observation-to-realization framework and what standardized observation changes.
- **Fig. 2** — five candidate-free A/F/C/P systems, anthocyanin identified-set contraction, and yellow modular recurrence.
- **Fig. 3** — taxonomy and wild-colour evidence attrition.
- **Fig. 4** — accepted-species nuclear-topology concordance.
- **Fig. 5** — local colour conservatism across topologies plus explicit demotion of non-robust macro claims.
- **Fig. 6** — pattern without robust event identity and the cross-scale synthesis.
- **Fig. S1–S2** — sequence/copy-level molecular support and ecological-screen boundaries.

## Stop rule

Do not infer taxon-level A/F/C/P states from visible colour, and do not run branch-specific climate, pollination, or molecular enrichment unless new data produce transition events robust to accepted taxonomy, wild-colour uncertainty, and nuclear topology.

The current repository task is submission/QC consolidation around this v0.2 contract. New branch-causal science requires new empirical information rather than additional tuning of the present public hard-state data.
