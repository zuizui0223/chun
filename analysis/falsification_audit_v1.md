# Falsification audit v1

Status: **three clean supportive radiations + Iris MIXED; Nicotiana HOLD_OBSERVATION_REGIME; external 51-clade panel HOLD_SOURCE_ACCESS; Epimedium formal REFUTATION blocked as HOLD_IDENTIFIABILITY after a post-endpoint validity audit**.

## Already falsified / superseded

The earlier stronger cross-radiation interpretation is no longer the target. `CROSS_RADIATION_STATE_GRANULARITY_V0_3` already establishes:

- shared transition direction: 0/3 comparable Mk systems pass the strong directional gate;
- privileged biological coarse boundary: 0/3 radiations are ENRICHED under the pre-frozen exhaustive-partition rule (Linoideae NOT_ENRICHED; Angraecinae INTERMEDIATE; Antirrhineae NOT_ENRICHED).

Therefore the earlier wording that a coarse ancestral/display or pigment state generally constrains flower-colour evolutionary state space is superseded/refuted at the tested cross-radiation level.

## Surviving positive object before prospective stress tests

Fine-state phylogenetic organization persisted after conditioning on an a priori coarse state in 3/3 independent testable radiations:

- Linoideae — hue within WHITE/non-WHITE conditioning;
- Angraecinae — four-organ colour configuration within primary GREEN/WHITE conditioning;
- Antirrhineae — pigment-class organization within pigment-presence conditioning.

The surviving claim is representation dependence, not a universal direction, ancestral state, causal mechanism, or privileged binary coding.

## Prospective fourth-radiation test: Iris

The Iris endpoint was frozen before computation in `analysis/iris_fine_state_falsification_prefreeze_v1.md`. Exact one-to-one OpenTree admission retained 205/226 taxa (90.7%).

Frozen endpoint results:

- **Primary source-pigment grouping:** SUPPORT — observed minimum changes = 63, null mean = 70.6966, observed/null = 0.8911, `p_lower = 0.0001`.
- **WHITE/non-WHITE sensitivity:** SUPPORT — observed/null = 0.8496, `p_lower = 0.0001`.
- **Single-coarse-only sensitivity:** FAILS the frozen support gate — observed = 53, null mean = 55.4521, observed/null = 0.9558, `p_lower = 0.0308`.

The predeclared classifier therefore returns **MIXED**. This is neither a fourth clean replication nor a refutation.

Frozen Iris result: `analysis/iris_fine_state_falsification_result_v1.json`.

## Prospective fifth-radiation attempt: Nicotiana

The Nicotiana test was frozen in `analysis/nicotiana_fine_state_falsification_prefreeze_v1.md` before supplement inspection or endpoint computation. Source/trait admission produced 21 non-hybrid diploid taxon units with all trait gates passing.

Exact OpenTree admitted 17/21 taxa (80.95%), which passed the frozen >=80% coverage requirement but failed the separately frozen minimum **n >=20** gate. The four rejected TNRS queries could not be rescued without violating exact/unambiguous matching rules. Therefore the biological endpoint was never opened.

Final Nicotiana classification: **HOLD_OBSERVATION_REGIME**.

Frozen Nicotiana result: `analysis/nicotiana_fine_state_falsification_result_v1.json`.

## Broad 51-clade prospective panel: source-access HOLD

A panel rule was frozen before row-level inspection for the public 51-clade / 2960-species flower-colour dataset (`10.5061/dryad.r4xgxd2sc`). Admission was designed to be signal-blind and to include all clades meeting machine-readable tree, n/coverage and state-diversity gates.

The execution environment could retrieve Dryad metadata but not file contents: whole-dataset and file-download routes returned HTTP 401/403. A related Phaidra route was also blocked by service/anti-bot behavior. No row-level flower matrix, tree, admission list, Sankoff score or permutation endpoint was opened.

Final panel classification: **HOLD_SOURCE_ACCESS**. It is not biological evidence in either direction.

Frozen panel result: `analysis/multiclade_51_fine_state_falsification_result_v1.json`.

## Epimedium prospective test: formal REFUTATION, validity HOLD

Epimedium was then chosen because the complete source workbook was already checksum-pinned in-repository and could be re-audited without an external file-download dependency. The source yielded 41 named taxa, 4 inner-sepal codes, 5 spur codes and 7 exact joint organ-colour states. Exact OpenTree admission retained 36/41 taxa (87.8%); all source/state-diversity gates passed.

Before endpoint computation the exact taxon/state records and topology were frozen:

- state-row SHA-256 `63cc336c5748479afa10f66a6bd21961899ac3289a3dd5e56cc54fa048afefb6`;
- OpenTree Newick SHA-256 `7b5001b9787e97cd4ad39b60c3b57075e0ef2b1a78528a429894480641f444f7`.

The prefreeze used exact `SepalC:SpurC` joint state as fine state and two co-primary conditional nulls so that no favorable organ could be selected after inspection:

1. sepal-conditioned;
2. spur-conditioned.

The prospective endpoint mechanically returned **REFUTATION**:

- primary sepal-conditioned: observed = 27, null mean = 27, ratio = 1.0, `p_lower = 1.0`;
- primary spur-conditioned: observed = 27, null mean = 27, ratio = 1.0, `p_lower = 1.0`;
- S9 ingroup sensitivity: both directions observed = null = 22, `p_lower = 1.0`;
- largest-five-source-row deletion: both directions observed = null = 23, `p_lower = 1.0`.

Because every null had `null_min == null_max`, this apparently strong adverse result was subjected to an independent post-endpoint identifiability audit without changing the frozen classifier.

The audit found the cause: the frozen OpenTree is a **complete 36-tip star** — exactly one internal node with degree 36 and zero binary internal nodes. On such a topology the unordered Fitch/Sankoff score is invariant to the allowed conditional rearrangements. All six permutation nulls were degenerate, and multiple deterministic reverse/rotate/sorted within-coarse rearrangements also produced exactly the same scores.

Therefore:

- prospective classifier output: **REFUTATION** — retained unchanged as an audit artifact;
- validity classification: **NON_IDENTIFIABLE_DEGENERATE_NULL**;
- final evidence status: **HOLD_IDENTIFIABILITY**;
- counts as biological refutation: **false**.

Frozen wrapper result: `analysis/epimedium_fine_state_falsification_result_v1.json`.
Identifiability audit run: `34195980857`.

This exposed a missing validity condition in the previous decision rule: n and coverage are insufficient if the topology/statistic/null combination has zero randomization support. Future tests must pass a **non-degenerate-null / topology-informativeness gate** before either support or refutation is admitted.

## Current cross-radiation state

The correct current statement is:

> Fine-state phylogenetic organization is robustly supported in three independent radiations and is present but sensitivity-dependent in a prospectively tested fourth radiation. Additional prospective attempts have so far been limited by tree sample size, source access, or topology/statistic identifiability rather than yielding an admissible biological counterexample. No tested coarse coding is universally privileged, and no universal transition direction is supported.

Counted biological evidence therefore remains **3 supportive + 1 mixed prospective radiation**.

- Nicotiana is not in the biological denominator because its frozen minimum-n gate failed before endpoint opening.
- the 51-clade panel is not in the denominator because source files could not be opened.
- Epimedium is not a biological refutation because the admitted topology is a complete star and the frozen statistic is invariant under its null.

Do **not** report `4/4`; do **not** report Iris as a counterexample; do **not** report Nicotiana or the 51-clade panel as negative biological results; do **not** report the Epimedium mechanical classifier as biological refutation.

Aquilegia remains a cross-level mechanistic admission HOLD and does not refute the macro phenotype-level result.

## Next falsification target

The next independent radiation must pass four gates **before** endpoint interpretation:

1. source files actually retrievable in the execution environment;
2. adequate matched fine/coarse trait n and coverage;
3. machine-readable topology with nontrivial internal resolution;
4. a conditional null under which the frozen statistic demonstrably has non-zero variation before observed assignment is interpreted.

Only after these gates pass should a new prospective Sankoff/permutation endpoint be opened. Iris, Nicotiana and Epimedium must not be re-partitioned or have their frozen rules relaxed post hoc to force cleaner answers.
