# Falsification audit v1

Status: **Iris prospective test completed as MIXED; Nicotiana fifth-radiation attempt completed as HOLD_OBSERVATION_REGIME before endpoint opening**.

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

The Iris endpoint was frozen before computation in `analysis/iris_fine_state_falsification_prefreeze_v1.md`. The publisher workbook contains 226 unique analysis taxa with no flower-colour missingness. Exact one-to-one OpenTree admission retained 205/226 taxa (90.7%), so the predeclared >=80% observation gate passed.

Frozen endpoint results:

- **Primary source-pigment grouping:** SUPPORT — observed minimum changes = 63, null mean = 70.6966, observed/null = 0.8911, `p_lower = 0.0001`.
- **WHITE/non-WHITE sensitivity:** SUPPORT — observed/null = 0.8496, `p_lower = 0.0001`.
- **Single-coarse-only sensitivity:** FAILS the frozen support gate — observed minimum changes = 53, null mean = 55.4521, observed/null = 0.9558, `p_lower = 0.0308`.

The predeclared classifier therefore returns **MIXED**.

This is not a fourth clean replication and not a refutation. Fine-state organization is clearly detectable in Iris under the primary and binary coarse-conditioning representations, but the signal weakens below the frozen significance gate when taxa spanning multiple pigment classes are removed.

Frozen Iris result: `analysis/iris_fine_state_falsification_result_v1.json`.

## Prospective fifth-radiation attempt: Nicotiana

A second prospective test was frozen in `analysis/nicotiana_fine_state_falsification_prefreeze_v1.md` before supplement inspection or endpoint computation. The test unit was source-defined non-hybrid diploid Nicotiana, with eight spectral categories as the fine alphabet and explicit petal chlorophyll/chloroplast presence/absence as the primary coarse layer.

Source and trait admission succeeded:

- stable publisher supplement `.doc` SHA-256 `45bbedb8a1ef419cf0128a3a6df63fd364d61a50402f610dcd196c70f8c14959`;
- S1/S2 each contain 62 source rows and S4 contains 26 hybrid-origin rows;
- all eight source spectral categories are recoverable;
- 21 non-hybrid diploid taxon units have a joint fine/coarse observation regime;
- definite coarse classes contain 5 chlorophyll-absent and 16 chlorophyll-present taxa;
- the pre-tree diversity/size gates therefore pass.

The topology gate did not pass completely. The article supplement supplies the final plastid majority-rule tree only as a document figure, not as machine-readable Newick/NEXUS, so the predeclared exact OpenTree fallback was used. It admitted 17/21 taxa (80.95% coverage), satisfying the >=80% coverage gate but failing the separately frozen **minimum n >=20** gate.

The four exact-TNRS exclusions are not safely recoverable under the frozen rules:

- `Nicotiana attenuata` returns two score-1 exact hits pointing to different OTT ids (`N. attenuata` OTT 882065 and a synonym hit resolving to `N. tabacum` OTT 222787);
- `Nicotiana undulata` returns two score-1 exact hits pointing to different OTT ids (`N. undulata` OTT 210478 and a synonym hit resolving to `N. suaveolens` OTT 806473);
- `Nicotiana obtusifolia var. obtusifolia` has zero exact hits;
- `Nicotiana obtusifolia var. palmeri` has zero exact hits.

Relaxing exactness, discarding explicit infraspecific rank, or choosing among distinct exact OTTs would violate the prefreeze. Therefore the biological Sankoff/permutation endpoint was **not run**.

Final Nicotiana classification: **HOLD_OBSERVATION_REGIME**. This is an observation-regime failure, not a counterexample and not support.

Frozen Nicotiana result: `analysis/nicotiana_fine_state_falsification_result_v1.json`.

## Current cross-radiation state

The correct current statement is:

> Fine-state phylogenetic organization is robustly supported in three independent radiations and is present but sensitivity-dependent in a prospectively tested fourth radiation. A fifth prospective candidate reached source/trait admission but remained unadjudicated because its frozen minimum tree-sample gate failed. No tested coarse coding is universally privileged, and no universal transition direction is supported.

Counted biological evidence remains **3 supportive + 1 mixed prospective radiation**. Nicotiana is a prospective HOLD and is not added to either numerator or denominator of the biological recurrence claim.

Do **not** report `4/4`; do **not** report Iris as a counterexample; do **not** report Nicotiana as a negative biological result.

Aquilegia remains a cross-level mechanistic admission HOLD. It is not evidence against the macro fine-state result because the required matched radiation-wide molecular observation regime is absent.

## Next falsification target

The next independent radiation should be selected for a machine-readable source topology and a sufficiently large matched fine/coarse trait intersection **before** endpoint computation. It should count as a genuine counterexample only if the matched coarse-conditioned fine-state test fails with adequate predeclared observation coverage and all admitted sensitivities also fail. Iris and Nicotiana should not be re-partitioned or have their admission rules relaxed post hoc to force cleaner answers.
