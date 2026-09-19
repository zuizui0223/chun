# Article type

Letter

# Title

**Flower-color evolutionary memory is transient but lacks a universal phenotypic scale**

Running title: Evolutionary memory in flower color

## Teaser text

Flower color is known to carry phylogenetic signal, but the biological scale at which that history is most visible need not be universal. Across angiosperm radiations, exact color similarity generally decays with relative divergence, while a preregistered intermediate-resolution prediction fails in *Iris* and standardized clades produce coarse, fine, tied, and no-signal profiles. Flower-color history is therefore transient and readable at different phenotypic scales in different radiations.

# Abstract

Flower color can show phylogenetic signal, but whether that historical structure is consistently strongest at one biological scale has not been tested across standardized radiations. The same variation can be represented as coarse pigmentation, intermediate color classes, or fine visible and biochemical states. We first preregistered the prediction that same-state phylogenetic structure should peak at intermediate resolution in an independent *Iris* radiation. It failed: coarse, intermediate, and fine AUCs were 0.462, 0.454, and 0.487, respectively. We then applied the same estimator to a standardized 51-clade flower-color dataset. Twenty-eight clades met the frozen common-frame requirements, yielding three coarse winners, zero intermediate winners, three fine winners, six ties, and sixteen cases without detectable signal; four pre-outcome tree-geometry moderators also failed leave-one-clade-out qualification. We subsequently re-expressed the already-observed pairwise structure as a retrospective relative-divergence persistence profile. The source trees were effectively ultrametric, and exact visible flower color was analyzable in 32 clades. Persistence slopes were negative in 23 of 32 clades (median = -0.190; one-sided Wilcoxon P = 0.0012; sign-test P = 0.010), indicating that excess same-color retention is concentrated among more recent divergences and generally decays with relative evolutionary depth. This derived analysis is not independent of the AUC evidence and does not estimate absolute time. Together, the results show that flower-color evolution retains evolutionary memory, but no universal coarse, intermediate, or fine representation consistently captures that memory best. The next problem is biological: identifying ecological or mechanistic properties that predict the rate and phenotypic scale of memory loss across radiations.

Keywords: flower color; evolutionary memory; phylogenetic signal; phenotype persistence; phenotype representation; preregistration; anthocyanin; macroevolution

# Introduction

Evolutionary history leaves memory in phenotypes. Closely related lineages often resemble one another because ancestral states persist after divergence, yet ecological shifts, repeated adaptation, hybridization, and developmental accessibility can erode that resemblance through time. A central problem in comparative evolution is therefore not only whether a trait is phylogenetically structured, but how rapidly that structure is lost as lineages diverge and whether the answer depends on what aspect of the phenotype is measured.

Flower color is a useful system for this problem because floral pigmentation is genetically and biochemically well characterized while remaining evolutionarily labile across angiosperms. Repeated transitions can involve recurrent pathway regions, alternative pigment systems, and different regulatory routes. Prior work has shown that transition direction, pathway architecture, and phenotype dimension affect which molecular changes are likely to recur (Ng & Smith, 2016; Rausher, 2008; Sobel & Streisfeld, 2013; Wessinger & Rausher, 2012). Phylogenetic structure in flower color is itself not a new observation: community- and clade-level studies have asked whether related species resemble one another in floral color, often finding weak or context-dependent signal (McEwen & Vamosi, 2010; Shrestha et al., 2014). The same flower can also be represented at several biological resolutions: coarsely as pigmented versus unpigmented, at an intermediate level as a pigment or hue class, or finely as a specific visible state or biochemical composition.

Ecology provides an explicit route by which that historical memory could be eroded. In a companion macroecological analysis spanning 2,815 animal-pollinated and animal-dispersed species from 51 plant clades, flower-color diversity and the distributions of individual colors were associated with mean annual temperature, aridity, and UV-B exposure (Dellinger et al., 2026). Those spatial associations make repeated environmental sorting a biologically motivated candidate for between-clade differences in flower-color persistence, while leaving open whether environmental heterogeneity actually predicts phylogenetic memory loss.

These observations create two linked questions. First, does flower-color state similarity show a general persistence profile across evolutionary divergence, with excess same-color retention concentrated among recent splits and decaying toward deeper divergence? Second, if such evolutionary memory exists, is it consistently strongest at one phenotypic resolution? Character construction is not statistically neutral: aggregation or recoding need not preserve the original evolutionary dynamics (Tarasov, 2019; Vera-Ruiz et al., 2022). But a purely methodological statement that coding matters does not answer the biological question of how phenotype memory is distributed across evolutionary depth.

We approached these questions through increasingly restrictive tests. Retrospective comparisons across flower-color radiations initially suggested a candidate rule: perhaps phylogenetic predictability peaks at an intermediate resolution, retaining biological structure without the sparsity of very fine states. We converted that idea into a preregistered ordering and tested it in an independent *Iris* radiation. The prospective test failed. We therefore standardized one same-state phylogenetic estimator across 51 flower-color clades, tested simple outcome-independent tree moderators, and extended the representation comparison to biochemical composition in Petunieae.

After those resolution-profile analyses were complete, we asked the time-oriented biological question directly using the already-opened standardized flower-color data. Because the source phylogenies are effectively ultrametric, pairwise patristic separation can be normalized by crown depth and interpreted as relative divergence depth within each clade. This retrospective derived analysis does not provide independent replication of the AUC result; instead, it exposes the shape of the same phylogenetic memory along a relative evolutionary-time axis.

Our aim is therefore not to establish that flower color has phylogenetic signal, nor merely to show that character coding affects inference. We test the stronger proposition that one phenotypic resolution should consistently preserve flower-color history best across independent radiations, subject that proposition to prospective falsification, and then quantify the relative-divergence shape of the remaining signal. The resulting evidence rejects a universal privileged resolution while giving the heterogeneity a biological time-axis interpretation, shifting the next question toward the ecological and mechanistic causes of between-clade differences in memory loss.

# Methods

## General estimand

Here, phylogenetic predictability means same-state phylogenetic discrimination: how well phylogenetic proximity distinguishes pairs of taxa that share the same phenotypic state from pairs that do not. It does not estimate transition probabilities or forecast evolutionary transitions; below, we use “predictability” only in this restricted sense.

For each biological unit we represented the phenotype at three nested resolutions: coarse, intermediate, and fine. Analyses used one common retained-tip frame across all three levels. Fine states represented by fewer than five eligible tips were excluded before computing any of the three resolution-specific statistics, preventing a finer representation from being evaluated on a different taxon set.

For a given tree and state representation, every pair of retained tips was labeled according to whether the two tips shared the same state. Negative patristic distance was used as the predictor of same-state membership, and phylogenetic predictability was quantified as the area under the receiver-operating characteristic curve (AUC). AUC > 0.5 indicates that tips closer on the tree are more likely to share a state. Null distributions were generated by jointly permuting the complete coarse/intermediate/fine state triplet among tips 9,999 times, preserving the nesting relationship among resolutions while breaking its phylogenetic association. Unless otherwise stated, analyses used seed 20260913.

A unique winning resolution required (i) its AUC to exceed 0.5 with one-sided permutation P <= 0.05, (ii) its observed AUC to exceed both alternatives, and (iii) the winner-minus-runner-up contrast to have one-sided joint-permutation P <= 0.05. Units with phylogenetic signal but no unique winner were classified as tied. Units in which no representation exceeded the signal threshold were classified as no signal. Frozen schema, source-access, and common-frame failures were treated as HOLD states rather than biological negatives.

## Relative-divergence persistence extension

After the resolution-profile outcomes had been opened and analyzed, we performed a retrospective derived analysis to make the evolutionary-depth structure explicit. This analysis is therefore not a new prospective test and is not counted as an independent replication. We first assessed source-tree ultrametricity using the coefficient of variation of root-to-tip distances. For eligible trees, the maximum observed root-to-tip CV was below 3.0 × 10^-11. We then defined relative divergence depth for each species pair as patristic distance divided by twice the source-tree crown height. On an ultrametric tree this scales pairwise divergence from recent splits toward crown-depth separation, but it is not an absolute-time calibration and is never interpreted in millions of years.

For the direct biological persistence analysis we used exact source visible flower-color states. Fine states represented by fewer than five tips were removed, after which a clade required at least 20 retained tips and at least two fine color states. Unlike the three-resolution comparison, this fine-only frame did not require coarse or intermediate variation and yielded 32 eligible clades.

Within each clade, unordered species pairs were divided into ten equal-count bins of relative divergence depth. For each bin we calculated the probability that a pair shared the same exact flower-color state. We centered this probability on the exact without-replacement same-state probability implied by that clade's observed state frequencies and scaled the difference by the remaining range to one, producing an excess-retention curve. We summarized each clade by the linear slope of excess retention across the ten bins, its signed integrated area, and the nearest-minus-farthest-bin contrast. Cross-clade inference treated clade, not species pair, as the replication unit. One-sided Wilcoxon and sign tests assessed whether slopes tended to be negative and integrated areas positive. These summaries were specified after the original resolution outcomes and are interpreted as retrospective descriptions of persistence shape.

As a secondary model-based time-scale sensitivity, we also applied the exponential form fixed in the pre-outcome PR #300 contract to the existing 28-clade common frame: P(same state | d) = q + (1 - q) exp(-lambda d), where q is the exact finite-sample same-state probability from the retained state frequencies. Lambda was estimated by pairwise Bernoulli pseudo-likelihood with q fixed, and half-depth was defined as ln(2)/lambda, the relative crown-depth interval over which modelled excess same-state retention falls by half. Species pairs were not treated as independent inferential replicates; all cross-resolution inference remained paired at the clade level. Because this restrictive exponential form fixes P(same | d = 0) = 1, we use half-depth only as a descriptive sensitivity and never as an absolute persistence duration.

## Prospective *Iris* falsification

The intermediate-resolution ordering was preregistered before row-level *Iris* outcome ingestion. The source study sampled a genus-scale *Iris* phylogeny and documented extensive inter- and intraspecific flower-color variation (Roguz et al., 2020). The frozen hierarchy defined coarse pigment presence, intermediate major pigment class, and fine visible hue. A trait-blind six-locus tree was fixed before outcome exposure. Rare fine states were removed on the common-frame rule above. The primary prediction required intermediate AUC > 0.5 and intermediate to exceed both coarse and fine under the joint-permutation contrasts. No sensitivity analysis was allowed to upgrade a failed primary result.

## Standardized 51-clade visible-color batch

We next analyzed the 51-clade angiosperm flower-color dataset of Sinnott-Armstrong et al. (2025, 2026) using a rule frozen before CHUN opened species-level `flower_color` values. The source dataset contains 2,960 species scored in eight human-perceived flower-color categories together with one branch-length phylogeny per clade. Exact source files and all 51 clade-to-tree mappings were frozen, followed by an identifier-only crosswalk. All 2,960 species matched exactly to their designated trees after source normalization, with no tree-only or data-only mismatches.

The same visible-color hierarchy and estimator were then applied independently to each clade. A clade required at least 20 retained tips and at least two states at every resolution after the frozen rare-state filter. Twenty-three clades failed those predeclared requirements and remained HOLD. Twenty-eight clades completed the exact profile.

## Tree-geometry moderator qualification

After the standardized batch exceeded the numerical replication floor, we evaluated four outcome-independent candidate moderators: log tip number, coefficient of variation of pairwise patristic distances, coefficient of variation of branch lengths, and coefficient of variation of root-to-tip distances. Model complexity was restricted to one predictor plus intercept. A moderator was required to reduce leave-one-clade-out RMSE relative to an intercept-only model for both independent resolution contrasts, intermediate-minus-coarse and fine-minus-intermediate. The derived fine-minus-coarse contrast was retained as an additional diagnostic but was not sufficient alone for qualification.

## Petunieae biochemical cross-representation profile

To test whether the visible-color results depended on human-perceived state coding, we separately standardized the Petunieae comparative pigment dataset of Wheeler et al. (2023a, 2023b). The source combines a dated species phylogeny with floral HPLC measurements and pathway-expression data. Because these source values had been inspected previously for a different molecular-subspace analysis, this component is retrospective standardized training rather than a new prospective replication.

Before computing this profile AUC, we froze a biochemical hierarchy: coarse = presence versus absence of any of six anthocyanidins; intermediate = presence pattern across three anthocyanidin classes (pelargonidin, cyanidin, delphinidin branches); fine = exact six-compound presence pattern. A pre-AUC lexical erratum corrected only the audited source outgroup key and changed no biological state or statistical rule. The analysis then used the same common-frame, AUC, 9,999-permutation, and winner criteria as above.

# Results

## The preregistered intermediate optimum failed in *Iris*

The *Iris* primary frame retained 169 tips. The observed AUCs were 0.4617 for coarse pigment presence, 0.4544 for intermediate pigment class, and 0.4871 for fine visible hue. Intermediate resolution therefore did not produce positive phylogenetic signal and did not exceed either alternative. Its difference from coarse was -0.0073 and its difference from fine was -0.0327. The preregistered fine-over-intermediate fail-side comparison was significant (P = 0.0486). The frozen decision was FAIL.

This result rejects the universal intermediate-optimum prediction but does not constitute a fine-resolution success: all three *Iris* AUCs were below 0.5.

## Standardization across clades revealed heterogeneous resolution profiles

Of 51 visible-color clades, 28 met all common-frame and state-variation requirements. Their outcomes were heterogeneous: three clades had unique coarse winners, none had a unique intermediate winner, three had unique fine winners, six had significant signal without a unique winner, and sixteen showed no detectable phylogenetic signal. The unique coarse winners were *Ilex*, *Maytenus*, and *Symplocos*; the unique fine winners were *Passiflora*, *Rosa*, and *Solanum*.

The central result is therefore not simply another failure of the intermediate level. Under one phenotype ontology, source protocol, pairwise estimand, rare-state rule, and permutation scheme, independent clades occupied qualitatively different resolution profiles. A single preferred scale did not emerge even after methodological standardization.

## Exact flower-color memory decayed with relative divergence depth

The direct fine-color persistence frame retained 32 of the 51 source clades. Their source trees were effectively ultrametric: the median root-to-tip coefficient of variation was 2.08 × 10^-16 and the maximum was 2.98 × 10^-11. Relative patristic separation could therefore be interpreted as within-clade relative divergence depth, although not as calibrated absolute time.

Exact visible flower-color persistence declined with divergence in most clades. Twenty-three of 32 clades had negative excess-retention slopes, with a median slope of -0.1897 (one-sided Wilcoxon P = 0.00120; one-sided sign-test P = 0.0100; bootstrap 95% interval for the median, -0.373 to -0.090). The integrated excess-retention area was positive in 23 of 32 clades (median = 0.0207; Wilcoxon P = 0.00467; sign-test P = 0.0100). Across the median binned profile, excess same-color retention was positive at shallower divergence depths and approached or crossed the clade-frequency baseline toward deeper divergence.

This result gives the existing phylogenetic signal a time-oriented biological interpretation: exact visible flower-color states generally retain memory among more recently diverged lineages and lose that excess similarity as divergence deepens. It is not independent evidence from the same-state AUC. On the common 28-clade frame, fine-color persistence slope and fine AUC were strongly associated (Spearman rho = -0.845, P = 1.60 × 10^-8), as expected because both reuse the same pairwise distances and state-sharing labels.

The temporal profile did not reveal a replacement universal resolution. On the common 28-clade three-resolution frame, the largest signed persistence area occurred at coarse resolution in 13 clades, intermediate resolution in 10, and fine resolution in five. None of the paired area contrasts among coarse, intermediate, and fine resolutions was significant (all P > 0.10).

The model-based half-depth sensitivity led to the same conclusion. Median relative half-depth was 0.0060 of crown depth at coarse resolution, 0.0107 at intermediate resolution, and 0.0104 at fine resolution; the corresponding upper quartiles were 0.083, 0.097, and 0.099. The paired Friedman test showed no resolution effect (P = 0.443), so the frozen rule did not open pairwise follow-up tests. Three coarse, four intermediate, and four fine fits reached the high-lambda boundary, consistent with effectively immediate decay toward the state-frequency baseline under this restrictive model.

## Simple tree geometry failed to predict profile differences

None of the four pre-outcome tree-only candidates passed the joint leave-one-clade-out qualification rule. All four failed to improve prediction over intercept-only for both independent profile contrasts. Each also worsened leave-one-clade-out RMSE for the derived fine-minus-coarse contrast. Log tip number modestly improved one contrast but worsened the other and therefore failed the full-profile rule.

Thus the observed heterogeneity cannot be reduced to the tested differences in tree size or basic branch-length geometry. This negative result does not exclude biological moderators that were not measured.

## Fine biochemical composition was informative in Petunieae

The frozen Petunieae rare-state rule left 47 tips. Coarse and intermediate representations collapsed to the same partition, with six anthocyanidin-absent and 41 anthocyanidin-present taxa. Their AUCs were identical (0.5189; P = 0.1985). Fine six-compound composition retained six common states and produced substantially stronger phylogenetic predictability (AUC = 0.6996; P = 0.0001). Fine exceeded the runner-up by 0.1806, with joint-permutation P = 0.0001, yielding terminal class `PROFILE_SIGNALLED_FINE`.

Petunieae therefore provides a cross-representation example in which fine biochemical composition carries strong same-state phylogenetic structure that disappears under coarser summaries. Because it is currently the only completed biochemical exact-profile unit, it cannot establish that biochemical representations generally favor fine resolution.

# Discussion

Flower-color evolution is neither memoryless nor governed by one universally privileged phenotypic scale. The first part of that statement is not the novelty claim: phylogenetic signal and relatedness-dependent similarity in floral color have been reported previously (McEwen & Vamosi, 2010; Shrestha et al., 2014). Our contribution is the second part and the way it was tested. A candidate intermediate optimum was fixed prospectively and failed, after which a standardized 51-clade analysis still yielded heterogeneous coarse, fine, tied, and no-signal profiles. The relative-divergence analysis then places that same heterogeneity on a biological time axis: exact visible flower-color states generally showed greater-than-baseline similarity among relatively recent divergences, and that excess retention declined toward deeper divergence.

The persistence result provides a biological reading of the pairwise phylogenetic signal rather than an independent line of evidence. The strong association between fine-color AUC and persistence slope confirms that both summarize the same underlying combination of patristic distance and state sharing. What the persistence representation adds is shape: instead of reducing a clade to one discrimination statistic, it shows how excess state similarity is distributed across relative divergence depth. The source trees are effectively ultrametric, allowing a relative-time interpretation, but they are not calibrated here in absolute time.

A restrictive exponential half-depth sensitivity provides a complementary scale translation, not a second test of the phenomenon. Median fitted half-depths were approximately 0.6–1.1% of crown depth, whereas the upper quartiles extended to roughly 8–10%, emphasizing strong among-clade heterogeneity. Because the model forces same-state probability to one at zero divergence and to the frequency baseline at long distance, these small median values are model dependent and should not be confused with an observed threshold in the binned persistence curve. Their main use here is comparative: half-depth again showed no consistent coarse, intermediate, or fine ordering across clades.

The prospective *Iris* result remains crucial. Before outcome exposure, retrospective patterns motivated the attractive hypothesis that intermediate resolution would be biologically privileged. That prediction failed, with all three *Iris* AUCs below 0.5. The standardized 51-clade analysis then showed that no replacement universal optimum emerged: coarse, fine, tied, and no-signal profiles all occurred, and no clade had a uniquely supported intermediate optimum. The temporal-persistence extension reaches the same boundary from a different summary of the data: flower-color memory is common, but coarse, intermediate, and fine representations do not show a consistent ordering in how strongly they retain it.

This shifts the biological problem from finding the correct universal coding scale to explaining variation in memory loss among clades. Pollinator turnover could accelerate visible-color change when floral signals track different sensory environments. Climatic or edaphic shifts could repeatedly favor different pigments through physiological as well as signaling functions. Developmental accessibility could make some color states easy to regain, while hybridization or introgression could decouple phenotype similarity from tree-like history. Visible colors may also collapse distinct biochemical pathways, so the ecological process that matters may operate at a finer or different biological representation than human-perceived hue.

The abiotic hypothesis is supported by independent macroecological evidence, but not yet by the required cross-clade persistence test. Dellinger et al. (2026) found that temperature, aridity, and UV-B were associated with flower-color diversity and with the distributions of particular flower colors in the same broad 51-clade study system. Their analysis therefore establishes that environmental variation is relevant to flower-color ecology at continental to global scales. It does not test whether clades occupying more heterogeneous environments lose flower-color phylogenetic memory more rapidly, so that causal and predictive link remains a separate target rather than a conclusion of the present analysis.

Our present data do not identify which of these explanations is responsible. Four simple tree-geometry predictors failed leave-one-clade-out qualification, so the observed heterogeneity cannot be reduced to tree size or elementary branch-length geometry. Representation type itself also remains predictively unidentified because Petunieae is the only completed biochemical exact-profile unit. Its fine six-compound composition is strongly structured, but one biochemical unit cannot establish a general biochemical advantage.

The analysis also exposes an applicability boundary. Some datasets do not admit a defensible nested phenotype hierarchy, and others remain blocked by source or phylogenetic provenance. Such HOLD states are not biological failures. Likewise, the current persistence analysis concerns interspecific flower-color states, not the long-term maintenance of within-population polymorphism. Demonstrating ancestral polymorphism persistence, sorting, or repeated reactivation would require population-level or ancestral-state information beyond the present comparative frame.

The next decisive step is therefore ecological and prospective. Candidate moderators should be specified before another held-out outcome is opened and should predict either the rate at which flower-color memory decays across relative divergence or which phenotype representation retains that memory most strongly. Pollination regime, environmental heterogeneity, and biochemical pathway diversity are concrete candidates, but any successful explanation must improve out-of-sample prediction across clades rather than merely fit the present profiles retrospectively.

The broader conclusion is positive but conditional: flower-color states retain detectable evolutionary memory across independent angiosperm radiations, yet that memory erodes with divergence and is not captured most strongly by one universal phenotypic scale. Predicting why some clades retain coarse pigmentation history while others preserve finer visible or biochemical structure is now the central comparative problem.

# Data and code availability

All analysis code, preregistration contracts, source manifests, frozen receipts, validation workflows, and machine-readable results are versioned in the `zuizui0223/chun` repository. The 51-clade source data and phylogenies are archived in Dryad at https://doi.org/10.5061/dryad.r4xgxd2sc (Sinnott-Armstrong et al., 2025). The Petunieae processed pigment data, phylogenetic inputs, and associated analysis resources are available through the Open Science Framework at https://osf.io/zg9cu/ (Wheeler et al., 2023b), with the corresponding published study described by Wheeler et al. (2023a). The *Iris* source data and phylogenetic sampling are documented in Roguz et al. (2020) and its supplementary materials. A submission-specific CHUN code snapshot will be archived with a persistent identifier before submission.

# Author contributions

To be completed using CRediT roles before submission.

# Funding

To be completed before submission.

# Conflict of interest

The authors declare no conflicts of interest.

# Acknowledgements

To be completed before submission.

# Figure legends and alt text

**Figure 1. Prospective *Iris* test of the intermediate-resolution prediction.** Same-state phylogenetic AUC for coarse pigment presence, intermediate pigment class, and fine visible hue. The dashed reference is AUC = 0.5. The frozen primary decision was FAIL. **Alt text:** Three bars show coarse, intermediate, and fine AUCs, all below 0.5; intermediate is the lowest and fine is the highest.

**Figure 2. Resolution profiles across 28 completed standardized visible-color clades.** Coarse, intermediate, and fine AUCs are shown for each clade passing the frozen common-frame and state-variation requirements. Clades are ordered by fine-minus-coarse AUC. **Alt text:** A multi-line plot across 28 named clades shows substantial variation in which of the three resolution levels has the highest AUC; there is no consistent intermediate peak.

**Figure 3. Qualification of outcome-independent tree-geometry moderators.** Leave-one-clade-out improvement relative to an intercept-only model is shown for the two independent profile contrasts and four predeclared tree-only predictors. Positive values indicate improved prediction. No predictor improved both contrasts. **Alt text:** Two series of points lie around zero across four tree predictors; each predictor fails because at least one contrast has zero or negative leave-one-out improvement.

**Figure 4. Petunieae biochemical resolution profile.** Same-state phylogenetic AUC for coarse anthocyanidin presence, intermediate anthocyanidin-class presence pattern, and fine six-compound composition. Fine composition was the unique winner (P = 0.0001). **Alt text:** Coarse and intermediate bars are identical near 0.519, while the fine bar rises to about 0.700 and is marked P = 0.0001.

**Figure 5. Exact flower-color memory across relative evolutionary divergence.** Median excess same-color retention across 32 eligible clades is shown over ten equal-count bins of relative divergence depth, with interquartile ranges. Excess retention is centered on each clade's exact frequency-based same-state expectation. The profile is positive at shallower divergence and approaches or crosses the baseline toward deeper divergence. **Alt text:** A curve across relative divergence depth starts above the zero excess-retention baseline at shallow divergence and trends downward toward approximately zero or negative values at deeper divergence; an interquartile band shows substantial among-clade variation.

# References

Dellinger, A. S., Meier, L., Smith, S. D., & Sinnott-Armstrong, M. (2026). Does the abiotic environment influence the distribution of flower and fruit colors? *American Journal of Botany, 113*(1), e70044. https://doi.org/10.1002/ajb2.70044

McEwen, J. R., & Vamosi, J. C. (2010). Floral colour versus phylogeny in structuring subalpine flowering communities. *Proceedings of the Royal Society B: Biological Sciences, 277*(1696), 2957–2965. https://doi.org/10.1098/rspb.2010.0501

Shrestha, M., Dyer, A. G., Bhattarai, P., & Burd, M. (2014). Flower colour and phylogeny along an altitudinal gradient in the Himalayas of Nepal. *Journal of Ecology, 102*(1), 126–135. https://doi.org/10.1111/1365-2745.12185

Ng, J., & Smith, S. D. (2016). How to make a red flower: The combinatorial effect of pigments. *AoB PLANTS, 8*, plw013. https://doi.org/10.1093/aobpla/plw013

Rausher, M. D. (2008). Evolutionary transitions in floral color. *International Journal of Plant Sciences, 169*(1), 7–21. https://doi.org/10.1086/523358

Roguz, K., Gallagher, M. K., Senden, E., Bar-Lev, Y., Lebel, M., Heliczer, R., & Sapir, Y. (2020). All the colors of the rainbow: Diversification of flower color and intraspecific color variation in the genus *Iris*. *Frontiers in Plant Science, 11*, 569811. https://doi.org/10.3389/fpls.2020.569811

[dataset] Sinnott-Armstrong, M., Maier, L., Smith, S. D., & Dellinger, A. S. (2025). Data from: Flower clades and fruit clades: Trade-offs in color diversification across angiosperms. Dryad. https://doi.org/10.5061/dryad.r4xgxd2sc

Sinnott-Armstrong, M., Maier, L., Smith, S. D., & Dellinger, A. S. (2026). Flower clades and fruit clades: Trade-offs in color diversification across angiosperms. *American Journal of Botany, 113*(1), e70146. https://doi.org/10.1002/ajb2.70146

Sobel, J. M., & Streisfeld, M. A. (2013). Flower color as a model system for studies of plant evo-devo. *Frontiers in Plant Science, 4*, 321. https://doi.org/10.3389/fpls.2013.00321

Tarasov, S. (2019). Integration of anatomy ontologies and evo-devo using structured Markov models suggests a new framework for modeling discrete phenotypic traits. *Systematic Biology, 68*(5), 698–716. https://doi.org/10.1093/sysbio/syz005

Vera-Ruiz, V. A., Robinson, J., & Jermiin, L. S. (2022). A likelihood-ratio test for lumpability of phylogenetic data: Is the Markovian property of an evolutionary process retained in recoded DNA? *Systematic Biology, 71*(3), 660–675. https://doi.org/10.1093/sysbio/syab074

Wessinger, C. A., & Rausher, M. D. (2012). Lessons from flower colour evolution on targets of selection. *Journal of Experimental Botany, 63*(16), 5741–5749. https://doi.org/10.1093/jxb/ers267

Wheeler, L. C., Dunbar-Wallis, A., Schutz, K., & Smith, S. D. (2023a). Evolutionary walks through flower colour space driven by gene expression in *Petunia* and allies (Petunieae). *Proceedings of the Royal Society B: Biological Sciences, 290*(2002), 20230275. https://doi.org/10.1098/rspb.2023.0275

[dataset] Wheeler, L. C., Dunbar-Wallis, A., Schutz, K., & Smith, S. D. (2023b). Evolutionary walks through flower colour space driven by gene expression in *Petunia* and allies (Petunieae): Processed data and code. Open Science Framework. https://osf.io/zg9cu/
