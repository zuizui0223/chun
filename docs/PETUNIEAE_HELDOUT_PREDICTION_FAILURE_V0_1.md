# Petunieae: phylogenetic memory is detectable, but a nearest-relative predictor does not beat the pigment-state mean

**Source and decision:** retrospective 47-tip Petunieae reanalysis; the independent new prediction design was frozen in commit `0c6721f` before its new prediction result was opened. However the same public source had already been used in CHUN exploratory analyses. It is **not prospective independent biological replication**.

## Question and predeclared prediction

The previous matched same-tree result was **positive**: pathway-gene expression distance and patristic distance were correlated even among species sharing the same exact six-compound anthocyanidin presence code (rho +0.60744; within-fine whole-vector permutation P=0.0001).

But **does that association improve prediction of expression for a taxon left out of the training sample?**

We fixed a head-to-head prediction test, with no phenotype or gene changes after opening:

1. **State-only baseline:** mean log1p TPM10K across *all other* taxa with the held-out taxon's exact six-bit anthocyanidin-presence code.
2. **State plus local phylogeny:** mean log1p TPM10K across only the **two** closest species, on the fixed source tree, within that *same* exact pigment class, excluding the target.
3. **Loss:** per-gene squared error scaled by the 46 training taxa's own gene-expression variance (no held-out-expression information in fold-specific normalization); average all 21 fixed genes and all 47 left-out tips.
4. **Relative gain:** `(state-only MSE - nearest-two MSE) / state-only MSE`.
5. **Success:** gain **> 0**, and one-sided within-fine-class whole-expression-vector 9,999-permutation P ≤ 0.05. No optimization of neighbor count, distance kernel, gene subset or alternative predictor.

The original source table, published tree and analysis script are each SHA-256 checked against the previously frozen public OSF artifact.

## Main outcome — predeclared positive prediction FAIL

| Predictor | Held-out 21-gene standardized MSE |
|---|---:|
| All other species in the same fine pigment class (state-only) | **1.138379** |
| Two nearest relatives within the same fine pigment class | **1.251167** |

**Observed relative prediction gain = −0.099078**, i.e. the nearest-two rule has **9.91% larger MSE relative to the class-average baseline**. The frozen decision is:

`NOT_SUPPORTED`.

The conditional permutation-null mean for the gain was −0.234744 (central 95% null interval −0.325890 to −0.145811). The observed gain was less negative than 99.86% of the permutation draws (upper-tail P=0.0014). **That is not a prediction PASS**, because it fails the independent and explicitly predeclared `gain>0` requirement.

This is a particularly informative distinction:

- **Detectable conditional genealogical structure:** supported by earlier within-state expression-distance correlation and better-than-shuffled nearest-neighbor performance.
- **Prediction that improves on a stable within-state mean:** **not supported** by the frozen nearest-two estimator.

A significant permutation contrast relative to random whole-vector reassignment does not certify that a predictive strategy is better than a relevant nonphylogenetic baseline.

### Across the six fixed fine states (descriptive after primary)

Only the `000011` state has positive local predictor gain (+0.0170); the other five range from −0.0719 to −0.2351. Excluding one entire fine state from the *evaluation set* at a time leaves all six remaining pooled relative gains negative (range −0.1309 to −0.0839). This is descriptive sensitivity, not six new tests or independent biological replicates.

## Why the two results can legitimately differ

A positive pairwise correlation says that **on average, expression differences are larger over longer evolutionary distances** within pigment classes. It does not imply that the closest two species together are less noisy estimators than the mean of 5–12 other species with the same pigment code. A two-donor mean may retain high variance, and the state mean may already exploit a stable, shared component of pathway expression.

These are possible explanations, **not proven causes**. The test cannot distinguish prediction variance, heterogeneous within-clade trajectories, plant sampling context, source measurement error, and phylogenetic/process structure. Do not change `k=2` or fit weights to rescue the failure: any such exploratory models would require a separately labeled question and independent evaluation.

## Contribution to the integrated CHUN paper

The new, defensible contrast is:

> **The existence of hidden evolutionary history within a biochemical phenotype class is not equivalent to the ability to predict an unmeasured molecular phenotype from its nearest living relatives.**

This is relevant to the difference between **phylogenetic signal as historical information** and **predictive transfer across taxa**. It improves the biological specificity of the one-paper integration but remains one retrospective Petunieae dataset, not a universal property of floral traits.

The cross-radiation visible-colour hidden-memory result (18/21), Schistanthe prospective visible PASS, biochemical Gesnerioideae FAIL, and the seven-system heterogeneous mechanistic benchmark remain separate evidence tiers. None independently validates this 21-gene prediction failure.

No effect on frozen Camellia Paper 1 AJB v1.0 or Evolution Letters v0.3.

## Reproduction and claim audit

- Predetermined rules: `data/petunieae_nested_regulatory_leaveoneout_prediction_design_v0_1.json`.
- Pinned script: `scripts/run_petunieae_nested_regulatory_leaveoneout_prediction_v0_1.py`.
- Frozen completed output: `results/petunieae_nested_regulatory_leaveoneout_prediction_v0_1/result_v0_1.json`.
- Source run artifact: https://github.com/zuizui0223/chun/actions/runs/37765499812.
- CI: 4 unit tests passed; full 9,999-permutation calculation completed and matched a separate local SHA-verified calculation.
