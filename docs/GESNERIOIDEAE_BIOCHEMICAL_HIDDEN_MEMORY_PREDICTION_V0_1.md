# Gesnerioideae biochemical hidden-memory prediction — v0.1

## New estimand, old HOLD preserved

The earlier Gesnerioideae three-resolution test remains `HOLD_SCHEMA_SOURCE_AXES_NOT_NESTED` because pigment chemistry and visible reflectance cross-cut.

This is a **different, newly frozen two-level biochemical estimand**. At freeze time CHUN has not opened row-level chemistry values for this target analysis.

## Frozen hierarchy

Fine state is the exact presence/absence pattern across 13 source-measured individual compounds, in the fixed source-column order:

Pelargonidin-3-rutinoside; Pelargonidin-7-glucoside; Pelargonidin-3-sambubioside; Cyanidin-3-rutinoside; Cyanidin-3-glucoside; Peonidin-3-rutinoside; Delphinidin-3-glucoside; Delphinidin-rhamnose-glucose; Malvidin-3-rutinoside; Apigenidinin-5-glucoside; Luteolidinin-5-glucoside; Trihydroxymethoxyl flavylium-glucuronide; Unknown glycosylated anthocyanin.

Detection rule: numeric concentration >0 = present; numeric zero or blank = absent. Any other nonblank nonnumeric token triggers HOLD before AUC.

Coarse state is derived deterministically:

- PRESENT if any of the 13 bits is 1;
- NONE if all 13 bits are 0.

Aggregate/derived columns (Total anthocyanin, Total HYD, Total DEO, Dominant Anthocyanin) and all visible-color/reflectance columns are excluded.

## Frozen sample/common-frame rule

Species is the unit. Duplicate source samples are resolved by retaining the first source-table row in original Table_1 row order, as already frozen before outcome opening.

Tree/species crosswalk is frozen before chemistry values are read.

After crosswalk:
- remove fine states represented by fewer than 5 retained species;
- require >=20 common tips;
- require >=2 coarse and >=2 fine states;
- use one identical retained frame for both levels.

## Prospective hidden-memory test

Opportunity exists only if fine-state count > coarse-state count.

If opportunity exists:
- retain same-coarse species pairs;
- score by negative patristic distance;
- outcome = same exact 13-bit biochemical state;
- conditional ROC AUC;
- 9,999 fine-label permutations within coarse groups;
- seed 20260920.

PASS requires a positive observed-minus-null-mean AUC effect and one-sided P <= 0.05.

The source paper is known, so this is not literature-blinded. The **CHUN target estimand and row-level state pattern remain prospective**.

A PASS may open a new v0.9 promotion audit. It does not rewrite the pre-existing Ruellia-specific v0.7/v0.8 gate and does not automatically replace current EL v0.3.
