# chun

**Evolutionary-time analysis of flower-colour variation using *Camellia* as a comparative model system.**

## Programme position

`chun` is the **evolutionary-time arm** of a broader programme on the spatiotemporal organization of flower-colour variation. Its central question is:

> **When similar flower-colour states are repeatedly generated through evolutionary time, how much of the underlying pigment-network transition is replayed?**

The complementary [`fcp`](https://github.com/zuizui0223/fcp) project is the **geographic-space arm**, asking whether intraspecific flower-colour variation is maintained as local coexistence or sorted into geographic differentiation.

The shared conceptual decomposition is:

`generation through time -> establishment/persistence -> organization in space`

Across the programme, **flower-colour variation** is the umbrella term. **Polymorphism** is reserved for documented within-population coexistence. See [`docs/FLOWER_COLOUR_VARIATION_TEMPORAL_PROGRAM.md`](docs/FLOWER_COLOUR_VARIATION_TEMPORAL_PROGRAM.md).

## Scope

`chun` is *Camellia*-only. East Asian *Cirsium* work is maintained separately in [EAzami](https://github.com/zuizui0223/EAzami). Historical cross-family scaffolds remain in Git history but are not current analysis inputs.

## Current Paper 1

**Working title:** *Repeated generation of flower-colour states does not replay one pigment-state programme in Camellia*

Current frozen layers:

- **science:** Paper 1 **v0.2.2**;
- **temporal framing:** **v0.3.2**;
- **AJB submission route:** **v0.9**;
- **science reference contract:** 17 DOI rows (`paper1_reference_registry_v0_2_2.csv`);
- **journal-facing reference contract:** 25 DOI rows (`paper1_reference_registry_v0_5.csv`).

The molecular state is represented on four pathway-wide transcript-state axes:

- **A** — anthocyanin branch;
- **F** — flavonol branch;
- **C** — carotenoid core;
- **P** — proanthocyanidin diversion.

Visible hue never fills a missing molecular axis, and expected direction or statistical significance never determines whether a candidate-free measurement is retained.

## Why *Camellia*

*Camellia* is used as a **natural temporal comparative system**, not as the endpoint of the question. The genus combines repeated red/pink, white and yellow visible states, multiple public molecular contrasts, dense nuclear phylogenomic resources, and heterogeneous reproductive environments including insect-, bird- and mixed-pollination contexts.

A white-like ancestral baseline is biologically plausible from independent genus-scale work, but `chun` does **not** equate white with a molecular zero and does **not** claim a definitive white ancestor from its own accepted-species reconstruction, which retains W/Y uncertainty. The intended formulation is a **white-like visible baseline with retained pigment-network capacity**.

Pollinator diversity is likewise model-system context rather than a branch-causal assignment. Visibly red *C. japonica* and *C. rusticana* recruit different pollinators and differ in pollinator-visible signals, while golden *C. petelotii* receives substantial service from both sunbirds and honeybees. These contrasts make visible colour, molecular implementation and ecological function separable rather than interchangeable.

## Current validated results — science v0.2.2

### Literature observation layer

After formal database search and citation chasing, the literature matrix contains **12 biological systems in 6 dependence clusters**. Luo et al. (2016; DOI `10.3389/fpls.2015.01257`) resolves the literature-side `CJAPONICA:F` direction as down within the existing `CJAPONICA` cluster.

Published A/F/C/P coverage is:

- system level: **10/5/1/3**; exact A-axis enrichment **P=0.0015277863**;
- after dependence collapse: **5/4/1/2**; exact A-axis enrichment **P=0.078125**.

Thus reporting is clearly nonuniform across published biological-system records, but **A-specific enrichment is not retained below 0.05 after dependence collapse**. Observation nonuniformity is therefore an identification issue supporting the temporal repeatability analysis, not the biological headline.

### Anthocyanin gain

Three independent matched dependence clusters are compared under literature-selected and standardized candidate-free observation.

- literature exact whole-signature recurrence: **0.333–1.0**;
- candidate-free exact recurrence: **0.333 exactly**;
- literature pairwise A/F/C/P concordance: **0.333–1.0**;
- candidate-free pairwise concordance: **0.333–0.5**;
- direct literature/candidate-free agreement: **2/6** resolved comparable cells.

The four direct conflicts are `CJAPONICA:A`, `CJAPONICA:F`, `CRETICULATA:P`, and `CSIN_WHITE_PINK:A`. `CJAPONICA:A` remains near-flat in the standardized measurement and must not be described as a strong reversal.

### Yellow development

Two independently frozen five-stage trajectories use the same estimator.

- literature exact whole-signature recurrence: **0.5–1.0**;
- candidate-free exact recurrence: **0.5 exactly**;
- literature pairwise concordance: **0.25–1.0**;
- candidate-free pairwise concordance: **0.75 exactly**;
- direct literature/candidate-free agreement: **4/5**.

The standardized trajectories share **A down / C up / P down** and differ at F. The supported interpretation is therefore **transition-class-dependent modular recurrence**, not no recurrence and not replay of one invariant complete A/F/C/P package.

### Macroevolutionary realization and event identity

Accepted-species wild colour remains locally phylogenetically structured across independent nuclear-topology and trait-coding sensitivities. The robust headline is local nearest-same-colour conservatism, not global same-state MPD and not A-specific lineage clustering.

Individual historical events are less identifiable:

- strict wild-colour scenario: **0** strong robust branches;
- dominant-colour sensitivity: **1** W→A branch;
- shared strict × dominant robust branches: **0**.

Thus **pattern-level persistence is identifiable while individual historical event identity and branch-specific ecological causation are not** under the current public hard-state data.

## Biological conclusion

The current Paper 1 conclusion is:

> **Flower-colour variation can be repeatedly generated through evolutionary time without replaying one invariant complete pigment-state programme. Molecular repeatability is modular and transition-class dependent. Realised visible states remain locally phylogenetically structured, but individual transition events are not robustly identifiable. Generation, establishment/persistence and event identity must therefore be separated.**

Observation-regime analysis is the identification strategy that makes the molecular replay question estimable; it is no longer the biological endpoint of the paper.

## Current authoritative files

The immutable historical manuscript source remains [`manuscript/PAPER1_AJB_MANUSCRIPT_V0_2.md`](manuscript/PAPER1_AJB_MANUSCRIPT_V0_2.md). Current science and framing are generated as versioned layers rather than silently overwriting that source.

Current contracts include:

- [`data/paper1_authoritative_results_v0_2_2.csv`](data/paper1_authoritative_results_v0_2_2.csv) — authoritative result hierarchy;
- [`data/paper1_main_figure_manifest_v0_2_2.csv`](data/paper1_main_figure_manifest_v0_2_2.csv) — Main/Supp figure dependency contract;
- [`data/paper1_fig1_observation_contract_v0_2_2.csv`](data/paper1_fig1_observation_contract_v0_2_2.csv) — current Fig. 1 literature-observation inputs;
- [`data/paper1_fig2_recurrence_intervals_v0_2_2.csv`](data/paper1_fig2_recurrence_intervals_v0_2_2.csv) — Luo-updated molecular identified sets;
- [`data/paper1_fig2_direct_overlap_v0_2_2.csv`](data/paper1_fig2_direct_overlap_v0_2_2.csv) — Luo-updated direct overlap;
- [`data/paper1_reference_registry_v0_2_2.csv`](data/paper1_reference_registry_v0_2_2.csv) — 17-reference science contract;
- [`data/paper1_reference_registry_v0_5.csv`](data/paper1_reference_registry_v0_5.csv) — 25-reference journal-facing contract;
- [`docs/PAPER1_LUO2016_LITERATURE_RECHECK_RESULT.md`](docs/PAPER1_LUO2016_LITERATURE_RECHECK_RESULT.md) — result-changing citation-chase recheck;
- [`docs/PAPER1_CITATION_CHASE_SCREEN_2026-08-27.md`](docs/PAPER1_CITATION_CHASE_SCREEN_2026-08-27.md) — backward/forward citation-chasing screen;
- [`docs/PAPER1_CHINESE_GREY_LITERATURE_SCREEN_2026-08-27.md`](docs/PAPER1_CHINESE_GREY_LITERATURE_SCREEN_2026-08-27.md) — Chinese/thesis/grey-literature decision layer;
- [`docs/PAPER1_NOVELTY_LITERATURE_AUDIT_2026-08-27.md`](docs/PAPER1_NOVELTY_LITERATURE_AUDIT_2026-08-27.md) — prior-art boundary;
- [`scripts/build_paper1_temporal_framing_v0_3_2.py`](scripts/build_paper1_temporal_framing_v0_3_2.py) — temporal framing builder.

## Current AJB submission route — v0.9

AJB **v0.9** is the current and only active submission bundle route. It is documented in [`docs/PAPER1_AJB_UPLOAD_BUNDLE_V0_9_README.md`](docs/PAPER1_AJB_UPLOAD_BUNDLE_V0_9_README.md) and built by [`.github/workflows/paper1-ajb-upload-bundle-v0-9.yml`](.github/workflows/paper1-ajb-upload-bundle-v0-9.yml).

Hosted run **33067022836** passed all steps. Independent final-artifact QA confirmed:

- **51/51** manifest-listed files matched size and SHA256, with no missing or unregistered files;
- **25/25 reference DOIs** matched the journal-facing registry;
- AJB structured Abstract = **221 words**;
- Fig. 1 uses **10/5/1/3**, **5/4/1/2**, and **P=0.078125** without annotation collision;
- Fig. 2 uses the Luo-updated anthocyanin literature interval and **2/6** direct overlap;
- Appendix S1 tracks science v0.2.2; S3/S4 track Luo-updated recurrence/overlap; S2 and S5–S8 retain their frozen inputs;
- candidate-free, yellow and macro change flags are all false;
- Word/DOCX structural checks passed: continuous line numbering, sequential page numbers, double spacing, one-inch margins, Times New Roman 12 pt body and page-number field;
- the final hosted DOCX rendered to **26 pages** and passed visual QA; a decorative Word Title-style border found in an earlier v0.9 artifact was removed and the final page 1 was reverified, while pages 2–26 remained pixel-identical to the previously inspected clean render.

v0.8 and earlier upload routes are **historical provenance only** and are not current submission routes.

## Literature-audit status

The prior-art/evidence search is now **database-counted, high-recall and citation-chased**. It includes:

- fixed OpenAlex/Crossref/PubMed searches;
- Chinese-language/thesis/grey-literature screening;
- backward/forward citation chasing from eight major seed references;
- an explicit manual eligibility/independence screen.

It is **not labelled PRISMA-complete** because an exhaustive CNKI/Wanfang export, one closed cross-database dedup/full-text flow, and a final formal grey-literature stopping rule remain incomplete.

## Novelty boundary

Do **not** claim priority for:

- the general fact that the same phenotype can arise through different mechanisms;
- pathway-level or modular flower-colour convergence;
- candidate/discovery-method effects on apparent repeatability;
- partial identification or identified sets as a general statistical idea;
- phylogenetic ancestral-event uncertainty or model identifiability;
- measurement-process dependence as a general biological concept;
- the first micro-to-macro study of *Camellia* flower colour.

The retained contribution is empirical: **the same auditable public *Camellia* systems are placed in one common A/F/C/P state space, incomplete literature states are bounded explicitly, standardized remeasurement tests how much multivariate molecular replay survives, and that result is separated from macroevolutionary pattern robustness and a stricter historical-event identity gate.**

## Frozen boundaries

- Do **not** infer taxon-level A/F/C/P states from visible flower colour.
- Do **not** equate visible white with a molecular zero state.
- Do **not** claim a definitive white *Camellia* ancestor from the current accepted-species reconstruction.
- Do **not** assign ecological causes to individual colour-transition branches while event identity is not robust.
- Do **not** treat system-level literature recurrence sensitivity as the primary recurrence estimator.
- Do **not** add *C. semiserrata* to the candidate-free arm unless auditable public raw reads are located and admitted under the frozen protocol.
- Do **not** restore the obsolete `visible transition -> recurrent whole pathway package -> macro transition` narrative.
- **Reactivation/re-expression** remains reserved for cases with active→suppressed/absent→active history plus evidence that the machinery persisted; otherwise use retention, recruitment or gain.

## Remaining submission inputs

The reproducible science/framing/bundle route is closed. Remaining AJB submission blockers are human metadata or final archive state:

- author list and order;
- affiliations;
- corresponding-author details and ORCID;
- acknowledgments and funding;
- CRediT author contributions;
- permanent archive DOI;
- conflict-of-interest declaration in the journal submission system.

Until those are supplied, the generated manuscript deliberately retains explicit placeholders rather than inventing metadata.
