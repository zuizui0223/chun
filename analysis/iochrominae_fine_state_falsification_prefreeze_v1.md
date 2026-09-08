# Iochrominae fine-state falsification — endpoint pre-freeze v1

Freeze status: **FROZEN BEFORE COMPUTATION OR INTERPRETATION OF THE IOCHROMINAE CONDITIONAL FINE-STATE ENDPOINT**.

Outcome note (added after source-only execution, without changing any frozen rule): **HOLD_TRAIT_SOURCE**. The biological endpoint was never opened. Frozen result: `analysis/iochrominae_fine_state_falsification_result_v1.json`.

## Role of this test

Test unit: **Iochrominae**.

This is an independent biological radiation relative to the three counted macro systems (Linoideae, Angraecinae, Antirrhineae), but it is **not a fully blind candidate-selection exercise**: Iochrominae was already inspected in the repository for a retrospective phenotype-to-molecular bridge. The present document therefore freezes a new macro endpoint before its computation and must be reported as a **retrospectively selected independent radiation with a prospectively frozen endpoint**, not as a pristine prospective discovery.

The question is the surviving cross-radiation claim only:

> Does fine flower-pigment state retain phylogenetic organization after conditioning on an a priori coarse pigment-presence state?

No transition direction, ancestral state, pollinator cause, or shared molecular mechanism is tested here.

## Frozen trait source and phenotype representation

Primary phenotype source: Larter et al. (2018), *Convergent Evolution at the Pathway Level: Predictable Regulatory Changes during Flower Color Transitions*, Molecular Biology and Evolution, DOI `10.1093/molbev/msy117`.

The source sampled 28 Iochrominae species and reports HPLC-resolved primary anthocyanidin state. The frozen fine alphabet is:

- `DELPHINIDIN`
- `CYANIDIN`
- `PELARGONIDIN`
- `NONE`

The frozen coarse map is biological and source-motivated rather than chosen from the endpoint:

- `PIGMENTED`: DELPHINIDIN, CYANIDIN, PELARGONIDIN
- `UNPIGMENTED`: NONE

If a machine-readable source record explicitly assigns more than one allowed primary anthocyanidin state to a taxon, preserve the complete allowed set. Do not force a single state using the phylogenetic result.

### Trait-source admission rule

Use a row-level publisher/Dryad table or another machine-readable source-derived table whose taxon-state mapping can be checksum-pinned. The article text and plotted figure may be used to audit identities and definitions, but **do not infer a complete 28-row state table from raster colour alone**.

If the complete taxon-state mapping cannot be recovered without manual visual assignment, stop as `HOLD_TRAIT_SOURCE` before endpoint computation.

## Frozen primary topology

Primary topology source: Smith & Kriebel (2018), *Convergent evolution of floral shape tied to pollinator shifts in Iochrominae (Solanaceae)*, Evolution, DOI `10.1111/evo.13416`, Dryad DOI `10.5061/dryad.5jn7b`.

The published archive is reported to contain a 36-ingroup-species BEAST maximum-clade-credibility (MCC) tree and a posterior sample of 100 trees. The MCC tree is the frozen primary topology. The 100 posterior trees are the frozen topology-uncertainty sensitivity.

A Smith & Baum (2006) TreeBASE study (`TB2:S1553`, legacy `S1498`; DOI `10.3732/ajb.93.8.1140`) may be used only as an **older source-native topology sensitivity** if it independently passes the same taxon-coverage and identifiability gates. It cannot replace the 2018 MCC tree because of the observed endpoint.

Branch lengths are not used by the primary statistic.

## Frozen taxon matching

1. Keep the Larter source taxon string as the immutable trait identifier.
2. Normalize only deterministic orthographic differences: whitespace, underscore/space, terminal author strings, and source-documented spelling corrections.
3. Synonym replacement is allowed only when supported by a taxonomic/source crosswalk fixed before endpoint computation; no trait-result-dependent synonym choice is allowed.
4. Require one-to-one trait row ↔ tree tip mapping. Any collision is excluded as topology-unresolved; no member is selected using pigment state.
5. Record the admitted and rejected taxa and the reason for every rejection before scoring.

## Frozen admission gates

Open the biological endpoint only if all are true:

1. complete machine-readable trait mapping is recovered and checksum-pinned;
2. a machine-readable 2018 MCC topology is recovered and checksum-pinned;
3. at least 80% of the 28 source taxa are represented one-to-one in the MCC tree–trait intersection (`n >= 23`), and absolute admitted `n >= 20`;
4. every admitted tip has at least one frozen fine state;
5. the admitted `PIGMENTED` class contains at least three distinct fine anthocyanidin states and at least 10 tips;
6. the admitted tree has nontrivial internal resolution and is not a complete star/pure terminal fan;
7. the conditional null has demonstrably non-zero randomization support under the frozen statistic before the observed assignment is interpreted.

Failure of gates 1–5 => `HOLD_OBSERVATION_REGIME` (or the more specific `HOLD_TRAIT_SOURCE` / `HOLD_SOURCE_ACCESS`).

Failure of gates 6–7 => `HOLD_IDENTIFIABILITY`.

Neither HOLD class is biological evidence in either direction.

## Frozen identifiability audit

Before interpreting the observed score, use the admitted fine-state count vector and coarse membership counts but **not the observed taxon-to-fine-state arrangement** to generate at least 512 deterministic-seed conditional rearrangements within coarse class.

Seed: `20260908`.

Compute the frozen statistic for those rearrangements. Require:

- at least two distinct null scores; and
- `null_max > null_min`.

Also record tree diagnostics: admitted tips, number of internal nodes, number of binary internal nodes, maximum internal degree, and whether the tree is a complete star.

If the null is score-invariant, stop at `HOLD_IDENTIFIABILITY`; do not mechanically label the system supportive or refuting.

## Frozen primary statistic and null

Statistic: unordered Sankoff/Fitch minimum number of changes among the four frozen fine states on the admitted MCC topology.

Null: 9,999 conditional permutations. Exchange complete fine-state records only among tips with the same frozen coarse class (`PIGMENTED` or `UNPIGMENTED`). This preserves coarse state and fine-state counts exactly. Because `UNPIGMENTED` contains the single fine state `NONE`, inferential randomization is expected to occur within `PIGMENTED`; this is part of the frozen design and is not to be altered after endpoint inspection.

Observed assignment is permutation zero.

Primary outputs:

- `observed_minimum_changes`;
- `null_min`, `null_max`, `null_mean`, and null quantiles;
- `observed_over_null_mean`;
- `p_lower = (1 + count(null <= observed)) / 10000`.

## Frozen primary decision

Primary MCC support requires both:

- `p_lower <= 0.01`; and
- `observed_over_null_mean < 1`.

Otherwise the MCC primary endpoint is `PRIMARY_FAIL`.

A primary fail alone is not sufficient for a final cross-radiation refutation because the 2018 study supplies posterior topology uncertainty.

## Frozen posterior-tree sensitivity

If the published 100-tree posterior sample is recovered, retain every source tree whose induced tree passes the same n/coverage and identifiability gates. For each admitted posterior tree, run 999 conditional permutations with a deterministic tree-index-derived seed and apply the same support criterion (`p_lower <= 0.01` and ratio < 1`).

Define `posterior_support_fraction` over admitted posterior trees.

Final topology-robust classification:

- `SUPPORTIVE_ALIGNMENT`: MCC supports and `posterior_support_fraction >= 0.80`;
- `REFUTATION`: MCC fails and `posterior_support_fraction <= 0.20`;
- `MIXED`: all other cases with an adjudicable posterior sample;
- `SUPPORTIVE_BUT_TOPOLOGY_UNRESOLVED`: MCC supports but the posterior sample cannot be adjudicated for source/access reasons;
- `ADVERSE_BUT_NOT_REFUTATION`: MCC fails but the posterior sample cannot be adjudicated for source/access reasons.

If fewer than 20 posterior trees pass the frozen admission/identifiability gates, topology sensitivity is considered unavailable rather than adverse.

## Older TreeBASE sensitivity

If `TB2:S1553` supplies a machine-readable source tree with at least 80% trait coverage, `n >= 20`, one-to-one matching, and a non-degenerate conditional null, run the same primary test as a named older-topology sensitivity. Otherwise record `NOT_ADMITTED` with the failed gate. This sensitivity can make a result `MIXED` if materially contradictory, but failure to admit it is not biological evidence.

## Cross-radiation counting rule

Iochrominae counts as one additional independent biological radiation only for `SUPPORTIVE_ALIGNMENT`, `REFUTATION`, or `MIXED` after all mandatory gates above are satisfied.

Because candidate selection was retrospective, report it separately from the fully prospective Iris stress test even if its endpoint is clean.

## Prohibited post-endpoint moves

After the first observed endpoint is computed, do not:

- change the four-state fine alphabet;
- move anthocyanidins between coarse classes;
- redefine `NONE`;
- alter n/coverage or identifiability thresholds;
- choose a different tree because it gives a preferred result;
- omit taxa because they weaken support;
- alter the p-value threshold;
- substitute visual/raster phenotype guesses for the frozen machine-readable trait-source gate;
- count posterior trees as independent radiations.

This pre-freeze must precede any Iochrominae conditional fine-state score used for biological interpretation.
