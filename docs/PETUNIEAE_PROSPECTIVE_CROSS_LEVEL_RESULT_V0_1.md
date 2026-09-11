# Petunieae prospective cross-level result — v0.1

## Decision

**`PETUNIEAE_PROSPECTIVE_BRIDGE_MIXED`**

The pre-frozen two-axis PASS gate was not met. The hue/hydroxylation component passed strongly, whereas the preregistered raw pigment-amount component did not select a distinct late/regulatory molecular subspace with the required AICc separation. Consequently **prospective full-bridge replication is not admitted**.

Paper 1 science remains unchanged.

## Prospective provenance

The gate was committed before source acquisition and analysis code:

1. `6b2f9b5dd1da990e1599302affb644f64d4567cb` — **Freeze Petunieae prospective cross-level gate before OSF inspection** — 2026-09-08 02:48:47 UTC.
2. `10ba13620ddee802c2a96a4c4821021149a72392` — **Add Petunieae OSF processed-source acquisition** — 2026-09-08 02:49:42 UTC.
3. `34df90ed5a54d36f7043c355d42890da14d6b3ae` — **Implement frozen Petunieae prospective PGLS gate** — 2026-09-08 03:10:52 UTC.
4. `3dd8aa65023daabda342661010c3f098b1de6c80` — **Execute frozen Petunieae prospective analysis in CI** — 2026-09-08 03:11:22 UTC.

The original successful hosted execution was run `34182646549`, job `101924667736`. The exact result recovered from artifact `10039433170` is frozen in `data/petunieae_prospective_cross_level_v0_1.json`; the workflow now performs an exact numerical replay check and uses full git history to verify the ordering above.

## Coverage

- processed source rows before source-defined outgroup exclusion: **60**;
- Petunieae taxa after excluding `BROWALLIA_AMERICANA_BROW`: **59**;
- anthocyanin-positive taxa available for the hue axis: **53**;
- source tree join: **60/60** before outgroup exclusion;
- all four frozen molecular subspaces were testable.

Coverage items 1–3 of the pre-frozen gate therefore passed.

## Hue / hydroxylation axis — PASS

The preregistered abundance-weighted anthocyanidin hydroxylation index selected:

- best subspace: **`BRANCHING_HUE`**;
- AICc = **26.61293763**;
- next-best subspace: `EARLY_CORE`, AICc = **38.21576699**;
- best-vs-next AICc margin = **11.60282936**;
- null AICc = **38.34002462**;
- `BRANCHING_HUE` improvement relative to null = **11.72708699 AICc units**.

This cleanly satisfies the pre-frozen hue criterion. Within this radiation, anthocyanidin hue/hydroxylation is prospectively aligned with the branching/hue molecular subspace rather than early-core, late-output, or regulatory expression summaries.

## Raw pigment-amount axis — FAILS its component gate

The preregistered primary response was the **raw summed anthocyanin mass fraction**. It selected:

- best subspace: **`BRANCHING_HUE`**;
- AICc = **120.99361154**;
- `LATE_OUTPUT` AICc = **121.43797960**;
- best-vs-next AICc margin = **0.44436806**;
- null AICc = **120.93638460**.

Thus the best model was not `LATE_OUTPUT` or `REGULATORY`, did not exceed the next-best subspace by >=2 AICc units, and did not improve on the null. The amount-axis criterion is therefore false under the response fixed before source-value inspection.

## Source-method log-amount sensitivity — informative but non-upgrading

Using the source-author-style sensitivity `log(total_anthocyanin*100+1)` gives:

- best subspace: **`LATE_OUTPUT`**;
- best-vs-next margin = **2.80766099 AICc**;
- improvement relative to null = **6.87691264 AICc**.

This direction is consistent with the retrospective expectation for pigment amount/depletion, but the transform was not the preregistered primary response. It therefore **cannot upgrade** the frozen classification. The contrast between the raw and log amount responses is retained as evidence that the amount-axis subspace assignment is response-definition sensitive in this dataset.

## Cross-radiation consequence

Before Petunieae, the matched high-level bridge had retrospective alignment in two independent radiations:

- Iochrominae;
- Cape Erica.

Petunieae is the first prospectively specified test under that bridge definition. It provides a **strong prospective component replication for the hue axis**, but not a prospective replication of the full two-axis separation. Therefore:

- retrospective matched-definition alignments: **2 radiations**;
- prospective full-bridge PASS: **0**;
- prospective partial/MIXED tests: **1 (Petunieae)**;
- prospectively supported component: **hue → `BRANCHING_HUE`**.

The result strengthens the evidence that visible hue can map to a specific molecular subspace across radiations, but it does not establish a universal phenotype-axis-to-distinct-subspace law.

## Claim boundary

Do not recode this result as PASS. Do not use the log-amount sensitivity to replace the frozen raw-amount response. Do not infer universal causal genes, common ecological drivers, or transition direction. The correct conclusion is a pre-specified prospective **MIXED** result with a strong hue-axis positive and a non-supportive raw amount axis.
