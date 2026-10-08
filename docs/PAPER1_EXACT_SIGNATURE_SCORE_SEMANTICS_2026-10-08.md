# Paper 1 exact-signature score semantics — post-closure QA (2026-10-08)

## Scope and decision

**Non-blocking interpretation audit only.** Paper 1 science v0.2.2, framing v0.3.4, AJB v1.0 bundle, all existing estimators, signed A/F/C/P states, conclusions, and journal route remain frozen. This document clarifies the meaning of the numerical *exact-signature recurrence* index already reported in Fig. 2 and its source results. It is not another outcome analysis or a new statistical significance test.

## Identity that matters

The implementation in `scripts/analyze_observation_corrected_recurrence_v0_1.py` defines exact-signature recurrence as Simpson concentration:

```text
R = sum_s (c_s / n)^2
```

where `c_s` is the number of admitted **dependence clusters** with complete four-axis signature `s` and `n` is the number of clusters. This *includes a self-match term*, so it is not the proportion of distinct cluster pairs sharing an identical signature.

For `n >= 2`, the corresponding fraction of **unordered distinct-cluster pairs** with an identical full signature is exactly:

```text
M_exact_pairs = (n * R - 1) / (n - 1)
```

The mathematical floor `R = 1/n` means that *every cluster has a different complete signature* and thus `M_exact_pairs = 0`. Conversely `R = 1` means all complete signatures match.

## Frozen data read on the correct scale

| Candidate-free transition class | Matched dependence clusters | Full-signature Simpson R | Identical distinct-cluster pairs | What remains |
|---|---:|---:|---:|---|
| Anthocyanin gain | 3 | 1/3 | 0 of 3 pairs, under **all three** completions of the unresolved `CSIN_WHITE_PINK:P` cell | Partial cross-axis concordance: pairwise mean 1/3–1/2 |
| Yellow development | 2 | 1/2 | 0 of 1 pair | The two signed four-axis trajectories agree at **A down, C up, P down**, but differ at **F**; pairwise concordance = 3/4 |

The reported `R=1/2` for yellow is **not stronger exact replay than** `R=1/3` for anthocyanin: their different numerical floors arise solely from different group counts. In **both** classes the admissible candidate-free completions contain zero matching complete four-axis signatures.

The scientifically relevant *positive* yellow observation is the three-of-four **directional module agreement**, not the raw magnitude of Simpson `R`.

The literature-selected regime admits complete-signature matches under some missing-axis completions (`R` up to 1), whereas candidate-free remeasurement restricts the complete-signature identified set to its floor. This is an identification result, not a claim that exact molecular replay is absent from nature.

## Strength of directional evidence is not the same as signature coding

The frozen yellow-development rows use all signed five-stage OLS slopes, **without choosing directions on the basis of significance**. Their stage-order exact P values are retained as uncertainty metadata:

| Shared axis | *C. nitidissima* | *C. perpetua* | Interpretation |
|---|---|---|---|
| A down | 0.0833 | 0.0167 | Same estimated sign, but the *C. nitidissima* stage-order test does not cross 0.05 |
| C up | 0.1667 | 0.0667 | Same estimated sign; neither stage-order test crosses 0.05 |
| P down | 0.0333 | 0.0167 | Same estimated sign; both individual, unadjusted order-test P values are below 0.05 |

Thus **3/4 directional matches must not be paraphrased as three independently significant replicated pathways**. These are transcript-module trajectories, not metabolite fluxes, causal genetic substitutions, or independent macroevolutionary colour-transition events. No multiple-testing-adjusted or joint module-recurrence significance claim is supplied here.

## Submission-safe interpretation

> In matched public *Camellia* molecular contrasts, standardizing the four-module observation rule eliminates the previously admissible *complete* A/F/C/P signature matches within both comparison classes. Partial signed module alignment persists—most visibly the shared A/C/P directions across two yellow-development series—but its biological strength depends on module-specific uncertainty and it does not identify repeated historical branch events.

Use `Simpson concentration` or `exact-signature recurrence index` if reporting `R`; do **not** describe `R=0.5` as “50% of yellow transitions recurred exactly” or `R=0.333` as “one third of anthocyanin transitions replayed the full mechanism.”

## Verification and governance

- Frozen candidate-free inputs: `data/paper1_fig2_candidate_free_signature_v0_2.csv`.
- Frozen bounds: `data/paper1_fig2_recurrence_intervals_v0_2_2.csv`.
- Frozen yellow slope/order-test metadata: `docs/YELLOW_TWO_CLUSTER_RECURRENCE_RESULT_V0_1.md`.
- Added regression checks: `tests/test_paper1_recurrence_contract_v0_1.py`.
- Molecular dependence clusters are **not** independent observed macroevolutionary transition events.
- This is supplementary author/reviewer interpretation QA. It does not modify the frozen AJB submission bundle or reopen Paper 1 science.
