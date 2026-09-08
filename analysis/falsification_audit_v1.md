# Falsification audit v1

Status: **first prospective fourth-radiation test completed; outcome MIXED**.

## Already falsified / superseded

The earlier stronger cross-radiation interpretation is no longer the target. `CROSS_RADIATION_STATE_GRANULARITY_V0_3` already establishes:

- shared transition direction: 0/3 comparable Mk systems pass the strong directional gate;
- privileged biological coarse boundary: 0/3 radiations are ENRICHED under the pre-frozen exhaustive-partition rule (Linoideae NOT_ENRICHED; Angraecinae INTERMEDIATE; Antirrhineae NOT_ENRICHED).

Therefore the earlier wording that a coarse ancestral/display or pigment state generally constrains flower-colour evolutionary state space is superseded/refuted at the tested cross-radiation level.

## Surviving positive object before the prospective test

Fine-state phylogenetic organization persisted after conditioning on an a priori coarse state in 3/3 independent testable radiations:

- Linoideae — hue within WHITE/non-WHITE conditioning;
- Angraecinae — four-organ colour configuration within primary GREEN/WHITE conditioning;
- Antirrhineae — pigment-class organization within pigment-presence conditioning.

The surviving claim is representation dependence, not a universal direction, ancestral state, causal mechanism, or privileged binary coding.

## Prospective fourth-radiation test: Iris

The Iris endpoint was frozen before computation in `analysis/iris_fine_state_falsification_prefreeze_v1.md`. The publisher workbook contains 226 unique analysis taxa with no flower-colour missingness. Exact one-to-one OpenTree admission retained 205/226 taxa (90.7%), so the predeclared >=80% observation gate passed.

Frozen endpoint results:

- **Primary source-pigment grouping:** SUPPORT — observed minimum changes = 63, null mean = 70.6966, observed/null = 0.8911, `p_lower = 0.0001`.
- **WHITE/non-WHITE sensitivity:** SUPPORT — observed/null = 0.8496, `p_lower = 0.0001`.
- **Single-coarse-only sensitivity:** FAILS the frozen support gate — observed minimum changes = 53, null mean = 55.4521, observed/null = 0.9558, `p_lower = 0.0308`.

The predeclared classifier therefore returns **MIXED**.

This is not a fourth clean replication and not a refutation. Fine-state organization is clearly detectable in Iris under the primary and binary coarse-conditioning representations, but the signal weakens below the frozen significance gate when taxa spanning multiple pigment classes are removed. The fourth radiation therefore shows that the recurrence itself is representation/sample-composition dependent at a finer level than the earlier 3/3 summary implied.

## Current cross-radiation state

The correct current statement is:

> Fine-state phylogenetic organization is robustly supported in three independent radiations and is present but sensitivity-dependent in a prospectively tested fourth radiation. No tested coarse coding is universally privileged, and no universal transition direction is supported.

Do **not** report `4/4`, and do **not** report Iris as a counterexample. The clean 3/3 recurrence has been stress-tested and becomes **3 supportive + 1 mixed prospective radiation**.

Aquilegia remains a cross-level mechanistic admission HOLD. It is not evidence against the macro fine-state result because the required matched radiation-wide molecular observation regime is absent.

## Next falsification target

A further independent radiation should be frozen before endpoint computation and should count as a genuine counterexample only if a matched coarse-conditioned fine-state test fails with adequate observation coverage and all predeclared admitted sensitivities also fail. Iris itself should not be re-partitioned post hoc to force a cleaner answer.

Frozen Iris result: `analysis/iris_fine_state_falsification_result_v1.json`.
