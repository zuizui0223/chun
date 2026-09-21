# Article type

Letter

# Title

**Flower-color evolutionary memory is hierarchical rather than scale-optimal**

Running title: Hierarchical memory in flower color

## Teaser text

Flower-color history is not stored at one privileged phenotypic scale. Across standardized radiations, broad color states can retain historical structure while finer identities preserve additional phylogenetic organization inside them. This nested architecture explains why a prospectively predicted intermediate optimum failed and why coarse-versus-fine winners vary among clades.

# Abstract

Phenotypes can preserve evolutionary history at several nested biological scales, so asking which single resolution is most predictable may be the wrong problem. Flower color is a useful test because broad pigmentation states, visible color identities, and biochemical compositions form natural hierarchies. A preregistered prediction that same-state phylogenetic structure should peak at intermediate resolution failed in an independent *Iris* radiation, and a standardized 51-clade analysis yielded heterogeneous coarse, fine, tied, and no-signal profiles. We therefore reparameterized the already-opened profiles as an exploratory memory architecture. Overall memory amplitude explained 90.65% of between-clade profile variation, whereas coarse-to-fine scale tilt explained 6.49% and intermediate-specific curvature only 2.86%. We then asked whether finer identities retain phylogenetic organization after coarse state membership is fixed. Among 21 clades with genuine fine-to-coarse compression opportunity, 18 showed positive within-coarse hidden-memory effects; the median permutation-centered conditional AUC effect was +0.0270 (one-sided Wilcoxon P = 3.34 × 10^-5; sign-test P = 7.45 × 10^-4). Hidden memory was largely independent of both global scale tilt and overall memory amplitude. The same conditional estimand in a biochemical Petunieae hierarchy produced a +0.1879 AUC effect (9,999-permutation P = 0.0001), while three additional external radiations independently support conditional fine-state organization under source-specific estimators. These retrospective tiers are not pooled and do not establish a universal law. A biochemical *Ruellia* prediction has therefore been frozen prospectively but remains outcome-unopened pending authoritative tree recovery. The emerging result is that evolutionary memory is hierarchical: coarse states can preserve broad history while finer states retain additional organization within them.

Keywords: flower color; evolutionary memory; phenotype hierarchy; phylogenetic signal; state aggregation; anthocyanin; macroevolution; predictability

# Introduction

Phenotypic similarity among relatives is often summarized as a single measure of phylogenetic signal, yet biological phenotypes are rarely single-level objects. A flower can be represented as pigmented or unpigmented, assigned to a visible color class, decomposed into pigment families, or resolved into exact biochemical compounds. These descriptions are nested but not equivalent. If evolutionary history is distributed across such levels, a search for one universally optimal coding resolution can obscure rather than clarify the biological structure of the trait.

Flower color makes this problem unusually explicit. Its developmental and biochemical basis is comparatively well understood, repeated transitions occur across angiosperms, and the same visible endpoint can arise through different pigment pathways or regulatory changes. Prior work already demonstrates that hidden mechanism can retain phylogenetic structure inside a convergent visible phenotype. In Solanaceae, convergently red flowers can be produced by anthocyanins, carotenoids, or both, and pathway use itself shows phylogenetic signal (Ng & Smith, 2016). Anthocyanin state space is also constrained by flavonoid pathway architecture, with evolutionary changes often following stepwise biochemical routes (Ng, Freitas, & Smith, 2018). More generally, aggregation of a richer state space can alter what evolutionary information is recoverable from phylogenetic data (Weber et al., 2021). We therefore do not claim that nested phenotype structure, pathway contingency, or aggregation effects are new.

The unresolved question is whether those isolated observations generalize into a cross-radiation architecture. Does a coarse phenotype simply replace finer information, or can multiple levels retain distinct historical structure at the same time? If the latter is true, then “which resolution wins?” is not the right evolutionary question. A clade could retain strong broad-scale history while finer states remain non-randomly organized inside each broad state. Conversely, a clade could have weak total memory but a strong local distinction among fine states. These possibilities require separating how much history remains from where that history is expressed.

Our programme began with the simpler winner-based hypothesis. Retrospective comparisons motivated a preregistered prediction that same-state phylogenetic discrimination should peak at intermediate phenotype resolution. That prediction failed in an independent *Iris* radiation. A standardized 51-clade visible-color analysis then produced coarse winners, fine winners, ties, and many no-signal clades, with no unique intermediate winner. The immediate interpretation was that no universal phenotypic scale captures flower-color history best.

Here we ask a different question using the already-opened cross-radiation outcomes: is the apparent heterogeneity better understood as a hierarchical memory architecture? We first decompose the three-resolution profiles into overall memory amplitude, coarse-to-fine scale tilt, and intermediate-specific curvature. We then introduce a direct within-coarse estimand: among species pairs that already share the same coarse state, does phylogenetic proximity predict shared fine identity more strongly than expected after permuting fine labels within coarse groups? This conditional design asks whether fine historical information remains after the coarse phenotype has been held fixed.

We evaluate the resulting architecture in four deliberately separated evidence tiers. The standardized visible-color batch supplies the broadest same-estimand evidence. Petunieae provides a biochemical cross-representation application of the same conditional AUC logic. Three external radiations provide independent qualitative replication under source-faithful conditional hierarchy tests that are not pooled statistically with the standardized batch. Finally, an outcome-unopened biochemical *Ruellia* test has been frozen prospectively and will provide a genuine falsification gate if its authoritative tree can be recovered. Our goal is therefore not to declare a universal hierarchical-memory law, but to determine whether the negative search for one optimal resolution conceals a positive, nested organization of evolutionary history.

# Methods

## Same-state phylogenetic discrimination

The base estimand is same-state phylogenetic discrimination: whether phylogenetic proximity distinguishes pairs of taxa sharing a phenotypic state from pairs that do not. Negative patristic distance is used as the pairwise score and discrimination is summarized by ROC AUC. This quantity does not estimate transition probabilities or forecast future evolutionary transitions.

The original resolution-profile analyses represented each phenotype at coarse, intermediate, and fine levels on one common retained-tip frame. Fine states with fewer than five eligible tips were removed before any resolution-specific AUC was computed. Joint permutations moved the complete nested state triplet among tips, preserving the mapping among resolutions while breaking its phylogenetic association.

## Prospective *Iris* test and standardized visible-color batch

The universal intermediate-optimum hypothesis was frozen before row-level *Iris* outcomes were ingested. The hierarchy comprised coarse pigment presence, intermediate major pigment class, and fine visible hue. The primary rule required intermediate AUC to exceed 0.5 and both alternative resolutions under 9,999 joint permutations. No sensitivity could rescue a failed primary result.

The standardized batch used the 51-clade flower-color dataset of Sinnott-Armstrong et al. under one frozen visible-color hierarchy and the same AUC/permutation framework. A clade required at least 20 retained tips and at least two states at all three resolutions after the rare-state filter. Twenty-eight clades completed the exact profile; 23 remained predeclared HOLD states.

## Memory-architecture coordinates

After the three-resolution outcomes were open, we performed an explicitly exploratory reparameterization. For each completed clade with coarse, intermediate, and fine AUCs C, I, and F, we defined:

memory amplitude = (C + I + F) / 3 - 0.5,

scale tilt = F - C,

intermediate curvature = I - (C + F) / 2.

For variance partitioning we used the corresponding orthogonal coordinates: (C + I + F)/sqrt(3), (F - C)/sqrt(2), and (2I - C - F)/sqrt(6). Between-clade sums of squares were partitioned across these fixed axes, with 10,000 clade bootstrap resamples.

Memory amplitude was related to the previously derived fine-color relative-divergence persistence slope and integrated persistence area using Spearman correlations. Because these summaries reuse the same source states and phylogenies, these correlations establish interpretation rather than independent replication.

## Representation opportunity

Fine-versus-coarse differences are impossible when the retained fine and coarse partitions are identical. We therefore separated structural opportunity from realized scale tilt. For the frozen common frame of each completed clade, compression opportunity was present when the number of fine states exceeded the number of coarse states. We also quantified the number of collapsed states, Shannon entropy loss under coarse coding, and the increase in random-pair same-state probability caused by coarse aggregation.

## Within-coarse hidden-memory estimand

The primary hierarchical analysis was restricted to completed clades with genuine fine-to-coarse compression opportunity. For each clade we retained only unordered species pairs already sharing the same coarse state. The binary outcome was whether each pair also shared the same fine state, and the score was negative patristic distance.

The null preserved the coarse partition exactly. Fine-state labels were independently permuted within each coarse group, preserving fine-state frequencies and coarse membership. We performed 9,999 permutations with seed 20260920. Because coarse groups can differ in fine-state diversity and phylogenetic distance distributions, the conditional null AUC need not equal 0.5. The clade-level effect was therefore the observed conditional AUC minus the mean within-coarse permutation AUC. Cross-clade inference treated clade as the replication unit and summarized the median effect, a clade bootstrap interval, a one-sided Wilcoxon test, and a sign test.

The hidden-memory effect was compared descriptively with global scale tilt and memory amplitude using Spearman correlations. These analyses were post-outcome and pilot-exposed and are not presented as prospective tests.

## Petunieae biochemical bridge

We applied the same conceptual within-coarse conditional-AUC estimator to the already-audited Petunieae biochemical hierarchy. Coarse state was any of six anthocyanidins present versus absent; fine state was the exact six-compound presence pattern after the frozen support filter. Petunieae source values had already been used in earlier CHUN analyses, so this is retrospective cross-representation evidence rather than an independent prospective replication.

## External conditional-hierarchy radiations

Linoideae, Angraecinae, and Antirrhineae were retained as a separate evidence tier. Each has a source-faithful analysis asking whether finer phenotype organization persists after conditioning on a coarser state, but their phenotype dimensions and source-specific statistics differ. We therefore report them as three independent radiation-level qualitative replications and do not pool their P values, tree sensitivities, or effect sizes with the standardized AUC analyses.

## Prospective *Ruellia* gate

A biochemical *Ruellia* prediction was frozen before CHUN opened row-level HPLC state patterns, state frequencies, or resolution AUCs. The existing hierarchy and common-frame rules were not modified. If the retained frame contains fine-to-coarse compression opportunity, the preregistered hidden-memory test retains only same-coarse pairs, computes conditional fine-state AUC, and compares it with 9,999 within-coarse fine-label permutations using seed 20260920. PASS requires the observed conditional AUC to exceed the permutation mean and one-sided P <= 0.05. If there is no compression opportunity, the system terminates structurally rather than being counted as either biological success or failure. The test remains blocked because the exact author-used 2023-derived timed phylogeny has not been recovered; HPLC outcomes remain unopened.

# Results

## A universal intermediate optimum failed prospectively

The *Iris* primary frame retained 169 tips. Coarse, intermediate, and fine AUCs were 0.4617, 0.4544, and 0.4871, respectively. All were below 0.5, and the preregistered intermediate ordering failed. Fine exceeded intermediate on the frozen fail-side contrast (P = 0.0486), but this does not constitute a fine-resolution success because none of the three representations showed positive same-state discrimination.

## Winner heterogeneity was dominated by memory amplitude, not an intermediate peak

Across the 28 completed standardized visible-color clades, three had unique coarse winners, none had a unique intermediate winner, three had unique fine winners, six had signal without a unique winner, and sixteen had no detectable signal.

The exploratory orthogonal decomposition showed that most between-clade variation was not a three-way shift among winner classes. Overall memory amplitude accounted for **90.65%** of between-clade profile variance, compared with **6.49%** for coarse-to-fine scale tilt and **2.86%** for intermediate-specific curvature. Bootstrap 95% intervals were 79.1–96.2%, 2.5–14.6%, and 0.9–7.1%, respectively.

Memory amplitude had a clear temporal interpretation. It was strongly negatively associated with the fine-color relative-divergence persistence slope (Spearman rho = -0.773, P = 1.44 × 10^-6) and positively associated with integrated persistence area (rho = 0.661, P = 1.28 × 10^-4). By contrast, amplitude and scale tilt were essentially independent (rho = -0.017, P = 0.931).

## Structural opportunity did not determine realized scale tilt

Seven of the 28 common-frame clades had no fine-to-coarse compression opportunity; in all seven, global fine-minus-coarse tilt was necessarily zero because the partitions were identical. Twenty-one clades contained fine distinctions hidden by the coarse coding. Among those 21, 15 had positive global fine-minus-coarse tilt and six had negative tilt; median tilt was +0.01998 AUC.

However, the magnitude of coarse aggregation did not determine the realized tilt. Within opportunity clades, collapsed-state count, Shannon entropy loss, and pair-collision gain were not significantly associated with signed tilt. Fine-state richness was unrelated to overall memory amplitude (rho = 0.0057, P = 0.977). The hierarchy therefore determines which scale differences are possible, but not how much history is retained overall.

## Fine identity retained hidden phylogenetic memory inside coarse states

The direct within-coarse analysis revealed a more general pattern than global winner status. Of the 21 opportunity clades, **18/21** had positive permutation-centered hidden-memory effects. The median effect was **+0.0270 AUC**, with a clade-bootstrap 95% interval of +0.0084 to +0.0453. The cross-clade one-sided Wilcoxon test gave **P = 3.34 × 10^-5**, and the one-sided sign test gave **P = 7.45 × 10^-4**.

Six individual clades cleared P <= 0.05 under 9,999 within-coarse permutations: *Diospyros*, *Lonicera*, *Passiflora*, *Rosa*, *Solanum*, and *Symplocos*. The broader cross-clade result was not driven only by those large effects; most remaining clades showed smaller effects in the same direction.

Hidden fine memory was not simply another expression of the global fine-versus-coarse winner. The hidden-memory effect was weakly related to global scale tilt (rho = 0.110, P = 0.634) and to overall memory amplitude (rho = 0.131, P = 0.571). Among the six clades with negative global fine-minus-coarse tilt, **5/6** nevertheless retained positive hidden fine-memory effects. Thus a clade can be globally coarse-tilted while still preserving non-random fine organization inside the coarse phenotype.

## The same conditional pattern occurred in biochemical Petunieae

The Petunieae common frame retained 47 tips and six supported fine compound states. Within the frozen coarse anthocyanidin-presence groups, the observed conditional fine-state AUC was 0.7018. The within-coarse permutation mean was 0.5139, giving a centered hidden-memory effect of **+0.1879 AUC** with 9,999-permutation **P = 0.0001**.

Petunieae therefore provides a same-concept cross-representation example: biochemical compound identity remains phylogenetically organized after coarse pigment presence is fixed. Because the system is retrospective and is currently the only completed biochemical same-estimand bridge, it cannot establish a universal biochemical hierarchy.

## Independent external radiations support conditional fine-state organization

Three additional radiations—Linoideae, Angraecinae, and Antirrhineae—each support conditional fine-state phylogenetic organization in a source-faithful analysis. Their phenotype dimensions are hue, floral-organ configuration, and pigment class, respectively. All three testable radiations support the conditional pattern, but their estimators and source structures differ from the standardized visible-color and Petunieae analyses. We therefore treat this **3/3** as qualitative radiation-level replication rather than a pooled significance calculation.

## Prospective cross-representation validation remains unresolved

The outcome-unopened *Ruellia* biochemical system now carries a frozen conditional prediction. If its retained HPLC frame contains fine-to-coarse compression opportunity, fine compound states are predicted to retain positive within-coarse hidden memory under the same 9,999-permutation logic. Row-level HPLC states, frequencies, and AUCs remain unopened. The only blocker is recovery of the authoritative tree used by the source analysis. Consequently, current evidence supports a replicated candidate architecture but not a universal hierarchical-memory law.

# Discussion

The search for one optimal phenotype resolution led to a negative result because the phenotype does not store history at only one level. The cross-radiation evidence instead supports a nested interpretation: coarse states can retain broad historical structure while finer identities preserve additional phylogenetic organization inside those states. Under this view, coarse and fine resolutions are not competing descriptions from which evolution must choose one winner. They can simultaneously encode different components of lineage history.

This distinction resolves several otherwise awkward results. The preregistered intermediate optimum failed in *Iris*, and no replacement universal coarse or fine winner appeared in the standardized clade batch. Yet the failure of a global winner does not imply absence of fine structure. Five of six clades that were globally coarse-tilted still showed positive fine-state organization after coarse membership was held fixed. The apparent contradiction disappears once global scale tilt and within-state hidden memory are treated as distinct quantities.

The architecture now separates at least three components. Memory amplitude measures how much historical organization remains across the phenotype overall and is strongly related to relative-divergence persistence. Global scale tilt measures whether the full clade-level signal is more visible in a coarse or fine representation. Hierarchical hidden memory asks whether finer distinctions remain organized after a broad state has already been fixed. These axes are empirically weakly coupled. The biological problem therefore shifts from identifying one best coding scale to predicting the processes controlling each component.

The hierarchical interpretation is consistent with, but goes beyond, earlier single-system observations. Ng and Smith (2016) showed that convergent red flowers can retain phylogenetic signal in the biochemical pathway used to produce red coloration. Ng, Freitas, and Smith (2018) showed that anthocyanin evolution follows constraints imposed by pathway architecture. These studies establish that mechanism can be historically structured within a broad phenotype and that biochemical state space is nonuniform. Likewise, aggregated-state-space theory demonstrates that recoding can hide phylogenetic information (Weber et al., 2021). Our novelty claim is therefore not first recognition of any of those principles. It is the cross-radiation generalization and decomposition: a standardized conditional estimand reveals hidden fine-state memory in 18 of 21 visible-color clades, that hidden memory is empirically distinct from overall memory amplitude and global winner status, the same conceptual estimator produces a strong biochemical Petunieae effect, and three additional radiations provide independent conditional-hierarchy support without being statistically pooled.

The Petunieae result is especially informative because it changes phenotype representation while retaining the conceptual question. Its +0.1879 conditional AUC effect indicates that exact compound identity remains organized inside a coarse pigment-presence state. This mirrors the visible-color pattern, but one biochemical radiation is insufficient to establish cross-representation generality. For that reason we have not upgraded the retrospective synthesis into a universal rule.

The prospective *Ruellia* gate is therefore decisive. Its HPLC hierarchy was frozen before CHUN opened row-level compound states, and the hidden-memory prediction was fixed while outcomes remained unavailable. A PASS would supply a genuinely held-out biochemical test of whether fine identity remains organized after coarse membership is fixed. A FAIL would show that the visible-color and retrospective Petunieae pattern does not automatically generalize to another biochemical radiation. A source or common-frame HOLD would remain non-biological. This candidate manuscript is intentionally not promoted over the frozen v0.3 submission before that gate is resolved; **the current submission remains v0.3**.

The new framework also sharpens future ecological and mechanistic questions. Processes that alter overall turnover—environmental shifts, repeated convergence, hybridization, or rapid signal evolution—may primarily affect memory amplitude. By contrast, developmental architecture, pollinator sensory discrimination, or biochemical pathway branching may determine whether fine distinctions remain organized within a coarse state. These predictions can be tested separately rather than forcing one moderator to explain the entire three-resolution profile.

There are important limitations. The standardized 21-clade hidden-memory result is exploratory and post-outcome, even though the estimator is fixed and source-exact. Petunieae is retrospective. The three external radiations use nonexchangeable estimators and cannot be pooled numerically. Hidden-memory AUC measures same-state phylogenetic organization, not ancestral polymorphism duration, transition direction, or absolute time. Nor does it identify one causal mechanism. Finally, the presently blocked source systems show that a phenotype hierarchy must be both biologically meaningful and supported by sufficient replicated state counts before this framework can be applied.

The strongest current conclusion is therefore conditional but positive. Flower-color history is not well described by one scale-optimal representation. Across multiple radiations, fine phenotype identity often preserves additional historical organization after coarse state membership is fixed, while the amount of retained history and the globally dominant scale vary separately. Evolutionary memory in flower color is thus better viewed as a hierarchical architecture than as a contest among coarse, intermediate, and fine encodings. Prospective biochemical falsification remains the next test.

# Data and code availability

All analysis contracts, exact-source manifests, machine-readable results, validation workflows, and evidence-tier syntheses are versioned in the `zuizui0223/chun` repository. The standardized 51-clade source data are archived in Dryad under DOI 10.5061/dryad.r4xgxd2sc. Petunieae processed data and code are archived at OSF node `zg9cu`. The outcome-unopened *Ruellia* source is deposited in Figshare under DOI 10.6084/m9.figshare.30282448; its authoritative author-used tree remains the current source-provenance blocker. A submission-specific repository snapshot would be assigned a persistent archive identifier before any promotion of this candidate.

# Figure legends and alt text

**Figure 1. From winner profiles to memory architecture.** The original coarse/intermediate/fine profile is decomposed into overall memory amplitude, global coarse-to-fine tilt, and intermediate curvature. Across 28 standardized clades, amplitude accounts for 90.65% of between-clade profile variance. **Alt text:** A schematic three-bar phenotype profile is projected onto three labeled axes; a variance bar chart shows amplitude as the dominant component, with much smaller tilt and curvature components.

**Figure 2. Hidden fine memory across standardized visible-color clades.** Permutation-centered within-coarse conditional AUC effects for 21 clades with fine-to-coarse compression opportunity. Eighteen effects are positive; the median is +0.0270 AUC. **Alt text:** A horizontal dot plot shows 21 clade effects around a zero reference line, with most points to the positive side and several larger positive effects.

**Figure 3. Hidden memory is distinct from global scale tilt.** Clade-level hidden-memory effects are plotted against fine-minus-coarse global AUC tilt. Positive hidden effects occur on both sides of zero global tilt, including five of six globally coarse-tilted clades. **Alt text:** A scatterplot spans negative and positive global tilt on the x-axis while most hidden-memory effects remain above zero on the y-axis.

**Figure 4. Petunieae biochemical hidden memory.** Observed within-coarse conditional AUC is compared with its 9,999-permutation distribution. The centered effect is +0.1879 AUC and P = 0.0001. **Alt text:** A null histogram is centered near 0.514, while the observed Petunieae AUC near 0.702 lies far to the right.

**Figure 5. Evidence tiers and prospective falsification gate.** Standardized visible-color evidence, retrospective biochemical Petunieae evidence, three non-pooled external conditional-hierarchy radiations, and the outcome-unopened prospective *Ruellia* test are shown as separate evidence tiers. **Alt text:** Four stacked boxes progress from standardized retrospective evidence to independent external support and end with a clearly marked pending prospective Ruellia gate.

# References

McEwen, J. R., & Vamosi, J. C. (2010). Floral colour versus phylogeny in structuring subalpine flowering communities. *Proceedings of the Royal Society B: Biological Sciences, 277*, 2957–2965. https://doi.org/10.1098/rspb.2010.0501

Ng, J., & Smith, S. D. (2016). Widespread flower color convergence in Solanaceae via alternate biochemical pathways. *New Phytologist, 209*, 407–417. https://doi.org/10.1111/nph.13576

Ng, J., Freitas, L. B., & Smith, S. D. (2018). Stepwise evolution of floral pigmentation predicted by biochemical pathway structure. *Evolution, 72*, 2792–2802. https://doi.org/10.1111/evo.13589

Roguz, K., Gallagher, M. K., Senden, E., Bar-Lev, Y., Lebel, M., Heliczer, R., & Sapir, Y. (2020). All the colors of the rainbow: Diversification of flower color and intraspecific color variation in the genus *Iris*. *Frontiers in Plant Science, 11*, 569811. https://doi.org/10.3389/fpls.2020.569811

Shrestha, M., Dyer, A. G., Bhattarai, P., & Burd, M. (2014). Flower colour and phylogeny along an altitudinal gradient in the Himalayas of Nepal. *Journal of Ecology, 102*, 126–135. https://doi.org/10.1111/1365-2745.12185

[dataset] Sinnott-Armstrong, M., Maier, L., Smith, S. D., & Dellinger, A. S. (2025). Data from: Flower clades and fruit clades: Trade-offs in color diversification across angiosperms. Dryad. https://doi.org/10.5061/dryad.r4xgxd2sc

Sinnott-Armstrong, M., Maier, L., Smith, S. D., & Dellinger, A. S. (2026). Flower clades and fruit clades: Trade-offs in color diversification across angiosperms. *American Journal of Botany, 113*, e70146. https://doi.org/10.1002/ajb2.70146

Weber, C. C., Perron, U., Casey, D., Yang, Z., & Goldman, N. (2021). Ambiguity coding allows accurate inference of evolutionary parameters from alignments in an aggregated state-space. *Systematic Biology, 70*, 21–32. https://doi.org/10.1093/sysbio/syaa036

Wheeler, L. C., Dunbar-Wallis, A., Schutz, K., & Smith, S. D. (2023). Evolutionary walks through flower colour space driven by gene expression in *Petunia* and allies (Petunieae). *Proceedings of the Royal Society B: Biological Sciences, 290*, 20230275. https://doi.org/10.1098/rspb.2023.0275
