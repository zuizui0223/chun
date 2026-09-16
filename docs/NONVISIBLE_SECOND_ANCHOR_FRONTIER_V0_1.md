# Non-visible second-anchor frontier v0.1

## Current state

The unconditional exact-profile programme still contains **30 completed biological units**: 28 standardized visible-colour clades, one retrospective biochemical unit (Petunieae), and the prospective mixed Iris unit.

This is enough replication to establish substantial profile heterogeneity, but it is **not enough representation diversity to identify a biochemical-versus-visible moderator**. Petunieae remains the only completed biochemical exact-profile observation. If Petunieae is held out under leave-one-out validation, the training fold contains zero biochemical examples.

A second non-visible candidate has now been executed without post-hoc rescue:

### Solanaceae red 27 — executed, structural HOLD

Frozen source/tree gate:

`PASS_ARCHIVED_TREEBASE_S16617_OBJECT_CROSSWALK_FROZEN`

Outcome terminal state:

`HOLD_INSUFFICIENT_COMMON_FRAME_OR_STATE_VARIATION`

The archived TreeBASE S16617 source tree supplied 25 exact source/tree matches. Of these, 24 had complete chemistry after outcome opening. The preregistered joint carotenoid × anthocyanidin-composition fine representation produced ten observed fine states with counts 1–4. Because **every fine state was below the frozen minimum of 5 taxa**, the common retained frame was 0 tips. No AUC, permutation p-value, or winner was computed.

This is not a negative biochemical profile and does not count as a second completed biochemical unit. Relaxing the support threshold or merging states after inspection is prohibited for the primary result.

Therefore the next gate remains one additional independent non-visible exact-profile unit that survives its frozen common-frame/state-variation gate.

## Remaining candidate frontier

### 1. Iochrominae — highest leverage if source bytes become accessible

Current terminal state:

`HOLD_DRYAD_SOURCE_BYTES_STILL_UNAVAILABLE_PROFILE_UNCOMPUTED`

Dryad DOI: `10.5061/dryad.p5dq84v`.

Frozen source objects:

- `Larter et al 2019 Dvdy Iochrominae development evolution DATA.rar`
  - file id `108456`
  - size `3,054,999` bytes
  - MD5 `76b46e384fb7c9bf1ef3fbd7d1e5d2f0`
- `README_for_Larter et al 2019 Dvdy Iochrominae development evolution DATA.txt`
  - file id `108458`
  - size `4,072` bytes
  - MD5 `2e4a251725ad4c13975fc09481da302d`

The public article establishes a 28-species biochemical/phylogenetic comparative panel, but CHUN has not opened the Dryad row-level profile source for this new estimand. No resolution-profile AUC has been calculated.

The preferred unlock is authenticated recovery of the exact frozen Dryad source bytes. Do not substitute manually assembled outcome data.

### 2. Ruellia

`HOLD_AUTHORITATIVE_2023_TREE_BYTES_OR_EXACT_RECONSTRUCTION_SOURCE_UNAVAILABLE_OUTCOMES_UNOPENED`

The biochemical source is available, but the exact author-used timed tree is not publicly recoverable. The source comparative tree derives from the Manzitto-Tripp & Daniel 2023 ddRAD phylogeny, but a newly reconstructed tree is not the frozen source tree and is not substituted.

### 3. Rhododendron

`HOLD_SOURCE_ACCESS_STILL_BLOCKED_OUTCOMES_UNOPENED`

A deterministic nested biochemical hierarchy was frozen, but the Wiley chemistry supplement and exact Dryad primary-tree payload remain inaccessible through the tested public routes. Chemistry outcomes remain unopened.

### 4. Antirrhineae

`HOLD_SCHEMA_NO_SOURCE_DEFINED_THREE_LEVEL_NESTING_INTERMEDIATE_FINE_COLLAPSE`

The source-native states are `0=unpigmented`, `1=anthocyanin`, `2=yellow`, `3=double-pigmented`. State 3 is absent from both existing exact-join frames, so any analyst-defined intermediate grouping collapses to the observed fine partition. The source colour-description workbook is taxonomic-description provenance rather than an independent structured fine-state ontology. The existing conditional-hierarchy PASS remains valid for its different estimand.

### 5. Cape Erica

Not admitted as the second exact-profile unit because the existing mechanistic bridge is an eight-taxon derived panel, below the current radiation-wide exact-profile frame.

## Stop rule

Do not broaden candidate hunting simply to obtain a second non-visible winner. Reopen the representation-moderator gate only when:

1. one of the blocked authoritative sources becomes available; or
2. a new independent source already satisfies the frozen exact-profile admission fields before its outcome is inspected.

Do not fit a biochemical-versus-visible moderator with one completed biochemical observation. Do not count source/schema/common-frame holds as biological negatives. Do not weaken the Solanaceae support rule after seeing its fragmentation. Do not reclassify Petunieae as prospective.

Camellia Paper 1 remains unchanged.
