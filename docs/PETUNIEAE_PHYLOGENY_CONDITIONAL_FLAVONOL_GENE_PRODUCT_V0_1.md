# Petunieae: original four-gene expression/product prediction no longer helps after a fixed working phylogenetic covariance baseline

**2026-10-20. New, source-exposed retrospective same-radiation analysis — `NOT_SUPPORTED_PHYLOGENY_CONDITIONAL_SOURCE_TRANSFER`.** This result tests a more stringent phylogeny-conditioned *prediction baseline*, not the causal influence of gene regulation on metabolic flux. It does not erase the earlier positive prediction result under a weaker chemical-presence-class-only baseline.

## Previous measured result and its confounder

Original source: Wheeler et al. (2023; DOI **10.1098/rspb.2023.0275**), authoritative SHA-verified original published OSF data `zg9cu`; same 47 species retained from the dated 60-tip molecular tree and source 60-row transcriptomic/floral chemical measurements. Original 6 anthocyanidin presence codes contain 6, 6, 6, 10, 6, 13 species. Original measured flavonol-related genes are `F3primeH, FLS, MYBFL, MYB12`; targets are **myricetin, quercetin and kaempferol** measured in mg/g.

The earlier distinct class-only comparison showed that a **fixed class-intercept four-gene ridge** predicted omitted species' own measured flavonol amounts better than the mean of all other same-pigment-state species: **MSE 1.146276 vs 1.224925**, **+6.42%** practical source gain, conditional whole-gene-vector shuffle **P=.0254**. This used the target species' **own measured expression** and original known chemical presence code but no shared-ancestry term in either predictor. Gene expression and measured product concentrations can both be structured by common ancestry, so part or all of that apparent improvement could be phylogenetically confounded.

## What we changed while keeping the original species and compounds fixed

The new test design was written in `data/petunieae_phylogenetic_conditional_gene_to_product_design_v0_1.json` **before opening the numerical outcome of this particular source phylogenetic comparison**. The original source and all previous outcomes were already publicly known. We did not change genes, metabolites, taxon inclusion, fixed pigment state, k=2 donor tests, metabolites' log1p transformation, gene expression normalization or predictor family labels.

The source dated tree was used to construct original root-shared-history covariance `C_ij = distance(root, MRCA(i,j))`, normalized by the mean 47-tip root height (approximately **40.494836** branch-length units). A deliberately **fixed working** phylogenetic residual covariance `V = 0.5 C + 0.5 I` combines Brownian shared ancestry and independent residual variance. This **λ=.5 is an assumption**, not an estimated optimum or the true covariance necessarily generating the source traits.

In each of the same **47 leave-one-species-out folds**, both models have:
- the **same original six pigment-code categorical fixed intercepts**, with target class known;
- the **same dated-tree covariance V**, with Gaussian conditional (kriging) prediction of omitted-species product residuals from the **other 46** species.

The only candidate-model addition is the target's **four measured original gene-expression values** with the same fixed **ridge α=10**, each gene normalized using only the other 46 source species' source-TPM10K expression variance. Both models predict transformed products `log1p(100×original mg/g)`; errors are scored against the actual omitted product vector and scaled by the **other 46 product values' variance**.

A special reproducibility guarantee: when V is set to **λ=0** (independent taxon residuals, no phylogenetic borrowing), the exact new GLS/kriging model must reproduce the previous four-gene vs class-only **+6.4207478%** gene→product source result (MSE **1.224925 → 1.146276**) to numerical precision. This was independently verified using source-internal exact source and synthetic direct 46-tip refit calculations.

## New original 47-species heldout outcomes

| Working phylogenetic residual covariance | Source pigment class + phylogeny MSE | Same + four measured genes MSE | Additional gene-expression practical gain | Decision |
|---|---:|---:|---:|---|
| **λ=0** (original no-phylogeny model, control) | 1.224925 | 1.146276 | **+6.42%** | Original retrospective positive (P=.0254 under a nonphylogenetic shuffle) |
| **λ=0.25**, descriptive sensitivity | 1.159142 | 1.162620 | **−0.30%** | No extra gain |
| **λ=0.50**, **new fixed working phylogenetic primary** | **1.162480** | **1.211401** | **−4.21%** | **NOT SUPPORTED** |
| **λ=0.75**, descriptive sensitivity | 1.217592 | 1.301964 | **−6.93%** | No extra gain |
| **λ=0.95**, descriptive sensitivity | 1.333756 | 1.458539 | **−9.36%** | No extra gain |

The source tree gives a defensible **comparative prediction source**, but larger λ is not always a better base model. The original pigment-only baseline MSE is 1.224925; the fixed λ=.5 pigment+phylogeny model improves that to 1.162480, though this does not prove the Brownian covariance is accurately specified.

### Parametric ancestry-preserving working null

An additional **9,999 source-model matrix-normal simulations** (seed 20261020) generated all three measured metabolite response vectors under a **six-code-only GLS null** with source V at λ=.5 and a measured three-compound residual covariance estimated from the 47 original source responses. Those null phenotypes maintain both tree-implied relatedness (under the specified Brownian+nugget V) and metabolite covariance. The observed original four measured gene expression vectors and six-bit pigment codes are fixed. Every simulated phenotype is run through the same 47-fold pigment+phylogeny and pigment+phylogeny+four-gene source prediction operators, including the original per-fold loss normalization.

Observed **additional gene gain −4.2083%** vs null-mean **−5.9078%**; working-null 2.5–97.5% range **−15.81% to +7.73%**; positive-tail **model-conditional P=.3439**. Under the prespecified requirement of **positive improvement and P<=.05**, the new phylogenetic benchmark is **NOT SUPPORTED**.

This null is **parametric and conditional on the original fixed Brownian/nugget model**. It is *not* a nonparametric phylogenetic blocked-permutation test, does not estimate true phylogenetic signal parameter λ or evaluate batch/environmental covariance, and does not establish causal null gene effects. Descriptive gains for three other λ values are shown without new significance or choosing an advantageous working λ.

## Biological inference: a narrower, stronger conclusion

The original 47-species results now separate three distinct prediction questions:

1. **Ancestral relatedness helps predict the fixed four flavonol-branch-associated source genes' expression** using two nearest same-pigment relatives: earlier source **+5.61%**, original Holm P=.0003, one radiation only.
2. **Those nearest two relatives fail to predict directly measured flavonol compound quantities** better than the same-pigment-class mean: earlier **−24.08%**, original chemical Holm P=.3545.
3. **Directly measured gene expression** had an earlier modest **+6.42%** source predictive gain for those compounds when compared with a baseline containing the source pigment state **but not phylogeny**. However, once a fixed shared-ancestry covariance and phylogenetic residual prediction are already included in both sides, the same four-gene panel adds **no practical source gain** (working λ=.5 **−4.21%**, parametric-model P=.3439). The original P=.0254 is therefore **not robust to this explicitly specified phylogenetic benchmark**, though it remains the correct result for its own original model contrast.

One biologically interesting explanation is that part of the earlier four-gene cross-species predictability shared information with ancestry rather than measuring independent gene-to-metabolite coupling. This is **only a hypothesis**: the new study does not identify the magnitude of mediated/shared genetic effects, direct enzyme activity, transcriptional causality or environmental extraction conditions. Source metabolite accumulation can still depend on gene expression; absence of extra gain in this small source at this particular regularization/covariance is not evidence that it does not.

The source includes **no measured UV reflectance, pollinator visitation/preference, pigment-dependent flower fitness, controlled metabolic perturbation, species trait evolution event counts or independent second radiation** in the current test. Such ecology and causation require separate original biological data and experimental approaches. The claim of a general upstream flavonoid memory principle, a trait memory half-life or interaction-mediated selection is **not established**.

## Repository source and publication governance

- New source frozen benchmark: `data/petunieae_phylogenetic_conditional_gene_to_product_design_v0_1.json`.
- Original source and exact full algorithm: `scripts/analyze_petunieae_phylo_conditional_gene_product_v0_1.py`, exact 47-fold GLS low-rank prediction validated against explicit 46-species training on synthetic source covariance.
- Actual measured source output: `results/petunieae_phylo_conditional_gene_product_v0_1/result_v0_1.json`, **GitHub Actions source run [39415329473](https://github.com/zuizui0223/chun/actions/runs/39415329473)**.
- Source-identical full rerun tests also verify all λ sensitivity values, 47 fixed taxa, 9,999 simulated nulls, original tree height, and original λ0 +6.42% reconstruction without class / gene selection.

**Keep Draft #430 stacked on Draft #429, original integrated temporal manuscript PR #414 Draft.** The original *Camellia* AJB Paper 1 and frozen *Evolution Letters* v0.3 first-submission science, original Petunieae positive conditional expression-history association, original Petunieae nearest-two full-gene FAIL, and original Erica source-level NOT_SUPPORTED exploratory result remain intact. No effect differences or cross-radiation universality promoted.
