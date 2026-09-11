# Cross-radiation axis-localization literature search plan — v0.1

Frozen: 2026-09-11, before detailed web/source extraction for additional systems.

## Candidate-independent queries

Run each query exactly as written (minor spelling variant colour/color may be added only as the paired equivalent):

1. `flower color hue anthocyanin hydroxylation comparative species F3'5'H`
2. `flower colour anthocyanidin hydroxylation comparative transcriptome phylogeny`
3. `floral pigmentation intensity MYB comparative species anthocyanin`
4. `flower color pigment amount comparative transcriptome phylogeny anthocyanin`
5. `repeated flower color evolution molecular mechanism F3'H F3'5'H DFR MYB`

## Candidate-specific queries

For each candidate name below, run the same two templates:

- `<candidate> flower color hue anthocyanin F3'H F3'5'H molecular`
- `<candidate> flower pigmentation intensity amount MYB DFR ANS comparative`

Candidates fixed before extraction:

- `Phlox`
- `Penstemon`
- `Antirrhinum`
- `Ruellia`
- `Ipomoea`

Candidates may additionally enter from candidate-independent searches or citation chasing, but every newly discovered candidate must be recorded in the screening ledger together with the query/citation path that produced it; absence of a convenient result is not a reason for exclusion.

## Screening order

1. Screen title/abstract/snippet for a directly defined HUE or AMOUNT_INTENSITY axis.
2. Require a comparative evolutionary system with at least two taxa/populations/independent transitions; single-cultivar developmental studies are excluded from the primary synthesis.
3. Require Tier A or B molecular evidence under `CROSS_RADIATION_AXIS_LOCALIZATION_GATE_V0_1.md`.
4. Collapse nested publications to one biological system × axis before any statistical summary.
5. Record exclusions and `UNRESOLVED`; do not silently drop contradictory or null systems.

## Search stop

Stop the first pass after:

- all 15 fixed queries have been screened (5 candidate-independent + 10 candidate-specific), and
- backward/forward citation chasing has been performed on every newly admitted Tier-A/B primary source that materially changes a system classification.

A second pass is allowed only to resolve source identity, full-text availability, duplicate-system dependence, or molecular-category ambiguity; it must not be used to hunt for support after seeing the primary statistic.
