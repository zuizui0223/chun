# Article type

Letter

# Title

**No universal scale of predictability in flower-color evolution**

Running title: Resolution-dependent flower-color evolution

## Teaser text

Evolutionary predictability is often discussed as though a trait has a single natural level of description. Using flower color as a test case, we asked whether phylogenetic signal is maximized consistently at coarse, intermediate, or fine phenotypic resolution. A preregistered prediction that intermediate resolution would be optimal failed prospectively in *Iris*. We then applied one estimator to 51 additional clades and found coarse, fine, tied, and no-signal outcomes, but no unique intermediate winner among 28 analyzable clades. Simple tree geometry did not predict these differences. Finally, a standardized biochemical analysis of Petunieae showed strong signal only at fine compound composition. The results indicate that evolutionary predictability depends on how phenotype space is represented, but not according to one universal optimal scale.

# Abstract

Evolutionary predictability depends not only on the process being studied, but also on how phenotypes are represented. Flower color provides a useful test because the same biological variation can be described as coarse pigment presence, intermediate biochemical or color classes, or fine hue and compound states. We first derived a cross-radiation prediction that phylogenetic predictability should peak at intermediate resolution, then preregistered and tested that ordering in an independent *Iris* radiation. The prediction failed: coarse, intermediate, and fine same-state phylogenetic AUCs were 0.462, 0.454, and 0.487, respectively, with fine exceeding intermediate in the preregistered fail-side test. We next applied the same three-resolution estimator and 9,999 joint permutations to a standardized 51-clade flower-color dataset. Twenty-eight clades met the frozen common-frame requirements; their terminal profiles were three coarse winners, zero intermediate winners, three fine winners, six ties, and sixteen cases without detectable phylogenetic signal. Four pre-outcome tree-geometry moderators all failed leave-one-clade-out qualification. A separate standardized biochemical Petunieae profile further showed that coarse pigment presence and intermediate anthocyanidin class were uninformative whereas fine six-compound composition was strongly structured (AUC = 0.700, P = 0.0001). Together, these results reject a universal optimal scale of flower-color predictability. Predictive signal is representation dependent, heterogeneous among clades, and not explained by simple phylogenetic geometry. The next challenge is to identify biological properties that prospectively predict which representation will be informative.

Keywords: character coding; flower color; phylogenetic signal; predictability; phenotype representation; preregistration; anthocyanin; macroevolution

# Introduction

A central question in evolutionary biology is whether repeated phenotypic evolution is predictable. Research on flower color has made this question especially tractable because floral pigmentation is genetically and biochemically well characterized, yet highly labile across angiosperms. Repeated transitions can involve recurrent pathway regions, alternative pigment systems, and different regulatory routes. This literature has established that transition direction, pathway architecture, and phenotype dimension affect which molecular changes are likely to recur (Ng & Smith, 2016; Rausher, 2008; Sobel & Streisfeld, 2013; Wessinger & Rausher, 2012).

A less frequently tested problem is whether evolutionary predictability itself depends on the biological resolution at which a phenotype is encoded. The same flower can be represented coarsely as pigmented versus unpigmented, at an intermediate level as a pigment or hue class, or finely as a specific visible state or biochemical composition. Character construction is not statistically neutral: structured biological characters can require explicit hierarchical models, and aggregation or recoding need not preserve the original Markov dynamics (Tarasov, 2019; Vera-Ruiz et al., 2022). Yet the empirical question remains unresolved: is there a biological scale at which evolutionary predictability is consistently maximized?

We addressed this question through a sequence of increasingly restrictive tests. Retrospective analyses across independent flower-color radiations suggested that broad transition direction was unstable whereas finer within-state organization could recur. That pattern motivated a stronger hypothesis: perhaps predictability generally peaks at an intermediate resolution, where biologically meaningful structure is retained without the sparsity of very fine states. Rather than treating this as a post hoc interpretation, we converted it into a preregistered ordering and tested it in an independent *Iris* radiation.

The prospective test falsified the intermediate-optimum prediction. We therefore changed the question from “does intermediate resolution win?” to “how heterogeneous are resolution profiles when the estimator and state hierarchy are standardized?” We applied the same pairwise phylogenetic AUC framework to 51 flower-color clades under a frozen three-level ontology and then tested whether simple, outcome-independent tree geometry could explain between-clade differences. Finally, we extended the same estimator to an independently standardized biochemical phenotype hierarchy in Petunieae, asking whether the result generalized beyond human-visible color.

Our aim is not to show that character coding matters in general; that principle is already established. Instead, we test a stronger empirical proposition: whether independent flower-color systems share one privileged scale of predictability after analysis choices are standardized and whether departures from that scale can be prospectively predicted. The resulting evidence rejects a universal optimum and identifies a sharper problem for comparative evolutionary biology: predicting which representation of a phenotype will preserve evolutionary signal in a given system.

# Methods

## General estimand

Here, phylogenetic predictability means same-state phylogenetic discrimination: how well phylogenetic proximity distinguishes pairs of taxa that share the same phenotypic state from pairs that do not. It does not estimate transition probabilities or forecast evolutionary transitions; below, we use “predictability” only in this restricted sense.

For each biological unit we represented the phenotype at three nested resolutions: coarse, intermediate, and fine. Analyses used one common retained-tip frame across all three levels. Fine states represented by fewer than five eligible tips were excluded before computing any of the three resolution-specific statistics, preventing a finer representation from being evaluated on a different taxon set.

For a given tree and state representation, every pair of retained tips was labeled according to whether the two tips shared the same state. Negative patristic distance was used as the predictor of same-state membership, and phylogenetic predictability was quantified as the area under the receiver-operating characteristic curve (AUC). AUC > 0.5 indicates that tips closer on the tree are more likely to share a state. Null distributions were generated by jointly permuting the complete coarse/intermediate/fine state triplet among tips 9,999 times, preserving the nesting relationship among resolutions while breaking its phylogenetic association. Unless otherwise stated, analyses used seed 20260913.

A unique winning resolution required (i) its AUC to exceed 0.5 with one-sided permutation P <= 0.05, (ii) its observed AUC to exceed both alternatives, and (iii) the winner-minus-runner-up contrast to have one-sided joint-permutation P <= 0.05. Units with phylogenetic signal but no unique winner were classified as tied. Units in which no representation exceeded the signal threshold were classified as no signal. Frozen schema, source-access, and common-frame failures were treated as HOLD states rather than biological negatives.

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

## Simple tree geometry failed to predict profile differences

None of the four pre-outcome tree-only candidates passed the joint leave-one-clade-out qualification rule. All four failed to improve prediction over intercept-only for both independent profile contrasts. Each also worsened leave-one-clade-out RMSE for the derived fine-minus-coarse contrast. Log tip number modestly improved one contrast but worsened the other and therefore failed the full-profile rule.

Thus the observed heterogeneity cannot be reduced to the tested differences in tree size or basic branch-length geometry. This negative result does not exclude biological moderators that were not measured.

## Fine biochemical composition was informative in Petunieae

The frozen Petunieae rare-state rule left 47 tips. Coarse and intermediate representations collapsed to the same partition, with six anthocyanidin-absent and 41 anthocyanidin-present taxa. Their AUCs were identical (0.5189; P = 0.1985). Fine six-compound composition retained six common states and produced substantially stronger phylogenetic predictability (AUC = 0.6996; P = 0.0001). Fine exceeded the runner-up by 0.1806, with joint-permutation P = 0.0001, yielding terminal class `PROFILE_SIGNALLED_FINE`.

Petunieae therefore provides a cross-representation example in which fine biochemical composition carries strong same-state phylogenetic structure that disappears under coarser summaries. Because it is currently the only completed biochemical exact-profile unit, it cannot establish that biochemical representations generally favor fine resolution.

# Discussion

Our analyses reject a simple view of evolutionary predictability in which there is one natural scale at which flower-color evolution is most structured. The strongest version of that idea—an intermediate optimum—was converted from retrospective pattern into a preregistered prediction and failed in an independent *Iris* radiation. Standardizing the estimator and phenotype ontology across 28 additional clades did not reveal a replacement universal optimum: coarse, fine, tied, and no-signal profiles all occurred, whereas no clade showed a uniquely supported intermediate optimum. A biochemical extension in Petunieae then showed that fine compound composition can contain information absent from coarse biochemical summaries.

This sequence matters because several weaker conclusions were already available from prior work. Character coding can affect phylogenetic inference, similar visible colors can arise through different biochemical routes, and different flower-color transitions can favor different molecular targets. Our contribution is not another demonstration of those principles in isolation. Instead, we empirically test whether one resolution of phenotype space repeatedly maximizes evolutionary signal across independent flower-color systems, subject that candidate rule to prospective falsification, and then measure the heterogeneity that remains under standardization.

The prospective *Iris* result is especially important for interpretation. Had we stopped at the retrospective discovery stage, the claim that intermediate resolution was biologically privileged could have remained an attractive but weakly falsifiable synthesis. Its failure forced a narrower inference: representation matters, but the informative resolution is system dependent. The subsequent many-clade analysis supports that revision directly.

Why should resolution profiles differ? Our current data do not identify the answer. Simple tree geometry was insufficient, and representation type cannot yet be evaluated as a predictive moderator because Petunieae is the only completed biochemical exact-profile unit; holding it out leaves no biochemical training observation. Treating the mixed pigment/hue *Iris* hierarchy as a second biochemical replicate would manufacture replication. The next representation-level prediction therefore requires another independent non-visible exact-profile system.

Several biological explanations remain plausible. Different clades may vary in how strongly visible states collapse multiple biochemical pathways, in the number and accessibility of developmental routes to similar colors, in reticulation or hybridization, or in how phenotype states partition environmental and pollinator selection. These hypotheses now have a concrete target: they must predict the full three-resolution profile before another held-out outcome is opened.

The analysis also exposes an applicability boundary. Some datasets do not admit a defensible nested state hierarchy at all. Gesnerioideae, for example, contains pigment-chemistry and visible-reflectance dimensions that cross-cut rather than nest, and the preregistered analysis stopped before outcomes were computed. Other candidate systems remain blocked by source or tree provenance. Such HOLD states should not be collapsed into biological failures, because doing so would confound data availability and ontology with evolutionary signal.

More broadly, our results suggest that “predictability of a trait” is incomplete without specifying the representation of that trait. Evolutionary regularity can disappear when states are aggregated and can emerge when biologically informative detail is retained, but finer is not always better: most standardized clades showed either no detectable signal or non-unique winners, and coarse winners occurred in several clades. The problem is therefore not to maximize resolution indiscriminately. It is to identify which representation preserves the causal and historical structure relevant to a particular evolutionary system.

The next decisive test is accordingly predictive rather than descriptive. A second independent non-visible exact-profile system is needed before representation class can be evaluated as a one-predictor moderator under leave-one-out validation. If such a moderator qualifies, its prediction for a new held-out radiation must be frozen before outcome exposure. That sequence—discovery, explicit prediction, prospective test, and refusal to rescue failed predictions post hoc—offers a route toward stronger claims about evolutionary predictability than repeated retrospective fits alone.

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

**Figure 5. Representation training remains unbalanced.** Completed exact-profile units comprise 28 standardized visible-color clades, one biochemical-composition unit, and one prospective mixed pigment/hue unit. **Alt text:** A bar chart has a tall bar of 28 visible-color units and two bars of one unit each for biochemical and mixed representations, illustrating why representation type cannot yet be learned out of sample.

# References

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
