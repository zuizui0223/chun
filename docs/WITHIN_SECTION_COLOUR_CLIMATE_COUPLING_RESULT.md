# Within-section visible-colour × climate coupling screen

## Question

Does a visible A/W difference mark greater climatic divergence when coarse historical background is held approximately constant?

This is a pre-phylogenetic screening analysis. Traditional sections are used only as a history proxy and are not assumed monophyletic.

## Input and statistic

Input: the exact-taxonomy Fan2026 × GBIF × CHELSA 50-species table, excluding the known duplicate alias `Camellia kissi`.

Only traditional sections containing both A and W states are used: `Camellia` and `Paracamellia`.

To avoid the known range-tail provenance/estimator problem, the primary distance uses only:

- BIO1 median;
- BIO6 median;
- BIO1 IQR.

Each axis is standardized across the exact species set. For every within-section species pair, Euclidean climatic distance is calculated. The statistic is:

`mean climatic distance of different-colour A-W pairs - mean climatic distance of same-colour A-A/W-W pairs`.

A/W labels are permuted within section 100,000 times, preserving observed colour counts in each section.

## Result

Across 26 species (A=14, W=12):

- same-colour pairs: n=133, mean distance = **2.35668**;
- different-colour A-W pairs: n=24, mean distance = **1.88475**;
- difference = **-0.47193**;
- one-sided test for `different-colour pairs are farther apart`: **P=0.92889**;
- two-sided permutation P = **0.18486**.

The direction is the opposite of a general `visible colour divergence -> climatic niche divergence` prediction, although the two-sided deviation is not significant.

The direction is also consistent in the two available history proxies:

- `sect. Camellia`: same-colour mean 2.22167 vs different-colour 1.86112;
- `sect. Paracamellia`: same-colour mean 2.54815 vs different-colour 1.91268.

## Connection to existing `chun` results

This result strengthens a pattern already visible at three levels:

1. **micro/mechanistic layer:** pigment deployment is repeatedly accessible through regulatory/flux changes (8/8 independence clusters; red-direction anthocyanin recurrence 6/6);
2. **species-level macro layer:** A versus W does not show a robust genus-wide thermal-position/cold-edge difference after provenance and estimator uncertainty are addressed;
3. **within-history proxy layer (this analysis):** A/W state differences do not identify unusually large climatic divergence even within the only two traditional sections containing both states.

Therefore the current data do not support the simple chain:

`molecular accessibility -> visible A/W transition -> climatic niche divergence`.

Instead they increase the priority of the competing chain:

`molecular accessibility -> pigment/spectral variation -> lineage/ecological filtering -> reproductive/sensory function and persistence`,

with direct abiotic effects retained only as branch-specific conditional hypotheses.

## Hypothesis consequences

- `H_COLD_UNIVERSAL`: remains not supported.
- `H_VISIBLE_HUE_MACRO_NULL`: strengthened for current thermal screens.
- `H_LINEAGE_PERMISSIVITY`: strengthened as an explanation for the contrast between strong micro accessibility and narrow macro persistence of A.
- `H_REPRODUCTIVE_NICHE`: priority increases because visible colour divergence remains weakly coupled to climate while same-hue reproductive/sensory collisions are already documented.
- `H_COLD_CONDITIONAL`: remains open; this screen cannot reject rare branch-specific climate-linked transitions.
- `H_REACT_ORDER`: remains unresolved because no primary dated nuclear branch history is yet admitted.

## Claim boundary

This is not a nuclear phylogenetic result and does not estimate transition timing. It cannot establish that pollinators caused colour evolution. It establishes only that, under the current coarse history control, **visible A/W differences are not associated with greater thermal niche divergence**.

Reproducer: `scripts/analyze_within_section_colour_climate_coupling.py`.
Workflow: `Camellia within-section colour-climate coupling`.
