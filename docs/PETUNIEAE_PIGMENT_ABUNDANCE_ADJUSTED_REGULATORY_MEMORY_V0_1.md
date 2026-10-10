# Petunieae regulatory memory after adjustment for measured pigment abundance — v0.1

**Decision:** `RETROSPECTIVE_SUPPORT`; specific new estimator fixed before its outcome was opened. The underlying Petunieae source had already been outcome-exposed for other analyses, so this is **not an independent prospective validation**. This result supplements the previously frozen 47-tip expression-memory and nearest-two predictor results; neither is changed.

## Biological alternative

The original source-matched Petunieae result found that even among species with an **identical fine six-bit anthocyanidin-presence state**, phylogenetically closer tips had more similar expression profiles of 21 floral pigment-network genes (Spearman rho = +0.60744; P = 0.0001 under taxon-vector permutations). Because identical binary pigment presence need not imply identical *concentration*, this could conceivably reflect unmodelled pigment abundance differences.

This new analysis specifically asks whether a phylogenetic relationship remains in **gene-expression residuals** after linearly adjusting for all nine measured pigment amounts and a fixed effect for each of the six retained pigment states.

## Retained source and data boundary

- Original source: Wheeler et al. (2023), DOI `10.1098/rspb.2023.0275`; OSF `zg9cu`.
- Exact source checks: the previously frozen phyloCCA expression/pigment table, 11-gene dated source tree and source analysis R script, all SHA-256 matched.
- The **same 47 species** from the already frozen minimum-five-tips per fine class gate. **Twelve of 59 ingroup species remain excluded**; the new analysis does not relax the original admission rule.
- **183 unordered taxon pairs** share one of six retained exact six-bit pigment-presence states.
- Of six nominal anthocyanidin-presence assay components, only Del/Pet/Malv vary in the retained frame. Pel/Cyan/Peon are all zero there. This constrains the biological scope of the result.
- Twenty-one original floral structural/regulatory gene columns. No gene-by-gene selection.

## Frozen adjustment and permutation

Per 47-tip source frame, we used `log1p(TPM10K)` and column-wise population standardization of gene expression, `log1p(100 × mg/g)` and analogous standardization of all nine measured pigment columns, with constant-zero columns contributing zero. The nuisance design consists of six exact pigment-state indicator columns and nine predefined pigment-concentration columns. Its observed matrix rank was **12**.

Let `G` be the 47 × 21 standardized expression matrix and `D` the fixed nuisance design. We obtained residualized expression `R = (I − D D⁺)G`. For the 183 same-fine-state tip pairs, we computed RMS expression-residual distance and tested its rank correlation with source-tree patristic distance.

The 9,999-draw null exchanges **whole 21-gene residual vectors** among species **only within identical fine pigment states**, then reapplies the same residual projector for each draw (a constrained Freedman–Lane-style residual permutation). No pair is considered statistically independent. The primary one-sided prediction was an observed rank correlation exceeding the null mean and P ≤ 0.05, with seed `20261010`.

Important qualification: the residual-exchangeability null is approximate, and partialling out the measured pigment concentrations does not condition on every possible biochemical, environmental, developmental or technical covariate.

## New result

| Quantity | Value |
|---|---:|
| Same-class species / unordered pairs | 47 / 183 |
| Unadjusted gene-expression distance–tree distance rho | **+0.60744** |
| After pigment abundance and exact-state adjustment | **+0.51120** |
| Conditional residual-vector permutation null mean rho | +0.09533 |
| Centered adjusted rho minus null mean | **+0.41587** |
| Null central 95% interval | −0.08297 to +0.34566 |
| One-sided 9,999-permutation P | **0.0002** |
| Gene-expression sum-of-squares retained in the residuals | 48.17% |
| Leave-one-species-out residual rho | +0.43122 to +0.55689; **47/47 positive** |

**Interpretation:** under this specific nine-pigment/fine-state adjustment, phylogenetic proximity still predicts similarity in the residual 21-gene expression phenotype. This supports **historical organization not exhausted by the assayed pigment identity and abundance**, in one Petunieae source. It does **not** establish that the pigment-regulatory program is genetically causal for species colour differences, or that this effect transports to independent radiations or all possible pigment pathways.

## Relation to the separately frozen held-out prediction

The nearest-two relative predictor still has **NOT_SUPPORTED** status versus the all-other-same-pigment-class mean:

- class-wide mean MSE 1.13838;
- same-class random-two expected MSE 1.40594;
- two closest relatives MSE 1.25117;
- relative gain against class mean −9.91%.

The algebraic donor-count diagnostic showed a positive phylogenetic locality benefit against random two donors, but that does not rescue failure against the lower-variance full-class baseline. **The present residualized association is a different estimand and must not be used to relabel the nearest-two prediction as PASS.**

## Evidence hierarchy and manuscript ceiling

The integrated paper now has:

1. standardized visible-colour hidden memory across **18/21** opportunity radiations (exploratory on a shared source ontology);
2. independent **visible-colour prospective PASS** in *Rhododendron* sect. *Schistanthe*;
3. prospective **biochemical FAIL** in Gesnerioideae;
4. in one retrospective, same-source 47-tip Petunieae radiation, fine pigment-state memory inside coarse pigment status, and gene-expression history inside those fine states that **persists after adjusting for measured pigment abundance**;
5. a separate **negative** test of the practical two-relative predictor.

The additional Petunieae association is biologically relevant but remains **one independent phylogeny**, not a cross-radiation test connecting molecular repeatability to the 32-clade temporal decline. No ecological selection cause or general cross-representation law has been demonstrated.

## Reproducibility and provenance

- Frozen design: `data/petunieae_pigment_abundance_adjusted_regulatory_memory_design_v0_1.json`; created before running this new estimand.
- Runner: `scripts/analyze_petunieae_pigment_adjusted_regulatory_memory_v0_1.py`.
- Exact result: `results/petunieae_pigment_adjusted_regulatory_memory_v0_1/result_v0_1.json`.
- Hosted run: https://github.com/zuizui0223/chun/actions/runs/38013192771.
- Unit tests: `tests/test_petunieae_pigment_adjusted_regulatory_memory_v0_1.py`.
- No changes to Camellia Paper 1 science v0.2.2 / framing v0.3.4 / AJB upload v1.0 or frozen Evolution Letters v0.3.
