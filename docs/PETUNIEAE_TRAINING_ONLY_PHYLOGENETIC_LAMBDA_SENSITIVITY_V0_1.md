# Petunieae: training-only inference of phylogenetic covariance does not restore four-gene product prediction

**2026-10-21 source result — post-outcome sensitivity of one original 47-species radiation.** The previously verified original source phenotype is 3 measured floral flavonol amounts (myricetin, quercetin and kaempferol, original mg/g), with six unchanged original anthocyanidin-presence codes and four measured flavonol-related gene-expression predictors (F3primeH, FLS, MYBFL, MYB12). Authoritative original source: Wheeler et al. (2023), DOI `10.1098/rspb.2023.0275`, original OSF source node `zg9cu`, previously SHA256-verified original 60-row data CSV and original dated molecular tree.

## The source objection we examined

The preceding phylogenetic adjustment in integrated temporal Draft PR #430 assumed a predetermined working Brownian plus independent-residual covariance `V(λ)=λ C+(1−λ)I`, with λ=.5. Under that model, adding all four original measured expression predictors to an otherwise identical six-pigment-presence-class-and-phylogeny GP predictor increased held-out product MSE, corresponding to **−4.21%** relative gain (source-model parametric P=.3439). Although λ=.25, .75 and .95 source sensitivities also yielded negative gains, the scientific objection remains that λ=.5 could have been a poorly chosen arbitrary relative weight.

## What the new experiment actually does

Each of 47 original species is held out in turn. Its measured **three-product Y_i** is not used to select the fold's covariance model. From the other **46** source species, fit the **six unchanged pigment-code fixed effects** and original tree shared-root Brownian+nugget covariance using an eight-value working λ grid:

`λ ∈ {0, .10, .25, .50, .75, .90, .95, .99}`.

Select each fold's λ using the **multivariate restricted marginal likelihood** of all three original measured flavonol responses under the **class-only baseline**, including the source shared residual three-metabolite covariance; no gene predictors or their predictive performance are used to select λ. Then apply **that same selected λ** to both source candidate predictors:

- Baseline: six original pigment-presence states + exactly specified tree-dependent Gaussian kriging, trained on the other 46 species' measured flavonol outputs.
- Candidate: same baseline, *plus all four original target-species measured gene expressions* with previously fixed α=10 ridge; source training-only expression variances and other-46 metabolite response variances.
- Biological metric: `(MSE_baseline−MSE_candidate)/MSE_baseline` over all original 47 folds × three source metabolites.

Original source tree, full 47-tip eligibility, original biochemical code, original 21-gene source and retained four flavonol-related expression genes all remain unchanged. The original date/topology is not rerooted or re-estimated. The methodology was developed **after previous source outcomes were exposed**; it is an analysis-sensitivity diagnostic, not new blind preregistration or independent data collection.

## Result from the exact original source

Hosted verified analysis: [GitHub Actions #39449020678](https://github.com/zuizui0223/chun/actions/runs/39449020678) (3 focused regression tests passed, original published OSF source restored and chemical/genetic SHA constraints enforced).

| Source training rule | Pigment+phylogeny mean MSE | Same + four measured genes mean MSE | Additional practical gain |
|---|---:|---:|---:|
| Previous fixed λ=.5 working model | 1.162480 | 1.211401 | **−4.21%** |
| **New multivariate REML-selected λ, separately trained on other 46 metabolites** | **1.238880** | **1.318516** | **−6.43%** |

The source λ choices were **.75 for 46/47 omitted taxa** and **.90 for 1/47 omitted taxa**. Although the Gaussian covariance that maximizes training-set restricted likelihood need not optimize held-out squared-error prediction, **genes do not provide a practical incremental MSE improvement under this training-only fitted ancestry benchmark**.

The earlier **class-only, no-phylogenetic-GP** four-gene ridge improves MSE +6.42% (original within-code gene-vector shuffle P=.0254). A fixed source λ=.5 already removed that practical gain (−4.21%, prior working model P=.3439). Training-only REML covariance refitting yields another negative gain (−6.43%). **These figures answer distinct prediction-baseline questions and must all remain separately reported**.

## No new P value or gene-to-product causal claim

This is deliberately **post-outcome and descriptive**, and no new permutation, phylogenetic parametric bootstrap P, or cross-radiation significance test is calculated for REML-selected λ. Original phylogenetic training values are estimated under a Brownian+nugget model and a multivariate Gaussian response residual assumption. No independent external test determines the true covariance or how much of the earlier association was shared environment, identical ancestry, developmental state, batch calibration or direct transcriptional regulation.

Consequently, it is reasonable to state that **the original measured flavonol-related expression has no demonstrated incremental held-out prediction benefit after a specified phylogenetic baseline, including when the baseline's ancestry weight is fitted using only training taxa**. It is **not** reasonable to state that gene expression is physiologically unrelated to flavonol output, that historical regulatory memory has been proven erased, or that any pollinator/fitness selection mechanism has been identified.

## Reproducibility, source integrity and governance

- Frozen explicit post-outcome method document: `data/petunieae_training_estimated_phylo_lambda_diagnostic_v0_1.json`.
- Reproducer: `scripts/audit_petunieae_training_estimated_phylo_lambda_v0_1.py` (source hash checks, 47 species, original six compound-presence codes, source tree covariance from the exact dated Newick).
- Numerical output and all original 47 foldwise selected λ values archived in GitHub Actions; permanent result will be placed in `results/petunieae_training_estimated_phylo_lambda_v0_1/result_v0_1.json`.
- Synthetic regression tests verify that arbitrarily changing the omitted species' metabolite values cannot affect **that omitted fold's λ choice**, and verify the multivariate REML formula against independent matrix arithmetic.
- Original λ=0 independent-source +6.4207% and fixed λ=.5 −4.2083% numerical predictions must be identically recovered, verifying preserved underlying 47 species, chemistry, gene predictors and source tree.

Integration remains a **Draft** after original PR #414. The **Camellia** American Journal of Botany Paper 1 and frozen **Evolution Letters** v0.3 first-submission scientific artifacts remain untouched. Independent comparable molecular/radiation replicates and ecological/pollinator functional data remain the main generality bottlenecks.
