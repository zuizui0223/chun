# Petunieae: which parts of the flavonoid pathway retain ancestry within fixed pigment states?

**2026-10-19 — Source-specific retrospective result and subsequent outcome-opened diagnostics.**

## Scientific question

Earlier matched data in Wheeler et al. (2023; DOI `10.1098/rspb.2023.0275`) established phylogenetic structure of 21-gene floral expression **among 47 taxa with the same measured anthocyanidin-presence code**, after conditioning linearly on all nine assayed pigment abundances and six source pigment-state fixed effects. On the exact original 183 same-code species pairs, its source-held adjusted rank correlation is **rho +0.511199**, residual-vector permutation P **0.0002**. The correlation remains observational and taxon-dependent, not a molecular-selection mechanism or a validated interspecific prediction rule.

Does that history occur only in the terminal anthocyanin output machinery, or also in earlier shared and branched flavonoid functions?

## Three fixed functional partitions — direct data reanalysis

The **21 original annotated genes were partitioned exactly once** before calculating these module-specific outcomes (source values were already public and previously inspected for other endpoints). Same taxa, tree, six fine pigment-state classes, nine pigment nuisance columns and expression normalization were carried through unchanged. The three groups are *not* matched housekeeping/control gene sets:

| Fixed gene function | Genes | Residual expression/tree rho | Nominal P | 3-module maxT P | Predeclared module decision |
|---|---:|---:|---:|---:|---|
| Anthocyanin late synthesis, decoration and transport | 9 | **+0.215146** | 0.0108 | **0.2709** | NOT SUPPORTED after familywise adjustment |
| Flavonol branch and activating regulators | 4 | **+0.372517** | 0.0036 | **0.0162** | POSITIVE exploratory |
| Shared early biosynthesis and mixed regulators | 8 | **+0.458260** | 0.0006 | **0.0007** | POSITIVE exploratory |

All three modules have positive observed rho, including the late/output group. The late module's **nominal one-sided P = 0.0108** does not survive the originally frozen raw-statistic familywise maxT adjustment. It would be incorrect to say terminal pigment genes demonstrably lack evolutionary history. A **difference in P values does not directly test a difference in effect sizes**, and there is no valid housekeeping-expression genome-wide negative control.

Reproduction: `data/petunieae_functional_module_memory_design_v0_1.json`, `scripts/analyze_petunieae_functional_module_memory_v0_1.py`, exact `results/petunieae_functional_module_memory_v0_1/result_v0_1.json`, and CI [#39202948995](https://github.com/zuizui0223/chun/actions/runs/39202948995). All modules originate from **one** Petunieae radiation, not three independent radiations.

## Impact of removing one published species or pigment state

A separate **post-outcome** source audit `scripts/audit_petunieae_functional_module_influence_v0_1.py` refits the exact source nuisance projection on each remaining frame. All three module rho values remain positive for **47/47 leave-one-tip analyses** and **6/6 leave-one-fine-state analyses**. The observed order early/regulatory `>` flavonol `>` late/output occurs in **46/47** tip deletions and **6/6** fine-state deletions.

This is meaningful *descriptive influence stability*, not 53 independent validation experiments or a formal test of a module-effect difference. Reproduction: [#39203476760](https://github.com/zuizui0223/chun/actions/runs/39203476760).

## Does unequal gene count explain the ordering?

We subsequently performed a second **post-outcome, no-P-value** check using **every possible four-gene combination** within each of the three already defined, nonoverlapping modules — not a selected subset. The full original source is checked and the same nuisance projection applied before any four-gene subpanel score.

| Original module | Four-gene subpanels | Median within-state adjusted rho | Range | Positive |
|---|---:|---:|---:|---:|
| Late anthocyanin output (9 genes) | 126 | **+0.17093** | −0.11075 to +0.56051 | 108/126 |
| Flavonol branch (4 genes) | 1 | **+0.37252** | fixed four-gene panel | 1/1 |
| Shared early and regulatory (8 genes) | 70 | **+0.36664** | +0.08130 to +0.54473 | 70/70 |

Across the **8,820 combinations of one fixed early-four and one fixed late-four subset**, the early subset has greater rho in **6,469 combinations (73.3%)**. No empirical P value is attached: these repeatedly overlapping gene combinations are **not independent biological observations**. Several late-output subsets still show substantial historical structure, and the early group does not dominate every possible late group.

Thus the descriptive ordering is **not solely an artifact of comparing 8 measured early genes against 9 late genes**; the source cannot exclude gene-specific variance, correlated expression or alternative module classifications as contributing factors.

## How much expression variance remains after measured pigment adjustment?

Using the same 47-tip least-squares projection onto six pigment-presence state dummies and the nine predeclared pigment-abundance covariates, we can decompose the sum of squared **standardized** expression values remaining outside that nuisance subspace:

| Module | Fraction of standardized expression variation remaining | Raw unadjusted rho → pigment-adjusted rho |
|---|---:|---|
| Late/output | **44.0%** | +0.2410 → +0.2151 |
| Flavonol/activation | **41.5%** | +0.4819 → +0.3725 |
| Early/shared/regulatory | **56.2%** | +0.5965 → +0.4583 |

The early/shared/regulatory genes retain somewhat more **source-standardized variation not linearly described by the assayed pigment concentrations and presence classes**, and retain a stronger descriptive ancestry-distance association in this one radiation. The nuisance projection is not a causal variance decomposition: it includes correlated pathways, phylogenetic confounders and possibly measurement effects. Nor can these results establish stronger genetic constraint or different evolutionary half-lives.

The 197 full four-gene panels, ten eight-gene panels, raw/adjusted rho values and conserved source-alignment checks were computed without new permutations or significance testing. Their full original result is archived in [the GitHub Actions artifact](https://github.com/zuizui0223/chun/actions/runs/39204012833/artifacts/12165170748); the durable condensed result is `results/petunieae_module_gene_count_and_chemistry_v0_1/summary_v0_1.json`.

## Implication and a falsifiable biological hypothesis

The positive fine-chemistry-conditioned full-pathway effect is **not only traceable to the terminal pigment-output enzymes**. In the original data, history is detectable within early/shared/regulatory and flavonol-related genes. A biologically plausible explanation is that **earlier shared flavonoid capacity and transcriptional regulation can preserve historical organization even as terminal flower colour converges**. This might arise through metabolic pleiotropy or regulatory-network architecture, but this dataset does **not** distinguish these hypotheses from generic phylogenetic transcriptomic conservation or common measurement biases.

This is a proposal for a *separately matched, future test*, not a proven new universal law. Specifically, comparable source trees, pigment profiles and expression/housekeeping controls from a second radiation, and preferably fitness and pollinator interactions, would be needed to connect pathway ancestry to selection or phenotype evolution.

**Important exclusions:** in the retained 47-species frame only Del/Pet/Malv of the nominal six assayed anthocyanidins vary; Pel/Cyan/Peon are absent following the preexisting rare-state filter. These analyses do not establish general regulation of all pigment families. The frozen nearest-two-relative expression prediction remained **NOT SUPPORTED** against full-class means. The independent Erica name-level visible-hue analysis remains `NOT_SUPPORTED` for its **different**, less commensurable source question.

### Manuscript governance

This is a retrospective **mechanistic enrichment** of the integrated paper proposal, not a new temporal cross-radiation slope, direct matched origin count, causal proof, independent validation or manuscript submission. Draft integration PR #414 and its stacked functional work PR #426 remain draft; the original Camellia AJB Paper 1 and Evolution Letters v0.3 frozen submission routes are unchanged.
