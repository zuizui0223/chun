# Antirrhineae unconditional resolution-profile schema hold v0.1

## Decision

`HOLD_SCHEMA_NO_SOURCE_DEFINED_THREE_LEVEL_NESTING_INTERMEDIATE_FINE_COLLAPSE`

Do **not** run a new unconditional coarse/intermediate/fine AUC for Antirrhineae under the current source schema.

## Why this was checked

After Petunieae supplied the first completed biochemical cross-representation exact profile, the moderator programme requires a second independent non-visible nested representation. Antirrhineae was checked because its CC0 source bundle and 1,000-tree posterior ensembles are already acquired and audited in CHUN, so it could in principle provide an additional system without a new external source dependency.

The existing Antirrhineae result is a different estimand: a **conditional fine-state organization test** that shuffles pigment class within coarse pigment-presence groups. It cannot simply be counted as an unconditional exact-profile observation.

## Source-native state space

The Ellis & Field source README defines `face_phenotype` as:

- `0` — unpigmented;
- `1` — anthocyanin-pigmented;
- `2` — yellow;
- `3` — double-pigmented.

The source bundle also contains `colour_descriptions.xls`, but the README identifies this as the **verbatim taxonomic colour descriptions and citations** used to derive the pigment coding. It is provenance text, not a second structured biological state layer.

The existing exact-join result shows:

### Monomorphic primary frame — 152 tips

- state 0: 21;
- state 1: 68;
- state 2: 63;
- state 3: 0.

### Polymorphic sensitivity frame — 179 tips

- state 0: 29;
- state 1: 83;
- state 2: 67;
- state 3: 0.

## Why a three-resolution ladder is not source-defined

Two levels are unambiguous:

1. **coarse** — unpigmented (`0`) versus pigmented (`1/2/3`);
2. **fine** — the four source-native pigment-pattern codes (`0/1/2/3`).

A unique intermediate level is not provided by the source. One could choose, for example, to group double-pigmented (`3`) with anthocyanin (`1`) or with yellow (`2`). Both are biologically intelligible projections of the same two pigment components, but the source does not privilege one as the intermediate hierarchy.

Choosing one after prior inspection would therefore be an analyst-defined recoding, not a source-defined resolution ladder.

There is also an empirical collapse: state `3` occurs zero times in both exact-join frames used by the existing comparative analyses. Consequently, either proposed three-category intermediate grouping would reduce on the observed tips to the same `0/1/2` partition as the source-native fine coding. The nominal three levels would contain only two distinct observed partitions.

## Why `colour_descriptions.xls` is not used as a rescue

Using exact verbatim colour-description strings as fine states would measure taxonomic wording/citation language, not a reproducible biological state space. Normalizing those strings into colour categories would require a new analyst-defined coding rule after the descriptions are already known. Neither is admitted merely to create a second cross-representation observation.

## Consequence

Antirrhineae does **not** increment the unconditional exact-profile training count and does not unlock the representation-type moderator.

This does not weaken the prior Antirrhineae conditional result. The existing finding that anthocyanin/yellow organization remains stronger than a within-coarse null is retained under its original conditional estimand.

No new patristic-distance profile, AUC, permutation null or winner class is computed here.

## Next gate

Resume Antirrhineae as an unconditional exact-profile system only if an independent, source-defined nested state layer can be recovered without outcome-dependent recoding. Otherwise the second non-visible profile must come from another system such as the already-frozen Ruellia, Rhododendron or Iochrominae routes once their source/provenance holds are resolved.

Camellia Paper 1 remains unchanged.
