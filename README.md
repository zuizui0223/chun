# chun

Comparative project on **floral pigment-state recurrence, observation regimes, and macroevolutionary realization** in *Camellia*.

## Programme position

`chun` is the **evolutionary-time arm** of a broader programme on the spatiotemporal organization of flower-colour variation. Its biological question is not simply why *Camellia* species have different colours, but **how similar flower-colour states are repeatedly generated through evolutionary history and how repeatable the underlying molecular transition is**. The complementary [`fcp`](https://github.com/zuizui0223/fcp) project is the geographic-space arm, asking whether intraspecific flower-colour variation is maintained as local coexistence or sorted into geographic differentiation.

The shared conceptual decomposition is:

`generation through time -> establishment/persistence -> organization in space`

See [`docs/FLOWER_COLOUR_VARIATION_TEMPORAL_PROGRAM.md`](docs/FLOWER_COLOUR_VARIATION_TEMPORAL_PROGRAM.md) for the full positioning and terminology. Across the programme, **flower-colour variation** is the umbrella term; **polymorphism** is reserved for documented within-population coexistence.

## Scope

`chun` is *Camellia*-only. East Asian *Cirsium* phylogenomics, colour history and molecular mechanism are maintained in [EAzami](https://github.com/zuizui0223/EAzami). The initial cross-family scaffold remains recoverable in Git history but is not an active analysis input here. See [repository scope and handoff](docs/REPOSITORY_SCOPE.md).

## Current Paper 1 mainline

**Working title:** *Repeated flower-colour change does not imply repeated pigment-state packages in Camellia*

The temporal question is: when evolution repeatedly reaches similar visible flower-colour states, does it replay the same complete pigment-network transition or assemble similar phenotypes from different modules?

The analysis separates four pathway-wide transcript-state axes:

- **A** — anthocyanin branch;
- **F** — flavonol branch;
- **C** — carotenoid core;
- **P** — proanthocyanidin diversion.

The inferential hierarchy is:

`feasibility -> observation regime -> identified mechanistic recurrence -> macroevolutionary realization -> persistence/filtering`

Visible hue is never used to fill a missing molecular axis, and candidate-free directions are never selected by expected direction or statistical significance. The observation-regime analysis is an identification step required to answer the biological repeatability question; it is not the biological endpoint by itself.

## Why Camellia

*Camellia* is used as a natural temporal model system because repeated red/pink, white and yellow states occur across the genus, public multi-omic flower-colour systems are available, and reproductive environments include insect-, bird- and mixed-pollination regimes. Independent genus-scale phylogenomics suggests a likely white most recent common ancestor, but `chun` does **not** treat white as a molecular zero and its own accepted-species reconstruction retains W/Y uncertainty. The appropriate framing is a **white-like visible baseline with retained pigment-network capacity**, not an empty pigment state or a definitive white-ancestor claim.

Pollinator diversity is likewise used to motivate ecological heterogeneity, not to assign visible hues to fixed syndromes. For example, visibly red *C. japonica* and *C. rusticana* recruit different pollinators and differ in pollinator-visible UV/fluorescence signals, while golden *C. petelotii* receives substantial service from both sunbirds and honeybees.

## Last validated Paper 1 result

### Formal literature observation layer

The current validated v0.2.1 literature matrix contains **11 biological systems in 6 dependence clusters**. The formal OpenAlex/Crossref/PubMed search recovered one previously omitted independent red-versus-white *Camellia semiserrata* system (Jiang et al. 2025; DOI `10.1007/s10722-025-02606-6`). It supports canonical white→red **A=up**, while F/C/P remain unresolved.

Validated published A/F/C/P coverage is:

- system level: **9/4/1/3**, exact A-axis enrichment **P=0.0027885437**;
- after dependence collapse: **5/3/1/2**, exact A-axis enrichment **P=0.046875**.

Thus the published molecular observation process is anthocyanin-heavy even after dependence collapse. The dependence-collapsed complete-signature recurrence test remains unsupported (**P=0.1989801**). The system-level signature-recurrence sensitivity (**P=0.0458954**) is descriptive only because individual systems are not independent.

No auditable public raw RNA-seq accession was located for the new *C. semiserrata* study, so it does **not** enter the standardized candidate-free common set.

### Candidate-free matched common set

Five public RNA-seq systems remain the frozen standardized common set: three independent `anthocyanin_gain` clusters and two independent `yellow_development` clusters.

**Anthocyanin gain**

- literature exact whole-signature recurrence: **0.333–1.0** in the last validated v0.2.1 freeze;
- candidate-free exact recurrence: **0.333 exactly**;
- literature pairwise A/F/C/P concordance: **0.25–1.0** in the last validated v0.2.1 freeze;
- candidate-free concordance: **0.333–0.5**.

**Yellow development**

- literature exact whole-signature recurrence: **0.5–1.0**;
- candidate-free exact recurrence: **0.5 exactly**;
- literature pairwise concordance: **0.25–1.0**;
- candidate-free concordance: **0.75 exactly**.

The two standardized yellow trajectories agree on **A down / C up / P down** and differ at F. The supported interpretation remains **transition-class-dependent modular recurrence**, not recurrence of one invariant whole pigment-state package.

### Macroevolutionary realization

Accepted-species nuclear analyses retain non-random visible-colour phylogenetic structure across topology and wild-colour sensitivities, while no individual transition branch survives the strict × dominant colour-coding robustness gate. Thus a **macroevolutionary pattern can be identifiable even when individual historical events and causes are not**.

## Active literature recheck — submission hold

Backward/forward citation chasing on 2026-08-27 identified Luo et al. 2016 (DOI `10.3389/fpls.2015.01257`) as a potentially result-relevant *C. japonica* source. It reports a canonical white-to-red contrast with higher DFR in red and higher FLS in white. Under the existing A/F/C/P mapping this can resolve the literature-side `CJAPONICA:F` cell as **down**, rather than unknown.

Therefore the **literature-conditioned anthocyanin identified set and direct literature/candidate-free overlap must be recomputed under the existing frozen collapse/enumeration rules before the next submission freeze**. The candidate-free five-system measurements and macro results are not reopened by this source.

AJB v0.8 remains the last fully validated hosted artifact, but it is now a **pre-Luo submission checkpoint**, not the file to submit until this recheck is closed.

## Authoritative Paper 1 files

The immutable scientific source remains [`manuscript/PAPER1_AJB_MANUSCRIPT_V0_2.md`](manuscript/PAPER1_AJB_MANUSCRIPT_V0_2.md). Current validated science is generated from that source as **v0.2.1**, so the formal-database update is explicit and reversible rather than silently overwriting v0.2. The active Luo recheck may require the next numbered science freeze.

Current validated contracts:

- [`data/paper1_authoritative_results_v0_2_1.csv`](data/paper1_authoritative_results_v0_2_1.csv) — validated result hierarchy, including M07 literature-axis ascertainment;
- [`data/paper1_main_figure_manifest_v0_2_1.csv`](data/paper1_main_figure_manifest_v0_2_1.csv) — validated Main/Supp figure contract;
- [`data/paper1_fig1_observation_contract_v0_2_1.csv`](data/paper1_fig1_observation_contract_v0_2_1.csv) — validated literature-observation inputs for Fig. 1;
- [`data/paper1_reference_registry_v0_2_1.csv`](data/paper1_reference_registry_v0_2_1.csv) — 16-reference science-source contract;
- [`data/paper1_reference_registry_v0_4.csv`](data/paper1_reference_registry_v0_4.csv) — current 22-reference journal-facing contract before the Luo recheck;
- [`data/micro_accessibility_edge_registry_v0_2.csv`](data/micro_accessibility_edge_registry_v0_2.csv) — validated 11-system/6-cluster literature observation matrix before the Luo recheck;
- [`docs/MICRO_ACCESSIBILITY_V0_2_RESULT.md`](docs/MICRO_ACCESSIBILITY_V0_2_RESULT.md) — formal-database-updated ascertainment result;
- [`docs/PAPER1_BIBLIOGRAPHIC_DB_SEARCH_2026-08-27.md`](docs/PAPER1_BIBLIOGRAPHIC_DB_SEARCH_2026-08-27.md) — database search/screening record;
- [`docs/PAPER1_CHINESE_GREY_LITERATURE_SCREEN_2026-08-27.md`](docs/PAPER1_CHINESE_GREY_LITERATURE_SCREEN_2026-08-27.md) — indexed Chinese/thesis/grey-literature decision layer;
- [`docs/PAPER1_NOVELTY_LITERATURE_AUDIT_2026-08-27.md`](docs/PAPER1_NOVELTY_LITERATURE_AUDIT_2026-08-27.md) and [`docs/PAPER1_NOVELTY_CORE_ATTACK_ADDENDUM_2026-08-27.md`](docs/PAPER1_NOVELTY_CORE_ATTACK_ADDENDUM_2026-08-27.md) — prior-art and novelty boundaries.

The former open-web saturation statement that no new eligible cluster existed is **superseded** by the formal database search that recovered `CSEMISERRATA`.

## Last validated journal-facing route

AJB **v0.8** is the last fully validated upload bundle, documented in [`docs/PAPER1_AJB_UPLOAD_BUNDLE_V0_8_README.md`](docs/PAPER1_AJB_UPLOAD_BUNDLE_V0_8_README.md) and built by `.github/workflows/paper1-ajb-upload-bundle-v0-8.yml`.

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

Because Luo 2016 was discovered after this freeze, **v0.8 must not be described as the final submission file until the literature-side recurrence recheck is complete**.

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

At the programme level, the contribution is framed as a temporal-evolution question: **how repeatable is the generation of flower-colour states through evolutionary history?** The observation audit is what makes that biological question identifiable rather than the endpoint of the paper.

The literature work is now **database-counted and high-recall**, includes an indexed Chinese/thesis decision layer, and has a reproducible citation-chasing workflow. It is still not labelled PRISMA-complete because a formal exhaustive CNKI/Wanfang export, one closed cross-database screening flow, and a final citation-chasing/grey-literature stopping rule remain incomplete.

## Frozen boundaries

- Do **not** infer taxon-level A/F/C/P states from visible flower colour.
- Do **not** equate visible white with a molecular zero state.
- Do **not** claim a definitive white *Camellia* ancestor from the current accepted-species `chun` reconstruction.
- Do **not** assign ecological causes to individual colour-transition branches while event identity is not robust.
- Do **not** treat the non-independent system-level recurrence sensitivity as the primary recurrence result.
- Do **not** add *C. semiserrata* to the candidate-free arm unless auditable public raw reads are located and admitted under the frozen protocol.
- Do **not** restore the obsolete `visible transition -> recurrent whole pathway package -> macro transition` narrative.
- Do **not** restore the historical ecological-driver panel as current Main Fig. 6.
- The term **reactivation/re-expression** remains reserved for cases with both an active→suppressed/absent→active history and evidence that the underlying machinery persisted; otherwise use retention, recruitment, or gain.

## Current execution goal

The active scientific task is now singular:

1. add Luo et al. 2016 to the literature evidence for the existing `CJAPONICA` dependence cluster under the frozen coding rule;
2. recompute literature ascertainment, anthocyanin identified-set bounds, and direct literature/candidate-free overlap with the existing analysis code;
3. if any validated result changes, create the next numbered science/reference/figure/submission freeze and rebuild the AJB bundle;
4. only after that re-freeze, return to final author metadata, archive DOI, and journal-system declarations.

The candidate-free five-system recurrence and macro event-identity analyses are not reopened unless the recomputation itself exposes a separate contract violation.

Issue #94 records the completed core hypothesis test; the active Luo audit is a post-closure literature-completeness correction, not a return to open-ended mechanism hunting.
