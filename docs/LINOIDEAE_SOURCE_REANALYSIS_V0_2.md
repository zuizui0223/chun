# Linoideae: hue structure survives conditioning on white status

## Status and scientific result

The second external radiation has now been independently reanalysed from terminal observations and public sequences, after Hydrangea (#195). This is no longer a four-row text recovery or an audit of published transition counts. The principal positive result is **hue-specific phylogenetic organization in Linoideae that cannot be reduced to the distribution of white versus nonwhite terminals under the tested null**. Neither a universal transition direction nor a robust white ancestor has been demonstrated.

Camellia Paper 1 science v0.2.2, framing v0.3.4 and AJB v1.0 are unchanged. Three Linoideae trees and the sensitivity combinations below represent ONE radiation, not independent clade replications.

## Original sources and execution provenance

Villalvazo-Hernandez et al. (2022), *Plants* 11:1579, DOI `10.3390/plants11121579`, PMC9231132 (CC-BY), supplies Table S1 and the Figure 2 / Figure S5 terminal colour markers. Its 112-species wording is not a count of independent accession rows. No author Newick or ancestral-node state was used as the atlas estimator.

Actual source acquisition, GenBank reconciliation, alignments and the two four-locus trees: Actions run **34115602382**, artifact **10016488210**, SHA256 `143c2b09acc4d31ee3fe7d9b78f09fb445cf4638b2429270b5efac3a97910f6d`. Nuclear ITS-only tree: run **34117696576**, artifact **10016967681**, SHA256 `7892531a19d4dcba142a333dd75d911af646a76bf425a854e8d1d444765831b4`. Both ZIP hashes were checked after download. The source manifest pins original PDFs, source assignments, recovered terminal matrix and all three executed trees.

## What was recovered and what was excluded

Table S1 has **121 composite source rows: 120 ingroup plus Hugonia**. All have independent Figure 2 and Figure S5 terminal-state records with source-table row, figure ordinal and pixel coordinates. A/B records are retained; the hirsutum subspecies is not silently dropped. These are composite taxon rows, not proven single individuals shared across genes. For balanced analyses, one row per source binomial is sampled, grouping that subspecies with its binomial; this is a sampling convention, not an accepted-taxonomy determination.

**42 of 120 ingroup terminal colour sets disagree between the two figures.** For example, L. album and L. catharticum have white S5 tips but yellow Figure 2 tips. Multiple-colour markers and figure disagreements are retained as sets, not forced into single colours and not labelled verified natural population polymorphism. Primary coding is the union of the two source sets; each figure separately is a sensitivity. All **242 terminal-marker checks** agree with the transcribed sets in an independent pixel replay. This checks what the figures depict, not which figure is botanically correct. Terminal labels were read visually; no OCR or ancestral-node colours were used.

All **450 valid unique GenBank accessions** were retrieved. Across 484 source gene-assignment cells: 427 match the source taxon/gene, 10 have a gene-column mismatch resolved explicitly from the record's gene metadata while retaining the taxon match, 18 taxon mismatches are held, one malformed accession is held, and 28 are source-missing. Thus **437 gene assignments** are admitted (ndhF 102, matK 112, trnL-F 112, ITS 111). Some held names could be legitimate synonyms or spelling variants; the 18 holds are NOT 18 demonstrated biological errors or contaminations. Examples of different-organism accession records are excluded rather than interpreted as plant sequence data.

L. bungei and L. mumbyanum lack an admitted exact-name assignment under this protocol. The four-locus trees therefore contain **118 ingroup tips** (plus the outgroup during reconstruction). The ITS-only sensitivity contains **110 ingroup tips**. A separate exclusion of L. usitatissimum (LINO113) prevents the principal result from depending on that cultivated-flax species. It does not establish that all remaining source observations are wild populations.

## Independent trees and common estimators

MAFFT 7.505 aligns each metadata-admitted locus, checking strand orientation. IQ-TREE 2.0.7 fits GTR+G4 with locus partitions, Hugonia (LINO001) as outgroup and 1,000 ultrafast bootstrap replicates plus BNNI. Full and >=50% base-occupancy concatenations have 4,689 and 2,754 sites. An additional GTR+G4 ITS-only tree has its own 1,000 bootstrap replicates. The source reconstruction contains three plastid loci and ITS, not a nuclear-only multilocus species tree. The ITS sensitivity reduces this dependence but is still one nuclear marker with different coverage. The trait analyses below use the three ML topologies; bootstrap support is retained, but this is NOT a trait posterior integrated over all 3,000 bootstrap trees.

Outgroups are removed before trait likelihoods. Binary WHITE/NONWHITE Mk uses the same verified optimizer as the Hydrangea reanalysis; ER and ARD are compared under equal and stationary root priors. For two states, SYM is identical to ER. Uncertain terminal states have 0/1 allowed-state likelihood vectors. Expected jumps and state-occupied branch lengths are calculated separately from transition rates. Branch units are sequence substitutions per site, not years. Six-colour ER is an observation-space sensitivity, not a claimed identifiable 30-rate ARD fit.

The calculation contains 36 primary binary fits, 180 fits across ten balanced source-binomial draws per tree/coding, nine six-state ER fits, and 36 additional crop-exclusion fits. Boundary fits and rate plateaus cannot receive an ordinary likelihood-ratio/profile-inference claim. Seven interior equal-root ARD fits have conditional profile checks; open limits are retained as open, not replaced by the search limit.

## Positive result: structure among hues beyond white status

Using one row per source binomial and the first three deterministic draws, six-colour Sankoff minimum-change scores are compared with 9,999 exchanges of whole allowed-state vectors. All **27** tree/coding/draw combinations have permutation **p=0.0001**, with observed/null-mean score ratios **0.233-0.591**. These are minimum-change scores, NOT estimated counts of independent biological origins.

The white/nonwhite collapse has **p=0.1307-1.0** across the corresponding 27 combinations. This is not proof of no binary signal: few definite white units and source ambiguity limit power. Comparing two p-values alone would also not establish a difference between representations.

Therefore the direct test freezes each tip's definite-white, definite-nonwhite, or ambiguous status and shuffles six-colour vectors only within that status class. **All 54 conditional tests** (three trees x three source codings x three balanced draws x inclusion/exclusion of L. usitatissimum) have **p=0.0001**. Observed/null-mean scores range **0.263-0.611**, approximately 39-74% fewer minimum changes than these conditional randomizations. The result survives the ITS-only topology and both separate source codings. These 54 settings are correlated sensitivity analyses, not 54 independent studies.

The supported interpretation is that the flower-colour history contains hue-specific organization beyond a binary white/nonwhite summary. Phylogenetic inheritance, pigment-network constraints and ecological filtering remain alternative contributors; this dataset has not separated their causes. It does not measure molecular-module reuse or identify pollinators or climate as causes.

## Why the direction and ancestral baseline remain unpromoted

Under primary UNION coding, full-tree ER has AIC **22.8397**, compared with **23.9353** for equal-root ARD. The ARD point return/gain rate ratio is **0.1065**, but its conditional profile includes 1 and remains open at the high-ratio search end (LR p **0.3416**). ITS-only UNION likewise favors ER (AIC **15.7768** versus **17.6419**, LR p **0.7135**). On the occupancy-filtered tree, equal-root ARD reaches a near-zero return-rate boundary; its numerical near-zero ratio and root probability near 1 are diagnostic limits, not regular evidence for a precisely known directional mechanism or ancestor.

A notable sensitivity is **ITS-only plus S5-only**: its conditional return/gain profile is **0.0284-0.1534**, with LR p approximately **2.93e-7**. That source-specific result is retained rather than hidden, but it does not persist under Figure 2 or the primary union coding. No source-independent direction is promoted.

For the same full-tree UNION observations, root P(WHITE) is **0.0246** under ER but **0.6916** under equal-root ARD, and **0.1254** under stationary-root ARD. A published yellow-white baseline cannot therefore be entered as a known-white predictor. Yellow is nonwhite in the binary analysis and is not equated with absent pigment chemistry.

## Relation to the cross-clade goal

Hydrangea and Linoideae now have actual source-to-tree-to-trait reanalyses under a common binary estimator. Hydrangea's conditional return-rate point estimates lean above 1; Linoideae's ARD points lean below 1, but neither contrast establishes a shared directional law or a pooled baseline effect. The stronger new, bounded result is Linoideae's hue organization conditional on white status. Originality here is the rebuilt, uncertainty-preserving comparison and its tests, not a claim that flower-colour conservatism itself is a newly invented concept.

Remaining research gates are a third independently reanalysed radiation, ancestry uncertainty carried as uncertainty rather than a taxon-admission fact, and comparable pigment/organ and molecular data before testing a general molecular rule. The current result is not an ecological causal test or a pooled estimate of white ancestry.

## Replay

All inference inputs are committed; no expiring artifact, NCBI connection or PDF download is needed for the offline inference job. Missing or modified inputs fail hash checks. Source refresh and ITS reconstruction workflows are manual; they preserve their separate original-data provenance.

```bash
python -m unittest discover -s tests -p 'test_linoideae_mk_v0_2.py' -v
python scripts/analyze_linoideae_mk_v0_2.py --snapshot data/linoideae_source_reanalysis_v0_2/source_manifest.json --out build/linoideae_replay_v0_2
python scripts/audit_linoideae_hue_signal_v0_2.py --snapshot data/linoideae_source_reanalysis_v0_2/source_manifest.json --out build/linoideae_replay_v0_2/conditional_hue_results.json
python scripts/summarize_linoideae_reanalysis_v0_2.py --manifest data/linoideae_source_reanalysis_v0_2/source_manifest.json --results-dir build/linoideae_replay_v0_2 --out build/linoideae_replay_v0_2/summary.json --expected data/linoideae_source_reanalysis_v0_2/analysis_summary.json
```

The frozen summary is numerically checked (relative tolerance 2e-4, absolute tolerance 2e-5), not described as byte-identical optimizer output. Source CSV/tree hashes are exact. The full results retain all fits, profile grids, sampled rows, and conditional-null checks. Optional original-PDF verification uses `verify_linoideae_source_pixels_v0_2.py` with the downloaded source directory and independently checks 242 depicted marker sets.
