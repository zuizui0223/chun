# Camellia flower-colour evolution: general meta-synthesis

## Scope

This document broadens the project from yellow-camellia evolution to **flower-colour evolution across the genus**. The target is not a categorical red/white/yellow comparison. The target is to reconstruct how a conserved pigment network moves among alternative floral deployment states, how often those state transitions occurred, and whether ecological filtering by pollinators helps explain which states persist or recur.

The working levels are:

1. visible phenotype: white, pink, red/crimson, yellow, mixed/sectorial;
2. pigment deployment: anthocyanin, flavonol, carotenoid, proanthocyanidin/procyanidin and unresolved components;
3. regulatory architecture: structural-gene expression, MYB/bHLH/WD40/WRKY regulators, TE/SV and other cis effects;
4. phylogenetic history: gain, loss/suppression, retention, recruitment, reactivation and introgression;
5. ecological filtering: pollinator visual system, UV/reflectance, nectar, flowering season and local pollinator fauna.

## 1. Current genus-level evolutionary result

Fan et al. 2026 (`10.1111/pbi.70442`) provide the strongest current genus-wide nuclear framework: 237 accessions, 4.18 million nuclear SNPs and seven major clades. Their maximum-parsimony and maximum-likelihood ancestral-state reconstructions both infer **white as the most likely visible ancestral flower colour**.

Important qualifications:

- this is an ancestral *visible phenotype*, not an ancestral molecular state;
- early-diverging Clade 1 already contains white, yellow and red flowers;
- the paper explicitly notes multiple potential red-white transitions;
- later-diverging clades lack yellow in that sampling frame;
- the full 237-accession raw package is not yet locally reproduced in this repository.

Therefore the project treats `ancestral visible white` as a strong published prior/hypothesis, not a frozen local result.

## 2. Initial study-level directional meta-synthesis

The first evidence table is `data/camellia_flower_color_mechanism_meta_v0_1.csv`. It contains nine mechanistic studies spanning:

- genus-wide phylogenomics;
- between-species red/yellow/white comparisons;
- within-species cultivar gradients;
- within-genotype red/white or red/pink sectors;
- developmental pink-to-white fading;
- developmental yellow-pigment accumulation.

The table deliberately treats each paper as at most one directional vote per mechanistic question. This is **not yet a standardized effect-size meta-analysis** because expression pipelines, metabolite units, contrasts and experimental units are incompatible.

The deterministic summary in `data/camellia_flower_color_mechanism_meta_summary_v0_1.csv` gives the following initial pattern:

| Question | Interpretable studies | Directionally concordant |
|---|---:|---:|
| Anthocyanin abundance is higher in the more red/pink state | 8 | 8/8 |
| DFR/ANS or the downstream anthocyanin branch is more active in the more red state | 5 | 5/5 |
| A competing branch is more active in the less-red / white / yellow state | 6 | 6/6 |
| Regulatory/flux differences are implicated | 9 | 9/9 |
| Structural-gene loss is required to explain the contrast | 4 directly informative | 0/4 |

This is a directional synthesis, not proof of a universal mechanism. The included literature is enriched for studies designed around anthocyanin/flavonoid mechanisms and ornamental cultivars. Nevertheless, the repeated direction across different biological scales is notable.

## 3. The repeated red-pink-white mechanism

### 3.1 Camellia sinensis: white versus pink flowers

Zhou et al. 2020 (`PRJNA597123`, `PRJNA597289`) compared developmental series of white and pink tea flowers. Pink flowers accumulated anthocyanins absent from white flowers. `DFR`, `ANS` and `LAR` expression was higher in pink material, whereas `FLS` expression was higher in white flowers.

This is a direct example of **competition within the flavonoid network**: stronger FLS deployment is associated with the low-anthocyanin state, while stronger downstream anthocyanin deployment is associated with pink colour.

### 3.2 Camellia japonica: a white-to-crimson series

A five-cultivar transcriptome/metabolome series (`CRA003840`) spans white, pink, deep pink, red and crimson petals. Anthocyanin composition and abundance track colour intensity, with cyanidin derivatives contributing strongly to redder states.

This provides a continuous rather than binary phenotype and is valuable for testing whether expression scores scale monotonically with pigment intensity.

### 3.3 Camellia reticulata: red, pink and white cultivars

The `PRJCA012977` study reports a red > pink > white pattern for anthocyanin accumulation and for much of the anthocyanin-biosynthesis expression programme.

This is a second within-species/cultivar system in which colour intensity behaves as a quantitative change in pathway deployment rather than a simple pathway-present/pathway-absent character.

### 3.4 Within-genotype red-white sectors

The `GSE236364` comparison is especially important because red and white petal regions occur within a multicoloured C. reticulata cultivar. Red regions contain more cyanidin; white regions show lower `CHS` expression and higher `ANR`, with MYB co-expression candidates.

A spatial contrast inside one genotype is strong evidence that a red-white switch can arise without gene birth/death between the two colour states.

### 3.5 Within-genotype red-pink sectors

C. japonica `Joy Kendrick` (`PRJNA913600`) provides a second spatial contrast within one cultivar. Its red and pink sectors differ in anthocyanin-related transcriptional profiles.

Again, colour-state differences can be generated inside one genetic background.

### 3.6 Developmental pink-to-white fading

C. reticulata `Tongzimian` changes from pale pink to white during flower opening. Zhou et al. 2026 (`10.3389/fpls.2026.1831409`) identify lower `CrANS` expression at full bloom, reduced cyanidin and redirection toward procyanidins. CrANS overexpression in tobacco increases anthocyanin accumulation and deepens corolla colour.

This is a particularly strong conceptual model for the project because the same individual phenotype moves from coloured to white over developmental time through **expression and flux changes**, not pathway deletion.

## 4. Yellow and white are not equivalent low-anthocyanin states

The red-pink-white evidence cannot simply be extended by defining yellow as `anthocyanin absent`.

### Yellow pathway deployment

- C. nitidissima (`SRP112181`) combines flavonol glycosides and carotenoids in golden petals.
- FLS functional work demonstrates the ability to redirect shared dihydroflavonol substrates toward flavonols and away from anthocyanin.
- C. longruiensis functional work supports WRKY23-mediated activation of FLS.
- Genus-wide TE/SV work implicates regulatory changes near MYB genes in red-versus-yellow/white differentiation.

Therefore white and yellow may both have low anthocyanin while occupying **different biochemical basins**.

## 5. A better evolutionary state space

A single ordered trait such as `white < pink < red < yellow` is biologically wrong.

The project should estimate at least three latent pathway axes:

- `A`: anthocyanin deployment;
- `F`: flavonol deployment;
- `C`: carotenoid deployment.

Optionally add:

- `P`: proanthocyanidin/procyanidin diversion;
- `UV`: spectral/UV phenotype when measured.

Visible colour is then an observation generated by a hidden biochemical state rather than the state itself.

Examples:

- white can be `A-low, F-present, C-low` rather than all pathways absent;
- pink can be moderate `A`;
- red/crimson can be high `A` with differences in anthocyanin composition and acylation;
- yellow can be high `F`, high `C`, or both;
- mixed flowers can contain spatial mosaics of these deployment states.

## 6. Main evolutionary hypotheses across all flower colours

### H0 — lineage-history model

Flower colour is mostly a phylogenetic consequence of a small number of early state changes. Ecology adds little after clade membership and geography are accounted for.

### H1 — ancestral accessible-white model

The most likely white-flowered ancestor retained intact pigment pathways in a weakly expressed or differently allocated state. Red/pink and yellow states were recruited by regulatory changes rather than reconstruction of deleted pathways.

Predictions:

- core structural genes are broadly conserved in white lineages;
- extant white flowers express substantial portions of the flavonoid network;
- colour transitions are enriched for expression, cis-regulatory, TF and TE/SV changes;
- within-genotype switches recapitulate between-species transitions at the same pathway nodes.

### H2 — repeated anthocyanin recruitment

Red/pink states arose multiple times from white or pale ancestors through repeated activation of anthocyanin modules.

Predictions:

- stochastic maps support multiple white-to-red/pink events;
- independent red lineages need not share one causal allele;
- repeated targets such as MYB/DFR/ANS appear, but exact variants differ.

### H3 — anthocyanin suppression and true reactivation

Some red/pink lineages underwent red/pink -> white suppression -> later red/pink reactivation.

Required evidence for a branch-specific `reactivation` claim:

1. topology and ancestral-state uncertainty support active -> inactive -> active history;
2. the intervening white lineage retains the relevant pathway;
3. descendant colour is produced through reuse of retained machinery rather than independent reconstruction.

### H4 — flux-allocation model

Colour evolution is dominated by shifting substrate allocation among competing branches, especially `FLS` versus `DFR/ANS` and anthocyanin versus procyanidin paths.

This hypothesis is directly suggested by the repeated white/pink and fading studies.

### H5 — introgressive colour recruitment

Colour-associated regulatory alleles can move between species in a reticulate genus. Phenotypic gain counts on a strictly bifurcating species tree may therefore overestimate the number of causal-allele origins.

Predictions:

- colour-locus trees conflict systematically with the species tree;
- colour-associated haplotypes are unusually similar across otherwise divergent taxa;
- local introgression signals concentrate near regulatory loci.

### H6 — pollinator-filtered deployment

Pollinators do not select a simple named hue. They filter multivariate signals generated by pigment chemistry and floral context.

The red C. japonica / red C. rusticana comparison already falsifies a simplistic `red = bird` rule: both have red petals, but the former is bird-associated and the latter insect-associated; UV reflectance and flower-level optical signals differ strongly.

For yellow camellias, bird contribution is substantial in several southern Chinese systems, but bees also participate and season changes the balance. Therefore the appropriate predictor set is:

`pigment deployment -> reflectance/UV -> flower geometry + nectar + season -> effective pollinator`.

### H7 — repeated accessible-state / evolutionary-neighbourhood model

The strongest general hypothesis emerging from the combined evidence is that flower colours occupy an **evolutionary neighbourhood of accessible regulatory states** rather than representing irreversible pathway inventions and losses.

White may be especially important because it can be produced by multiple regulatory routes while retaining biochemical capacity for later coloured states.

This yields a testable question:

> Are white states disproportionately adjacent to multiple future colour states in Camellia evolutionary history?

The Antirrhineae literature provides an external precedent for constrained transitions between anthocyanin and yellow states through white intermediates, but Camellia must be tested independently.

## 7. Initial quantitative result and its limits

The v0.1 directional synthesis has a striking pattern: every currently interpretable study reports higher anthocyanin in the more red/pink state (8/8), and all currently interpretable downstream-branch studies report greater DFR/ANS-side deployment in the redder state (5/5). All six studies informative about a competing branch report stronger alternative-branch deployment in the less-red/white/yellow state.

This should **not** be reported as a conventional meta-analytic effect size because:

- study endpoints are heterogeneous;
- many studies use cultivars rather than wild species;
- some comparisons are between species, some within species and some within one flower;
- expression units and pipelines differ;
- publication bias toward successful pigment mechanisms is likely.

The value of the v0.1 synthesis is to define the **recurrent directional hypothesis** that the raw public data can now test under a unified pipeline.

## 8. Public-data meta-transcriptomics: next executable layer

Priority datasets now include:

1. `PRJNA597123` + `PRJNA597289` — C. sinensis white/pink developmental flowers;
2. `CRA003840` — C. japonica white-to-crimson cultivar series;
3. `PRJCA012977` — C. reticulata red/pink/white series;
4. `GSE236364` — C. reticulata red/white sector and cultivar contrasts;
5. `PRJNA913600` — C. japonica red/pink sectors in Joy Kendrick;
6. `PRJNA1136134` — red/yellow/white comparison among three Camellia species;
7. `SRP112181` — C. nitidissima yellow developmental series;
8. broad published 2026 genus phylogenomics — evolutionary scaffold, pending full public-data admission.

### Common reanalysis target

For every dataset with raw reads and adequate metadata:

- quantify orthologous `CHS`, `CHI`, `F3H`, `F3'H`, `F3'5'H`, `FLS`, `DFR`, `ANS/LDOX`, `UFGT`, `ANR`, `LAR`;
- quantify selected MYB/bHLH/WD40/WRKY regulators where orthology is defensible;
- derive module scores rather than compare platform-specific raw expression values;
- compute within-study standardized contrasts;
- pool only comparable module-level effect sizes using a multilevel meta-analysis with study and taxon as random effects;
- keep developmental, within-genotype, within-species and between-species contrasts as separate moderators.

This is the first route to a true quantitative meta-analysis.

## 9. Phylogenetic meta-analysis: transition counts

The second quantitative layer should estimate colour-history uncertainty.

### Visible-state analysis

Start with white / red-pink / yellow / mixed-unknown and compare:

- ER;
- SYM;
- ARD;
- models that constrain or penalize direct red-yellow transitions;
- hidden-state models if required.

### Mechanistic-state analysis

After chemistry is available, infer states from pathway deployment rather than hue alone.

### Output

Do not report one integer count of gains. Report posterior or bootstrap distributions such as:

- `P(N_red_gains = k)`;
- `P(N_yellow_gains = k)`;
- `P(N_white_gains = k)`;
- probability that a transition passed through white;
- probability that a candidate branch represents retention, recruitment or reactivation.

Repeat over nuclear-tree uncertainty and reticulation-sensitive alternatives.

## 10. Pollination meta-analysis: what is and is not possible now

Current Camellia pollination studies are too sparse and heterogeneous for a reliable colour-category pooled effect size.

What can be tested first:

- bird versus insect contribution as a response;
- petal spectral/UV variables rather than human hue alone;
- nectar volume and sugar composition;
- winter versus warm-season flowering;
- nuclear phylogenetic placement.

The key null is that pollinator identity adds no explanatory power after phylogeny, geography and flowering season are controlled.

## 11. Main unresolved gaps

### Gap 1 — molecular identity of the ancestral white state

White is the best current visible ancestral reconstruction, but nobody has reconstructed the molecular deployment state of that ancestor.

### Gap 2 — how many independent red/pink gains occurred

The genus-wide paper notes repeated red-white transitions, but event-count uncertainty under alternative transition models has not been resolved.

### Gap 3 — how many independent yellow mechanisms occurred

Visible-yellow trajectories are phylogenetically heterogeneous, but identical colour does not imply identical flavonol/carotenoid architecture.

### Gap 4 — whether white is a privileged evolutionary intermediate

The external Antirrhineae result suggests anthocyanin-yellow transitions may pass through white. Whether Camellia shows a comparable constraint is unknown.

### Gap 5 — whether recurrent pathway nodes are true evolutionary hotspots

`FLS`, `DFR`, `ANS`, MYBs and related regulators recur in molecular studies, but cross-study raw-data reanalysis is needed to distinguish biological recurrence from candidate-gene publication bias.

### Gap 6 — pollinator causality

Colour and pollinator associations exist, but visible hue alone is insufficient and branch-level temporal ordering of pollinator shifts versus colour shifts is unresolved.

### Gap 7 — wild versus horticultural evolution

Much mechanistic evidence comes from cultivars. These systems are excellent for identifying accessible regulatory mechanisms but cannot by themselves establish the frequency of those mechanisms in natural evolution.

## 12. Central problem statement

The project should now be framed as:

> **How has Camellia repeatedly moved among white, anthocyanin-rich and yellow floral phenotypes, and are those transitions best explained by irreversible pathway gain/loss, repeated regulatory access to conserved pigment machinery, introgression, or ecological filtering by pollinators?**

The strongest current mechanistic prediction is:

> **flower-colour evolution in Camellia is predominantly a problem of regulatory accessibility and pathway allocation, with structural pigment machinery often retained across visually different states.**

That prediction is now testable with multiple independent public transcriptomic datasets and a nuclear phylogenomic scaffold.
