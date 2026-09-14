# Rhododendron 30-species biochemical resolution-profile preregistration — v0.1

## Purpose

Add an independent **biochemical-composition representation** to the exact resolution-profile training programme. This is not a literature-blinded held-out test; the CHUN state hierarchy and estimator are frozen before row-level anthocyanin values are ingested.

Trait source: Du et al. 2018, DOI `10.1111/plb.12649`.

Primary phylogeny source: Dryad DOI `10.5061/dryad.8cz8w9grq`, frozen file `1_WP_RAxML.tre` (whole-plastome RAxML tree; reported source tree has 161 Rhododendron species). No alternative tree may be selected after chemistry outcomes are opened.

## Frozen hierarchy

The primary phenotype axis stays entirely within anthocyanin composition:

1. **coarse:** any of the seven source anthocyanins present vs none;
2. **intermediate:** three-bit aglycone-class presence pattern `CY / DP / MV`;
3. **fine:** seven-bit source-compound presence pattern.

The seven source compounds and deterministic aglycone mapping are frozen in `data/rhododendron30_biochemical_resolution_mapping_v0_1.csv`.

Presence is defined as source quantitative content `> 0`; exact zero is absence and source missingness remains missing. Concentration magnitude, visible flower-colour category, CIELAB coordinates and flavonols are outside the primary estimand.

## Pre-outcome admission gate

Before row-level chemistry values are read, only source identities/schema, species identifiers and primary-tree tips/branch lengths may be inspected. Require at least 20 exact normalized trait-species/tree-tip matches and complete nonroot branch lengths. Otherwise stop as `HOLD_CROSSWALK_OR_TREE_COVERAGE`.

No automatic synonym substitution or favourable-tree switching is allowed.

## Primary estimator

If admitted, apply the same estimator as Iris and Flower-clades-51:

- one common retained-tip frame for all resolutions;
- fine states represented by fewer than five retained tips are removed from the common frame;
- at least 20 common tips and at least two states at every resolution;
- negative patristic distance predicts pairwise same-state status;
- ROC AUC;
- 9,999 joint triplet permutations with seed `20260913`.

Terminal profile classes and the no-post-hoc-upgrade rule are unchanged.

## Claim boundary

Completion would add one cross-representation biochemical training radiation to the 28-clade standardized visible-colour batch plus Iris. It does not by itself establish a moderator and does not alter Camellia Paper 1.
