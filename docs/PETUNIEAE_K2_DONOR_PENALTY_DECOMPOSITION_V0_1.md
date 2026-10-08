# Why hidden regulatory history did not beat a pigment-state mean — exact Petunieae donor-count decomposition

**Status:** POST-OUTCOME EXPLORATORY DIAGNOSTIC. The source was already examined and the earlier nearest-two predictor's `NOT_SUPPORTED` result is frozen. The decomposition question and exact analytic formula were committed before this diagnostic calculation. This note introduces no further P value, predictor, pathway subset or independent replicate.

## What was fixed before decomposing

The existing Petunieae test had 47 species on one dated tree, 21 prespecified flower-petal pathway genes and six exact anthocyanidin presence states. Holding out each species, two predictors were compared: the full mean of all other same-state species, versus the mean of its two nearest same-state relatives.

- State-only mean held-out standardized MSE: **1.138379**.
- Nearest-two mean held-out standardized MSE: **1.251167**.
- Predeclared nearest-two gain: **−0.099078**, frozen **NOT_SUPPORTED**.

The earlier permutation P=0.0014 establishes a locality advantage over a *whole-vector-shuffled* reference but cannot promote the k=2 prediction against the class-mean baseline.

## Exact comparison with random two donors

For a given held-out taxon and gene, let `m` be the number of other species sharing its exact pigment state, `mu` their mean log1p expression, and `V` the donor **population** variance (divisor m). If two of those m donors are sampled uniformly **without replacement**, then conditional on the observed expression values,

```text
E[(target - random_two_mean)^2]
  = (target - mu)^2 + [(m - 2)/(2(m - 1))] * V
```

We divide each term by the *same* 46-training-tip per-gene variance used in the frozen original prediction, average across the same 21 genes, then over the same 47 species. This is an exact algebraic expectation, not a fitted evolutionary model. The implementation was checked against brute-force enumeration of all donor pairs in a synthetic test.

| Predictor | Standardized MSE |
|---|---:|
| Full same-pigment-class mean | **1.138379** |
| Uniform random **two** donors in same pigment class — exact expected error | 1.405939 |
| Two **nearest relatives** in same pigment class | 1.251167 |

The whole error difference splits into two observed components:

```text
nearest_two - state_mean
    = (random_two - state_mean) - (random_two - nearest_two)

0.112788 = 0.267560 - 0.154771
```

Normalized to the full class mean error, the **two-donor penalty is +23.50%**, while selecting the closest relatives **recovers 13.60%** (relative to the same full-class-mean denominator). The net remains **+9.91% worse** than the full-state baseline. The mathematical identity residual was zero to displayed precision.

All six exact-pigment classes have a positive descriptive locality advantage over uniformly selected donor pairs; nevertheless, in five of the six classes the nearest-two predictor is still worse than the full class mean. The exception is fine code `000011`, where the nearest-two relative error gain over class mean is only +1.7%. These are within-source descriptive breakdowns, not six independent biological validations.

## What can and cannot be inferred

**Confirmed:** sampling fewer donors creates an exactly calculable conditional error penalty under the frozen training pool. Selecting phylogenetically close donors counteracts part, but not all, of that penalty. Therefore the raw prediction FAIL is **not** evidence that phylogenetic information is useless.

**Not established:** that phylogenetic divergence causally drives gene-expression differences; that the failure is explained uniquely by donor number rather than transcriptional variability, expression normalization, ecological filtering or measurement error; or that another tuned predictor will succeed. No nearest-neighbor count or gene subset was selected after the outcome.

The strongest calibrated statement is:

> **Residual molecular evolutionary history within a fine pigment phenotype can provide real locality information without beating a low-variance, class-wide prediction baseline under a fixed two-donor strategy.**

This supplies one source-specific explanatory diagnostic to the integrated temporal/mechanistic paper, not an independent phylogenetic-memory law.

## Exact sources

- Source: Wheeler et al. 2023, DOI `10.1098/rspb.2023.0275`, frozen Petunieae OSF `zg9cu` accession.
- Source-hash controls and fixed transcript columns: `data/petunieae_nested_regulatory_memory_preregistered_design_v0_1.json`.
- Original prediction result: `results/petunieae_nested_regulatory_leaveoneout_prediction_v0_1/result_v0_1.json`.
- Pre-diagnostic fixed algebra: `data/petunieae_k2_predictor_bias_variance_decomposition_design_v0_1.json`.
- Diagnostic computation: `scripts/diagnose_petunieae_k2_donor_penalty_v0_1.py`.
- Exact outcome: `results/petunieae_k2_donor_penalty_diagnostic_v0_1/result_v0_1.json`.
- Synthetic exhaustive-pair identity test: `tests/test_petunieae_k2_donor_penalty_v0_1.py`.

Frozen Camellia AJB v1.0 and Evolution Letters v0.3 outputs are unchanged.
