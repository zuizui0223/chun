# Layered evolutionary memory in flower colour: temporal persistence, hidden variation and molecular repeatability

**Status:** Integrated single-article candidate v0.1 — exploration, not a submission-ready replacement. No frozen result, prior manuscript or preregistered gate is overwritten.

**Alternative question-led title:** *What does flower-colour evolution repeat, retain and forget?*

## Abstract — integration candidate

Repeated flower-colour states can arise through different molecular pathways, while related species may retain similar colours over evolutionary divergence. Whether this reflects one invariant level of evolutionary repeatability remains unclear. We integrated standardized, source-bounded evidence for temporal retention, nested phenotypic organization and molecular-route variation without treating unlike comparisons as interchangeable. Across 32 eligible angiosperm radiations, exact visible-colour excess similarity declined with relative phylogenetic divergence in 23, with a median retention slope of −0.1897. A separate 28-radiation common-resolution comparison revealed no universally superior coarse, intermediate or fine representation, and an independent preregistered *Iris* intermediate-optimum prediction failed. Yet, within broad colour classes, 18 of 21 eligible radiations retained positive permutation-centered fine-state phylogenetic organization (median +0.0270 AUC). This hierarchical pattern passed prospective validation in *Rhododendron* sect. *Schistanthe* (+0.0642 AUC, P = 0.0033), but the prospective Gesnerioideae biochemical generalization failed (−0.00779 AUC, P = 0.5005). A separate seven-system molecular benchmark, including *Camellia*, revealed recurrence from exact regulatory genes to pathway modules and heterogeneous causal nodes, rather than an invariant complete programme. Standardized *Camellia* transcripts showed no matching complete four-module signatures across distinct compared dependence clusters, but three of four directional modules agreed between two yellow-development systems. A separate retrospective analysis now directly joined pigment composition, 21-gene expression and one dated tree across 47 Petunieae taxa. Among 183 species pairs with identical six-anthocyanidin presence codes, gene-expression divergence increased with phylogenetic distance (Spearman rho +0.6074; 9,999 within-code permutations, P = 0.0001). A nine-pigment concentration comparison did not meet its exploratory one-sided threshold (rho +0.2199; P = 0.0554). Thus flower-colour history can be recovered at successively finer states within one phylogeny, while the molecular-route atlas remains heterogeneous. These data do **not** establish that molecular-route variation causes the distinct 32-radiation temporal memory-decay patterns. Independent matched-radiation testing remains necessary.

## Introduction

When similar traits arise repeatedly, two distinct historical questions are often compressed into one. The first is **generation**: does a recurrent visible outcome require the same genetic or biochemical implementation? The second is **retention**: after a lineage acquires a phenotype, which aspects of that phenotype remain historically organized as descendants diverge?

There is strong prior art on each question. Colour can converge through alternative pigment pathways, and even the *choice* of pathway has phylogenetic signal in Solanaceae (Ng & Smith 2016, DOI 10.1111/nph.13576). Repeated pigment losses can re-use late-pathway transcriptional modules (Larter et al. 2018, DOI 10.1093/molbev/msy117). General hierarchical convergence and developmental history are established concepts (Lau et al. 2021, DOI 10.1111/brv.12672; Allard & Kumar 2026, DOI 10.1038/s41576-026-00933-7). More generally, state aggregation can change what a comparative analysis detects. Simply juxtaposing these observations would not be a new biological discovery.

The more testable biological question is whether the history carried by a **coarse displayed phenotype**, a **finer biochemical or colour state**, and a **particular molecular implementation** behaves as one common memory or as separable components. This question makes a prediction about *where* information survives, not merely whether phylogenetic signal exists.

Here we assemble the already frozen CHUN research in three independent evidence layers, with explicit boundaries between them: (1) a cross-radiation relative-time retention profile; (2) conditional fine-state retention within broader colour states, including independent prospective validations and failures; and (3) comparative molecular recurrence, treating *Camellia* as one case among seven rather than as the anchor of a genus-only paper. The present synthesis tests the architecture of the separate layers; it does not invent an unobserved clade-level genotype-to-memory mapping.

## Methods — evidence tiers and estimands

### Temporal retention of visible flower colour

The frozen Flower-clades-51 source universe contains 51 pre-specified source clades and one source phylogeny per clade. Thirty-two clades meet the existing fine-visible-state persistence eligibility gate. Within each clade, we relate unordered-tip same-colour status to relative phylogenetic separation. Excess same-colour retention is measured relative to the observed within-clade colour-frequency baseline. A negative depth-profile slope denotes reduced excess same-colour similarity among more separated species. The axis is **relative phylogenetic depth, not absolute time in millions of years**. Pairwise observations are not independent cross-clade replicates; radiation is the unit.

A different but overlapping 28-clade common-frame analysis applies the original frozen coarse/intermediate/fine state hierarchy and joint-permutation same-state discrimination AUC. The temporal slope and resolution AUC reuse source pair information and are **not independent replications**. The preregistered *Iris* test is an independent prediction failure, not a retrospective positive fine-state result.

### Conditional, hidden fine-state history

For 21 clades with actual fine-to-coarse compression opportunity, we restrict species pairs to those already sharing the same coarse colour class, then measure whether phylogenetic proximity distinguishes matching versus different fine states. Fine labels are permuted **within coarse groups** and the observed conditional ROC AUC is centered on its own permutation-null mean. This centered effect is not equivalent to global fine-minus-coarse AUC, and its null need not equal 0.5.

The 21-clade analysis was exploratory and pilot-exposed. The independent *Rhododendron* sect. *Schistanthe* prospectively validates the visible-colour conditional estimand. Petunieae is retrospective biochemical concordance. Gesnerioideae is a separate prospective biochemical **FAIL** and remains a negative/limiting result. These are different evidence tiers.

### Molecular repeatability and the *Camellia* case

The seven-system pre-existing mechanistic atlas comprises *Ipomoea*, Iochrominae, *Aquilegia*, *Epimedium*, *Petunia* (long-tube lineage), Cape *Erica*, and *Camellia*. Observations range from independent historical origins to terminal endpoint taxa, developmental series, and dependence clusters. Their ratios are **not pooled** into one molecular repeatability percentage.

*Camellia* compares a literature-selected, partially observed A/F/C/P pigment-module signature with a standardized annotation-driven, outcome-independent transcript-module measurement of the **same admitted public molecular systems**. The exact-signature index is a Simpson concentration with group-count-dependent minimum (1/n); it is not the percentage of distinct species pairs that underwent the same evolutionary origin. Candidate-free measurements yield no identical complete four-axis signatures between distinct matched dependence clusters in either the three-group anthocyanin or two-group yellow class; yellow systems share A down, C up and P down signs, while F differs. Statistical uncertainty on the individual module slopes remains relevant. These contrasts are not mapped to independently reconstructed macroevolutionary branch events.

### A directly matched Petunieae biochemical-to-expression history test

The newly frozen source-level design (GitHub commit `91b10be`) uses Wheeler et al. (2023) OSF node `zg9cu`, retaining the previously eligible 47 species and published dated phylogeny, with exact source SHA-256 checks. Six-bit presence/absence across pelargonidin, cyanidin, peonidin, delphinidin, petunidin and malvidin defines an *exact fine pigment-presence class*. Retaining only unordered pairs within these classes yields 183 species pairs. The source supplies 21 flavonoid structural/regulatory gene-expression measurements for the same tips.

We predeclared the analysis rule for this **new** statistic before calculating it, although the publicly available source had been exposed in earlier analyses. Each gene's TPM10K expression was transformed by log1p and z-scored over the unchanged 47-species frame. Within exactly identical pigment-presence classes, we computed Euclidean RMS distance across all 21 gene-expression components and correlated it with tree patristic distance using Spearman rho. The conditional null shuffles complete 21-gene vectors **within each identical fine pigment class** 9,999 times, preserving class membership and inter-gene covariance. The taxon, not the species pair, is the exchangeability unit; pairwise P values are never treated as independent observations.

A secondary, already specified analysis applies an analogous within-code procedure to log-transformed measured concentrations of nine anthocyanidin/flavonol compounds. Its P value is descriptive; a comparison of the raw expression and pigment correlation coefficients does not test their difference. A leave-one-tip-out primary sensitivity is descriptive. The analysis remains retrospective in one radiation.

### Cross-tier integration gate

We audit whether identical biological radiations are represented in both the main 32-clade temporal table and the seven-system mechanistic benchmark. There are **zero exact analytic-unit name matches**; *Camellia* is absent from the standardized temporal cohort. Consequently we do not calculate a cross-radiation mechanism–memory slope, mediation coefficient, joint random effect or causal evolutionary model. The new **within-Petunieae** conditional Spearman test is a distinct same-tree association of pathway expression with phylogenetic distance after fixing exact pigment-presence identity; it is not a pooled linkage to the original 32-radiation slope outcomes. The remaining integration is triangulation across evidence types rather than identification of one common parameter.

## Results

### 1. Flower-colour history is concentrated at shallower relative evolutionary divergence, but decay is heterogeneous

Among 32 fine-colour eligible clades, 23 have negative relative-depth excess-retention slopes (median −0.1897). This places the memory question explicitly on a within-clade divergence coordinate; it does not say that every lineage or pigmentation axis decays at the same rate. Re-expression of same-state pair information over divergence does not add a statistically independent dataset to the original phylogenetic-signal analysis.

### 2. No representation has a universal privilege

Twenty-eight clades complete the standard three-resolution profile: 3 unique coarse winners, 0 intermediate winners, 3 fine winners, 6 significant ties and 16 without detectable global signal. The frozen independent *Iris* intermediate-resolution prediction fails on its primary 169-tip frame (AUCs coarse 0.462, intermediate 0.454, fine 0.487); no level achieves positive same-state AUC. These outcomes reject the proposed universal intermediate optimum; they do not establish universal fine-level superiority or a universal no-signal law.

### 3. Broader states repeatedly conceal finer phylogenetic history

Of 21 clades with true nested-state opportunity, 18 have positive conditional fine-state memory, with median permutation-centered effect +0.0270 AUC (clade-level Wilcoxon P = 3.34 × 10⁻⁵). Five of six globally coarse-tilted clades nonetheless have positive within-coarse effects. This is the most informative **positive cross-radiation result**: a globally favoured coarse code need not eliminate finer lineage organization.

The independent outcome-blind *Schistanthe* validation retains 129 tips and confirms a positive conditional fine-state effect (+0.06416 AUC; P = 0.0033). Petunieae offers one retrospective biochemical concordance (+0.18794 AUC; P = 0.0001). The prospective Gesnerioideae biochemical attempt instead fails (−0.00779 AUC; P = 0.5005), prohibiting a universal cross-representation claim. A larger compression opportunity by itself also fails to predict stronger hidden memory (rho −0.2571; permutation P 0.26023); this is a failed specific moderator, not proof that all coding artifacts or all developmental causes have been ruled out.

### 4. Molecular routes repeat at different levels — *Camellia* is one example

The comparative molecular examples span repeated exact F3'H regulation in *Ipomoea*, recurrent late pigment modules in Iochrominae and *Aquilegia*, shared-core but heterogeneous endpoint implementation in *Epimedium*, alternative R2R3-MYB restoration/recruitment in *Petunia*, and highly heterogeneous nodes in Cape *Erica*. These categories are source-faithful qualitative comparisons; they do not establish a single event-level cross-taxon recurrence rate.

*Camellia* contributes a same-system **observation-regime control** rather than a privileged model for the entire paper. After frozen A/F/C/P transcript remeasurement, none of the three anthocyanin dependence clusters matches another in its complete resolved signature under any admitted completion; nor do the two yellow-development clusters match. Their Simpson exact-signature values of 1/3 and 1/2 are both **mathematical floors**, not different levels of complete-package repetition. In yellow development, the two trajectories share estimated A/C/P directions and differ in F (three of four signed axes); this does not imply three significantly replicated pathways, direct functional flux or repeated ancestral events.

### 5. Identical pigment identity can conceal deeper gene-expression history in Petunieae

The previous Petunieae biochemical conditional AUC analysis established that the six-bit anthocyanidin-presence state carries additional lineage structure inside the coarse anthocyanidin-present/absent grouping (47 taxa; centered conditional AUC +0.1879, P = 0.0001). The new source-matched test asks whether the 21-gene pathway-expression vector retains *still finer* phylogenetic organization **after exact six-bit presence identity is fixed**, on the same 47-species tree.

Among 183 within-exact-code unordered pairs, gene-expression distance covaried positively with phylogenetic separation (Spearman rho **+0.60744**). The within-code whole-vector 9,999-permutation null mean was +0.16540 (central 95% interval −0.00820 to +0.36428); the observed value was more positive than all shuffled values (**one-sided P = 0.0001**). All 47 leave-one-tip-out correlations remained positive (range +0.5854 to +0.6442). These values indicate non-random expression structure within exact *presence/absence* pigment types, not directly observed causal molecular mutation reuse.

In the prespecified secondary analysis, distances based on concentrations of nine pigment compounds gave rho **+0.21986** and a one-sided permutation P = **0.0554** on the same taxon-pair frame. This comparison does not establish that gene-expression memory decays more slowly than pigment concentration; the two raw effect sizes and their inferential tests are not a formal matched difference.

### 6. Cross-radiation molecular explanation remains untested despite the Petunieae bridge

The main standardized 32-radiation temporal cohort and curated seven-case mechanistic benchmark still share no exact analytic unit. The new Petunieae result gives a **single-radiation biological bridge between fine biochemical states and pathway-wide expression**; it does not identify which developmental, ecological or selection processes explain variation in relative-time flower-colour memory among the 32 other radiations. An independent common-tree phenotype/pigment/expression system is required for cross-radiation validation. This is not evidence that molecular-route variation causes temporal memory decay across the original 32 radiations.

## Discussion

### Where the genuine empirical advance lies

The informative result is not merely that colour can recur by different mechanisms. Nor is it simply that trait coding changes phylogenetic signal. The strongest current empirical advance is that **within a standardized cross-radiation frame, fine visible identity repeatedly carries additional history after coarse class membership is fixed** and that this statement survived an independent visible-colour prospective test but failed one distinct biochemical transport test. Molecular evidence then locates the kinds of mechanisms to which a future cross-level explanation must answer: exact targets, shared modules, distinct regulators and divergent complete implementations.

The new Petunieae comparison links **two nested levels within the same 47-species tree**: fine anthocyanidin presence identity within a coarse biochemical class and further gene-expression structure within that fine identity. This strengthens the biological example behind hierarchical memory beyond a descriptive alignment of unrelated systems. It is nonetheless one retrospective source, and shared species phylogeny, source gene-expression normalization and possible phylogenetically patterned technical effects remain potential alternatives. The prospective visible-colour Schistanthe PASS and biochemical Gesnerioideae FAIL remain different observation tiers; neither independently replicates this gene-expression test. The present evidence supports **hierarchical, representation-conditional historical organization**, not one universal molecular replay mechanism, a universal temporal scale, or a demonstrated ecological cause of memory strength.

### A nontrivial mechanistic hypothesis for the next direct bridge

*Hierarchical-memory crossing hypothesis.* Within one radiation and a common dated/branch-length phylogeny, the relationship between evolutionary divergence and state sharing depends on which layer is conditioned upon:

- a broad flower-colour class may remain stable even when fine pigment identity changes;
- conditional fine pigment identity may retain phylogenetic structure within that class;
- molecular implementations may show still another trajectory of retention or turnover, depending on developmental pathway architecture and transition class.

This hypothesis predicts that **the relative ordering and potential crossing of distinct layer-specific memory curves** is measurable, not that there is always one fixed order. Under a simple common-memory alternative, after preserving state-frequency effects, the distinct layers' standardized distance–sharing profiles should be explainable by one common decay coordinate. Under layer-specific retention, that one-coordinate model will fail on independent held-out biological radiations. This is a *future falsifiable comparison*, not a result already obtained.

Petunieae now provides the first completed same-tree retrospective expression-versus-pigment-class comparison. The next source should be **independent**: Iochrominae (28 published taxa with comparative pigment chemistry and expression) remains a candidate **only after its frozen source-availability and provenance problem is resolved**. The *Camellia* developmental/petal contrasts must not be relabelled as tip-specific ancestral mechanisms to manufacture such a paired dataset.

### What would make the integrated manuscript genuinely stronger than two stand-alone papers?

One common biological radiation must carry a **validly matched, source-traceable phylogenetic** comparison of at least phenotype and a finer biochemical/molecular representation, followed by independent cross-radiation validation or a clearly demonstrated inability to generalize. The test must be defined before opening *new decisive* outcomes; retrospective data are explicitly exploratory. A new integrated analysis must test an actual competing prediction about representation-specific retention/turnover, not merely recalculate two existing signals and call them connected.

Without that bridge, the combined manuscript would be an evidence-tier synthesis combining separate studies, potentially less decisive than the already validated Camellia AJB study and frozen cross-radiation EL candidate.

### Novelty and publication limits

Ng & Smith (2016) already demonstrated both pigment-route convergence and phylogenetic signal of route use within red-flowered Solanaceae; Larter et al. (2018) identified modular molecular convergence. Multi-level convergence (Lau et al. 2021) and general phenotype–mechanism integration (including a 2026 Annual Review, DOI 10.1146/annurev-ecolsys-102924-043757) are established prior art. We do not claim conceptual priority for these components or for the general distinction between developmental and evolutionary history.

No current ecological/environmental variable is demonstrated to causally connect the temporal decay and molecular architectures, and no cross-species trait-agnostic law is established. A single merged paper should therefore lead with the independently supported nested-memory result, not an untested story that ecological filtering makes molecular pathways change at a particular rate.

## Proposed single-paper figure architecture

1. **Figure 1 — The inferential question.** Distinguish generation, nested historical retention and molecular implementation using non-equivalent observation units; highlight the no-joint-link boundary explicitly.
2. **Figure 2 — Relative-time retention atlas.** Thirty-two-clade slope distribution and depth profiles; clade is the inferential unit. Position the 28-clade resolution profile as a paired analytical description, not independent replication.
3. **Figure 3 — Hidden memory and its limits.** Twenty-one-clade conditional effects, prospective *Schistanthe* PASS and biochemical Gesnerioideae FAIL. Present Petunieae separately as retrospective biochemical evidence.
4. **Figure 4 — Molecular hierarchy with examples.** A seven-case qualitative molecular-resolution ladder. *Camellia* occupies one panel with zero exact whole-signature matched pairs in each transition class but yellow A/C/P signed reuse; include status of true historical event identity.
5. **Figure 5 — A matched Petunieae nested-history result and its independent-validation boundary.** Show the conditional fine-pigment AUC and within-exact-pigment-code expression-memory Spearman test separately (not on a misleading common y-axis), with source-verified 47-tip / 183-pair scope and prespecified nulls. Illustrate the still-untested cross-radiation phenotype–pigment–regulatory-history coupling as an explicit next prediction.

Supplementary material retains the full Camellia candidate-free uncertainty, literature ascertainment analysis, strict/dominant macro sensitivity, and the original 51-clade methods. Nothing is silently dropped.

## Submission and authorship governance

This file is a **proposal**, not a new submission decision. Preserve the two independent scientific freezes and their journal-specific assets. Any decision to submit one combined article instead of two requires agreement on authorship, data rights, journal strategy and re-evaluation of the single-paper claim relative to the strongest existing prior art.

The immediate next scientific action is **independent same-tree validation** of the fixed Petunieae nested-history question, not retrospective searching for significance in other gene subsets or refitting the same 21 visible-clade moderators.

## Key sources

- CHUN: `data/integrated_temporal_mechanisms_evidence_gate_v0_1.json`; `data/flowerclades51_fine_time_persistence_clades_v0_1.csv`; `data/flowerclades51_hidden_fine_memory_clades_v0_1.csv`; `data/cross_clade_mechanistic_recurrence_levels_v0_1.csv`; `data/paper1_fig2_candidate_free_signature_v0_2.csv`; `data/petunieae_nested_regulatory_memory_preregistered_design_v0_1.json`; `results/petunieae_nested_regulatory_memory_v0_1/result_v0_1.json`.
- Ng & Smith 2016. DOI 10.1111/nph.13576.
- Smith & Goldberg 2015. DOI 10.3732/ajb.1500163.
- Larter et al. 2018. DOI 10.1093/molbev/msy117.
- Lau et al. 2021. DOI 10.1111/brv.12672.
- Allard & Kumar 2026. DOI 10.1038/s41576-026-00933-7.
- *Mechanisms of Phenotypic Evolution from Molecules to Organisms* (2026). DOI 10.1146/annurev-ecolsys-102924-043757.
