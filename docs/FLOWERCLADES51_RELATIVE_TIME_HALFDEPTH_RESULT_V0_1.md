# Relative phylogenetic-time flower-color half-depth — result v0.1

## Result

The pre-outcome contract from PR #300 specified an exponential decay estimand before PR #299 froze the relative-time persistence outcomes:

`P(same state | d) = q + (1-q) exp(-lambda d)`.

Here `d` is relative divergence depth within an effectively ultrametric source tree and `q` is the exact same-state probability implied by the retained state frequencies.

The model was fitted on the existing 28-clade common frame at coarse, intermediate and fine resolution. Species pairs define the within-clade pseudo-likelihood; **clade remains the inferential replication unit**.

## Half-depth

The derived quantity `ln(2)/lambda` is the fraction of crown depth over which modelled excess same-state retention falls by half.

Median half-depth:

| resolution | median | Q25 | Q75 |
|---|---:|---:|---:|
| coarse | 0.00600 | 0.000347 | 0.08297 |
| intermediate | 0.01067 | 0.000270 | 0.09746 |
| fine | 0.01043 | 0.000255 | 0.09929 |

Thus the median fitted memory half-depth is short on the relative crown-depth scale, but the distribution is highly heterogeneous among clades. The upper quartile extends to roughly 0.08–0.10 of crown depth at all three resolutions.

These are **relative** depths, not millions of years.

## No universal persistence timescale by resolution

The paired Friedman test across the 28 clades gives:

- statistic = 1.629
- P = **0.443**

The frozen rule therefore does not open pairwise resolution tests.

The resolution with the largest half-depth within a clade was:

- coarse only: 7 clades;
- intermediate only: 1;
- fine only: 3;
- coarse + intermediate tie: 1;
- intermediate + fine tie: 8;
- all three tied: 8.

This reinforces the earlier persistence-curve result: flower-color memory has a measurable relative timescale, but coarse, intermediate and fine representations do not have a universal ordering in how long that memory persists.

## Model boundary

Three coarse, four intermediate and four fine fits reached the frozen high-lambda boundary, corresponding to effectively immediate loss toward the clade-frequency baseline on this normalized scale. They are retained rather than deleted.

The half-depth model is deliberately restrictive because it fixes `P(same|d=0)=1` and the long-distance baseline to `q`. It is used as an interpretable descriptive estimand, not as an independent likelihood-based proof or transition-rate model.

## Scientific interpretation

The result adds a quantitative time-scale vocabulary to the EL temporal-memory story:

> flower-color state identity often loses much of its excess phylogenetic memory early in relative clade history, but the rate of loss varies strongly among radiations and is not consistently longest at one phenotype resolution.

This remains a transformation of the same source states and trees used by the AUC and binned persistence analyses. It does not increase the independent replication count.

Camellia Paper 1 and frozen EL v0.2 remain unchanged.
