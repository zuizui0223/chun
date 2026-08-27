# chun

Comparative project on **floral pigment-state recurrence, observation regimes, and macroevolutionary realization** in *Camellia*.

## Scope

`chun` is *Camellia*-only. East Asian *Cirsium* phylogenomics, colour history and molecular mechanism are maintained in [EAzami](https://github.com/zuizui0223/EAzami). The initial cross-family scaffold remains recoverable in Git history but is not an active analysis input here. See [repository scope and handoff](docs/REPOSITORY_SCOPE.md).

## Current Paper 1 mainline

**Working title:** *Repeated flower-colour change does not imply repeated pigment-state packages in Camellia*

The analysis separates four pathway-wide transcript-state axes:

- **A** — anthocyanin branch;
- **F** — flavonol branch;
- **C** — carotenoid core;
- **P** — proanthocyanidin diversion.

The inferential hierarchy is:

`feasibility -> observation regime -> identified mechanistic recurrence -> macroevolutionary realization -> persistence/filtering`

Visible hue is never used to fill a missing molecular axis, and candidate-free directions are never selected by expected direction or statistical significance.

## Main result

### Formal literature observation layer

A reproducible OpenAlex/Crossref/PubMed search expanded the molecular literature matrix to **11 biological systems in 6 dependence clusters**. The formal search recovered one previously omitted independent red-versus-white *Camellia semiserrata* system (Jiang et al. 2025; DOI `10.1007/s10722-025-02606-6`). It supports canonical white→red **A=up**, while F/C/P remain unresolved.

Updated published A/F/C/P coverage is:

- system level: **9/4/1/3**, exact A-axis enrichment **P=0.0027885437**;
- after dependence collapse: **5/3/1/2**, exact A-axis enrichment **P=0.046875**.

Thus the published molecular observation process is anthocyanin-heavy even after dependence collapse. The dependence-collapsed complete-signature recurrence test remains unsupported (**P=0.1989801**). The system-level signature-recurrence sensitivity (**P=0.0458954**) is descriptive only because individual systems are not independent.

No auditable public raw RNA-seq accession was located for the new *C. semiserrata* study, so it does **not** enter the standardized candidate-free common set.

### Candidate-free matched common set

Five public RNA-seq systems remain the frozen standardized common set: three independent `anthocyanin_gain` clusters and two independent `yellow_development` clusters.

**Anthocyanin gain**

- literature exact whole-signature recurrence: **0.333–1.0**;
- candidate-free exact recurrence: **0.333 exactly**;
- literature pairwise A/F/C/P concordance: **0.25–1.0**;
- candidate-free concordance: **0.333–0.5**.

**Yellow development**

- literature exact whole-signature recurrence: **0.5–1.0**;
- candidate-free exact recurrence: **0.5 exactly**;
- literature pairwise concordance: **0.25–1.0**;
- candidate-free concordance: **0.75 exactly**.

The two standardized yellow trajectories agree on **A down / C up / P down** and differ at F. The supported interpretation is **transition-class-dependent modular recurrence**, not recurrence of one invariant whole pigment-state package.

### Macroevolutionary realization

Accepted-species nuclear analyses retain non-random visible-colour phylogenetic structure across topology and wild-colour sensitivities, while no individual transition branch survives the strict × dominant colour-coding robustness gate. Thus a **macroevolutionary pattern can be identifiable even when individual historical events and causes are not**.

## Authoritative Paper 1 files

The immutable scientific source remains [`manuscript/PAPER1_AJB_MANUSCRIPT_V0_2.md`](manuscript/PAPER1_AJB_MANUSCRIPT_V0_2.md). Current science is generated from that source as **v0.2.1**, so the formal-database update is explicit and reversible rather than silently overwriting v0.2.

Current contracts:

- [`data/paper1_authoritative_results_v0_2_1.csv`](data/paper1_authoritative_results_v0_2_1.csv) — current result hierarchy, including M07 literature-axis ascertainment;
- [`data/paper1_main_figure_manifest_v0_2_1.csv`](data/paper1_main_figure_manifest_v0_2_1.csv) — current Main/Supp figure contract;
- [`data/paper1_fig1_observation_contract_v0_2_1.csv`](data/paper1_fig1_observation_contract_v0_2_1.csv) — updated literature-observation inputs for Fig. 1;
- [`data/paper1_reference_registry_v0_2_1.csv`](data/paper1_reference_registry_v0_2_1.csv) — 16-reference science-source contract;
- [`data/paper1_reference_registry_v0_4.csv`](data/paper1_reference_registry_v0_4.csv) — current 22-reference journal-facing contract;
- [`data/micro_accessibility_edge_registry_v0_2.csv`](data/micro_accessibility_edge_registry_v0_2.csv) — 11-system/6-cluster literature observation matrix;
- [`docs/MICRO_ACCESSIBILITY_V0_2_RESULT.md`](docs/MICRO_ACCESSIBILITY_V0_2_RESULT.md) — formal-database-updated ascertainment result;
- [`docs/PAPER1_BIBLIOGRAPHIC_DB_SEARCH_2026-08-27.md`](docs/PAPER1_BIBLIOGRAPHIC_DB_SEARCH_2026-08-27.md) — database search/screening record;
- [`docs/PAPER1_NOVELTY_LITERATURE_AUDIT_2026-08-27.md`](docs/PAPER1_NOVELTY_LITERATURE_AUDIT_2026-08-27.md) and [`docs/PAPER1_NOVELTY_CORE_ATTACK_ADDENDUM_2026-08-27.md`](docs/PAPER1_NOVELTY_CORE_ATTACK_ADDENDUM_2026-08-27.md) — prior-art and novelty boundaries.

The former open-web saturation statement that no new eligible cluster existed is **superseded** by the formal database search that recovered `CSEMISERRATA`.

## Current journal-facing route

The only current AJB upload route is **v0.8**, documented in [`docs/PAPER1_AJB_UPLOAD_BUNDLE_V0_8_README.md`](docs/PAPER1_AJB_UPLOAD_BUNDLE_V0_8_README.md) and built by `.github/workflows/paper1-ajb-upload-bundle-v0-8.yml`.

v0.8:

1. regenerates science v0.2.1 from the immutable v0.2 source;
2. applies novelty framing v0.3.1 and requires exact agreement with the **22-reference v0.4 DOI registry**;
3. uses an AJB **237-word structured abstract**;
4. rebuilds Fig. 1 with the formal-database-expanded ascertainment result while retaining frozen Fig. 2–6 scientific inputs;
5. materializes Appendix S1 from the v0.2.1 authoritative registry and retains frozen S2–S8 inputs;
6. produces Markdown plus a structurally audited Word/DOCX manuscript;
7. includes the bibliographic query registry and screening decisions in provenance;
8. produces a SHA256 bundle manifest.

Hosted run **33041756422** passed all steps. Independent artifact inspection confirmed:

- **48/48 manifest-listed files** matched size and SHA256, with no missing or unregistered files;
- **22/22 reference DOIs** matched;
- Abstract = **237 words**;
- Appendix S1 contains `M07_LITERATURE_AXIS_ASCERTAINMENT`;
- DOCX structural checks all passed;
- updated Figure 1 shows **9/4/1/3**, **5/3/1/2**, and **P=0.046875** without annotation overlap;
- `candidate_free_recurrence_changed = false` and `macro_results_changed = false`.

v0.7, v0.6, and v0.5 are historical provenance only and are not current submission routes.

## Novelty boundary

Do **not** claim priority for:

- the general idea that the same phenotype can arise through different mechanisms;
- pathway-level or modular flower-colour convergence;
- candidate/discovery-method effects on apparent repeatability;
- partial identification or identified sets as a general statistical idea;
- phylogenetic ancestral-event uncertainty or model identifiability;
- measurement-process dependence as a general biological concept;
- the first micro-to-macro study of *Camellia* flower colour.

The retained contribution is empirical and application-specific: **the same auditable public *Camellia* systems are compared under literature-selected versus one frozen pathway-wide observation regime, incomplete A/F/C/P states are bounded explicitly, transition-class-specific recurrence is quantified, and that molecular result is separated from a topology/coding-robust macro pattern and a stricter event-identity stop rule.**

The formal database expansion strengthens this framing rather than replacing it: broader literature coverage made anthocyanin-axis ascertainment more clearly nonuniform, while the matched candidate-free common-set recurrence and macro conclusions remained unchanged.

The literature work is now **database-counted and high-recall**, but it is still not labelled PRISMA-complete. Dedicated CNKI/Wanfang screening, full cross-database screening-flow documentation, and a closed grey-literature/citation-chasing protocol would still be required for that methodological label.

## Frozen boundaries

- Do **not** infer taxon-level A/F/C/P states from visible flower colour.
- Do **not** assign ecological causes to individual colour-transition branches while event identity is not robust.
- Do **not** treat the non-independent system-level recurrence sensitivity as the primary recurrence result.
- Do **not** add *C. semiserrata* to the candidate-free arm unless auditable public raw reads are located and admitted under the frozen protocol.
- Do **not** restore the obsolete `visible transition -> recurrent whole pathway package -> macro transition` narrative.
- Do **not** restore the historical ecological-driver panel as current Main Fig. 6.
- The term **reactivation/re-expression** remains reserved for cases with both an active→suppressed/absent→active history and evidence that the underlying machinery persisted; otherwise use retention, recruitment, or gain.

## Current execution goal

The molecular common-set recurrence, formal-database ascertainment update, novelty audit, science v0.2.1 re-freeze, and machine-generated AJB v0.8 bundle gates are closed. Remaining submission work is:

1. supply final author list/order, affiliations, and corresponding-author/ORCID information;
2. supply acknowledgments/funding and CRediT author contributions;
3. create and insert the versioned archive DOI;
4. enter the conflict-of-interest declaration in the journal submission system;
5. reopen mechanistic-phylogeny causal work only when direct taxon-level A/F/C/P coverage and robust accepted-species event identity are adequate.

Issue #94 records the completed hypothesis test and scientific claim boundary.
