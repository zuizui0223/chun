# Flexible molecular routes coexist with locally conserved flower colours in *Camellia*

**Running head:** Molecular flexibility and flower-colour conservatism

> Draft v0.1. This manuscript consumes the frozen Paper 1 authoritative-result and analysis-disposition registries. It must not be used to reintroduce provenance-only or excluded results as positive claims.

## ABSTRACT

### Premise of the study

Flower-colour states can be generated through multiple pigment-pathway routes, but molecular accessibility need not imply macroevolutionary lability. We asked whether molecular routes to colour are repeatable and whether wild flower colours remain phylogenetically constrained after accounting for taxonomy, polymorphism, and nuclear-topology uncertainty.

### Methods

We combined sequence-aware synthesis of *Camellia* pigment mechanisms with a 339-locus Angiosperms353 nuclear framework. FLS, DFR, ANS/LDOX, and ANR evidence was resolved to paralog or family level where possible. Nuclear tips were normalized to World Flora Online 2026-06 accepted species, and colour states were audited against wild/floristic descriptions. We tested colour structure with count-preserving permutations on accepted-species topologies derived from FastTree and IQ-TREE/UFBoot gene trees.

### Key results

Molecular recurrence did not require one exact gene: FLS showed same-lineage recurrence, whereas independent DFR clusters used different paralog subclasses. Ninety-three legacy *Camellia* tips collapsed to 55 accepted species; 35 provisional hard colour states became strict 24-species and dominant-colour 30-species seeds. The nuclear pipelines shared 46/50 nontrivial splits. Nearest-same-colour conservatism persisted across trait and topology sensitivities; on the UFBoot topology, *P* = 0.00116 (strict) and *P* = 0.000080 (dominant). Broad same-colour mean pairwise-distance clustering was topology-sensitive, and no accepted-species colour-transition branch was robust to both trait scenarios.

### Conclusions

Flexible molecular implementations coexist with local phylogenetic conservatism of wild flower colour. Current public data identify this cross-scale pattern but not robust transition events to which ecological or molecular causes can be assigned. Population-resolved sensory, reproductive, environmental, and paralog-specific expression data are needed to test why accessible floral states persist.

**Key words:** anthocyanin; *Camellia*; evolutionary constraint; flavonol; flower colour; macroevolution; paralog substitution; phylogenetic conservatism; pollination; trait evolution

---

# INTRODUCTION

A central problem in evolutionary biology is to distinguish the processes that make a phenotype *accessible* from those that make it *persistent*. Developmental and biochemical systems can permit many phenotypic states, yet only a subset may recur, spread, or remain stable over macroevolutionary time. Flower colour is an unusually tractable system for studying this distinction because its biochemical basis is comparatively well characterized, transitions are common enough to compare among lineages, and the resulting phenotypes can be exposed simultaneously to biotic and abiotic selection. Anthocyanins and other flavonoids can affect floral appearance while also participating in physiological functions, and colour phenotypes can alter interactions with animal visitors. Consequently, the evolutionary interpretation of a flower-colour shift cannot be inferred from visible hue alone (Rausher, 2008; Wessinger and Rausher, 2012; Trunschke et al., 2021; Berardi et al., 2026).

Much of the molecular literature on flower-colour evolution has focused on the identity of genes associated with completed phenotypic shifts. The anthocyanin pathway is sufficiently conserved that repeated phenotypes can sometimes involve homologous genes or homologous regulatory changes, but the pathway also contains duplicated enzymes and multiple regulatory entry points. Whether evolutionary repetition should therefore be expected at the level of an exact gene, a paralogous gene family, a biochemical module, or only a final pigment state remains an open question. This distinction matters for macroevolutionary prediction. If the same exact node is repeatedly reused, molecular accessibility may strongly constrain which transitions occur. If alternative paralogs or regulatory routes can implement similar pathway states, then molecular accessibility may be broad even when realized phenotypes remain phylogenetically restricted.

Ecological explanations are similarly plural. Pollinators have long been invoked as agents of flower-colour evolution, but direct evidence for pollinator-mediated selection on within-population colour variation remains limited and context dependent (Trunschke et al., 2021). Pigments can also respond to temperature, radiation, drought, herbivores, pathogens, or other selective agents, and recent syntheses emphasize interactions rather than one universal driver (Rausher, 2008; Lacey, 2025; Berardi et al., 2026). Visible colour itself is an imperfect ecological state variable: two flowers perceived as similar by humans can differ in ultraviolet reflectance, fluorescence, pigment chemistry, reward, morphology, phenology, and pollinator perception. Thus, a macroevolutionary association between visible hue and environment may fail either because colour is not under ecological selection or because visible hue compresses the actual sensory and functional phenotype on which selection acts.

The genus *Camellia* provides a useful test case because it combines extensive visible flower-colour diversity with a growing body of mechanistic, genomic, transcriptomic, ecological, and phylogenomic data. Recent phylogenomic studies have also demonstrated that *Camellia* is a difficult system in which to infer trait history naively. Transcriptomic and genomic analyses recover rapid radiation, substantial gene-tree discordance, and reticulate evolution, while historical taxonomy contains many names that do not correspond one-to-one with currently accepted species (Wu et al., 2022; Zan et al., 2023; Zhang et al., 2023; Yan et al., 2024). Most recently, Fan et al. (2026) used 237 accessions and 11 genome assemblies to reconstruct a broad *Camellia* genomic framework, infer a likely white ancestral flower, and identify transposable-element-mediated structural variants associated with regulatory rewiring and flower-colour diversification. Those advances make it unnecessary—and unhelpful—for another study to claim novelty simply by reconstructing a *Camellia* tree or proposing a white ancestor. A remaining question is instead whether the growing molecular evidence for accessible pigment changes translates into evolutionary lability of wild flower-colour states.

Here, we used a falsification-oriented, cross-scale analysis to ask four linked questions (Figure 1). First, do independent *Camellia* flower-colour studies repeatedly implicate the same molecular node, or can similar pathway states be reached through different paralogs? Second, after normalizing nuclear samples to a current accepted-species taxonomy and auditing species-level colour assignments against wild/floristic evidence, do flower-colour states remain phylogenetically structured? Third, is any inferred macro pattern robust to uncertainty in nuclear gene-tree inference and to alternative treatment of naturally variable colour states? Fourth, do the available public data identify particular transition branches strongly enough to assign climate, pollination, or molecular causes? Our results show that molecular implementation can be flexible while wild flower colour remains locally phylogenetically conservative. At the same time, the accepted-species trait evidence is insufficient to identify branch-specific causal events robustly. This combination shifts the empirical question from how flower-colour states can be generated to why accessible states persist.

# MATERIALS AND METHODS

## Study design and inferential hierarchy

We separated molecular accessibility, phylogenetic pattern, trait history, and ecological interpretation into sequential gates. Information from a downstream layer was not used to tune an upstream layer. In particular, flower-colour, climate, pollinator, and molecular mechanism labels were absent from nuclear marker selection and species-tree inference. Analyses that were later invalidated by taxonomy, wild-colour polymorphism, or topology sensitivity were retained as provenance but excluded from current positive claims. The current result set, figure dependencies, and analysis disposition are machine-readable in `data/paper1_authoritative_results_v0_1.csv`, `data/paper1_main_figure_manifest_v0_1.csv`, and `data/paper1_analysis_disposition_v0_1.csv`.

## Sequence-aware synthesis of pigment-pathway accessibility

We compiled public *Camellia* flower-colour studies that contained transcriptomic, genomic, sequence, primer, or functional evidence for pigment-pathway genes. Evidence was grouped into independent study clusters rather than counted by individual differential-expression rows. We focused here on four recurrent pathway families—flavonol synthase (FLS), dihydroflavonol 4-reductase (DFR), anthocyanidin synthase/leucoanthocyanidin dioxygenase (ANS/LDOX), and anthocyanidin reductase (ANR)—and resolved the implicated sequence to paralog or family level where public evidence allowed.

For FLS, the petal-associated CnFLS2 target from *C. nitidissima* was connected to the public telomere-to-telomere genome using the published primer pair, source PacBio reads, full-length sequence recovery, protein-family comparison, and local gene-context comparison. The corresponding tea source locus `CSA008358` was resolved through a public gene crosswalk and compared at nucleotide, protein, and local-context levels. CnFLS1 (`JF343560.1`) was retained as an independent FLS reference rather than conflated with CnFLS2. Primary provenance includes Feng et al. (2024), the public F01 PacBio run `SRR22729450`, the *C. nitidissima* T2T genome, and Zhou et al. (2013).

For DFR, the partial *C. japonica* CjDFR clone `AB524885.1` (Tateishi et al., 2010) was compared with the six tea DFR-family reference candidates classified by Mei et al. (2019). Published CjDFR primer pairs, including the 167-bp assay of Larcher et al. (2015), were used as independent assay-to-sequence links. The white/pink tea source locus `CSA003949` from Zhou et al. (2020) was cross-walked to the tea DFR reference family before paralog classification. ANS/LDOX and ANR evidence was treated more conservatively because several source contrasts use reference-mapped or family-level features rather than deposited species-native orthologs. These analyses support copy-aware directional heterogeneity but were not interpreted as strict-node recurrence.

All source claims were separated from project inference. The machine-readable source-provenance table lists the primary article, DOI or stable locator, public accession/run, exact claim supported by the source, and the additional inference made by sequence matching or crosswalk (`data/paper1_micro_source_provenance_v0_1.csv`).

## Nuclear marker recovery and topology sensitivity

We used the publicly released transcriptomic resources associated with the genus-scale sampling of Wu et al. (2022) as an independent nuclear backbone rather than reproducing the published 405-locus tree itself. Public transcriptome assemblies were audited for provenance, and unavailable or colliding assembly resources were explicitly moved to raw-read fallback rather than silently duplicated. For the topology-input panel, protein-coding sequences were screened against public Angiosperms353 targets. Candidate loci were retained only after global occupancy screening; 339 loci met the predeclared ≥80% occupancy criterion and were aligned independently with MAFFT. Marker selection and alignment were completed before any flower-colour data were joined.

We inferred two independent gene-tree ensembles from the same frozen locus set. A rapid sensitivity pipeline used FastTree with an LG+gamma protein model. A stronger pipeline used IQ-TREE with fixed LG+G4 and 1000 ultrafast bootstrap replicates. Gene trees were summarized with current ASTRAL/ASTER methods. The purpose of these trees was not to establish a new genus phylogeny, but to test whether downstream flower-colour patterns depended on gene-tree inference method. Existing *Camellia* phylogenomic studies document substantial deep discordance and reticulation (Zan et al., 2023; Zhang et al., 2023; Yan et al., 2024), so downstream claims were required to survive topology sensitivity where possible.

## Accepted-species taxonomy

Historical *Camellia* names in the nuclear sampling were normalized against a pinned World Flora Online Plant List 2026-06 snapshot (Zenodo DOI `10.5281/zenodo.20782718`). All legacy tree tips were mapped before accepted-species inference. The 93 legacy *Camellia* tips represented 55 accepted species; 20 accepted groups contained multiple legacy tips. We therefore used ASTRAL's multi-individual mapping rather than pruning an arbitrary representative. *Polyspora speciosa* was retained as an independent outgroup where the relevant marker data were available.

For topology sensitivity on the stronger UFBoot gene-tree ensemble, 53 accepted *Camellia* species were shared with the FastTree accepted-species topology. We compared nontrivial unrooted splits and Robinson–Foulds distance on this common species set.

## Wild/floristic flower-colour audit

Species-level colour states were not accepted directly from a single compiled source. After taxonomic collapse, 36 accepted species had at least one colour observation or taxonomically induced conflict, including 35 provisional single hard states. We audited every observed accepted species against species-level wild/floristic evidence. Sources were graded as authoritative flora/peer-reviewed/official species descriptions, curated species registers, or insufficient secondary evidence. Polymorphic states were not forced into one strict colour. Species described as having one dominant colour with rare alternatives or senescence-related tints were included only in a separate dominant-colour sensitivity.

This produced two trait seeds. The strict wild seed contained 24 accepted species (A = 1, W = 19, Y = 4). The dominant-colour sensitivity contained 30 species (A = 4, W = 22, Y = 4). Eleven provisional hard labels were demoted in the strict analysis. High-risk examples included *C. japonica*, *C. saluenensis*, *C. brevistyla*, and *C. cuspidata*, which were treated as naturally polymorphic rather than assigned one hard A/W state. *C. reticulata*, *C. polyodonta*, and *C. subintegra* were treated as dominant-A/rare-W sensitivities rather than strict A. Exact source locators and evidence grades are given in `data/wfo55_accepted_species_wild_colour_registry_v0_1.csv` and the source audit.

## Tests of phylogenetic flower-colour structure

We tested phylogenetic structure using unrooted topology edge counts so that the primary pattern analysis did not depend on ancestral-state assumptions or treating ASTRAL branch lengths as divergence times. For each trait scenario and topology, we calculated (1) mean pairwise distance among species sharing a colour state, where estimable, and (2) the mean distance from each labelled species to its nearest same-colour relative. Observed values were compared with 100,000 count-preserving permutations of A/W/Y labels among the same labelled nuclear tips.

We separately tested a global same-state mean pairwise-distance statistic and the nearest-same-state statistic. This distinction was pre-specified as a robustness check because a state can exhibit local clustering without forming one globally compressed clade. Singleton colour categories were excluded symmetrically from nearest-same-state calculations in observed and permuted data.

## Rooted colour-history and event-identifiability sensitivity

For the accepted-species FastTree/ASTRAL sensitivity tree, we fitted three-state continuous-time Mk models under equal-rates (ER), symmetric (SYM), and all-rates-different (ARD) parameterizations. We compared use of ASTRAL branch lengths with unit-edge topology sensitivity and equal versus stationary root priors. Models were compared by AICc, and root and branch endpoint-state probabilities were model-averaged within each treatment.

Trait history was reconstructed independently for the strict and dominant-colour seeds. A branch was eligible for downstream event-level analysis only if it showed the same top directional endpoint contrast across all four Mk treatments within each trait scenario, passed the predeclared posterior threshold within each scenario, retained the same direction in strict and dominant analyses, and had cross-scenario minimum directional posterior ≥0.5. This gate was designed to prevent branch-level ecological or molecular analyses from being conditioned on trait assignments that disappear when natural polymorphism is acknowledged.

## Climate and pollination screening

Ecological analyses were treated as screening evidence, not branch-level causal tests. For climate, we used provenance-audited central thermal summaries derived from species occurrence data and CHELSA variables. A within-section screen compared standardized climatic distance for A–W pairs with same-colour pairs in the two historical sections containing both states. Colour labels were permuted within section 100,000 times to preserve the coarse history proxy and observed colour counts. This analysis tested a narrow prediction of a universal visible A/W–thermal divergence chain.

For pollination, we compiled primary studies only where a broad effective or functional pollinator class could be defended. Because experimental designs were heterogeneous, we did not pool incompatible effect sizes. Instead, we tested whether coarse visible A/W/Y state behaved as a deterministic reproductive-function category and documented cases in which pollination weighting changed with season, weather, or disturbance without a corresponding visible-hue change. This layer was used to evaluate whether visible hue is a sufficient ecological state variable, not to infer genus-level pollinator-driven evolution.

## Reproducibility and manuscript-result governance

All analyses were implemented as versioned scripts and GitHub Actions workflows. Authoritative, sensitivity, superseded, and excluded results are frozen in `data/paper1_authoritative_results_v0_1.csv`. Figure dependencies are frozen separately, and continuous-integration checks prevent superseded results from re-entering the Main figure pipeline. Current analyses are assigned explicitly to Main, Supplement, provenance-only, or excluded categories. The source audit separates primary-source statements from project inferences based on primer matching, crosswalks, sequence comparison, or synteny.

# RESULTS

## Recurrent pigment modules permit more than one implementation mode

The molecular synthesis did not support a simple rule that repeated flower-colour variation uses the same exact gene. Instead, the best-resolved pathway families illustrated at least two implementation modes (Figure 2).

For FLS, the *C. nitidissima* CnFLS2 source target was resolved to a public full-length genomic/transcript candidate and shared a highly similar lineage with the tea source locus `CSA008358`. The complete coding sequences were 98.824% identical and their proteins were 98.23% identical; in the admitted FLS family tree the pair was exclusive sisters with support 0.977. Primer matching, source-read recovery, and local-context comparisons supported this same-lineage interpretation. The later white-directed tea locus `CSA006950` belonged to a different FLS paralog and was not collapsed into the same node.

DFR showed the complementary pattern. The *C. japonica* partial CjDFR clone `AB524885.1` matched canonical tea CsDFRa at 99.005% protein identity, whereas the independent white/pink tea source locus `CSA003949` mapped to CsDFRb2. Thus both evidence clusters implicated the DFR module but not the same paralog subclass. ANS/LDOX and ANR further showed copy-aware directional heterogeneity, but their public evidence did not justify species-native strict-node recurrence. Together these results supported molecular accessibility at the module/family level while showing that exact-node reuse was not a universal explanation.

## Taxonomic and wild-colour auditing reduced apparent macro trait information

The historical nuclear sampling initially contained 93 named *Camellia* tips. Mapping to WFO Plant List 2026-06 reduced these to 55 accepted *Camellia* species (Figure 3). Twenty accepted species groups contained multiple historical tips, demonstrating that treating each legacy label as an independent species would inflate evolutionary opportunities and trait-state counts.

Trait auditing caused an additional reduction. Thirty-five accepted species initially carried provisional single hard colour labels after taxonomy aggregation. Species-level wild/floristic evidence reduced the strict seed to 24 species (A = 1, W = 19, Y = 4), demoting 11 provisional hard labels. The dominant-colour sensitivity retained 30 species (A = 4, W = 22, Y = 4). Natural A/W polymorphism accounted for several important demotions, including *C. japonica*, *C. saluenensis*, *C. brevistyla*, and *C. cuspidata*. Species with a dominant pigmented colour but documented rare white flowers were retained only in the dominant sensitivity. Thus much of the apparent species-level colour certainty in the un-audited data reflected compression of within-species variation rather than stable wild states.

## Accepted-species nuclear topologies were highly, but not perfectly, concordant

On the 53 accepted species shared by the FastTree and IQ-TREE/UFBoot gene-tree ensembles, each ASTRAL topology contained 50 nontrivial splits (Figure 4). Forty-six splits were shared, corresponding to reciprocal split recall of 0.92, split Jaccard similarity of 0.8519, and a Robinson–Foulds symmetric difference of 8 (normalized RF = 0.08). Thus the accepted-species nuclear backbone was highly concordant across gene-tree methods, but four nontrivial splits per tree differed. We consequently required the flower-colour pattern to be evaluated independently on both topologies rather than assuming that the FastTree sensitivity tree was sufficient.

## Local same-colour conservatism survived trait and topology sensitivity

The most robust macroevolutionary pattern was local rather than global phylogenetic conservatism of flower colour (Figure 5). On the FastTree accepted-species topology, the mean distance to the nearest same-colour relative was lower than expected under count-preserving randomization in both the strict wild seed (*P* = 0.00212) and dominant-colour sensitivity (*P* < 0.00001). The result reproduced on the stronger UFBoot accepted-species topology: strict *P* = 0.00116 and dominant *P* = 0.000080.

By contrast, broad same-colour mean pairwise-distance clustering was not topology robust. It was significant on the FastTree accepted-species topology (strict *P* = 0.00803; dominant *P* = 0.00770) but not on the UFBoot topology (strict *P* = 0.1724; dominant *P* = 0.1327). We therefore rejected broad/global same-colour clade compression as a headline result. The surviving conclusion is narrower: a species with a known wild colour tends to have a closer same-colour relative than expected from random placement, even though all species of one colour do not form one globally compact phylogenetic set.

State-specific results reinforced the distinction between robust and sensitivity-only claims. Yellow states were clustered on the UFBoot topology in both trait scenarios. Anthocyanin-like A states could not be tested in the strict seed because only one accepted species retained a strict A state; A clustering appeared only under the dominant-colour sensitivity. A-specific lineage permissivity was therefore not retained as a strict result.

## Public hard-state data did not identify robust accepted-species transition branches

Accepted-species rooted colour-history analyses favoured W as the top crown state, but meaningful W/Y uncertainty remained under topology-only sensitivity, and ancestral colour was not treated as a primary result. More importantly, directional branch inference was highly sensitive to how naturally variable species were represented.

Under the strict wild-colour seed, no branch passed the predeclared strong-transition gate. Under the dominant-colour sensitivity, one W→A branch passed the within-scenario gate. No branch was robust to both strict and dominant assumptions. The strict × dominant cross-scenario accepted branch count was therefore zero (Figure 6).

This result superseded earlier legacy-tip analyses that had identified apparently robust W→A events before current taxonomy and wild-colour variation were imposed. Because no accepted-species event survived the trait-scenario gate, we did not proceed to branch-specific tests of climate, pollinator regime, or molecular-module enrichment using the same hard-state public data.

## Simple visible-colour ecological explanations were insufficient

The ecological screens provided context for the cross-scale pattern but did not identify its cause. Within the only two historical sections containing both A and W species in the climate screen, different-colour pairs were not more climatically divergent than same-colour pairs. Mean standardized climate distance was 1.88475 for A–W pairs versus 2.35668 for same-colour pairs; the one-sided permutation test for greater divergence of different-colour pairs gave *P* = 0.92889 and the two-sided test gave *P* = 0.18486. These data did not support a universal chain from visible A/W divergence to thermal-niche divergence.

The pollination synthesis likewise showed that visible hue was not a deterministic reproductive-function state. Primary evidence included contrasting broad pollinator functions within the same visible colour, and pollination weighting could change with season, weather, or disturbance without a visible-hue change. After updating *C. oleifera* with direct bird-exclusion evidence, the count-preserving hue–pollinator-function association remained weak in the small evidence seed (*P* = 0.77127). This result was not interpreted as evidence of independence; instead, it indicated that coarse A/W/Y labels are insufficient to represent the full sensory, reward, and reproductive phenotype relevant to ecological filtering.

# DISCUSSION

## Molecular accessibility does not guarantee macroevolutionary lability

The central result of this study is a mismatch across biological scales. At the molecular scale, *Camellia* pigment pathways provide more than one route to a related biochemical outcome. FLS contains a well-resolved case of recurrence within the same paralog lineage, whereas DFR demonstrates that independent evidence clusters can implicate the same pathway step through different paralog subclasses. ANS/LDOX and ANR add further evidence that copy identity and direction cannot safely be compressed into a single gene-symbol effect. These observations are consistent with a pathway architecture in which evolutionary change can occur through several molecular implementations.

At the macroevolutionary scale, however, wild visible colour is not correspondingly unconstrained. Once historical names were collapsed to accepted species and species-level colour was audited against wild descriptions, the remaining states still showed a repeatable nearest-same-colour signal on two independently inferred nuclear topologies. The result is not that colour states form a few globally compact clades—the broad MPD statistic was topology-sensitive—but that local phylogenetic neighbourhood matters. Closely related species are more likely than expected to share the same coarse colour state.

This mismatch suggests that the availability of a molecular route and the long-term persistence of its phenotypic outcome are different evolutionary problems. An accessible mutation or regulatory change can generate a colour state without guaranteeing that the state is maintained through speciation, ecological turnover, introgression, or changing reproductive environments. Conversely, local phylogenetic conservatism could arise from inherited developmental backgrounds, correlated floral traits, ecological niches, genetic interactions, or combinations of these processes. Our data do not distinguish among these mechanisms, but they show why molecular recurrence alone is insufficient to predict macroevolutionary lability.

## Taxonomy and polymorphism are part of the biological problem, not clerical noise

A major result of the analysis was the degree to which apparent macroevolutionary certainty depended on data representation. Ninety-three historical *Camellia* tree tips corresponded to only 55 WFO accepted species, and 35 provisional hard colour states fell to 24 strict wild states after floristic auditing. The same species that are most interesting for flower-colour evolution—*C. japonica*, *C. saluenensis*, *C. brevistyla*, and others—are also species in which one hard A/W label can be biologically misleading.

This is not merely a taxonomic nuisance. A polymorphic species contains information about the maintenance and accessibility of alternative states at the population level. Collapsing such a species to one colour can manufacture an apparently discrete macroevolutionary transition. In our analysis, previously robust legacy-tip W→A branches disappeared after accepted taxonomy and wild-colour uncertainty were imposed. The failure of those events to survive is therefore informative: the data resolution required to infer evolutionary events is finer than a one-state-per-species table provides for several key *Camellia* lineages.

The result also cautions against interpreting large compiled trait matrices as if all categorical entries were comparable observations. For flower colour, cultivated varieties, senescent colour change, rare morphs, taxonomic synonyms, and fresh wild-anthesis colour can all be compressed to the same categorical field. Explicit evidence grading and sensitivity seeds provide one way to prevent that compression from propagating into false certainty about transition history.

## The robust macro pattern is local, not global

The topology sensitivity sharpened rather than merely confirmed the macro result. FastTree and IQ-TREE/UFBoot accepted-species topologies were highly concordant overall, sharing 46 of 50 nontrivial splits, but the differences were sufficient to change the global MPD inference. Broad same-colour compression was significant on the FastTree topology but disappeared on the UFBoot topology. In contrast, nearest-same-colour conservatism survived both pipelines and both trait scenarios.

This distinction suggests a biologically plausible form of phylogenetic constraint. Colour states need not define one ancient conserved clade. Instead, they may persist within local regions of phylogenetic space while being gained, lost, or reconfigured elsewhere. Such a pattern is compatible with inherited developmental backgrounds or correlated trait complexes that act over limited evolutionary neighbourhoods. It is also consistent with the complex radiation and reticulation documented in *Camellia* by previous phylogenomic studies (Wu et al., 2022; Zan et al., 2023; Zhang et al., 2023; Yan et al., 2024).

The stricter result also weakens a tempting but unsupported narrative: anthocyanin-like A states are not demonstrably concentrated in one uniquely permissive nuclear background. A is not even estimable as a strict clustering category after wild-colour auditing. The general claim is therefore colour-wide local history dependence, not a special red-flower lineage.

## Visible hue is an observation layer, not necessarily the ecological selection target

Neither the climate nor pollination screens supplied a simple ultimate explanation. The direct thermal prediction failed at the available genus-level resolution: A/W differences did not correspond to greater thermal-niche divergence within coarse historical backgrounds. This does not exclude conditional effects of temperature, radiation, drought, or other abiotic variables on particular lineages or flowering windows. Indeed, anthocyanins can have physiological functions, and recent reviews emphasize direct and indirect temperature effects on flower-colour evolution (Lacey, 2025; Berardi et al., 2026). It does show that a universal visible-red/cold rule is not an adequate explanation for the current *Camellia* pattern.

Likewise, pollinator-mediated selection remains plausible but cannot be reduced to visible hue. The current primary-study synthesis contains different reproductive functions within the same coarse hue, and ecological context can alter pollinator weighting without changing visible colour. This agrees with broader evidence that flower-colour selection depends on receiver perception, behavioural context, and the relationship between floral signals and fitness (Trunschke et al., 2021). In *Camellia*, the selected phenotype may therefore be a latent combination of ultraviolet and visible reflectance, fluorescence, pigment chemistry, flower geometry, nectar reward, phenology, and visitor-specific effectiveness rather than A/W/Y alone.

This interpretation also connects back to the molecular result. If visible hue is a many-to-one projection of biochemical and sensory phenotypes, then paralog substitution need not imply ecological equivalence. Two pathways can converge on a similar human-visible state while differing in co-pigments, ultraviolet properties, pleiotropic effects, or developmental regulation. Conversely, the same visible state can be maintained while reproductive function changes through nectar, morphology, or season. A more mechanistic ecological test therefore requires joint measurement of the latent sensory/reward phenotype and fitness, not a larger categorical hue matrix alone.

## Pattern without identifiable events defines the public-data boundary

The most important negative result is that no accepted-species colour-transition branch was robust to both the strict wild-colour seed and the dominant-colour sensitivity. This does not mean that colour transitions did not occur. It means that current public hard-state data do not identify *which* accepted-species branch can safely be treated as a known event for causal enrichment.

That distinction defines a stop rule. Once event identity is trait-scenario sensitive, adding more complex branch×climate, branch×pollinator, or branch×molecular models cannot recover the missing information. The limiting data are population-level phenotype distributions and corresponding ecological and molecular measurements, not model sophistication. We therefore stopped the public-data causal program at the point where the macro pattern remained identifiable but event-level causes did not.

This boundary is particularly relevant in light of the rapidly expanding *Camellia* genomic literature. Fan et al. (2026) demonstrated lineage-specific TE-mediated structural variation and regulatory rewiring associated with flower-colour diversification across extensive genomic sampling. Our analysis addresses a different level of the problem. Rather than asking which genomic variants can generate colour diversity, we ask whether accessible molecular variation predicts how wild colour states are distributed and persisted across accepted species. The answer is mixed: molecular implementations are flexible and a local phylogenetic pattern remains, but the public phenotype data are not sufficiently resolved to match specific molecular or ecological causes to macroevolutionary transitions.

## Empirical tests should target persistence within naturally variable lineages

The public-data boundary specifies the next experiment rather than merely identifying a limitation. The highest-priority systems are naturally A/W polymorphic species such as *C. japonica*, *C. saluenensis*, *C. brevistyla*, and *C. cuspidata*, and pigmented-dominant species with rare white morphs such as *C. reticulata*, *C. polyodonta*, and *C. subintegra*. These systems allow comparisons within lineages and therefore reduce the phylogenetic confounding that limits genus-level species contrasts.

The key response variable should be effective pollination and reproductive performance, not visitor abundance alone. At the same populations and flowering windows, future studies should quantify morph frequencies; calibrated ultraviolet–visible spectra; fluorescence where present; anthocyanin/flavonol composition; flower size, orientation, and display; nectar quantity and composition; visitor identity and visitation; single-visit stigma pollen deposition; pollen removal; visitor-guild exclusion; fruit and seed set; and flowering-window temperature, radiation, rainfall, and wind. Petal developmental series should be sampled from the same material for paralog-specific FLS, DFR, ANS/LDOX, and ANR expression.

Such a design would distinguish several hypotheses that the present public data cannot separate. Pollination-service reliability predicts that sensory states track effective pollen transfer and reproductive success across weather or seasonal windows. Pollinator-conflict hypotheses predict that visual, chemical, or reward traits reduce costly visitors while retaining effective pollinators. A latent-state hypothesis predicts that spectra, chemistry, morphology, and reward outperform coarse A/W/Y labels in out-of-sample prediction of reproductive function. A molecular-memory hypothesis predicts that alternate morphs or seasonal states redeploy recurrent pathway modules through regulatory or paralog substitution rather than requiring repeated recreation of the same exact molecular node. Conditional abiotic filtering predicts morph-specific fitness or pigment deployment responses to environment that remain after pollination service is considered.

# CONCLUSIONS

Flower-colour evolution in *Camellia* cannot be summarized by either a single recurrent gene or a single ecological syndrome. Public molecular evidence shows that related pigment outcomes can be reached through both same-lineage recurrence and different-paralog implementation. After accepted-taxonomy normalization and wild-colour auditing, visible flower colour nevertheless retains a topology-robust local phylogenetic signal: species tend to have a nearer same-colour relative than expected by chance. Broad clade-level colour compression is not robust to nuclear-topology sensitivity, and no specific accepted-species colour-transition branch is robust to alternative treatment of naturally variable colour states.

The resulting picture is a cross-scale mismatch between flexible generation and constrained persistence. Current public data are sufficient to detect that mismatch, but not to assign branch-specific ecological or molecular causes. The next decisive step is therefore population-resolved empirical work in naturally variable *Camellia* lineages, where sensory phenotype, pollination service, reproductive fitness, flowering-window environment, and paralog-specific pigment-pathway deployment can be measured together.

# DATA AVAILABILITY AND REPRODUCIBILITY

All analyses use public source data and versioned reproducible workflows. The repository records exact public accessions/runs, taxonomy snapshot, species-level wild-colour source locators, sequence-anchor provenance, analysis scripts, GitHub Actions workflows, frozen result registries, and deterministic figure inputs. The WFO Plant List 2026-06 taxonomy snapshot is pinned by DOI `10.5281/zenodo.20782718`. Public nuclear transcriptomic provenance ultimately derives from the Wu et al. (2022) sampling and associated public resources; source-specific sequence accessions are listed in the repository machine-readable provenance files. The final manuscript should provide the archived repository DOI/release rather than a moving branch URL.

# FIGURE LEGENDS

**Figure 1. Hypothesis trajectory from molecular generation to evolutionary persistence.** Literature-derived abiotic, pollinator, and molecular-constraint alternatives were tested and refined across molecular and macroevolutionary layers. The universal direct climate chain and a deterministic visible-hue pollination syndrome were not supported by current screening data, shifting the central question toward persistence and a public-data identifiability boundary.

**Figure 2. Recurrent pigment modules can use different molecular implementations.** FLS provides a resolved same-lineage recurrence example, whereas independent DFR evidence clusters resolve to different paralog subclasses. ANS/LDOX and ANR provide supporting copy-aware heterogeneity but are not treated as strict-node macro recurrence.

**Figure 3. Taxonomy and wild-colour auditing reduce usable species-level trait states.** Ninety-three historical *Camellia* nuclear tips collapse to 55 WFO Plant List 2026-06 accepted species. Thirty-five provisional hard colour states are reduced to a strict 24-species wild seed and a 30-species dominant-colour sensitivity; 11 provisional hard labels are demoted in the strict analysis.

**Figure 4. Accepted-species nuclear topology is highly concordant across gene-tree methods.** On 53 shared accepted species, FastTree- and IQ-TREE/UFBoot-derived ASTRAL topologies share 46 of 50 nontrivial splits. Four splits are unique to each topology, giving Robinson–Foulds symmetric difference 8 and normalized RF 0.08.

**Figure 5. Local same-colour conservatism survives topology sensitivity, whereas global mean pairwise-distance clustering does not.** Nearest-same-colour permutation tests are significant under strict and dominant wild-colour assumptions on both FastTree and UFBoot accepted-species topologies. Global same-state MPD is significant on the FastTree sensitivity topology but not on the UFBoot topology and is not retained as a headline result.

**Figure 6. Public data identify a macro pattern but not robust accepted-species colour-transition events.** The strict wild-colour scenario yields zero strong transition branches; the dominant-colour sensitivity yields one; no branch is shared across scenarios under the predeclared robustness gate. Branch-specific causal modelling therefore stops, and the unresolved variables are handed to population-level empirical study.

# SUPPLEMENTARY ANALYSIS MAP

The Supplement should include: ANS/LDOX and ANR copy-aware evidence; accepted-species root-state sensitivity; FastTree topology and colour-conservatism sensitivity; the wild-colour/taxonomy stress test that invalidated legacy W→A events; intermediate Fan aggregation after taxonomy collapse; current machine-readable orthology tables; wild-colour source audit; and micro primary-source/accession audit.

Provenance-only analyses, including consumed runtime91 computation intermediates and historical orthology-ledger versions, should remain in the repository rather than being presented as independent Supplementary biological results. Excluded legacy headlines—the three 93-tip W→A events, definitive white-ancestor framing, A-specific lineage-permissivity headline, and topology-independent global-MPD headline—must not be presented as positive conclusions.

# REFERENCES — v0.1 verified core set

Berardi, A. E., J. C. del Valle, M. H. Koski, E. Narbona, and J. Whittall. 2026. Paradigm shifts in flower color: An introduction. *American Journal of Botany* 113: e70150. https://doi.org/10.1002/ajb2.70150

Fan, M., H. Jiang, Y. Qu, Y. Zhang, X. Li, and Y. Wang. 2026. Transposable Element-Mediated Structural Variation Drives Flower Colour Diversification in *Camellia*. *Plant Biotechnology Journal* 24: 1725–[final pages to verify in journal export]. https://doi.org/10.1111/pbi.70442

Feng, Y., J. Li, H. Yin, J. Shen, and W. Liu. 2024. Multi-omics analysis revealed the mechanism underlying flavonol biosynthesis during petal color formation in *Camellia nitidissima*. *BMC Plant Biology* 24: 847. https://doi.org/10.1186/s12870-024-05332-w

Geng, F., R. Nie, N. Yang, L. Cai, Y. Hu, S. Chen, X. Cheng, Z. Wang, and L. Chen. 2022. Integrated transcriptome and metabolome profiling of *Camellia reticulata* reveal mechanisms of flower color differentiation. *Frontiers in Genetics* 13: 1059717. https://doi.org/10.3389/fgene.2022.1059717

Lacey, E. P. 2025. Temperature and the evolution of flower color: A review. *American Journal of Botany* 113: e70106. https://doi.org/10.1002/ajb2.70106

Larcher, R., et al. 2015. Cold treatment breaks dormancy but jeopardizes flower quality in *Camellia japonica* L. *Frontiers in Plant Science* 6: 983. https://doi.org/10.3389/fpls.2015.00983

Mei, X., C. Zhou, W. Zhang, D. O. Rothenberg, S. Wan, and L. Zhang. 2019. Comprehensive analysis of putative dihydroflavonol 4-reductase gene family in tea plant. *PLOS ONE* 14: e0227225. https://doi.org/10.1371/journal.pone.0227225

Qu, Y., Z. Ou, Q. Q. Yong, X. Yao, et al. 2024. Coloration differences in three *Camellia reticulata* Lindl. cultivars: ‘Tongzimian’, ‘Shizitou’ and ‘Damanao’. *BMC Plant Biology* 24: 18. https://doi.org/10.1186/s12870-023-04655-4

Rausher, M. D. 2008. Evolutionary transitions in floral color. *International Journal of Plant Sciences* 169: 7–21. https://doi.org/10.1086/523358

Tateishi, N., Y. Ozaki, and H. Okubo. 2010. Molecular cloning of the genes involved in anthocyanin biosynthesis in *Camellia japonica*. *Journal of the Faculty of Agriculture, Kyushu University* 55: 21–28.

Trunschke, J., K. Lunau, G. H. Pyke, Z.-X. Ren, and H. Wang. 2021. Flower color evolution and the evidence of pollinator-mediated selection. *Frontiers in Plant Science* 12: 617851. https://doi.org/10.3389/fpls.2021.617851

Wessinger, C. A., and M. D. Rausher. 2012. Lessons from flower colour evolution on targets of selection. *Journal of Experimental Botany* 63: 5741–5749. https://doi.org/10.1093/jxb/ers267

Wu, Q., W. Tong, H. Zhao, R. Ge, R. Li, J. Huang, F. Li, et al. 2022. Comparative transcriptomic analysis unveils the deep phylogeny and secondary metabolite evolution of 116 *Camellia* plants. *The Plant Journal* 111: 406–421. https://doi.org/10.1111/tpj.15799

Yan, Y., R. R. da Fonseca, C. Rahbek, M. K. Borregaard, and C. C. Davis. 2024. A new nuclear phylogeny of the tea family (Theaceae) unravels rapid radiations in genus *Camellia*. *Molecular Phylogenetics and Evolution* 196: 108089. https://doi.org/10.1016/j.ympev.2024.108089

Zan, T., Y.-T. He, M. Zhang, T. Yonezawa, H. Ma, Q.-M. Zhao, W.-Y. Kuo, W.-J. Zhang, and C.-H. Huang. 2023. Phylogenomic analyses of *Camellia* support reticulate evolution among major clades. *Molecular Phylogenetics and Evolution* 182: 107744. https://doi.org/10.1016/j.ympev.2023.107744

Zhang, Q., R. A. Folk, Z.-Q. Mo, H. Ye, Z.-Y. Zhang, H. Peng, J.-L. Zhao, S.-X. Yang, and X.-Q. Yu. 2023. Phylotranscriptomic analyses reveal deep gene tree discordance in *Camellia* (Theaceae). *Molecular Phylogenetics and Evolution* 188: 107912. https://doi.org/10.1016/j.ympev.2023.107912

Zhou, C., X. Mei, D. O. Rothenberg, Z. Yang, W. Zhang, S. Wan, H. Yang, and L. Zhang. 2020. Metabolome and transcriptome analysis reveals putative genes involved in anthocyanin accumulation and coloration in white and pink tea (*Camellia sinensis*) flower. *Molecules* 25: 190. https://doi.org/10.3390/molecules25010190

Zhou, X. W., Z. Q. Fan, Y. Chen, Y. L. Zhu, J. Y. Li, and H. F. Yin. 2013. Functional analyses of a flavonol synthase-like gene from *Camellia nitidissima* reveal its roles in flavonoid metabolism during floral pigmentation. *Journal of Biosciences* 38: 593–604. https://doi.org/10.1007/s12038-013-9339-2

# OPEN ITEMS FOR v0.2

- Resolve the complete AJB-format Literature Cited entries for all non-core ecological primary studies and the WFO Plant List snapshot.
- Verify final bibliographic pagination/article numbering for Fan et al. 2026 and all source-register underlying references used in Supplement.
- Convert repository file names/PR references into formal Methods/Data Availability citations or Supplementary table references.
- Add author names, affiliations, acknowledgments, author contributions, funding, and final repository archive DOI.
- Build the Supplementary Tables/Figures from the frozen analysis-disposition map.
