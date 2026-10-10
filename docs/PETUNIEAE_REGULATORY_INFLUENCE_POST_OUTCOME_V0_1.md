# Petunieae regulatory-memory gene/state influence audit v0.1

**Status:** POST-OUTCOME DESCRIPTIVE DIAGNOSTIC ONLY. This is stacked on the integrated-proposal PR #414, not a change to frozen Camellia AJB Paper 1 or Evolution Letters v0.3.

## Question and exact frame

Does the positive Petunieae association between patristic distance and **nine-pigment-abundance-adjusted 21-gene expression distance**, among species with identical anthocyanidin-presence states, disappear when a single gene or a single retained pigment-presence class is removed?

- Original source: Wheeler et al. (2023), DOI 10.1098/rspb.2023.0275, source OSF artifact `10039433384`, GitHub Actions run `34182646549`.
- Source import verifies the three original frozen SHA256 hashes, authoritative table/tree alignment, and original six-class frequency gate before any calculation.
- Frame: 47 retained taxa, 183 unordered within-identical-code species pairs, six retained fine codes. The 12 originally excluded tips **remain excluded**, and pelargonidin/cyanidin/peonidin presence is invariant zero in the retained 47.
- Fixed covariates: six original pigment-presence-class dummies and all nine frozen compound-abundance columns. Rank 12 on full frame.
- Frozen adjusted benchmark: Spearman rho **+0.511199259788796**, one-sided 9,999 residual-permutation **P=0.0002**. Original inferential test is unchanged.

## New analysis (no new hypothesis test)

1. Fit exactly the existing fixed-effects residual projector; compute 21 **leave-one-gene-out** pooled within-class rho values using the remaining 20 gene residuals on the same 183 pairs. Original 47-tip feature standardization is unchanged.
2. Remove each of the six chemical-presence codes entirely, then **refit the same fixed nuisance model on the remaining taxa**, retaining the original feature scaling. Recalculate pooled within-code rho. This protects against an apparent whole-sample trend determined by one code.
3. Compute six **within-code** rho values from the original unchanged 47-tip residual fit as a descriptive concentration check. Within-code sample sizes are 6, 6, 6, 10, 6, 13 taxa, respectively; within-code species pairs are dependent.

No new threshold, class recoding, cherry-picked gene subset, P value, tuned k, null benchmark, or success gate is defined. These are all **retrospective source-exposed influence diagnostics**, not external validation.

## Exact hosted replay: 2026-10-10

GitHub Actions run [38045486129](https://github.com/zuizui0223/chun/actions/runs/38045486129) retrieved the original 23,338-byte artifact, passed all source hashes, ran **4/4 synthetic and contract regression tests**, and recovered rho +0.511199259788796 before calculating any influence summaries.

| Exclusion | Positive outcomes | Minimum rho | Median rho | Maximum rho |
|---|---:|---:|---:|---:|
| Leave one gene (21 analyses) | 21 / 21 | +0.434520 | +0.497842 | +0.570901 |
| Leave one six-bit fine code (6 full-refit analyses) | 6 / 6 | +0.324094 | +0.478436 | +0.511140 |

The **within-code** full-frame descriptive checks were:

| Code | Taxa | Pairs | rho |
|---|---:|---:|---:|
| 000000 | 6 | 15 | +0.170652 |
| 000010 | 6 | 15 | +0.216400 |
| 000011 | 6 | 15 | +0.448456 |
| 000100 | 10 | 45 | +0.370469 |
| 000110 | 6 | 15 | **−0.072471** |
| 000111 | 13 | 78 | +0.264593 |

One class has a slightly negative descriptive within-code rho. Consequently **do not assert a positive signal in every chemical state**. The all-class residualized signal is not reducible to any one gene or one excluded-class analysis, but class-specific signals differ and the six individual correlations are especially imprecise at n=6.

## Biological and inferential interpretation

**Bounded conclusion:** Petunieae retained within-pigment-state phylogenetic organization in pathway gene expression after conditioning on observed pigment quantities. On the fixed design and species sample, that structure is not erased by any one gene deletion or any one chemical-state exclusion.

This does **not** show hidden causal variants, fitness benefits, adaptive canalization, absolute memory half-life, regulatory-module substitution, independent genetic evolutionary origins, or a universal molecular-memory scale. The source remains a single retrospective radiation; plant phylogeny and possible technical factors remain confounded. Within-taxon permutations do not yield 183 independent biological replicates. Genes are correlated measurements, not 21 independent evolutionary events.

The frozen **two-nearest-relative prediction failure** (9.91% larger normalized MSE than the all-donor within-pigment-state mean) remains untouched. Structural association can be present while that particular fixed predictive borrowing scheme loses to the group-wide estimate; this is a source-specific result, not a novel universal fact.

**Publication consequence:** These diagnostics strengthen the **within-Petunieae robustness** part of the proposed one-paper narrative. They do not remedy the original absence of independent matched-radiation regulatory/chemical/phylogenetic data, and **do not authorize merging** frozen AJB and Evolution Letters first-submission routes.

## Reproduction

```bash
python scripts/audit_petunieae_regulatory_influence_v0_1.py \
  --source build/petunieae_frozen_source \
  --out build/petunieae_regulatory_influence_v0_1.json
pytest -q tests/test_petunieae_regulatory_influence_v0_1.py
```

The `petunieae-regulatory-influence-v0-1.yml` workflow downloads the frozen source by explicit original run and artifact name; it saves the **full per-gene and per-code results JSON** as a run artifact. The present version-controlled document includes exact headline and per-code values rather than allowing users to silently elevate sensitivity checks to new formal evidence.
