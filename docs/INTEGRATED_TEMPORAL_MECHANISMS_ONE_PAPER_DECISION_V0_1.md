# Decision gate — one temporal–mechanistic paper with Camellia as one case (2026-10-08)

## Verdict

**Scientifically coherent as one synthesis manuscript. A retrospective, same-phylogeny Petunieae biochemical-to-expression result is now measured, but cross-radiation causal and generalization claims remain unestablished.** The proper principal evidence is the multi-radiation hierarchical-memory analysis; *Camellia* moves into the mechanistic diversity tier, alongside six other examples.

A naïve merger of the complete six-figure *Camellia* AJB paper and the Evolution Letters v0.3 figures would create a long, two-centre manuscript. It is not recommended. The new draft instead concentrates on one question:

> Where does evolutionary history persist when flower-colour phenotypes are repeatedly generated through non-identical biological implementations?

Do not equate (i) phenotype similarity vs relative distance; (ii) additional within-coarse fine-state history; and (iii) independent molecular-event reuse. The three analyses currently use different observations and sometimes different taxa.

## Completed feasibility checks

| Gate | Actual result | Consequence |
|---|---|---|
| Temporal cohort | 32 fine-visible persistence clades, 23 with negative slopes | Strong multi-clade time-oriented descriptive tier |
| Hierarchical-memory cohort | 21 opportunity clades, 18 positive within-coarse effects | Positive cross-radiation result |
| Independent visible validation | *Schistanthe* prospective PASS | Not wholly an exploratory post-outcome story |
| Biochemical transport | Petunieae retrospective PASS; Gesnerioideae prospective FAIL | Not universal across representations |
| Mechanism benchmark | Seven distinct comparative systems | Supports diversity of recurrence level, **not seven pooled estimates** |
| Direct overlap of the ORIGINAL 32×7 cohorts | 0 exact named analysis-unit matches | **No cross-radiation mechanism–memory slope is identifiable** |
| NEW same-phylogeny Petunieae bridge | 47 taxa, 183 exact-six-bit-pigment-matched pairs; expression–distance rho +0.6074, P=0.0001 | Retrospective, fixed before this new statistic but not independently outcome-unexposed; **supports hidden pathway-expression history within finer pigment identity in one radiation** |
| *Camellia* placement | Excluded from main 32-clade source frame | Mechanistic case, **not** the flagship replicate in temporal decay |
| Raw-event linkage | *Camellia* has no robust shared historical branch set across strict/dominant coding | Molecular RNA-seq contrasts must not be labelled macro historical origins |

The exact-name overlap calculation compares those table-defined analysis units. Broader nesting (e.g. Solanaceae) is not a valid exact matched cohort.

## New completed source-matched biological bridge

The already existing Petunieae analysis showed that exact six-anthocyanidin pigment-presence identity retains phylogenetic information inside coarse anthocyanidin-present/absent classes on a 47-tip dated tree (centered conditional AUC +0.1879, P=0.0001). A newly commit-fixed, retrospective same-tree test now shows that the full 21-gene expression vector also retains phylogenetic organization among the **183 taxon pairs already sharing an identical six-bit pigment-presence code** (Spearman rho +0.60744; one-sided within-fine-vector permutation P=0.0001). The secondary nine-pigment concentration comparison (rho +0.21986; P=0.0554) did not pass its nominal threshold and was not tested as a significant difference from the expression statistic. All 47 leave-one-tip-out gene-expression rho values were positive; six leave-one-fine-class-out checks were performed after observing the result and are descriptive only.

This is the first **directly matched** bridge in the present integrated work, but it is one retrospective radiation, not a new cross-radiation estimate of the causes of relative-depth visible-colour memory. Exact fine code is compound *presence*, not equal pigment quantities, and gene expression is not a genetically proven causal route. See `docs/PETUNIEAE_NESTED_REGULATORY_MEMORY_RESULT_V0_1.md`.

## New decisive result: historical signal does not automatically deliver better prediction

The same 47-tip Petunieae source now has a separately predeclared **leave-one-species-out prediction** test (design commit `0c6721f`). Both predictions retain each held-out tip's exact six-compound presence/absence pigment class:

- **Phenotype-class baseline:** mean of every other species with the same six-bit pigment code.
- **Phylogenetic predictor:** mean of the two closest species with that same code on the frozen tree.
- **Scoring:** mean 21-gene squared prediction error divided by variance estimated exclusively among the other 46 tips; 47 held-out targets, fixed k=2, no post-outcome gene selection or kernel tuning.

The class mean gave standardized MSE **1.138379**; the two-nearest relatives gave **1.251167**, a **9.91% deterioration** (gain −0.099078). The frozen primary condition required **positive** gain, so **NOT_SUPPORTED** is the final result. Although the observed gain was markedly less negative than the within-pigment-class shuffled reference (null mean −0.234744, permutation P=0.0014), this relative-to-null P value **cannot reverse a failed positive-gain rule**.

The direction is robust descriptively to omitting each pigment code from evaluation (all six pooled gains negative); those six omissions do not constitute independent replications.

### Why the two estimands can disagree

A phylogenetic distance–expression distance association tests whether two taxa are *more similar on average* when closer on the tree. The prediction test instead compares one narrow nearest-neighbour rule against a stable class-wide mean. Under a simple exchangeable independent within-class null with per-gene variance σ², the expected target-versus-m-donor-mean squared prediction error is σ²(1+1/m). For a two-species local mean, m=2 gives 1.5σ²; for the baseline with the other m=5, 9 or 12 species, the reference is respectively 1.2σ², 1.111σ² or 1.083σ². Thus small donor number introduces a mathematical variance penalty even before considering any evolutionary effect. These values are **illustrative null expectations**, not estimates of the actual Petunieae molecular process. The significant within-class permutation result suggests phylogenetic locality counteracts some of that penalty, but it did not overcome it for the frozen k=2 predictor.

This strengthens the interpretation: **detectable hidden historical structure ≠ a guarantee of accurate interspecific molecular transfer**. It does not prove no phylogenetic predictor could succeed: other k values, shrinkage models or gene-specific predictors are not tested and must not be optimized on these opened data to rescue the primary failure.

### Exact explanation of the frozen k=2 failure — descriptive diagnostic

An outcome-exposed but formula-fixed finite-population decomposition distinguishes the **few-donor variance penalty** from the **phylogenetic-locality gain**. Using the same 47 held-out species, all 21 fixed genes and the same training-fold variance weighting:

| Donors | Exact or observed standardized MSE |
|---|---:|
| All other species in the same exact pigment class | **1.138379** |
| Uniformly selected two donors from that class (analytical expectation) | 1.405939 |
| Two nearest relatives in that class (frozen prediction) | 1.251167 |

Consequently the penalty for using two donors instead of the complete pigment-state mean is **+0.267560 MSE** (+23.50% relative to that baseline). Choosing the closest relatives recovers **0.154771 MSE** (13.60 baseline-percentage points) over arbitrary two donors. The net difference remains **+0.112788 MSE** (+9.91%).

This is a mathematically exact conditional expectation of sampling two donor means without replacement, not a newly fitted predictive model, independent prospective study, new permutation P value, evolutionary-rate estimate or proof of ecological causation. It explains the apparent coexistence of phylogenetic signal with a weaker-than-class-mean fixed k=2 predictor. The earlier one-sided permutation P=0.0014 is consistent with a source-specific locality advantage relative to shuffled tip assignments; the frozen positive-gain criterion against the **full** class mean still fails.

The strongest outcome is therefore **nested historical structure with a measurable but insufficient nearest-relative predictor gain at this donor budget**. That is a useful empirical distinction but, by itself, does not close the cross-radiation causal bridge needed to justify one general-evolution paper over both existing submission routes.

### One-paper publication decision after the new outcome

The integration proposal is **not promoted to replace the original two submissions**. A stronger cross-radiation flower-colour evolution paper remains a viable research target, and Petunieae is now a matched *single-radiation* bridge, but its positive conditional phylogenetic correlation is tempered by a failed prediction-gain test and its cohort still does not link molecular repetition with the original 32-radiation memory-decay rates. The prospective visible-colour Schistanthe PASS and biochemical Gesnerioideae FAIL remain distinct evidence tiers. Independent same-tip phenotype–pigment–expression validation is the next discriminatory science; another post hoc Petunieae tuning run would not resolve the generalization question.

## New limitation audit: the retained Petunieae biochemical contrast is narrower than six pigments

The inherited fine-state definition measures all six source anthocyanidins, but the *existing* requirement that each fine signature appear in at least five tips retained only 47 of 59 ingroup species (12 excluded). Before filtering, 15 distinct six-bit signatures were present; afterward six remained. **Pelargonidin, cyanidin and peonidin are constant zero in every retained tip**. Only delphinidin (29/47), petunidin (31/47) and malvidin (19/47) vary. Among the excluded 12 species, 7 produced pelargonidin, 4 produced cyanidin and 6 produced peonidin (counts can overlap).

Consequently the signal rho +0.60744 and the prediction FAIL are conditional upon six observed combinations of the **delphinidin-plus-methylated-derivatives branch**, *not* six biologically variable pigment pathways. A three-bit code for the retained Del/Pet/Malv components yields exactly the same six categories as the nominal six-bit code. This algebraic equivalence does not provide independent replication or warrant changing the primary estimator. It reveals a **selection/coverage ceiling**: the source analysis has no retained species whose fine pigment code includes detectable pelargonidin, cyanidin or peonidin, which are especially important to alternative hydroxylation and hue routes.

The original Wheeler et al. (2023; DOI 10.1098/rspb.2023.0275) study covered wider biochemical variation among 59 ingroup taxa. The narrowed 47-tip analysis was a legitimate preexisting reproducibility choice but cannot be presented as the evolution of all flower pigment routes. This is a source-support audit rather than a new positive biological outcome. The original frozen source, results, 183 paired comparisons, permutation P and nearest-neighbour failure stay unchanged.

**Implication:** the integrated paper must present the Petunieae expression result as a *restricted biochemical-within-state mechanism example*, not evidence that complete floral pigment pathways universally harbour the same kind of nested memory. Independent validation should preferentially sample pigment classes across the other anthocyanidin branches rather than merely reproduce a delphinidin-only filtered frame. Source: `results/petunieae_fine_pigment_state_retention_v0_1/coverage_v0_1.json`.

## Contribution vs existing prior art

- **Not new:** convergent red visible colour via different pigment routes and phylogenetic structure of pigment-route use (Ng & Smith 2016, DOI 10.1111/nph.13576).
- **Not new:** repeated late-pathway expression convergence and branching/hue dependence (Larter et al. 2018, DOI 10.1093/molbev/msy117).
- **Not new:** hierarchical/multi-level convergence as a concept (Lau et al. 2021, DOI 10.1111/brv.12672).
- **Potentially new empirical addition:** one frozen conditional within-coarse approach supports fine-state historical organization across 18/21 standardized clades, with prospective visible validation, alongside explicit prospective failure of biochemical generalization. Different molecular repetition levels provide biological *examples and hypotheses*, not direct explanatory covariates.
- **Stronger new empirical layer now present:** one retrospective same-phylogeny Petunieae *fine pigment class–21-gene expression* conditional association. Its novelty over Ng & Smith (2016) is the more restrictive multicomponent pigment-presence conditioning, but this still needs direct critical prior-art and independent-radiation validation. It is **not yet** a three-way visible phenotype–pigment–causal molecular implementation test.

A general-evolution journal decision should be re-opened only against an actual completed new bridge and current prior art, not based on the combined length of two papers.

## Proposed direct bridge: source-first

1. **Same-tip requirements:** published species tree with branch lengths, species-level flower-colour or measured pigment identity, and a measured finer biochemical/module state from the **same taxa**. Freeze an identifier-only join before looking at new target outcome correlations.
2. **Admissible layers:** coarse visible phenotype, fine visible or pigment state, transcript/metabolite pathway module. Never treat expression *contrast* as if it were a taxon-level ancestral transition event.
3. **Test two competing alternatives:** (A) one common memory-decay coordinate suffices across layers after frequency-centering; (B) layer-specific temporal persistence profiles are distinct and can cross. Fit/compare on a common distance frame with dependence-aware cross-taxon resampling, and validate in another independent radiation.
4. **Predeclare interpretability:** do not select a taxon, state coding, time bin or transformation because it creates a crossing. Distinguish within-coarse conditional similarity from global same-state AUC.
5. **External validation:** another independently admitted matched radiation or, if unavailable, report the test as a single-system discovery and **do not claim a new universal rule**.

### Existing source routes and prohibitions

- Petunieae: 47 retained HPLC-biochemical tips on one published dated tree. Useful for a first **retrospective biochemical depth-curve** but not enough by itself to identify colour→gene regulatory turnover. The data are already outcome-exposed and cannot be represented as prospective.
- Iochrominae: published 28-species comparison of pigment chemistry, expression and phylogeny is conceptually the highest-value complete bridge; exact Dryad reaccess remained HOLD in the existing source-frozen route. Do **not** reclassify HOLD as PASS or substitute a tree silently. A new independent public-source protocol would require its own frozen admission gate.
- Solanaceae red 27: the source/tree join succeeded but its primary exact-profile cohort collapsed under the frozen minimum fine-state count. Do not rescue by relaxing the historical threshold after outcome opening.
- *Camellia*: retain the matched molecular **observation-rule intervention** and the accepted-species macro local-colour context as separate inferential units; do not claim direct event-for-event molecular-to-phylogenetic matching.

## Manuscript restructuring

Main text should focus on five ordered results: (1) temporal decline with exceptions; (2) no universal representation; (3) persistent hidden fine-state history, prospective PASS and FAIL; (4) variation in molecular repeatability level, including *Camellia* as one qualitative mechanistic case; (5) quantified cross-tier coverage gap and decisive next cross-tier prediction.

The existing *Camellia* Paper 1 full literature ascertainment, macro coding/topology audits, multiple figures and appendices belong in supplemental evidence if the combined paper is selected, not as a second full manuscript inside the integrated one.

## Decision and preservation

**Current status: INTEGRATION_DRAFT_READY; SINGLE-ARTICLE_SUBMISSION_HOLD.**

The combined article outline and evidence gate are implemented as isolated proposal files. Neither original first-submission route is deprecated or modified. They remain valid fallback deliverables while the stronger one-paper cross-level link is evaluated. Replacing those routes also requires author approval, intellectual-property/data-rights checks, journal choice, and integration of overlapping acknowledgements.

The next actual research test is **an independent same-taxa/phylogeny replication of the Petunieae within-fine-pigment-class expression-history test**, preferably Iochrominae after verifying exact source access. Do not retrofit another favourable gene subset onto the outcome-open Petunieae sample or re-fit the existing 21-clade moderators.

## Independent Iochrominae source-audit result — 2026-10-08

The 2018 comparative expression study (Larter et al., DOI 10.1093/molbev/msy117; 28 species, seven pigment-pathway genes) cites Smith & Goldberg (2015, DOI 10.3732/ajb.1500163) for its tree. Its original archived tree is Dryad DOI 10.5061/dryad.0732g, version 3567, file ModeandTempoFlColor.zip (686,186 bytes; MD5 78957f5320749f5c022de78e8ad1ab32). This is distinct from the later Smith–Kriebel 2018 floral-shape tree (10.5061/dryad.5jn7b) and Larter 2019 developmental Dvdy source (10.5061/dryad.p5dq84v).

The exact original-tree archive name, size and MD5 were verified from live Dryad metadata. Both ordinary unauthenticated file-download and whole-dataset-download requests returned **HTTP 401 Unauthorized** on hosted run 37763678309. The tree archive has not been recovered or opened. A complete, species-level seven-gene qPCR numeric matrix for the 2018 paper has also not been source-verified. No new independent Iochrominae conditional-memory statistic was computed.

Thus the combined-manuscript promotion ceiling remains **one retrospective Petunieae nested biochemical-to-expression analysis**, not two independent radiations. Source-specific next steps are recorded in [Issue #415](https://github.com/zuizui0223/chun/issues/415). The legitimate authenticated exact-tree archive and species-level qPCR matrix are the missing inputs, not more tuning of Petunieae.

This is a source-access HOLD, not a negative biological result, and does not change any existing Evolution Letters or AJB scientific freeze.
