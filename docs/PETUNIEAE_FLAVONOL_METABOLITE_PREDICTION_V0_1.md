# Petunieae: conserved flavonol-associated gene expression does not predict actual flavonol amount

**Study date: 2026-10-20. Biological source result: BOTH CHEMICAL PRODUCT FAMILIES NOT_SUPPORTED for practical k=2 nearest-taxon prediction.** This is a measured, retrospective single-radiation comparison, not a negative ecological experiment or an independent second radiation.

## Question that was actually tested

The same original source supports a modest practical improvement when predicting *four fixed flavonol-branch-related gene expression values* from a target species' two nearest relatives within an identical anthocyanidin-presence class (**+5.61% MSE gain, original Holm P=.0003**, PR #427). Yet gene-expression structure need not imply stable product output. **Do the nearest two relatives also help predict original measured flavonol compounds?**

Original paper: Wheeler et al. (2023), DOI **10.1098/rspb.2023.0275**. Source: the original, SHA-verified OSF `zg9cu` dataset, archived by Actions run `34182646549`, original 60-row `phyloCCA` expression/HPLC/UPLC quantitative CSV and dated tree.

The exact **same 47 taxa**, six retained **measured anthocyanidin-presence codes**, original tree and previously frozen **k=2 same-code nearest relatives** were used. No new source sampling, binning, trait filter, gene panel selection or optimum-k search occurred. This test was fixed before its new biochemical prediction outcome in `data/petunieae_flavonol_metabolite_transfer_design_v0_1.json`, although the source and the earlier gene-expression outcomes were already exposed.

## Exact measured biochemical response groups

1. **Flavonol concentrations**: original `myr_mgg`, `quer_mgg`, `kaem_mgg` — myricetin, quercetin and kaempferol measured in mg/g.
2. **Anthocyanidin amounts in the retained fine-state frame**: original `Del_mgg`, `Pet_mgg`, `Malv_mgg` — delphinidin, petunidin and malvidin. The original rare-state retention excludes most pelargonidin, cyanidin and peonidin positive source species; these additional three nominal assayed features are zero or invariant in the retained 47 and must not be retroactively introduced as outcome-selected predictors.

For each held-out species, the target amounts are transformed as `log1p(100 × original mg/g)`. We compare the nearest-two source donors with the **mean of all other tips in the same anthocyanidin-presence class**, compute per-compound squared error scaled only by the other 46 taxa's transformed training variance, then average the three outcomes and 47 recipient errors. The original k=2 gene-expression evaluation uses a different target and therefore is shown as context rather than pooled with these chemical losses.

For the two new biological product groups, **9,999 permutations of the intact six-compound whole-taxon source vector** within the original six-bit pigmentation classes generated locality nulls. The two predeclared source targets' upper-tail permutation P values received **Holm familywise correction**. A practical source PASS requires **positive observed improvement over the full-class baseline** and corrected locality P≤0.05.

## New observed product result

| Endpoint on exact original Petunieae species | Class-average MSE | Nearest-two MSE | Practical gain vs class average | Locality P | Holm P | Predeclared decision |
|---|---:|---:|---:|---:|---:|---|
| **Flavonol-branch-associated 4-gene expression** (earlier, unchanged) | 0.975530 | 0.920767 | **+5.61%** | .0001 | .0003 (three-module family) | Positive exploratory |
| **Three measured flavonol concentrations** (new) | **1.224925** | **1.519890** | **−24.08%** | .3545 | **.3545** | **NOT_SUPPORTED** |
| **Three measured variable anthocyanidin concentrations** (new) | **0.483647** | **0.521305** | **−7.79%** | .0378 | **.0756** | **NOT_SUPPORTED** |

All three MSE pairs use source-specific, training-variance-scaled transformed targets. Expression and metabolite losses are **not chemically equivalent units or effect estimates**; relative gains are useful within each chosen endpoint but no formal statistical difference-of-gains test was performed.

The nominal locality P .0378 for anthocyanidin amount does **not** establish practical prediction: its closest-two MSE is worse than the class mean (negative gain), and the two-target Holm P becomes .0756.

### Actual source population coverage

For measured flavonol amounts, **20/47** source recipients improve with two close relatives while **27/47 worsen**. Within each of the six original fine anthocyanidin-presence classes, nearest-two prediction is worse than the corresponding full same-class average: **0/6 class-specific positive flavonol gains**. The pooled flavonol practical gain remains negative in **all 6/6 original-class recipient-only omissions**.

For variable anthocyanidin amount, **20 recipients improve and 21 worsen**; the remaining six belong to exact source code `000000`, in which all three measured target anthocyanidin amounts and both source predictions are zero. The class-specific improvement is therefore mathematically **undefined (0/0)**. The six taxa are nevertheless **included** in the original complete 47-species pooled prediction and in every source permutation. They were not removed, and original source presence codes are not recoded.

For the other five nonzero-anthocyanidin classes, individual class outcomes vary in sign; the whole-source anthocyanidin practical result remains negative.

### Biological interpretation

**At the original anthocyanidin-presence-class resolution, molecular phylogenetic proximity helps predict a subset of flavonol-related gene expression, but does not robustly predict source-measured flavonol compound amounts.** Thus detectable or operationally transferable *gene-expression history* is not identical to conservation of a measured *biochemical phenotype*.

Possible explanations include nonlinear enzyme saturation and pathway branching, regulation after transcription, different extraction/quantification precision, environmental or developmental plasticity, and species-level differences in flavonol use. These are **hypotheses, not directly tested mechanisms** here. The original source does **not** measure corresponding flower UV reflectance, pollinator behaviour, co-pigment optical effects, flower chemistry fitness, or functional metabolic flux in this test. It is inaccurate to conclude that flavonol genes are irrelevant to flavonol concentrations, that the pathway has causally decoupled, or that speciation systematically erases product information.

This source is one radiation only and all candidate source phenotypes/genes were published before the new analyses. No independently held-out radiation supports a general memory law. The original Petunieae nearest-two 21-gene predictive FAIL (**−9.91%**), original flavonol expression predictor PASS (+5.61%), adjusted 21-gene hidden phylogenetic correlation (+.5112/P=.0002), module results and earlier `Erica` NOT_SUPPORTED are **all unchanged**.

## Exactly what was executed and preserved

- Design: `data/petunieae_flavonol_metabolite_transfer_design_v0_1.json`.
- Reproducer: `scripts/analyze_petunieae_flavonol_metabolite_transfer_v0_1.py`, source-loader inherits CSV/tree/original R script SHA256 and validates the prior 21-gene FAIL and fixed flavonol expression +.0561368 gain **before opening two new chemical targets**.
- Full output: `results/petunieae_flavonol_metabolite_transfer_v0_1/result_v0_1.json`.
- Regression tests include a structural all-zero class to prevent accidental deletion or undefined positive classes, two-compound-family Holm correction, original target identity and frozen numeric results.
- Hosted exact original-source workflow: [GitHub Actions #39402255188](https://github.com/zuizui0223/chun/actions/runs/39402255188), source result PASS and 5 focused tests passed. The initial attempt legitimately exposed a structural all-zero anthocyanidin class; its per-class 0/0 handling was amended without altering the two original chemical endpoints, 47 taxa, donor weights or permutation null.

**Governance:** Draft #428 stacked on #427 → #426 → integrated temporal Draft #414. Original AJB Camellia and frozen Evolution Letters v0.3 first-shot science remain untouched. There is no cross-radiation selection, same-pathway phenotypic evolutionary-rate, pollinator, or phenotype UV-performance claim here.
