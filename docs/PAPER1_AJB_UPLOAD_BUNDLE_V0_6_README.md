# Paper 1 AJB upload bundle v0.6 — current v0.2 science

This bundle supersedes v0.5 **as the journal-facing submission route**. The v0.5 ecological-integration bundle remains historical provenance and must not be rebuilt as the current manuscript because its Main Fig. 6 and registry hierarchy predate the candidate-free Paper 1 v0.2 result.

## Scientific source of truth

The v0.6 bundle is generated directly from:

- `manuscript/PAPER1_AJB_MANUSCRIPT_V0_2.md`;
- `data/paper1_authoritative_results_v0_2.csv`;
- `data/paper1_main_figure_manifest_v0_2.csv`;
- `data/paper1_reference_registry_v0_2.csv`.

No v0.1 result registry is allowed to define the submission claim hierarchy.

## Current Main figures

- **Figure 1** — observation-to-realization framework and observation-regime contract.
- **Figure 2** — five candidate-free A/F/C/P systems, anthocyanin identified-set contraction, and yellow modular recurrence.
- **Figure 3** — accepted-taxonomy and wild-colour evidence attrition.
- **Figure 4** — accepted-species nuclear-topology concordance.
- **Figure 5** — topology-robust local colour conservatism and explicitly demoted macro claims.
- **Figure 6** — pattern without robust event identity and the cross-scale synthesis.

The ecological-driver synthesis is retained as filtering/persistence context in Supporting Information; it is **not** restored as Main Figure 6.

## Supporting Information

The bundle contains eight AJB-style appendices:

- **Appendix S1** — authoritative v0.2 result registry;
- **Appendix S2** — five-system candidate-free A/F/C/P signatures;
- **Appendix S3** — literature versus candidate-free recurrence identified sets;
- **Appendix S4** — direct literature/candidate-free overlap;
- **Appendix S5** — accepted-species wild-colour evidence registry;
- **Appendix S6** — ecological effect-size context with claim ceilings;
- **Appendix S7** — sequence/copy-aware molecular implementation support;
- **Appendix S8** — ecological filtering/persistence boundary.

The old root-state / state-specific-clustering / legacy-event Fig. S1–S3 set is not the current v0.2 Supplementary figure contract.

## Bundle gates

The workflow must:

1. validate the v0.2 authoritative registry and local source references;
2. build the submission-clean manuscript directly from current v0.2;
3. reproduce all six current Main figures from frozen v0.2 source tables;
4. build the two current registry-backed Supplementary figures;
5. reject stale v0.1 registry references, ecological Main Fig. 6 language, internal repository paths, and legacy Fig. S3 from the submission manuscript;
6. produce a SHA256 manifest for every generated upload/provenance file.

## Human inputs still required

The generated manuscript intentionally retains explicit placeholders for author list/order, affiliations, corresponding-author details, and the versioned archive DOI. Contributions, funding, acknowledgments, and conflict statements should be supplied according to the final author/journal metadata before upload.
