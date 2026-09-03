# Visible-colour A/W balance sensitivity v0.1

## Problem

The provenance-clean prediction matrix has A=14 and W=34. A remaining alternative explanation for the out-of-sample null is that unequal state counts make the colour mean unstable or unfairly penalized.

## Test

For each of 10,000 deterministic replicates (seed 20260903):

1. retain all 14 A taxa;
2. sample 14 of the 34 W taxa without replacement;
3. fit leave-one-species-out null and colour-mean predictions on the balanced A=14, W=14 subset;
4. calculate colour/null RMSE ratios for BIO1 median, BIO6 median, BIO6 q05 and BIO1 IQR.

The Tuberculatae minimal provenance correction is retained.

## Result

Across balanced subsets, median colour/null RMSE ratio is >1 for all four metrics.

Approximate deterministic results:

- BIO1 median: colour improves in **2.09%** of balanced replicates; median ratio **1.0348**;
- BIO6 median: **6.29%**; median **1.0313**;
- BIO6 q05: **20.15%**; median **1.0208**;
- BIO1 IQR: **1.43%**; median **1.0351**.

Combining the four ratios geometrically within each replicate:

- aggregate colour/null RMSE ratio <1 in only **1.08%** of replicates;
- median aggregate ratio ≈ **1.0275**;
- 5–95% interval ≈ **1.0111–1.0349**.

## Interpretation

The visible-colour predictive null is not explained by the W-heavy state count. Even when A and W are exactly balanced, coarse colour usually worsens rather than improves held-out annual-climate prediction.

Together with the provenance and section-holdout sensitivities, this closes three straightforward rescue explanations for the direct A/W annual-climate model:

1. extreme-coordinate provenance;
2. historical-section composition;
3. A/W sample-count imbalance.

The remaining plausible climatic role is therefore more conditional, especially flowering-window climate acting through pollinator reliability or correlated floral function, rather than a genus-wide annual-climate mapping to visible A/W state.
