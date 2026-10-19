# Petunieae: ancestral signal inside anthocyanidin-identical flowers is not confined to late anthocyanin output (2026-10-19)

## Evidence status

**One-radiation, retrospective, source-exposed functional-subspace result — not cross-radiation proof and not a formal between-module effect test.** Exact outcomes are recorded in `results/petunieae_functional_module_memory_v0_1/result_v0_1.json`. The module map and 9,999-shuffle maxT null were committed **before computing the new module outcomes**, but the original source, its pigment patterns and the 21-gene full-network positive result were already known; this is **not prospective external validation**.

## New biological question

The preexisting Wheeler et al. (2023), DOI `10.1098/rspb.2023.0275`, data had shown that expression distances among 47 species sharing exactly the same original six-anthocyanidin-presence signature still increase with molecular source-tree patristic distance, after controlling linearly for all nine measured flavonoid abundances and the six source pigment-presence classes. The whole-network rho was **+0.511199**, conditional residual-vector permutation **P=0.0002**.

But **phylogenetic similarity in gene expression is not automatically specific to the visibly relevant pigment-production steps**. In this study, where in the pathway does the residual phylogenetic signal actually appear?

All original 21 genes were assigned exactly once to **three functionally annotated, nonoverlapping groups** before calculating this new set of statistics:

| Fixed module | Source gene axes | Genes |
|---|---:|---|
| Late anthocyanin hydroxylation, execution, decoration, transport | 9 | F35H, DFR, ANS, UFGT, AAT, 5GT, MTlike, GST, 3RT |
| Flavonol branch and activation | 4 | F3primeH, FLS, MYBFL, MYB12 |
| Early shared flavonoid steps and mixed transcriptional regulation | 8 | CHS, CHI, F3H, MYB27, AN11, AN1, JAF13, MybsG6 |

The last group **includes anthocyanin regulators**, so it is not a housekeeping/non-pigment negative control. F3primeH is at a branch junction; the annotations are an interpretable functional partition rather than orthogonal causal gene pathways.

## Full measured result from exact original-source replay

Using the **same 47 species, 183 exact same six-bit pigment-state unordered taxon pairs, same tree, original nine-pigment/six-state residual projector**, 9,999 within-fine-class shuffles of the **entire 21-gene expression vector** (seed 20261019), the three source modules yielded:

| Module | Within-exact-pigment rho | Permutation null mean | Nominal one-tail P | MaxT-adjusted P (3 groups) | Exploratory result |
|---|---:|---:|---:|---:|---|
| Late anthocyanin execution | **+0.21515** | −0.06076 | 0.0108 | **0.2709** | **NOT_SUPPORTED after 3-group adjustment** |
| Flavonol branch | **+0.37252** | +0.05110 | 0.0036 | **0.0162** | **positive conditional signal** |
| Early/shared and transcription regulators | **+0.45826** | +0.13792 | 0.0006 | **0.0007** | **positive conditional signal** |

The original full-21-gene adjusted rho **+0.511199259788796** was recovered numerically before calculating module outcomes; its original P **0.0002** and the separately frozen k=2 nearest-relative predictor **FAIL** remain unchanged. Regression and hosted GitHub Actions source replay completed successfully.

### What is genuinely surprising here?

The residual ancestral similarity associated with the whole 21-gene floral pigment network is **detectable in the flavonol-associated branch and early/shared regulation**, whereas late anthocyanin output does **not** meet the **three-module adjusted** significance threshold.

This is biologically consistent with a **layered/latent biochemical-history** view: taxa that currently express the same final detected anthocyanidin-presence class may nevertheless retain phylogenetically structured information in upstream flavonoid supply, co-pigment/UV-absorbing flavonol biology and regulatory capacity. It is an empirical step toward asking how a phenotype can be accessed again under changing pollinator or abiotic contexts, but this dataset does **not** demonstrate future reversibility or ancestral reactivation.

### Why this does not mean "late-pathway memory disappeared"

- **The difference between module correlations was NOT directly tested.** A maxT-corrected positive result for one group but not another is **not evidence that the groups' true effect sizes differ**. The groups have unequal gene-axis counts (9, 4 and 8), unequal covariance/noise and unequal null distributions. The late module's nominal P=0.0108 is positive-directional; its adjusted P=0.2709 is not a biological zero.
- The null's maxT adjustment is an exploratory familywise positive-signal screen under the source-defined within-fine-class exchangeability hypothesis. It is not a randomized experiment or evidence for causal differences in evolutionary rates.
- **No housekeeping transcriptome-wide control gene set** is available in the admitted processed source. Significance in upstream shared genes could reflect ordinary inherited gene-expression differences, taxonomic assembly/cross-species-normalization effects, or modules affected by unrelated developmental processes.
- The 47 retained taxa cover six fine pigment-presence codes, but only **Del/Pet/Malv vary** after rare-state exclusions; all Pel/Cyan/Peon are zero. Ancestral shifts into other anthocyanidin branches are not represented within this cohort.
- The 183 dependent pairs are not species-independent historical origins. There is no supported inference about when the signal decays over **absolute time**, causal mutations, pollinator selection, adaptation, or re-evolution of anthocyanin.
- Gene function partition was chosen using known biology **after the original whole-network result had been opened**. The specific three-group outcomes were not previously opened, yet their inferential strength is exploratory; avoid describing this as prospective discovery of gene modules.

## Effect on the manuscript decision

This does **add a nontrivial molecular-layer insight within one matched radiation** to the integrated CHUN temporal synthesis: *final chemical pigment-state identity does not exhaust ancestry-dependent differences in upstream biochemical/regulatory potential*.

It **does not yet** bridge the original Flower-clades-51 cross-radiation temporal memory slopes to gene-function effects, nor turn Erica's distinct named-taxon/visible-hue null into a formal biological counterexample. Therefore **keep Draft integrated paper** and retain the frozen Camellia AJB and Evolution Letters v0.3 candidate submissions independently.

### Source, code and new exact outputs

- Frozen source: Wheeler et al. 2023 OSF node `zg9cu`, GitHub Actions original artifact `34182646549`.
- Design: `data/petunieae_functional_module_memory_design_v0_1.json`.
- Runner: `scripts/analyze_petunieae_functional_module_memory_v0_1.py`.
- Exact result: `results/petunieae_functional_module_memory_v0_1/result_v0_1.json`.
- Reproducible test: `tests/test_petunieae_functional_module_memory_v0_1.py`.
- Workflow: `.github/workflows/petunieae-functional-module-memory-v0-1.yml`.

**Source-text novelty boundary:** Wheeler et al. (2023) already reported flavonol/anthocyanin gene co-expression modules and how the branching pathway shapes accessible floral pigment phenotypes. The *new* CHUN statistic is specifically **phylogenetic structure within identical measured pigment-presence states after pigment-abundance adjustment**, disaggregated by original biological functional subspaces. Do not relabel the previously published co-expression insight as this paper's first discovery.

## Post-outcome influence audit: robust ordering, NOT a significant between-module difference

A separately source-replayed descriptive diagnostic now recomputes all three fixed module correlations after deleting **each of 47 species** and re-fitting the original pigment/state nuisance projection, then after deleting **each of the six fine pigment presence codes** and refitting. No new permutations or P values were computed for these deletions.

| Functional group | Leave-one-tip rho range (47) | Positive tip deletions | Leave-one-pigment-code rho range (6) | Positive code deletions |
|---|---:|---:|---:|---:|
| Late anthocyanin execution | +0.1066 to +0.2674 | 47/47 | +0.0533 to +0.3046 | 6/6 |
| Flavonol branch | +0.2944 to +0.4683 | 47/47 | +0.2154 to +0.4307 | 6/6 |
| Early/shared + regulators | +0.3674 to +0.5282 | 47/47 | +0.3425 to +0.4950 | 6/6 |

In **46/47 single-tip deletions** and **6/6 whole-code deletions**, the descriptive rho ordering remains early/shared > flavonol > late anthocyanin execution. These repeated omissions are **not** 53 independent evolutionary experiments and are **not** formal evidence of a different phylogenetic effect size for the pathways.

### Correction-method qualification: the late-pathway non-detection is NOT a robust "absence"

The primary **raw-rho maxT** procedure was fixed before these module outcomes; it gives 3-module adjusted P values late 0.2709, flavonol 0.0162, early/shared 0.0007. However the late module's **nominal one-sided** source permutation P is 0.0108. If the **same already observed nominal P values** were subjected to the standard step-down **Holm** adjustment instead, the three arithmetic P values would be early/shared **0.0018**, flavonol **0.0072**, late **0.0108**. This sensitivity is **post-outcome and descriptive**, not an alternative predeclared primary decision or a newly calculated permutation P.

The discrepancy reflects materially different module-specific permutation null locations/variances and conservativeness of using the raw maximum rho as the common maxT critical statistic. **Consequently the result does not establish that late anthocyanin expression lacks historical structure.** The defensible contribution is positive residual phylogenetic organization in upstream/shared and flavonol source axes, plus a stable descriptive ranking of rhos under original source omissions; NOT evidence that one group has proven less evolutionary memory or a faster memory-loss timescale.

Source files:
- `scripts/audit_petunieae_functional_module_influence_v0_1.py`
- `results/petunieae_functional_module_influence_v0_1/summary_v0_1.json`
- `tests/test_petunieae_functional_module_influence_v0_1.py`
- `.github/workflows/petunieae-functional-module-influence-v0-1.yml`
- Hosted source replay [run 39203476760](https://github.com/zuizui0223/chun/actions/runs/39203476760), three diagnostic tests passed. Full individual deletion rows are in the archived run artifact.
