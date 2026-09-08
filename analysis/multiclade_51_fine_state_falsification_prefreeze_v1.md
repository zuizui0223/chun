# 51-clade flower-colour fine-state falsification panel — prospective pre-freeze v1

Freeze status: **FROZEN BEFORE DOWNLOADING `final_dataset.csv`, BEFORE OPENING ANY TREE FILE, AND BEFORE COMPUTING ANY PHYLOGENETIC SIGNAL ENDPOINT FROM THIS DATASET**.

## Question

Does the surviving representation-level result — residual phylogenetic organization at fine flower-colour resolution after conditioning on an a priori coarse flower-colour representation — recur across a broad external panel of independent angiosperm clades?

This is a prospective external-panel falsification, not a search for one favorable fifth radiation.

Source dataset: Sinnott-Armstrong M., Maier L., Smith S.D. & Dellinger A.S. (2025 Dryad / 2026 AJB), *Flower clades and fruit clades: Trade-offs in color diversification across angiosperms*, Dryad DOI `10.5061/dryad.r4xgxd2sc`, article DOI `10.1002/ajb2.70146`.

Only public dataset metadata were inspected before this freeze. Metadata state that the dataset contains `final_dataset.csv` plus `trees.zip`, covering 51 source-defined clades and 2960 species, with flower colour coded into eight human-perceived categories. No row-level trait assignments, tree topology, clade-specific colour counts, transition counts, or new signal statistic were inspected before this freeze.

## No signal-based candidate selection

All source-defined clades that pass the frozen observation/admission gates below enter the panel. No clade may be selected or removed using Sankoff score, permutation p-value, observed/null ratio, published flower-versus-fruit lability class, or any other signal result.

The source paper's labels such as `flower clade` / `fruit clade` are prohibited as admission criteria and are not used in the endpoint.

## Frozen fine alphabet

Use the eight source flower-colour categories exactly as documented by Dryad metadata:

`BLACK_DARK, BLUE_PURPLE, GREEN, ORANGE, PINK, RED, WHITE, YELLOW`.

Permitted deterministic parser normalization is limited to case, surrounding whitespace, spaces versus underscores/hyphens, and the literal source slash in `black/dark` or `blue/purple`. Any non-empty source flower-colour token outside these eight categories causes a schema HOLD for the affected source layer; it is not recoded after seeing a result.

Fruit colour is retained only for source-integrity QC and future separate analyses. It is not used to select clades and is not part of the primary flower-colour endpoint.

## Frozen primary coarse representation

Primary coarse coding is the same binary representation already used as a cross-system sensitivity elsewhere in the programme:

- `WHITE`: fine state `WHITE`;
- `NON_WHITE`: all seven other fine states.

The primary question is therefore whether the identity of a non-white hue remains phylogenetically organized after the binary WHITE/non-WHITE representation is held fixed.

## Frozen clade admission gates

A source-defined clade enters the primary panel if and only if all are true before any signal statistic is computed:

1. exactly one machine-readable phylogeny in `trees.zip` can be deterministically associated with that source clade;
2. tree tips are unique after deterministic label normalization;
3. trait species identifiers are unique within the clade after the same deterministic normalization, or exact duplicate rows are demonstrably identical in flower colour and may be collapsed without choosing among conflicting states;
4. tree–trait matched tips `n >= 30`;
5. tree–trait overlap is at least 80% of the smaller of the source tree-tip count and source trait-row count for that clade;
6. at least 5 matched tips are `WHITE`;
7. at least 15 matched tips are `NON_WHITE`;
8. the matched `NON_WHITE` tips contain at least 3 distinct fine states;
9. no tip or clade is removed because of its contribution to the phylogenetic signal statistic.

If fewer than 10 source clades pass these gates, classify the panel `HOLD_OBSERVATION_REGIME` and do not interpret a cross-clade biological endpoint.

## Frozen label matching boundary

The source dataset is expected to use `genus_species` identifiers. Before signal computation, a source-only parser audit must freeze the exact label transformation required to join CSV rows and tree tips.

Allowed transformations without reopening this pre-freeze are purely syntactic and lossless: surrounding whitespace, quote removal, repeated whitespace, underscore/space conversion, and case normalization for comparison while preserving original labels. Infraspecific epithets may be retained if present on both sides. Taxonomic synonym substitution, fuzzy matching, genus replacement, manual nearest-tip assignment, or color-informed matching is prohibited in the primary panel.

If a clade cannot meet the gates under this boundary, it is a clade-level observation HOLD.

## Frozen statistic

For each admitted clade, compute the unordered Sankoff/Fitch minimum number of changes for the eight-state flower-colour character on the source machine-readable topology.

Branch lengths are not used by this statistic.

Panel primary statistic:

`T_panel = sum_c minimum_changes_c`

across all admitted clades `c`.

## Frozen null

Use 9,999 conditional permutations, seed `20260908`.

Within each admitted clade, exchange whole fine-state labels only among tips with the identical primary coarse state (`WHITE` or `NON_WHITE`). This preserves per-clade topology, tip count, WHITE/non-WHITE counts, and all eight fine-state frequencies.

For each permutation index, independently permute each admitted clade using a deterministic RNG stream derived from the frozen master seed plus clade identifier, then sum the clade scores to obtain the joint panel null statistic.

Primary outputs:

- number of source clades and admitted clades;
- for each clade: matched n, state counts, observed minimum changes, null mean, observed/null mean, lower-tail permutation p-value;
- panel observed sum;
- panel null mean and quantiles;
- panel observed/null mean;
- panel lower-tail permutation p-value `p_lower = (1 + count(null <= observed)) / 10000`;
- median per-clade observed/null ratio and the number of clades with ratio < 1, reported descriptively rather than used for clade admission.

## Frozen primary panel decision

Primary panel support requires both:

- `panel_p_lower <= 0.01`;
- `panel_observed_over_null_mean < 1`.

Classification after admissible sensitivities:

- `SUPPORTIVE_ALIGNMENT`: primary panel supports and no material predeclared panel sensitivity contradicts it;
- `REFUTATION`: primary panel fails, the equal-clade sensitivity also fails in the same direction, and the median admitted clade observed/null ratio is `>= 1`;
- `MIXED`: material disagreement between primary and predeclared sensitivities, or primary failure while the median clade ratio remains `< 1`;
- `ADVERSE_BUT_NOT_REFUTATION`: primary is adverse but a required robustness layer cannot be adjudicated;
- `HOLD_OBSERVATION_REGIME`: fewer than 10 admitted clades or primary source/tree/trait admission is inadequate.

A panel failure is not retroactively allowed to alter the earlier Iris, Linoideae, Angraecinae, or Antirrhineae endpoint definitions.

## Frozen sensitivities

### S1 — equal-clade weighting

Prevent the largest clades from dominating the summed-change statistic. For each admitted clade define its null mean from the same 9,999 permutations. Use

`T_equal = mean_c(score_c / null_mean_c)`.

Construct its empirical null from the same permutation matrix. Support requires lower-tail `p <= 0.01` and observed `T_equal < 1`.

### S2 — largest-clade deletion

Remove the single admitted clade with the largest matched n (ties broken lexicographically by immutable source clade identifier) and repeat the primary summed-change panel test with no other change.

### S3 — achromatic/chromatic coarse coding

Repeat only in clades that independently satisfy the primary n/coverage gates and have enough within-group state diversity under:

- `ACHROMATIC`: `WHITE`, `BLACK_DARK`;
- `CHROMATIC`: `BLUE_PURPLE`, `GREEN`, `ORANGE`, `PINK`, `RED`, `YELLOW`.

For this sensitivity require at least 5 matched tips in each coarse group and at least 3 distinct fine states in at least one group. If fewer than 10 clades remain, record this sensitivity `NOT_ADMITTED` rather than a biological failure.

### S4 — three-way hue coarse coding

Repeat under the predeclared representation:

- `ACHROMATIC`: `WHITE`, `BLACK_DARK`;
- `WARM`: `ORANGE`, `PINK`, `RED`, `YELLOW`;
- `COOL`: `BLUE_PURPLE`, `GREEN`.

A clade enters S4 only if it passes the primary n/coverage gates, at least two coarse groups contain >=5 tips, and at least one coarse group contains >=3 distinct fine states. If fewer than 10 clades remain, record `NOT_ADMITTED`.

## Prohibited post-hoc moves

After row-level data or a topology is inspected, do not:

- choose one clade because it gives a favorable or unfavorable result;
- use the source paper's flower/fruit-lability classification to include or exclude clades;
- alter the `n >= 30`, 80%, WHITE>=5, NON_WHITE>=15, or >=3 non-white-state gates;
- merge or split the eight fine states based on observed clustering;
- replace WHITE/non-WHITE as the primary coarse representation;
- relax exact syntactic tree/trait joining because a clade is scientifically attractive;
- count sensitivity codings as independent radiations;
- lower the support threshold after seeing the panel result.

This file is the prospective decision record for the external 51-clade falsification panel.