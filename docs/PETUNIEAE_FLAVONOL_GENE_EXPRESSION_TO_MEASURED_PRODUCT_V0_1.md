# Petunieae: do the four flavonol-associated expression genes explain measurable product abundance within a fixed pigment phenotype?

**2026-10-20 — retrospective, source-exposed, original matched 47-species result.** Original experimental source: Wheeler et al. (2023), DOI `10.1098/rspb.2023.0275`, original OSF node `zg9cu`. The exact archived source (CSV/tree/original analysis script SHA256 verified) is read from Actions run `34182646549`. PR #429 contains the full code and a source-frozen design committed before this specific gene-to-product prediction endpoint was opened.

## Why this test connects two previously separate results

The original source showed that the fixed four flavonol-related *gene-expression* measurements (F3primeH, FLS, MYBFL, MYB12) show **+5.61%** positive nearest-two-phylogenetic-relative held-out transfer compared with the mean across all other same-sixbit-pigment-code species (pre-existing three-module Holm P = .0003). Yet *measured flavonol concentrations* in exactly the same source are **−24.08%** worse when predicted from those same two nearest relatives than from their entire pigment class (two-target chemical Holm P=.3545).

This new test instead asks a different, direct conditional association question: **If measured expression of those four genes is available for the omitted species, can it improve prediction of its three actually measured flavonols beyond what is known from its original anthocyanidin-presence class alone?** This is not prediction from genetics/phylogenetic ancestry alone.

## Frozen model and original biological units

- **47 original source taxa**, **six unchanged six-bit anthocyanidin-presence states**, 6/6/6/10/6/13 taxa. Outgroup and original rare-state source exclusion unchanged.
- Original *four fixed flavonol-associated genes*: `F3primeH`, `FLS`, `MYBFL`, `MYB12`. F3primeH is a branching hydroxylase, **not exclusively flavonol-specific**.
- The source *three measured biochemical products*: original `myr_mgg`, `quer_mgg`, `kaem_mgg`; represent **myricetin, quercetin and kaempferol concentration (mg/g)**.
- In each held-out 47-taxon fold, the **baseline** is the mean of the other taxa carrying the **same pre-existing exact anthocyanidin-presence class**.
- The **new predictor** adds a class intercept and four predictors transformed with log1p(TPM10K), class-centred and training-only z-standardized, using a fixed **ridge alpha=10** (four genes, pooled slopes across source classes). The chemical target is log1p(100×original mg/g). The main mean-square loss is averaged equally over the three target metabolites and 47 withheld taxa; squared chemical errors are scaled only by variance among the **other 46 taxa**.
- Inference is conditional on known biochemical class and *measured target-species gene expression*. The predictor is not trained on held-out target-species metabolite concentrations.
- New source null: **9,999 intact four-gene expression-vector species permutations strictly within each original six-bit pigment state** (seed 20261020). For each shuffle, the complete 47-fold class-controlled ridge model and practical relative MSE gain are recomputed; one-sided empirical P is the fraction of shuffled gains at least as large as the original. The null retains four-gene covariance within a species but **does not preserve phylogenetic expression autocorrelation**, making this a source-constrained exploratory result rather than a causal phylogenetic-adjusted test.
- Alpha 1 and 100 were locked in design as **descriptive sensitivity** without P values, not alpha hyperparameter tuning after exposure.

## New measured gene-to-metabolite predictive result

| Original-source endpoint | Class-only baseline MSE | Four-gene class-controlled ridge MSE | Relative predictive gain | Original-source permutation P |
|---|---:|---:|---:|---:|
| **All three measured flavonol products** | **1.224925** | **1.146276** | **+6.42%** | **0.0254** |

The original source 47-taxon, six-state test meets the frozen positive-direction and one-sided P≤.05 criterion: `SUPPORTED_RETROSPECTIVE_WITHIN_SOURCE_EXPRESSION_TO_PRODUCT_TRANSFER`. Among 47 source recipient species, **28 improve** and **19 worsen**. The permutation null mean gain was **−5.52%**, and its 2.5–97.5% quantiles were −14.60% to +6.47%. Hence the observed +6.42% gain is **near the upper null boundary**, not a large effect.

The three original measured products show heterogeneous descriptive contributions (not individual tests):

| Metabolite | Class-only MSE | Gene + class ridge MSE | Relative gain |
|---|---:|---:|---:|
| Myricetin | 1.332881 | 1.355754 | **−1.72%** |
| **Quercetin** | **1.195458** | **1.014275** | **+15.16%** |
| Kaempferol | 1.146436 | 1.068798 | **+6.77%** |

The effect is therefore **mainly associated with quercetin** in this cohort. After the primary outcome was opened, we did not promote quercetin into a new single-compound primary analysis or assign a new P to any of the three.

### Heterogeneous pigment classes, influence and post-outcome robustness

Individual original same-sixbit-state improvement is positive in **4 of 6** classes, negative in the other two. The strongest positive descriptive state is `000011` (+23.05%), with source `000000` (+7.54%), `000110` (+1.77%), and `000111` (+12.58%). Codes `000010` (−6.97%) and `000100` (−8.23%) are negative.

The four genes' same-alpha=10 mean prediction gain is **positive under every one of 47 recipient-loss omissions**, with a source range **+4.09% to +8.71%**. Those calculations omit the scored recipient losses **without refitting the predictor or changing training variances** and are not independent validation experiments. Importantly, the **three recipients with the largest positive contribution** (`BRJA`, `LEAL`, `PBON`) account for **36.86%** of all positive error improvement. Deleting those *three* evaluated recipient losses together reduces the aggregate gain from +6.42% to **+0.34%**, a substantial attenuation. This was an **outcome-ranked, post hoc stress test**, not a valid new cohort or a second primary result. The fixed result must not be described as robust to multiple simultaneous influential species omissions.

At the predeclared descriptive alpha sensitivities, practical gains remained positive: **+3.58%** for alpha=1 and **+5.44%** for alpha=100. This does **not** select a better lambda than original alpha=10 or assign P values to those alternative models.

## Biological interpretation, no premature mechanism

There are now **three distinct observed source layers**:

1. Phylogenetic proximity within an identical measured anthocyanidin-presence state makes the original fixed four-gene flavonol-related **expression** modestly transferable (original **+5.61%, Holm P=.0003**).
2. The same phylogenetic proximity does **not** make the **accumulated flavonol quantities** better than source full-class mean (**−24.08%**, chemical Holm P=.3545).
3. **Directly measured expression** of those four related genes in the predicted species does carry modest additional statistical information on actual source flavonol amounts (**+6.42%**, source vector-permutation P=.0254) after accounting for the known anthocyanidin-presence class.

This resolves an important apparent contradiction: *ancestry as an indirect proxy for expression is not the same information as the measured expression state itself*. It does **not** establish regulatory ancestry causes flavonol metabolite accumulation or proves a phylogenetic memory half-life difference. Different gene/expression and compound target transformations, environmental effects, posttranscriptional control, species phylogenetic relatedness and extraction/batch differences remain plausible confounders. The present null permutes expression vectors among tips within pigment classes and therefore may not be valid under strong residual within-class phylogenetic autocorrelation: P=.0254 is **conditional on that exchangeability assumption**, not a phylogenetic-blocked or phylogenetic mixed-model P.

No floral UV reflectance, pollinator preference/visits, flower pigment optical effects, coevolution, population ecology or direct fitness outcome is measured in this test. The metabolite difference could be ecologically relevant but that relevance is a **hypothesis**, not an empirically confirmed pollinator-mediated relationship.

These original 47 species remain **one source radiation**; no independent source-matched radiation validates the gene-to-product effect, and no formal signed difference-of-effects inference compares the previous nearest2 regression with this new expression-conditioned model.

## Reproducibility and manuscript freeze

- Frozen design: `data/petunieae_flavonol_expression_to_product_design_v0_1.json`.
- Runner: `scripts/analyze_petunieae_flavonol_expression_to_product_v0_1.py`, training-only vectorized ridge LOOCV proven numerically identical to explicit 46-tip foldwise refitting on synthetic data.
- Durable result: `results/petunieae_flavonol_expression_to_product_v0_1/summary_v0_1.json`, complete original 47-tip evaluation/loss source result archived as [GitHub Actions artifact 12258141863](https://github.com/zuizui0223/chun/actions/runs/39407372990/artifacts/12258141863). The original genetic data, class labels, measured mg/g, and 21-gene fixed source SHA checks were all passed.
- GitHub CI: [original source run 39407372990](https://github.com/zuizui0223/chun/actions/runs/39407372990) passed all five held-out data-frame/source tests; repeat CI requires original full-source recomputation and exact core numerical result.
- Frozen original **Camellia** AJB Paper1 and **Evolution Letters** v0.3 first-submission contracts, the earlier **Petunieae** 21-gene original prediction FAIL, the functional/chemical source component results and the Erica noncommensurable exploratory result are all unchanged.

**Status:** Retrospective positive conditional association at one source-defined biochemical resolution, source-specific and fragile to multiple influential species. Not independent evolutionary-memory generality, causal molecular mediation, or tested ecological/fitness mechanism.
