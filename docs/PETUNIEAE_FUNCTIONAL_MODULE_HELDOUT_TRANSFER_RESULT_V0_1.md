# Petunieae: ancestral proximity predicts flavonol-module expression, but not every pigment pathway module

**New source-internal empirical result (2026-10-19).**
Original published matched Wheeler et al. (2023) source: DOI **10.1098/rspb.2023.0275**, OSF `zg9cu`, and the unchanged SHA-verified 47-taxon/6-exact-anthocyanidin-state combined pigment + 21 gene-expression source archive from GitHub Actions run `34182646549`.

## What was predicted, not merely correlated?

The earlier conditioned biochemical molecular phylogenetic analysis found residual gene-expression similarity among species with **identical measured six-anthocyanidin-presence profiles** on the same original dated species tree. However, the previously frozen **whole 21-gene practical prediction** using each species' **two closest same-state relatives** was worse than the mean of all other same-state species: original training-scaled mean square error (MSE) **1.251167 vs 1.138379**, relative gain **−9.91%**, `NOT_SUPPORTED`.

The new **three fixed functional gene sets** were already defined before this module-level predictive analysis. Its specific prediction/loss framework was fixed in `data/petunieae_module_heldout_transfer_design_v0_1.json` before opening the new outcomes (the public source and 21-gene / module correlation results were already outcome-exposed; therefore strictly **retrospective**).

- For each of the same **47** published species, assume its measured **six-bit pigment-presence class is already known**. Hold out its expression vector.
- Predict original log1p(TPM10K) expressions from either (i) the mean of **all** other species in the same pigment class (full-donor baseline), or (ii) the mean from the **two** phylogenetically nearest species in that identical class, with the previously frozen tree-distance/name tie-breaker.
- Compute squared error normalized by the *other 46 species' training-only per-gene variance*, average all source genes within the **predefined 9/4/8-member module**, then average equally across all 47 withheld taxa. No extra standardization used the held-out species.
- The three positive-tail **phylogenetic locality** null P values came from 9,999 permutations of intact 21-gene species expression vectors *within the existing six pigment codes*, preserving multigene covariance and the entire source tree. Multiplicity was addressed by **Holm adjustment across exactly three functional modules**.
- An exploratory *operational* PASS requires **both** strictly positive gain over the **full-class mean baseline** and Holm-adjusted locality P ≤0.05. A method which merely outperforms random two donors, or the permutation-null average while still performing worse than class mean, is **not a practical predictor**.

## Frozen observed result

| Original fixed gene module | Number genes | All-other-same-class MSE | Closest two MSE | Relative practical gain | Within-class permutation nominal P | Holm-adjusted P | Fixed decision |
|---|---:|---:|---:|---:|---:|---:|---|
| Late anthocyanin output, decoration and transport | 9 | 0.833609 | 0.959914 | **−15.15%** | 0.0597 | 0.1042 | NOT SUPPORTED |
| **Flavonol branch and activators** | **4** | **0.975530** | **0.920767** | **+5.61%** | **0.0001** | **0.0003** | **SUPPORTED — exploratory same-radiation heldout transfer** |
| Early shared flavonoid reactions and mixed regulators | 8 | 1.562670 | 1.744028 | **−11.61%** | 0.0521 | 0.1042 | NOT SUPPORTED |

The four fixed flavonol-associated genes are `F3primeH`, `FLS`, `MYBFL`, `MYB12`. *F3′H is a branching hydroxylation enzyme, not specific exclusively to flavonols*. The result is not proof of one causal flavonol gene family or a module-by-module evolutionary-rate difference.

**Biological surprise:** a pigment-abundance-adjusted phylogenetic correlation does not guarantee that the two nearest relatives are the best predictor for an unseen source species. Early/shared/regulatory genes had the strongest earlier within-state expression-distance tree correlation (rho **+0.45826**, original maxT-adjusted P **0.0007**), yet the full-class baseline predicted their held-out expression better than the nearest-two donor mean. In contrast, flavonol-associated genes had the intermediate earlier rho **+0.37252** (maxT P **0.0162**) but showed a **measurable 5.6% improvement** from lineage proximity in the new exact-source 47-species evaluation. The original 21-gene prediction FAIL remains unchanged.

### What the class structure allows us to say

In the original six pigment-presence classes, the *flavonol-associated* module's nearest-two gain was positive in **four** and negative in **two** separately defined classes. This must be stated even though the pooled 47-species improvement was positive. Original per-class gains were:

| Exact original six-bit source code | N species | Flavonol source gain vs full class mean |
|---|---:|---:|
| `000000` | 6 | +21.50% |
| `000010` | 6 | −1.56% |
| `000011` | 6 | +5.98% |
| `000100` | 10 | +6.30% |
| `000110` | 6 | −5.16% |
| `000111` | 13 | +1.55% |

A strictly **post-outcome descriptive** recipient-loss influence calculation removes one of the six pigment classes at a time from the **already-computed** held-out evaluations *without changing the original donor weights or training variances*. The pooled flavonol module gain remains positive in **six out of six** such omissions, ranging **+1.20% to +7.57%**. Both late-output and early/shared-regulatory gains remain negative under all six omissions. This is *not* six new independent replication tests, and no P was recomputed or newly interpreted on subsets.

The 47 held-out taxa share the same single phylogeny and the training folds overlap; the permutation treats a taxon vector as the unit. The evaluation is a **source-internal cross-validation**, not validation in a new radiation or laboratory phenotype-prediction experiment. Importantly, the target's **exact biochemical class is assumed known**, so the method does **not** infer unknown flower colour or unknown metabolite presence from DNA alone.

### Context, biology, and negative controls

A direct, source-bounded biological hypothesis is that a subset of flavonoid-branching capacity retains **operationally transferable phylogenetic local structure beneath shared terminal pigment presence**, even while broader regulatory expression (and late transport/output) suffers from high-dimensional or source-specific donor variance when only two relatives are used. This is plausible but **not causally identified**. Earlier functional modules differ in size (9/4/8 genes), and the source lacks matched genome-wide housekeeping genes, replicated perturbations, identical stage measurements across radiations, and verified external independent predictions. **Significance of one module and failure of another does not test the difference of their true prediction effects.**

The original late-expression module's nominal correlation P **0.0108** and original familywise raw-maxT association P **0.2709** are a **different analysis** from the new predictive Holm P values, and their apparent disagreement cannot be used to assert evolutionary memory loss. Molecular selection, pleiotropic costs, pollinator interactions and causal evolutionary memory decay are untested. The original Petunieae retained set excludes 12 rare-state species; only delphinidin, petunidin and malvidin vary in its retained six-bit assay, so the prediction result is not a general test of all floral pigments.

## Provenance and reproducibility

- New frozen design: `data/petunieae_module_heldout_transfer_design_v0_1.json`.
- Original data identity: `data/petunieae_nested_regulatory_memory_preregistered_design_v0_1.json` plus exact OSF source artifact `petunieae-prospective-osf-v0-1`, run `34182646549`.
- Source full-gene loss baseline: `results/petunieae_nested_regulatory_leaveoneout_prediction_v0_1/result_v0_1.json`.
- Original fixed biological modules: `data/petunieae_functional_module_memory_design_v0_1.json`.
- Runner: `scripts/analyze_petunieae_module_heldout_transfer_v0_1.py`, original source-replayed output `results/petunieae_module_heldout_transfer_v0_1/result_v0_1.json`.
- Descriptive original six-state influence: `scripts/audit_petunieae_module_heldout_class_influence_v0_1.py`, `results/petunieae_module_heldout_transfer_v0_1/class_influence_v0_1.json`.
- GitHub Actions: [original source analysis run #39206856187](https://github.com/zuizui0223/chun/actions/runs/39206856187); all five prediction test assertions passed after a test-file newline typo was fixed.

The original first-submission Camellia/AJB and frozen EL v0.3 scientific assets remain unchanged; the integrated CHUN and this functional extension remain stacked Draft PRs only.
