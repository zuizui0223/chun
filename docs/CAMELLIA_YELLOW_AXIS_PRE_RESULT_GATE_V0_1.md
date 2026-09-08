# Camellia yellow-axis validation — pre-result gate v0.1

## Motivation

The exhaustive hierarchy-specificity control was designed to falsify the preselected WHITE/non-WHITE and pigment-presence boundaries. Only after that control was completed, an exploratory pattern became visible: in Antirrhineae the best alternative partition was consistently YELLOW versus non-YELLOW, and in Linoideae the same partition was the most frequent best partition across retained settings.

This document freezes an **external validation** in Camellia before calculating its partition scores. Camellia was not used to generate the yellow-axis observation in those two systems.

## Frozen inputs

Accepted-species wild-colour data:
- strict seed: 24 species, source states W=19, A=1, Y=4;
- dominant-colour sensitivity seed: 30 species, W=22, A=4, Y=4;
- source artifact run `32552102861`, artifact `9470344149`, SHA256 `548eaaa16d3418fa2dc22e63631b56d388dea55fe39621fb53a4d0d5b477731f`.

Two accepted-species topology treatments:
- WFO55 FastTree-gene-tree ASTRAL topology: run `32440138207`, artifact `9432146191`, SHA256 `b5c067450332fd9b590c37c95325029a059a7368b1f20b390068565c8f807725`;
- WFO53 UFBoot ASTRAL sensitivity topology: run `32552618223`, artifact `9470509744`, SHA256 `e9d3a9f88dbbda7b8fa3bbe4d210c5665a2125b289b62639ea51c64614de9ed9`.

The UFBoot tree lacks `Camellia petelotii`, so it uses 23/24 strict and 29/30 dominant seed species. This missing tip is fixed before results and is not imputed.

## State space

Fine states are the source-audited visible states:
- `W` = white;
- `A` = anthocyanin/pink-red class;
- `Y` = yellow.

All three non-trivial bipartitions of the three-state alphabet are evaluated:
1. **YELLOW axis:** `Y | {W,A}`;
2. WHITE axis: `W | {A,Y}`;
3. ANTHOCYANIN axis: `A | {W,Y}`.

## Statistic

For each of four fixed tree × coding settings:
- compute observed three-state Sankoff minimum-change score `S_obs`;
- compute unconditional null mean `U` from 9,999 label permutations;
- for each partition P, compute conditional null mean `C_P` by permuting exact W/A/Y labels only within the two fixed coarse classes;
- calculate `capture(P) = (U - C_P)/(U - S_obs)`.

Higher capture means the partition explains more of the fine-state phylogenetic organization gap. This is a representation statistic, not a causal or adaptive effect size.

## Pre-frozen validation rule

`YELLOW_AXIS_VALIDATED` requires BOTH:
- YELLOW/non-YELLOW has the highest capture among all three partitions in at least **3 of 4** settings; and
- YELLOW-axis capture is positive in **all 4** settings.

Interpretation if not met:
- best in exactly 2/4 settings: `YELLOW_AXIS_MIXED`;
- best in 0–1/4 or non-positive capture in any setting: `YELLOW_AXIS_NOT_VALIDATED`.

No threshold may be changed after the Camellia scores are observed.

## Claim boundary

A PASS would validate a visible-state yellow/non-yellow axis in a third system, not prove a shared biochemical pathway, ancestral yellow state, ecological driver, or universal transition direction. A failure would leave the prior 3/3 fine-state state-granularity result unchanged.

Paper 1 remains unchanged.
