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

- [`manuscript/PAPER1_AJB_MANUSCRIPT_V0_2.md`](manuscript/PAPER1_AJB_MANUSCRIPT_V0_2.md) — frozen scientific manuscript source; v0.1 is provenance only.
- [`data/paper1_authoritative_results_v0_2.csv`](data/paper1_authoritative_results_v0_2.csv) — frozen result hierarchy.
- [`data/paper1_main_figure_manifest_v0_2.csv`](data/paper1_main_figure_manifest_v0_2.csv) — current Main/Supp figure contract.
- [`data/paper1_reference_registry_v0_3.csv`](data/paper1_reference_registry_v0_3.csv) — current 21-reference journal-facing contract after the novelty audit.
- [`docs/PAPER1_NOVELTY_LITERATURE_AUDIT_2026-08-27.md`](docs/PAPER1_NOVELTY_LITERATURE_AUDIT_2026-08-27.md) — high-recall prior-art audit and claim boundary.
- [`docs/PAPER1_NOVELTY_CORE_ATTACK_ADDENDUM_2026-08-27.md`](docs/PAPER1_NOVELTY_CORE_ATTACK_ADDENDUM_2026-08-27.md) — final attack on generic theoretical priority claims.
- [`docs/CANDIDATE_FREE_ACTUAL_RECURRENCE_RESULT_V0_1.md`](docs/CANDIDATE_FREE_ACTUAL_RECURRENCE_RESULT_V0_1.md) — authoritative molecular recurrence result.
- [`docs/YELLOW_TWO_CLUSTER_RECURRENCE_RESULT_V0_1.md`](docs/YELLOW_TWO_CLUSTER_RECURRENCE_RESULT_V0_1.md) — dedicated yellow-development result.

The v0.2 authoritative-registry gate checks result/figure dependencies and local source references. Main Fig. 1–6 remain rebuilt from frozen v0.2 source tables. The journal-facing framing is generated as Paper 1 v0.3 without changing those scientific results.

## Current journal-facing route

The only current AJB upload route is **v0.7**, documented in [`docs/PAPER1_AJB_UPLOAD_BUNDLE_V0_7_README.md`](docs/PAPER1_AJB_UPLOAD_BUNDLE_V0_7_README.md) and built by `.github/workflows/paper1-ajb-upload-bundle-v0-7.yml`.

v0.7:

1. validates the frozen Paper 1 v0.2 scientific result/figure contract;
2. generates the novelty-audited Paper 1 framing v0.3 and requires exact agreement with the 21-reference v0.3 DOI registry;
3. applies the AJB 239-word structured abstract and journal-facing section order without changing biological estimates;
4. rebuilds Main Fig. 1–6 and materializes Appendix S1–S8 from frozen v0.2 scientific sources;
5. produces both Markdown and structurally audited Word/DOCX manuscript files;
6. checks Times New Roman 12 pt body, double spacing, one-inch margins, continuous line numbering, and page numbering in the DOCX;
7. rejects stale/internal manuscript content and produces a final SHA256 bundle manifest.

The v0.7 hosted build passed with **38 files before the manifest (39 uploaded files total), 21/21 reference DOIs matched, Abstract = 239 words, DOCX present, and `scientific_results_changed = false`**.

v0.6 and the former v0.5 ecological-integration bundle are historical provenance only and are not current submission routes.

## Novelty boundary

Do **not** claim priority for:

- the general idea that the same phenotype can arise through different mechanisms;
- pathway-level or modular flower-colour convergence;
- candidate/discovery-method effects on apparent repeatability;
- partial identification or identified sets as a general statistical idea;
- phylogenetic ancestral-event uncertainty or model identifiability;
- measurement-process dependence as a general biological concept;
- the first micro-to-macro study of *Camellia* flower colour.

The retained contribution is empirical and application-specific: **the same public *Camellia* systems are compared under literature-selected versus one frozen pathway-wide observation regime, incomplete A/F/C/P states are bounded explicitly, transition-class-specific recurrence is quantified, and that molecular result is separated from a topology/coding-robust macro pattern and a stricter event-identity stop rule.**

The literature basis for this boundary is a **high-recall evidence audit**, not a claim of PRISMA-complete systematic-review coverage.

## Frozen boundaries

- Do **not** infer taxon-level A/F/C/P states from visible flower colour.
- Do **not** assign ecological causes to individual colour-transition branches while event identity is not robust.
- Do **not** restore the obsolete `visible transition -> recurrent whole pathway package -> macro transition` narrative.
- Do **not** restore the historical ecological-driver panel as current Main Fig. 6.
- The term **reactivation/re-expression** remains reserved for cases with both an active→suppressed/absent→active history and evidence that the underlying machinery persisted; otherwise use retention, recruitment, or gain.

## Current execution goal

The molecular discovery, novelty-audit, and machine-generated AJB bundle gates are closed. The remaining submission work is now:

1. supply final author list/order, affiliations, and corresponding-author/ORCID information;
2. supply acknowledgments/funding and CRediT author contributions;
3. create and insert the versioned archive DOI;
4. enter the conflict-of-interest declaration in the journal submission system;
5. reopen mechanistic-phylogeny causal work only when direct taxon-level A/F/C/P coverage and robust accepted-species event identity are adequate.

Issue #94 records the completed hypothesis test and final scientific claim boundary.
