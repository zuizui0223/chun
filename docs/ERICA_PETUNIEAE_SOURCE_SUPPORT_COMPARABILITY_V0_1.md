# Why the Erica negative and Petunieae positive tests cannot yet be compared as one evolutionary law

**Source-support audit v0.1 (2026-10-11). Status: `EVIDENCE_ESTIMANDS_NOT_EQUIVALENT_CANNOT_TEST_EFFECT_DIFFERENCE`.** This is a source composition / biological-inference audit of two *already fixed* numerical results, not a rerun, a new association test, a post-outcome rescue or a meta-analysis.

## Exact published units and measured support

| Property | Petunieae nested gene history | Erica developmental expression history |
|---|---|---|
| Primary biological conditioning | Exactly the **same measured anthocyanidin-presence profile** among retained source species | Same broad published **visible corolla hue** (red, pink, white, yellow) |
| Original tree and expression | Same 47 published tree-tip taxa and their 21 pathway measurements | 22 source **taxon names** and 21 gene×stage fold-change coordinates; different 2025 DNA specimens, averaged across all candidate voucher tips |
| Within-state taxon pairs | 183 | 83 |
| Largest state's within-state pairs | 78/183 = **42.6%** | Red 66/83 = **79.5%** |
| Other class support | Five further states (45 pairs in one; 15 each in four) | Pink 15 pairs; white and yellow **one each** |
| Adjustment | Six chemical-state dummies, nine assayed pigment concentrations (three invariant zero) | No matching six-pigment chemistry; different qPCR measurement, developmental-age normalization and broader same-hue matching |
| Relevant fixed outcome | Retrospective adjusted rho **+0.511199**, P **0.0002** (supported observational association) | Distinct retrospective combined-tree rho **+0.041497**, P **0.4988** (not supported) |
| Practical prediction | Nearest two relatives worse than within-state class mean (frozen FAIL) | No equivalent positive/negative transfer validation |

**The 183 and 83 pair observations are both non-independent.** They describe where the two tests have same-state pair opportunities, **not** 183 and 83 statistically independent replications.

### Original Erica A–J comparison groups show a second major support asymmetry

The 2019 Erica expression study used ten lettered A–J sets of close relatives to contrast pigmentation and molecular mechanisms. Of the new 22 taxon-name-level cohort and its **83 same-visible-hue pairs**, only **6/83 (7.2%)** are formed inside the **same** original lettered source comparison set; **77/83** compare taxa from **different** sets. These letters are source grouping devices, not reconstructed independently repeated evolutionary events.

Therefore the reported non-significant Erica rho is mainly an across-comparison-group result involving visibly red flowers. It cannot be presented as a strong, fully replicated developmental pathway-memory test *within multiple independent red/pink/white/yellow transition sets*. The white and yellow classes each contribute one within-colour pair, so they provide almost no independent depth profile on their own. It is nevertheless an actual fixed exploratory **negative result**, not a transport HOLD, and is not discarded.

### Quantitative descriptor (not an effective sample-size formula)

For each source, calculate the proportion of all within-state pairs contributed by each phenotype state and the reciprocal of the sum of squared pair proportions. This concentration inverse is **1.50** for Erica's four visible-colour classes and **3.72** for Petunieae's six retained biochemical-presence classes. It is **not** an estimate of independent biological samples, phylogenetic effective sample size, test power or significance. Its only role is to document how concentrated the two source pair universes are.

### Biological hypothesis hierarchy

The current positive result supports a narrowly specified proposition: *in one Petunieae radiation, residual expression differences within a frozen chemical pigment state are organized by a published species tree, after linear adjustment for nine measured pigment quantities*. The Erica result instead asks whether *developmental pathway-expression differences among named taxa with the same visible hue covary with accession-averaged molecular distances*.

They ask related but **nonidentical** questions. Their raw rho values must not be pooled, subtracted and tested as if they estimate a single evolutionary parameter. The difference could reflect distinct actual evolutionary processes **or** phenotype coding, taxon matching, source phylogenies, RT-qPCR vs RNA expression calibration, developmental stage comparability and very unequal colour-state opportunities. The source comparison alone cannot distinguish those mechanisms.

A *genuinely decisive* next comparative experiment would require two or more independent radiations with **verified species/individual tree tips and both fine biochemical profiles and comparable expression vectors**, matched phenotype-state definitions, frozen taxon and state-support rules, and a hierarchy controlling the phylogenetic and technical dependency. The actual causal questions about pollinator interactions, selection or phenotype fitness would require still further direct measurements.

## Exact source contracts

No raw measurements or first-submission science were changed. The audit reads only:
- `data/erica_table2_visible_colour_qpcr_taxon_crosswalk_v0_1.json`
- `results/erica_voucher_averaged_developmental_memory_v0_1/result_v0_1.json`
- `results/petunieae_nested_regulatory_memory_v0_1/result_v0_1.json`
- `results/petunieae_pigment_adjusted_regulatory_memory_v0_1/result_v0_1.json`

Reproduce the transparent source counts using `scripts/audit_erica_petunieae_source_support_comparability_v0_1.py`, with the frozen output in `results/erica_petunieae_source_support_comparability_v0_1/result_v0_1.json`. The regression suite checks the exact source units, the published state counts and **no new P values, no model selection, no regression claiming a significant cross-radiation effect difference**.

**Publication governance:** The integrated CHUN PR #414 remains Draft and the Erica specimen-verified original main test remains on HOLD. The observed source-specific Erica exploratory result remains `NOT_SUPPORTED`. *Camellia* AJB Paper 1 and Evolution Letters v0.3 remain separate, unchanged first-submission candidates.
