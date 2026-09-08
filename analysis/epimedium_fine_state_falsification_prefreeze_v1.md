# Epimedium organ-joint fine-state prospective falsification — pre-freeze v1

Freeze status: **FROZEN AFTER SOURCE/TOPOLOGY ADMISSION, BEFORE ANY SANKOFF SCORE OR PERMUTATION ENDPOINT**.

## Target claim

Test the surviving representation-level claim that phylogenetic organization can remain in a finer flower-colour state after conditioning on a coarser flower-colour representation.

This endpoint is explicitly **organ-representation level**. The source nominal colour codes are not translated post hoc into universal visible-hue, anthocyanin, or pollinator-perceptual categories.

Source: Zhang et al. 2023, DOI `10.3389/fpls.2023.1234148`.

## Frozen source and admission

Source workbook SHA-256:
`057a0aaa603cfa4d9683a2eac75e747cb14bd1294e541feb82483fe6bc160e45`

The source audit reconstructs 41 named taxa with 4 inner-sepal codes, 5 petal/spur codes and 7 observed joint combinations, with no within-source-taxon code variation.

Signal-free access run: `34194812437`.

Exact OpenTree admission retained **36/41 = 87.8%** source taxa. The five rejected source names are frozen in `analysis/epimedium_fine_state_admission_v1.json`; no rejected taxon may be rescued after seeing a biological result.

Frozen topology/source-state identities:
- OpenTree raw Newick SHA-256: `7b5001b9787e97cd4ad39b60c3b57075e0ef2b1a78528a429894480641f444f7`;
- ordered admitted state rows SHA-256: `63cc336c5748479afa10f66a6bd21961899ac3289a3dd5e56cc54fa048afefb6`.

If regenerated source rows or OpenTree topology fail either hash, classify `HOLD_OBSERVATION_REGIME`; do not silently use a changed topology or taxon set.

## Frozen fine state

Fine state is the exact source pair:

`JOINT = SepalC : SpurC`

Observed admitted joint alphabet:

`0:0, 0:1, 1:1, 2:1, 2:2, 2:4, 3:3`.

All seven are nominal source-code combinations. No ordinal distance is assumed.

## Why two co-primary coarse representations

The previous source audit already established that neither organ is information-equivalent to the joint state. To avoid selecting the organ that happens to give a favorable phylogenetic result, **inner sepal and petal/spur are co-primary conditioning representations**.

### Co-primary A — inner-sepal conditioned

Coarse state = source `SepalC` (four nominal states).

Null permutations exchange whole `JOINT` labels only among tips with the same `SepalC`.

This asks whether petal/spur information retained inside the joint state is phylogenetically organized after inner-sepal state is fixed.

### Co-primary B — petal/spur conditioned

Coarse state = source `SpurC` (five nominal states).

Null permutations exchange whole `JOINT` labels only among tips with the same `SpurC`.

This asks whether inner-sepal information retained inside the joint state is phylogenetically organized after petal/spur state is fixed.

Neither co-primary endpoint may be demoted after seeing its result.

## Frozen statistic

For both co-primary endpoints, the observed statistic is the same unordered Sankoff/Fitch minimum number of changes in the seven-state `JOINT` character on the frozen 36-tip topology.

Transition cost:
- 0 if parent and child joint states are equal;
- 1 for any change between different joint states.

Branch lengths are ignored.

## Frozen null and seed

For each co-primary endpoint use **9,999 conditional permutations**.

Master seed: `20260908`.

Use deterministic independent RNG streams derived from the master seed and literal endpoint labels `SEPAL_CONDITIONED` and `SPUR_CONDITIONED` using SHA-256, so results do not depend on Python hash randomization or execution order.

For each endpoint, permute whole joint-state labels within identical coarse groups. Thus the null exactly preserves:
- the topology;
- n=36;
- every fine-state frequency;
- every coarse-state frequency;
- the deterministic mapping from each joint state to its coarse component.

Permutation lower-tail p-value:

`p_lower = (1 + count(null_score <= observed_score)) / 10000`.

Also report null mean, median, 2.5/97.5% quantiles and `observed/null_mean`.

Individual co-primary SUPPORT requires both:
- `p_lower <= 0.01`;
- `observed/null_mean < 1`.

## Frozen classification

Let A = sepal-conditioned endpoint and B = spur-conditioned endpoint.

- `SUPPORTIVE_ALIGNMENT`: A SUPPORT and B SUPPORT.
- `MIXED`: exactly one of A/B SUPPORT.
- `REFUTATION`: neither A nor B SUPPORT **and** both `observed/null_mean >= 1.0`.
- `ADVERSE_BUT_NOT_REFUTATION`: neither A nor B SUPPORT, but at least one has `observed/null_mean < 1.0`.
- `HOLD_OBSERVATION_REGIME`: frozen admission/topology/source hash fails, n<30, or a required endpoint cannot be computed as specified.

This deliberately makes support harder than in a single chosen coarse representation. A null or adverse result is retained; the organ is not swapped after inspection.

## Frozen sensitivities

### S1 — source S9 ingroup subset

The article's S9 morphological summary contains 34 ingroup rows. Restrict the frozen 36-tip endpoint to taxa that join the source S9 ingroup under the already-audited exact/explicit source crosswalk.

Admit S1 only if:
- at least 25 frozen-tree tips remain;
- at least 5 joint states remain;
- both conditioning directions retain at least one coarse group containing >=2 joint states.

Run the same two conditional permutation endpoints, 9,999 each, with deterministic endpoint labels suffixed `_S9`.

If S1 does not meet these gates, record `NOT_ADMITTED`; do not count that as biological failure.

### S2 — remove five largest-source-row taxa

To ensure heavily measured source taxa are not driving a taxon-level result, remove the five admitted taxa with the largest `source_rows` in S4; ties are broken lexicographically by the frozen taxon name. This deletion rule is determined only from measurement counts, never from topology or signal.

Admit S2 only if n>=30 and at least 5 joint states remain. Run both conditioning directions unchanged.

### S3 — resolved-bifurcation sensitivity is prohibited

Do **not** arbitrarily resolve OpenTree polytomies. The primary statistic is evaluated on the frozen induced topology exactly as returned. Random or signal-based bifurcation of polytomies is not an admissible robustness analysis.

## Interpretation boundary

This endpoint can establish or challenge a repeated **representation-level phylogenetic organization** result across an organ-structured colour character. It cannot by itself establish:
- a white ancestral state;
- a universal hue direction;
- a universal molecular mechanism;
- pollinator or climatic causation;
- temporal modularity between organs.

A SUPPORTIVE result would be an additional independent macro representation-level alignment. A REFUTATION would be a genuine matched counterexample to the surviving recurrence claim. MIXED remains evidence that detectability depends on coarse representation.

## Prohibited post-hoc moves

After computation starts, do not:
- rescue any of the five rejected source taxa;
- change the 36-tip topology or admitted taxa;
- translate source codes into visible hue categories;
- choose only sepal or only spur as the primary endpoint;
- merge/split joint states;
- alter the 9,999 permutation count, seed, or p<=0.01 support gate;
- use source molecular data to reclassify an organ state;
- count S1/S2 as independent radiations.

This file plus `analysis/epimedium_fine_state_admission_v1.json` is the prospective decision record.