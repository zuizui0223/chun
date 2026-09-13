# Continuous pigment quantity prospective candidate screen — v0.1

## Status

`NO_QUALIFIED_UNUSED_RADIATION_AFTER_BOUNDED_SCREEN`

This screen was run **after** the prospective rule in `data/continuous_pigment_quantity_prospective_gate_v0_1.json` had been merged to `main` by PR #251. The gate is not edited here.

## Frozen question

For an unused independent flower-colour radiation, does continuous total floral pigment quantity map most strongly to the predeclared `OUTPUT_CONTROL` target family (`LATE_OUTPUT` or `PATHWAY_REGULATION`) rather than `EARLY_CORE` or `BRANCH_COMPOSITION`?

The primary test requires >=20 matched taxa, direct continuous numeric total floral pigment quantity, all four molecular target classes in flower/petal tissue on the same taxa, a branch-length phylogeny and public numeric data. Project-side target-class outcomes cannot be inspected before admission.

## Screen universe

The bounded screen contains **18 candidate frames from 17 unique source publications**, below the frozen cap of 20 publications.

### 1. Pre-existing atlas universe — 11 unused clades

Every unused clade in the pre-existing v0.5 cross-clade atlas was checked first using only metadata already frozen before this quantity gate:

- Antirrhineae;
- *Hydrangea* sect. Cornidia;
- Linoideae;
- *Polygonatum* sect. Verticillata;
- Angraecinae;
- *Silene* Physolychnis;
- *Euonymus*;
- *Nicotiana*;
- *Linanthus*;
- *Acer*;
- *Dalechampia*.

None contains the required same-taxon continuous-quantity + four-target-class molecular frame. These are admission failures, not biological negatives.

### 2. External plausibility screen — 7 additional frames

Seven source systems surfaced as the strongest plausible external candidates under flower-colour quantity / transcriptomic / metabolomic searches:

- 30 *Rhododendron* species — `10.1111/plb.12649`;
- four alpine *Rhododendron* species — `10.1093/treephys/tpab160`;
- ten *Ruellia* species — `10.1186/s12862-021-01955-x`;
- ten *Achimenes* species — `10.7717/peerj.8778`;
- five *Chiloglottis* species — `10.3389/fpls.2022.976283`;
- one experimental *Dendrobium* hybrid — `10.1093/aob/mcac103`;
- three *Paeonia lactiflora* cultivars — `10.3389/fpls.2026.1907085`.

No project-side target-class fit, AICc ranking or effect estimate was computed for any of these sources during admission screening.

## Closest candidate

The 30-species *Rhododendron* chemistry study is the closest source to the frozen phenotype requirement. It provides direct quantitative anthocyanin measurements across 30 species and public supporting tables. However, it does **not** provide the required same-taxon flower/petal molecular matrix spanning the four predeclared target classes. It is therefore `UNQUALIFIED` before any target-class outcome analysis.

The four-species *Rhododendron* multi-omics study contains both molecular and metabolomic information but fails the pre-frozen >=20 matched-taxon requirement. All other external candidates fail at the taxon-frame or direct continuous-quantity stage before a decisive target comparison is possible.

## Decision

No unused independent radiation currently passes the frozen gate.

This does **not** support the biological statement that continuous pigment quantity lacks a recurrent molecular target architecture. It establishes a data-availability boundary:

> Existing public comparative flower-colour datasets do not presently provide an unused >=20-taxon radiation with direct continuous total pigment quantity, all four predeclared same-taxon molecular target classes and a branch-length phylogeny under the frozen gate.

The prospective quantity hypothesis therefore remains **untested in a new independent radiation**.

## Stop rule

Do not relax the >=20-taxon threshold, replace chemical quantity with ordinal colour intensity, drop molecular target classes, reuse a calibration radiation as if independent, or continue open-ended candidate hunting.

Reopen this gate only if a newly released or previously unavailable source already satisfies all frozen admission fields **before** project-side target-class outcome inspection.

## What can proceed without violating the gate

A separate retrospective/context layer may summarize already known quantity mechanisms in Iochrominae, Petunieae, Antirrhinum or experimental systems. Those sources cannot be counted as the missing prospective independent radiation and cannot upgrade the prospective gate.

## Paper boundary

Camellia Paper 1 remains unchanged. The candidate-screen result belongs to the post-Paper-1 cross-radiation programme.
