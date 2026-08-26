# Yellow two-cluster candidate-free recurrence v0.1 — result

## Status

**COMPLETE.** The pre-outcome decision rule in `docs/YELLOW_TWO_CLUSTER_RECURRENCE_GATE_V0_1.md` remains unchanged. This file records the result obtained after that gate was frozen.

Frozen successful raw-result runs:

- `CNITIDISSIMA`: *Camellia nitidissima* ordered S1–S5 trajectory, run `32803242174`;
- `CPERPETUA`: *C. perpetua* ordered S1–S5 trajectory, run `32834693855`;
- `CPERPETUA` archive mapping audit: `32826721885`;
- unified five-system / 20-row actual-results recurrence: `32929846096`.

The cross-cluster estimator is the same in both systems: OLS slope across all five prespecified stage means, oriented from earlier/paler to later/more-yellow development. Exact 5! stage-order P values are retained as uncertainty metadata and never select direction.

## C. nitidissima trajectory

Candidate-free ordered S1–S5 signature:

- A: slope **-0.2406**, down, exact P = 0.0833;
- F: **+0.1240**, up, P = 0.6667;
- C: **+0.1567**, up, P = 0.1667;
- P: **-0.4503**, down, P = 0.0333.

Signature: **A down / F up / C up / P down**.

## C. perpetua trajectory

All 15 prespecified runs (S1–S5 × 3) passed the frozen raw-data workflow. Salmon mapping min/mean/max was **79.2054 / 81.4782 / 84.0166%**.

Candidate-free ordered S1–S5 signature:

- A: slope **-0.5817**, down, exact P = 0.0167;
- F: **-0.1691**, down, P = 0.3167;
- C: **+0.1792**, up, P = 0.0667;
- P: **-0.6156**, down, P = 0.0167.

Signature: **A down / F down / C up / P down**.

The separately preregistered within-system S1→S3 yellow-onset contrast remains a biological within-system result and is not used as the cross-cluster recurrence estimator. The cross-cluster result uses the matched five-stage slope exactly as frozen before outcome inspection.

## Frozen pre-outcome decision rule and observed branch

The gate specified:

- 4/4 directional matches → full whole-signature recurrence;
- 1–3/4 directional matches → axis-specific reuse without exact whole-signature recurrence;
- unresolved axes → partial-identification bounds.

Observed CN-versus-CP agreement is **3/4 axes**:

| axis | CNITIDISSIMA | CPERPETUA | match |
|---|---|---|---|
| A | down | down | yes |
| F | up | down | no |
| C | up | up | yes |
| P | down | down | yes |

Therefore the pre-frozen decision branch is:

> **axis-specific / modular reuse without exact whole A/F/C/P signature recurrence.**

## Literature versus candidate-free identified set

### Literature regime on the same two clusters

Three cluster × axis cells are unresolved, giving 27 exact completions.

- exact-signature recurrence: **0.5–1.0**;
- pairwise A/F/C/P concordance: **0.25–1.0**;
- pairwise identified-set width: **0.75**.

Complete whole-signature recurrence is therefore admissible under the selected literature representation.

### Candidate-free regime

All eight cluster × axis cells resolve, giving one completion.

- exact-signature recurrence: **0.5 exactly**;
- pairwise A/F/C/P concordance: **0.75 exactly**;
- pairwise identified-set width: **0.0**;
- width reduction relative to literature: **0.75**.

The standardized regime therefore removes complete whole-signature recurrence from the admissible set while retaining high modular concordance across A, C and P.

## Direct literature-versus-candidate-free overlap

Across cells independently resolved in both regimes:

- comparable cells: **5**;
- agreement: **4/5 = 0.80**;
- conflict: **1/5**.

The only conflict is `CPERPETUA`, F axis: literature **up** versus candidate-free **down**.

This is an important control. The candidate-free pipeline does not mechanically reverse selected literature directions: yellow-development agrees with directly comparable literature cells 80% of the time, yet standardized measurement of the previously missing axes is sufficient to reject exact whole-package recurrence.

## Inference

The yellow result does **not** support “no recurrence.” It supports a more specific model:

> **Repeated yellow development reuses a substantial subset of pigment-state directions (A down, C up, P down), but not one invariant whole A/F/C/P package.**

Together with the anthocyanin-gain result, the molecular evidence now distinguishes **whole-package recurrence** from **modular recurrence**. Whole-package recurrence is not supported in either canonical transition class, while the amount and identity of reused modules differ by class.
