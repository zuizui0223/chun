# Petunieae: expression history hidden within identical six-anthocyanidin presence states (v0.1)

**Analysis status:** `POSITIVE_EXPLORATORY`. This is a *retrospective source reanalysis*. The new statistical rule was recorded in GitHub commit `91b10bede74ead47953b7a838adf64d95c59b7ed` before calculating the new target statistic, but previous CHUN work had already exposed the source values. Do not describe the result as independent prospective validation.

## Biological test

Within one phylogeny containing the same species, can phylogenetic history still be detected in the **21-gene flavonoid expression profile** after conditioning on a considerably finer biochemical phenotype: identical presence/absence across all six measured anthocyanidins?

This test addresses a new within-radiation, cross-layer question rather than comparing two separately sampled studies.

## Verified source and retained frame

Wheeler et al. (2023), DOI `10.1098/rspb.2023.0275`, provided a dated Petunieae tree and processed data for 60 taxa with the same source keys. The pre-existing GitHub Actions source artifact `10039433384` (run `34182646549`, OSF node `zg9cu`) yielded:

- processed table SHA256 `5843d4cd4eb253046f97349fa6bd285ca77e43e7a9c3aaa0e78fae3e8e391edd`;
- dated tree SHA256 `95b4a688d3d71417b712b37a2b04cdc22a9431be3172d6509def4435f5fd8614`;
- source R script SHA256 `abbb43dbec756ca34e9f501b7eb9aaecb7330009b79739b8c1171d9cccce13b8`.

After excluding the source outgroup, the **previously frozen** rare-fine-state filter leaves 47 taxa in six exact six-bit anthocyanidin-presence states, with counts `6, 6, 6, 10, 6, 13`. The analysis examines 183 unordered same-fine-state taxon pairs. This is not a visible hue identity definition: a six-bit state says which compounds are detected, not whether the species are visually identical or whether pigment quantities are equal.

## Frozen primary estimator

1. Fix all 21 provided structural/regulatory expression columns before outcome calculation.
2. Apply `log1p(TPM10K)`, then standardize each column over the 47 retained species.
3. For pairs **already sharing one exact six-bit anthocyanidin-presence state**, compute Euclidean root-mean-square 21-gene expression distance.
4. Compute Spearman rho between frozen-tree patristic distance and that expression distance.
5. Permute the **complete multi-gene expression vector** among taxa *within each exact fine class* 9,999 times (`seed=20261008`), preserving the within-class sample counts, the tree and observed inter-gene covariance. The P value is one-sided for positive rho. Species pairs are not treated as independent inferential replicates.

## Outcome

| Quantity | Observed | Conditional permutation reference |
|---|---:|---:|
| Within-identical-pigment-class expression distance–phylogenetic distance Spearman rho | **+0.60744** | null mean **+0.16540** |
| 95% central permutation interval | — | −0.00820 to +0.36428 |
| One-sided 9,999-permutation P | **0.0001** | minimum attainable P=0.0001 |
| Leave-one-tip-out rho | +0.58538 to +0.64416 | **47/47 positive** |

Thus **phylogenetic proximity predicts similarity of gene expression even after exact anthocyanidin presence-class membership is fixed**. This is a source-specific, observational association; it does not establish a causal colour-production route or identify historical regain/loss events.

### Prespecified secondary concentration-level comparison

Using the same 47 species and 183 same-fine-class pairs but all nine anthocyanidin/flavonol measured mass fractions (log1p(100 × mg/g), per-column standardized), the distance correlation was rho **+0.21986**, one-sided P **0.0554** (9,999 within-fine whole-pigment-profile permutations; seed 20261009). This fails the 0.05 rule. Do **not** conclude that concentrations have no memory or that expression has a statistically longer retention time: **the difference of the two correlation effects was not itself tested**.

Three of the six anthocyanidin mass columns were constant zero in the frozen 47-tip frame (Pel, Cyan and Peon). They were retained as zero-variance axes with zero standardized contribution; no favourable feature selection occurred.

### Descriptive post-outcome sensitivity

Removing one entire six-bit pigment class at a time left the expression rho positive in all six analyses, ranging +0.5800 to +0.6397. This check was performed *after* seeing the primary result and is a descriptive robustness diagnostic, not additional independent validation.

## Why this helps the one-paper synthesis

The existing **same 47-species Petunieae chemical test** already finds additional fine-state phylogenetic memory within coarse anthocyanidin presence groups (conditional AUC = 0.7018; permutation-null mean = 0.5139; centered +0.1879, P=0.0001). The newly executed test moves **one layer deeper on the same phylogeny**:

```text
coarse anthocyanidin presence
    |  already measured fine six-bit pigment-state memory (+0.1879 conditional AUC)
    v
exact anthocyanidin presence signature
    |  new same-fine-class gene-expression memory (rho=+0.6074; P=0.0001)
    v
continuous 21-gene flavonoid network expression profile
```

The two metrics differ (conditional same-state AUC vs continuous molecular-distance Spearman) and must not be subtracted as if they share a scale. The new result is a **matched same-radiation hierarchy**, not a direct explanation of the 32 independently sampled Flower-clades-51 temporal slopes.

*Camellia* remains one qualitative, distinct molecular implementation case in the proposed synthesis; its RNA-seq developmental/petal-sector contrasts are not mapped to independent macroevolutionary events.

## Important alternative explanations and ceilings

- Phylogenetic correlation of gene expression is already known in many systems. The unique additional constraint here is conditioning on a fine six-bit pigment-presence state, not discovering generic transcriptomic phylogenetic signal.
- Source expression normalization, taxon sampling and potential technical differences in de novo transcriptome assembly can co-vary with phylogeny. The provided 21 pathway genes do not furnish a source-faithful housekeeping negative-control panel.
- Conditional label exchangeability within fine classes is a specific null model; this is not a process-based phylogenetic rate/causal inference.
- One radiation cannot demonstrate a universal cross-plant phenotype-to-regulation memory hierarchy; the independent *Schistanthe* test validates **visible fine-colour memory**, not this nested gene-expression result. Gesnerioideae remains a **prospective biochemical FAIL** for the earlier, different phenotype-class estimand.
- There is no direct environmental or pollinator manipulation, fitness estimate or robust shared macrohistorical event set.
- Do not treat negative secondary P=0.0554 as positive or as evidence for absence.

## Reproduction

- Frozen design: `data/petunieae_nested_regulatory_memory_preregistered_design_v0_1.json`.
- Frozen source: OSF `zg9cu` and SHA-verified GitHub Actions artifact `10039433384`.
- Analysis: `scripts/analyze_petunieae_nested_regulatory_memory_v0_1.py`.
- Outcome: `results/petunieae_nested_regulatory_memory_v0_1/result_v0_1.json`.
- CI checks: `tests/test_petunieae_nested_regulatory_memory_v0_1.py`.

The Paper 1 AJB science and the Evolution Letters v0.3 science are unchanged. This is an isolated post-v0.3 integration candidate.
