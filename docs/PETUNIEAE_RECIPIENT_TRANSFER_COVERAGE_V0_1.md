# Petunieae: recipient breadth and the limits of the flavonol transfer gain

Date: 2026-10-20. **Post-outcome descriptive audit, not a new primary test.**

## What is unchanged

The original 47 Petunieae species, six anthocyanidin-presence codes, 21 genes, three fixed 9/4/8 functional modules, original tree, two closest same-code donors and full same-code donor-mean baseline are unchanged. Training variances exclude the target species. All three module baseline, nearest-two and exact random-two MSEs were independently recomputed and matched the frozen PR #427 outputs within 1e-10. The original CSV, tree and source R-script SHA256 hashes all matched. Source: Wheeler et al. (2023), DOI 10.1098/rspb.2023.0275; original OSF archive from Actions run 34182646549, artifact 10039433384.

## New measured result: who benefits?

| Fixed module | Improved recipients | Worse recipients | Original pooled gain | Positive pooled gain after omitting any one recipient loss |
|---|---:|---:|---:|---:|
| Late anthocyanin execution | 17/47 | 30/47 | -15.15% | 0/47 |
| Flavonol branch and activation | **27/47** | **20/47** | **+5.61%** | **47/47** |
| Early shared and regulatory | 19/47 | 28/47 | -11.61% | 0/47 |

There were no tied losses under the declared 1e-12 numerical tolerance. For flavonol, the median paired standardized loss improvement was +0.084073. The pooled gain after each of the 47 individual recipient-loss omissions ranged from **+3.6002% to +8.9677%**. Thus the observed positive mean is not supported by only one influential recipient. It nevertheless does not improve prediction for every species: 20 recipients perform worse.

These omission calculations remove the evaluated recipient's losses only. The original donor predictions and training variances remain fixed. They are not re-trained leave-one-lineage-out predictions, independent validation datasets, binomial trials or confidence intervals.

## Important leverage limit

The largest positive paired-loss contributions were source IDs **LESC, BOER and BRGR**, with standardized loss improvements 0.973415, 0.950198 and 0.947167 respectively. These three recipients account for **32.99% of all positive improvements**. Omitting their evaluation losses together changes the pooled gain to **-0.72099%**.

This deliberately outcome-ranked stress test is not an unbiased alternative sample and must not replace the original +5.61% result. It shows that stability to any single recipient does not establish insensitivity to several influential recipients. Do not summarize this result as universally transferable or robust to arbitrary taxon deletion. Source IDs are retained without guessing a taxonomic-name crosswalk.

## Exact accounting: locality benefit must exceed the small-donor penalty

Let B be the error of the full same-pigment-class donor mean, R the exact expected error over all uniformly selected two-donor combinations from that class, and N the error of the two phylogenetically nearest donors. For each recipient and after averaging:

`B - N = (R - N) - (R - B)`.

The first right-hand term is the improvement from choosing close relatives rather than two random class members. The second is the finite-donor penalty relative to the full class mean. This is an error-accounting identity, not a new evolutionary law or a causal biological decomposition.

| Module | Locality benefit R-N | Two-donor penalty R-B | Net improvement B-N |
|---|---:|---:|---:|
| Late anthocyanin execution | 0.101798 | 0.228103 | -0.126305 |
| Flavonol branch and activation | **0.329749** | **0.274985** | **+0.054763** |
| Early shared and regulatory | 0.126878 | 0.308236 | -0.181358 |

All three modules benefit numerically from choosing nearby rather than random two donors. Only the fixed flavonol group offsets the cost of reducing the donor pool to two, under this particular source-internal predictor. No optimal k, gene partition or species set was selected in this audit. This accounting does not imply that the other modules lack phylogenetic expression structure.

## Interpretation for the manuscript

A supported source-specific statement is: **among species sharing the assayed anthocyanidin-presence code, ancestry gives a modest mean predictive advantage for the fixed flavonol-related expression module; the advantage benefits 27 of 47 species, survives any one-recipient omission, but remains sensitive to the joint contribution of several recipients.**

The existing Holm-adjusted P=0.0003 addresses the predeclared within-state locality permutation null. It is not a confidence interval or a separate test establishing that population-average practical gain is greater than zero. This audit adds no P values. It does not establish statistically significant between-module differences, an external radiation's predictive gain, selection, pollinator effects, UV reflectance, pigment concentrations or fitness. The prediction target is gene expression, not any of those ecological outcomes.

Wheeler et al. already connect flavonol biochemistry to UV absorption and flavonoid pathway structure (https://doi.org/10.1098/rspb.2023.0275). That prior biological context motivates follow-up measurements but is not a newly measured consequence of the present prediction analysis.

## Reproduction and outputs

Run `python scripts/audit_petunieae_recipient_transfer_v0_1.py --source <original-unzipped-OSF-artifact> --out-dir build/petunieae_recipient_transfer_v0_1`.

The runner writes the full 141 module-by-recipient rows, including original source ID, pigment code, both donor IDs, patristic distances, three losses and exact loss components, to `recipients_v0_1.csv`. The full report includes all 47 omission gains per module. The repository retains a compact numerical summary in `results/petunieae_recipient_transfer_v0_1/summary_v0_1.json`; the dedicated workflow archives the complete CSV and JSON.

Five synthetic tests were first observed to fail on unimplemented functions, then passed after implementation; they verify donor exclusion/tie-breaking, exact random-two enumeration, recipient leverage, and invalid-input rejection. Raw-data replay is separately checked against the previously frozen pooled and per-pigment-class losses. Original AJB/EL first-submission assets and primary inference statuses are unchanged. This remains part of Draft PR #427.
