# Yellow two-cluster recurrence gate v0.1

## Status

**Frozen before inspection of the candidate-free *Camellia perpetua* expression result.**

This gate prevents outcome-dependent reinterpretation when the second independent `yellow_development` cluster becomes available. It also separates the within-system biological contrast from the cross-cluster estimator before any *C. perpetua* A/F/C/P direction is observed.

## Independent clusters and canonical target

The class is `yellow_development`, canonically oriented toward `later_or_more_yellow` before expression inspection.

Independent dependence clusters:

- `CNITIDISSIMA` — existing frozen candidate-free ordered S1-S5 yellow-development trajectory;
- `CPERPETUA` — frozen 15-run S1-S5 series.

Within *C. perpetua*, S1 young bud -> S3 yellowing onset remains the preregistered **within-system primary biological contrast**. The S1 -> S5 pairwise endpoint remains secondary/correlated.

For **cross-cluster recurrence**, however, the estimator is frozen to the same quantity used for `CNITIDISSIMA`: the OLS slope across all five prespecified S1-S5 stage means. This avoids confounding biological disagreement with an estimator mismatch (ordered trajectory versus one selected pairwise contrast).

No stage pair may be selected from the expression outcome for the cross-cluster comparison.

## Literature regime on the same two clusters

From the frozen literature edge registry after dependence collapse:

- `CNITIDISSIMA`: A=down, F=up, C=up, P=down;
- `CPERPETUA`: A=unknown, F=up, C=unknown, P=unknown.

Therefore the literature-side two-cluster identified set has:

- 3 unresolved cluster x axis cells;
- 27 exact `{up,down,same}` completions;
- exact-signature recurrence: **0.5–1.0**;
- pairwise A/F/C/P concordance: **0.25–1.0**;
- pairwise-concordance identified-set width: **0.75**.

Complete multivariate recurrence is therefore admissible under the selected literature observation regime but is not identified.

## Candidate-free cross-cluster decision rule

Use only the four A/F/C/P directions from the frozen *C. perpetua* **five-stage ordered trajectory** for recurrence against the frozen `CNITIDISSIMA` five-stage ordered trajectory. Do not select directions by P value, expected biology, S1->S3 effect size, agreement with *C. nitidissima*, or agreement with the literature.

If all four *C. perpetua* axes are estimable across all five stages, the candidate-free two-cluster result is point-identified:

- exact-signature recurrence = **1.0** only if all four A/F/C/P ordered directions exactly match `CNITIDISSIMA`;
- otherwise exact-signature recurrence = **0.5**;
- pairwise concordance = number of matching axes / 4;
- candidate-free pairwise identified-set width = **0**;
- literature-to-candidate-free width reduction = **0.75**.

If one or more *C. perpetua* axes remain unresolved, retain exact partial-identification over those cells; do not impute from visible yellow colour, the S1->S3 pairwise result, or the published pathway narrative.

## Interpretation branches fixed before outcome

1. **4/4 ordered-direction match** — supports recurrence of the full A/F/C/P yellow-development trajectory signature across these two independent clusters, while still not establishing a universal yellow mechanism.
2. **Partial match (1-3/4)** — supports axis-specific reuse but rejects exact whole-signature recurrence across these two clusters.
3. **0/4 match** — rejects recurrence of the full candidate-free yellow-development trajectory signature in this two-cluster test and strengthens the distinction between visible yellow and biochemical state.
4. **Any unresolved axis** — the class remains partially identified; report bounds rather than choosing an outcome-compatible completion.

S1->S3 and ordered S1-S5 may legitimately disagree within *C. perpetua*: that would indicate developmental-window dependence, not a reason to choose whichever estimator agrees with the desired cross-species story.

In every branch, the observation-process question remains separate from macroevolutionary realization and from branch-specific ecological causation.

## Frozen provenance

- `CNITIDISSIMA` raw-result run: `32803242174`.
- `CPERPETUA` mapping audit: `32826721885`.
- `CPERPETUA` raw pilot: all 15 frozen S1-S5 runs, first 500,000 paired reads per run.
- Within-system primary: S1 -> S3 Hedges' g for A/F/C/P.
- Cross-cluster primary: OLS slope across all five prespecified stage means, with exact 5! stage-order permutation P retained only as uncertainty metadata.
- Literature registry: `data/micro_accessibility_edge_registry_v0_1.csv`.
- Canonical orientation: `data/micro_transition_canonical_orientation_v0_1.csv`.
- Recurrence engine: `scripts/analyze_observation_corrected_recurrence_v0_1.py`.

No expected *C. perpetua* A/F/C/P direction is encoded in this gate.