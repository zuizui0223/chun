# chun

Comparative project on **floral pigment-state recurrence, observation regimes, and macroevolutionary realization** in *Camellia*.

## Scope

`chun` is *Camellia*-only. East Asian *Cirsium* phylogenomics, colour history and molecular mechanism are maintained in [EAzami](https://github.com/zuizui0223/EAzami). The initial cross-family scaffold remains recoverable in Git history but is not an active analysis input here. See [repository scope and handoff](docs/REPOSITORY_SCOPE.md).

## Current Paper 1 mainline

**Working title:** *Repeated flower-colour change does not imply repeated pigment-state packages in Camellia*

The paper asks whether repeated visible flower-colour change really implies repeated use of one molecular mechanism. Instead of equating a visible colour with a pigment mechanism, the analysis separates four pathway-wide transcript-state axes:

- **A** — anthocyanin branch;
- **F** — flavonol branch;
- **C** — carotenoid core;
- **P** — proanthocyanidin diversion.

The inferential hierarchy is:

`feasibility -> observation regime -> identified mechanistic recurrence -> macroevolutionary realization -> persistence/filtering`

Visible hue is never used to fill a missing molecular axis, and candidate-free directions are never selected by expected direction or statistical significance.

## Main result

Five public RNA-seq systems were remeasured with one frozen annotation-driven A/F/C/P pipeline: three independent `anthocyanin_gain` clusters and two independent `yellow_development` clusters.

### Anthocyanin gain

- literature exact whole-signature recurrence: **0.333–1.0**;
- candidate-free exact recurrence: **0.333 exactly**;
- literature pairwise A/F/C/P concordance: **0.25–1.0**;
- candidate-free concordance: **0.333–0.5**.

### Yellow development

- literature exact whole-signature recurrence: **0.5–1.0**;
- candidate-free exact recurrence: **0.5 exactly**;
- literature pairwise concordance: **0.25–1.0**;
- candidate-free concordance: **0.75 exactly**.

The two standardized yellow trajectories agree on **A down / C up / P down** and differ at F. The supported interpretation is therefore **transition-class-dependent modular recurrence**, not recurrence of one invariant whole pigment-state package.

At the macro scale, accepted-species nuclear analyses retain non-random visible-colour phylogenetic structure across topology and wild-colour sensitivities, while no individual transition branch survives the strict × dominant colour-coding robustness gate. Thus a **macroevolutionary pattern can be identifiable even when individual historical events and causes are not**.

## Authoritative Paper 1 files

- [`manuscript/PAPER1_AJB_MANUSCRIPT_V0_2.md`](manuscript/PAPER1_AJB_MANUSCRIPT_V0_2.md) — current scientific manuscript source; v0.1 is provenance only.
- [`data/paper1_authoritative_results_v0_2.csv`](data/paper1_authoritative_results_v0_2.csv) — frozen result hierarchy.
- [`data/paper1_main_figure_manifest_v0_2.csv`](data/paper1_main_figure_manifest_v0_2.csv) — current Main/Supp figure contract.
- [`data/paper1_reference_registry_v0_2.csv`](data/paper1_reference_registry_v0_2.csv) — governed reference set.
- [`docs/CANDIDATE_FREE_ACTUAL_RECURRENCE_RESULT_V0_1.md`](docs/CANDIDATE_FREE_ACTUAL_RECURRENCE_RESULT_V0_1.md) — authoritative molecular recurrence result.
- [`docs/YELLOW_TWO_CLUSTER_RECURRENCE_RESULT_V0_1.md`](docs/YELLOW_TWO_CLUSTER_RECURRENCE_RESULT_V0_1.md) — dedicated yellow-development result.

The v0.2 authoritative-registry gate checks result/figure dependencies and local source references. Main Fig. 1–6 are rebuilt from frozen v0.2 source tables.

## Current journal-facing route

The only current AJB upload route is **v0.6**, documented in [`docs/PAPER1_AJB_UPLOAD_BUNDLE_V0_6_README.md`](docs/PAPER1_AJB_UPLOAD_BUNDLE_V0_6_README.md) and built by `.github/workflows/paper1-ajb-upload-bundle-v0-6.yml`.

v0.6:

1. starts directly from the current v0.2 scientific manuscript and result registry;
2. rebuilds the current Main Fig. 1–6, including identifiability/synthesis as Fig. 6;
3. materializes eight current Supporting Information appendices;
4. rejects stale v0.1 registry references, the obsolete ecological Main Fig. 6, and legacy Fig. S3 from the submission contract;
5. produces a SHA256 bundle manifest.

The former v0.5 ecological-integration upload bundle is **historical provenance only** and is not a current submission route.

## Frozen boundaries

- Do **not** infer taxon-level A/F/C/P states from visible flower colour.
- Do **not** assign ecological causes to individual colour-transition branches while event identity is not robust.
- Do **not** restore the obsolete `visible transition -> recurrent whole pathway package -> macro transition` narrative.
- Do **not** restore the historical ecological-driver panel as current Main Fig. 6.
- The term **reactivation/re-expression** remains reserved for cases with both an active→suppressed/absent→active history and evidence that the underlying machinery persisted; otherwise use retention, recruitment, or gain.

## Current execution goal

The molecular recurrence discovery gate is closed. The active work is now:

1. validate and freeze the v0.6 AJB upload artifact;
2. complete final manuscript/reference/figure QC without changing frozen biological estimates;
3. supply human submission metadata and the versioned archive DOI;
4. reopen mechanistic-phylogeny causal work only when direct taxon-level A/F/C/P coverage and robust accepted-species event identity are adequate.

Issue #94 records the completed hypothesis test and final claim boundary.
