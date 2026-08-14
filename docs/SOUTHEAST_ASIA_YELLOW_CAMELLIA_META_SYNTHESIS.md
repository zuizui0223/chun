# Southeast Asian yellow *Camellia*: meta-synthesis, gaps, and testable hypotheses

## Executive conclusion

The current literature does **not** support a simple story in which yellow flowers arose once in Southeast Asia and then spread geographically. Four observations have to be explained simultaneously:

1. the broadest current nuclear genomic analysis reconstructs the *Camellia* MRCA as most likely **white-flowered**;
2. early-diverging lineages are concentrated in southwestern China and northern Vietnam, and yellow flowers are concentrated in this putative ancestral region;
3. nuclear genomic studies identify a major China–Vietnam yellow lineage **plus phylogenetically distinct yellow trajectories**;
4. several southern Chinese yellow *Camellia* species have experimentally documented bird contribution to pollination, especially during winter flowering, but flower colour alone does not predict pollinator identity across the genus.

The central unresolved problem is therefore not simply biogeographic:

> **Why are yellow-flowered *Camellia* concentrated around southwestern China–northern Vietnam: relict retention of an old pigment deployment state, repeated regulatory recruitment from an ancestrally accessible white state, pollinator-mediated ecological sorting, or some combination of these processes?**

## 1. What the current phylogenomic evidence actually establishes

### 1.1 White is the current best-supported visible ancestral state

Fan et al. (Plant Biotechnology Journal, 2026; DOI `10.1111/pbi.70442`) analysed 237 accessions using 4,182,517 nuclear SNPs. Seven major clades were recovered. Their ancestral-state reconstruction coded visible flower colour as white, yellow, or red/pink and used both maximum parsimony and maximum likelihood. Both methods inferred the *Camellia* MRCA as most likely white-flowered.

This is a published reference result, not yet a locally reproduced result in this repository. It should therefore be stated as:

> `published nuclear ASR: white is the most likely ancestral visible phenotype`

and not as an established ancestral molecular state.

### 1.2 The putative ancestral region contains all three visible colour classes

In the same 237-accession study, basal/early-diverging Clade 1 is concentrated in southwestern China and northern Vietnam and contains white, yellow, and red flowers. Clade 2 is dominated by Sect. *Chrysantha* and also diverges early. Yellow species are much more geographically restricted than red and white species.

This pattern is compatible with several mutually exclusive histories:

- early gain of yellow followed by regional retention and repeated loss;
- multiple yellow gains/recruitments within the ancestral region;
- introgression of pigment-regulatory alleles among regional lineages;
- a combination of retention, loss, and repeated regulatory recruitment.

Geographic concentration alone cannot distinguish them.

### 1.3 The ~10 ka China–Vietnam split is not the age of yellow flower origin

Fan et al. (Industrial Crops and Products, 2026; DOI `10.1016/j.indcrop.2026.123200`) analysed 79 accessions, including 26 yellow accessions from China and 18 from Vietnam. Their demographic analysis estimated divergence between the sampled Chinese and Vietnamese yellow populations at approximately 10,000 years ago.

That date estimates **population divergence inside a major yellow lineage**. It must not be interpreted as the first evolutionary acquisition of yellow flowers.

Published nuclear phylogenomic studies place major *Camellia* clade radiation around 23–19 Ma and a later species burst around 10–5 Ma. Previous estimates cited for Sect. *Chrysantha* place its initial divergence roughly 17–20 Ma, although individual-species dates are method-sensitive. Thus the molecular machinery associated with yellow lineages is potentially orders of magnitude older than the late-Pleistocene China–Vietnam population split.

### 1.4 How many times did yellow evolve? Current answer: unresolved

The 79-accession nuclear study recovers a major yellow Clade 4, but *C. cucphuongensis* and *C. flava*, traditionally treated as yellow camellias, cluster in a distinct trajectory with *C. krempfii* and *C. vidalii* rather than with the major yellow lineage.

This establishes **at least two phylogenetically distinct visible-yellow trajectories in that sampling frame**. It does **not** establish two independent yellow gains. The alternatives are:

- two or more independent gains;
- one older yellow state followed by losses in intervening lineages;
- introgression/hybridization of colour-regulatory alleles;
- taxonomic or phenotype-state heterogeneity.

The 2025 ITS/chloroplast species-concept study provides an additional warning. Golden-flowered taxa are scattered across many ITS lineages and three major plastid clades, but the same study documents extensive hybridization and chloroplast capture. Consequently, plastid-clade counts cannot be used as counts of yellow origins.

**Required analysis:** estimate an event-count distribution from nuclear trees using stochastic character mapping / Bayesian discrete-state models across tree uncertainty. The target is not a single painted tree but `P(number_of_yellow_gains = k | trees, model, state uncertainty)`.

## 2. Did yellow require a new pathway, or reuse an ancestral pathway?

### 2.1 Current evidence argues against wholesale de novo invention

The 237-accession genomic study screened core flavonoid structural genes and reported no obvious losses among key structural genes across contrasting colour groups. Most candidate colour-associated differences were regulatory rather than coding losses.

Examples include:

- a red-lineage-associated TIR insertion upstream of `MYB114`, associated with higher petal expression and anthocyanin accumulation;
- a Sect. *Chrysantha*-associated insertion in `MYB7`, associated with altered expression relevant to flavonol regulation;
- a Sect. *Chrysantha*-associated TIR insertion near `MYB60`, experimentally shown to increase expression, with MYB60 suppressing anthocyanin biosynthesis.

These results favour a model in which a broadly conserved flavonoid network is repeatedly rewired or reweighted.

### 2.2 White is not equivalent to pathway absence

A directly useful public comparison is the petal transcriptome/metabolome study of:

- *C. amplexicaulis* — red;
- *C. petelotii* — yellow;
- *C. oleifera* — white.

The raw petal RNA-seq is public under `PRJNA1136134` (9 experiments; 3 biological replicates per species). The study detects extensive flavonoid metabolism in all three species. The white species is therefore not adequately represented as `flavonoid pathway absent`.

This does **not** prove that the *Camellia* ancestor carried exactly the same latent programme. It does make an irreversible-loss model less parsimonious as a default assumption and makes regulatory accessibility testable with extant white lineages.

### 2.3 Yellow is not one biochemical state

In *C. nitidissima*, public flower developmental RNA-seq (`SRP112181`; 15 libraries, five stages) plus pigment measurements show that golden-yellow colour combines:

- flavonol glycosides; and
- carotenoids.

FLS/CHS/F3H-related expression supports flavonol production, while PSY and other carotenoid-pathway genes increase with pigment accumulation. Therefore `visible yellow` must not be encoded as a single `FLS-on` state.

Within Sect. *Chrysantha*, a 2024 transcriptome/metabolome comparison of golden yellow *C. chuongtsoensis*, light-yellow *C. achrysantha*, and milk-white *C. parvipetala* also identifies strong quantitative shifts in flavonoids and candidate regulation by `CHI`, `FLS`, `DFR`, `CYP75B1`, and transcription factors.

The evolutionary unit to reconstruct should therefore be a **multidimensional pigment deployment state**, not just visible hue.

## 3. Is the Southeast Asian yellow concentration compatible with pollinator selection?

### 3.1 There is real evidence for bird contribution in yellow camellias

The strongest direct studies currently recovered are:

#### *Camellia petelotii* — golden/yellow

Sun et al. (American Journal of Botany, 2017; DOI `10.3732/ajb.1600428`) studied wild plants in southern Guangxi. Aethopyga siparaja sunbirds and honeybees were frequent visitors. Bird exclusion reduced fruit and seed set by 64%. Bagged flowers produced approximately 157 µL nectar at 19% sugar, with sucrose comprising about 87% of sugars. Bee visits declined in cloudy/rainy weather, while sunbirds made effective stigma contact.

This provides direct experimental evidence that bird pollination makes a major reproductive contribution in at least one yellow lineage.

#### *Camellia pubipetala* — Sect. *Chrysantha*, yellow-flower group

Chai et al. (Plant Species Biology, 2019; DOI `10.1111/1442-1984.12247`) found obligate outcrossing and identified the fork-tailed sunbird *Aethopyga christinae* as the primary pollinator in Guangxi karst populations. *Apis cerana* was an occasional pollinator. Open fruit set was 6.7% versus 23.3% after supplementary pollination, indicating strong pollen limitation.

#### *Camellia perpetua* — golden-camellia lineage

A 2025 *Flora* study found birds and bees visiting in both summer and winter, but bird visitation, fruit set, and seed set were higher in winter. Winter flowers produced much more nectar and a much higher sucrose ratio than summer flowers.

This is especially important because it suggests that pollinator association can be **seasonally plastic** rather than a fixed one-colour/one-pollinator syndrome.

### 3.2 But yellow ≠ bird-pollinated

A simple `yellow -> bird` hypothesis is contradicted by the broader genus.

- Red *C. japonica* is strongly bird-associated in Japan.
- Red *C. rusticana* is insect-pollinated despite similar visible red petals; spectral experiments show that *C. rusticana* is more conspicuous to bees whereas *C. japonica* is relatively cryptic to bees and conspicuous to birds.
- White/pale oil camellias can receive important insect pollination, and some *Camellia* systems are generalized mosaics.

Therefore **visible hue alone is not the causal pollination trait**. The correct candidate phenotype is a multivariate floral module:

`pigment/spectrum + UV signal + flower geometry + nectar volume + sugar composition + flowering season + local pollinator fauna`.

### 3.3 Preliminary meta-analytic status

At present there are too few phylogenetically independent yellow species with comparable pollinator-exclusion experiments to justify a conventional pooled effect-size meta-analysis of `yellow -> bird dependence`.

The current evidence supports a **systematic comparative synthesis**, not a robust species-level meta-effect size.

The next quantitative step should therefore build a species/population-level database with:

- visitor guild proportions;
- exclusion effect sizes when available;
- pollen-contact effectiveness;
- fruit/seed response;
- flower reflectance / UV;
- nectar volume and concentration;
- sugar composition;
- flowering month / temperature;
- pigment-state variables;
- nuclear phylogenetic placement.

Then fit a phylogenetic hierarchical model rather than treating published studies as independent replicates.

## 4. Main competing hypotheses

### H0 — Historical concentration only

Yellow is concentrated in southwestern China–northern Vietnam primarily because an old yellow-bearing lineage originated there and retained geographic/niche conservatism. Pollinators do not explain additional variation after phylogeny and geography are controlled.

**Predictions**

- yellow probability is largely explained by clade membership and ancestral range;
- pollinator guild adds little predictive value after phylogenetic random effects;
- the same ancestral yellow-regulatory haplotypes are shared across the main yellow radiation.

### H1 — Ancestral accessible white state / latent-pathway hypothesis

The ancestral white-flowered state retained intact flavonoid/carotenoid machinery. Yellow and red states evolved primarily by changing tissue-specific regulation and pathway flux rather than by reconstructing lost pathways.

**Predictions**

- white lineages retain intact orthologs of core flavonoid genes and substantial pathway expression/metabolites;
- branch-specific colour transitions are enriched for cis-regulatory / TF / TE/SV changes rather than structural-gene birth/death;
- white-to-yellow transitions recruit existing `FLS`/flavonol and carotenoid modules;
- white-to-red transitions activate anthocyanin regulators such as MYB modules.

**Falsifier:** repeated pseudogenization/loss of core pigment pathways in white ancestors followed by independent structural reconstruction in coloured descendants.

### H2 — Single ancient yellow deployment + repeated loss

Yellow was recruited once early near the southwestern China–northern Vietnam radiation and was retained in southern lineages but repeatedly lost/suppressed elsewhere.

**Predictions**

- distinct extant yellow lineages share derived regulatory haplotypes or ancient gene-tree ancestry at causal loci beyond what species relatedness predicts;
- ancestral-state models prefer a small number of gains and many losses;
- regulatory alleles associated with yellow predate the diversification of major yellow subclades.

### H3 — Repeated regulatory recruitment of yellow

Visible yellow evolved multiple times by independently shifting flux through a conserved pigment network.

**Predictions**

- phylogenetically separate yellow trajectories lack one universal derived yellow haplotype;
- different branches use different `FLS`, `WRKY`, `MYB`, TE/SV, or carotenoid-regulatory changes;
- metabolomics may reveal convergent visible yellow through different biochemical mixtures;
- stochastic maps support multiple gains across plausible nuclear trees.

### H4 — Introgressive recruitment

Yellow-associated regulatory modules arose in one/few lineages and subsequently moved among species through hybridization/introgression.

**Predictions**

- causal-locus gene trees disagree with the species tree in a directional pattern;
- yellow-associated haplotypes show unexpectedly low divergence across otherwise separated taxa;
- local ancestry / D-statistics / network methods identify introgression around colour loci;
- the number of phenotypic gains inferred from a bifurcating species tree exceeds the number of underlying allele origins.

This hypothesis is important because *Camellia* shows extensive reticulation and chloroplast capture.

### H5 — Winter bird-filter hypothesis

The southern yellow radiation is partly maintained or repeatedly favoured where winter-flowering plants obtain higher effective service from nectar-feeding birds than from insects under cool/rainy conditions.

This hypothesis is **not** `birds prefer yellow`.

**Predictions**

- bird contribution increases with winter flowering, high nectar volume, sucrose-rich nectar, and local sunbird availability;
- after controlling for phylogeny/geography, pigment/spectral traits interact with pollinator community rather than acting alone;
- bird-exclusion effects are strongest in populations where weather suppresses bee activity;
- yellow lineages may show a repeated floral package rather than a repeated hue alone.

### H6 — Pollinator-mediated repeated pigment recruitment

Pollinator regimes do not merely maintain an old yellow lineage; repeated shifts in pollinator functional groups repeatedly favour changes in pigment deployment.

**Predictions**

- branches with reconstructed pollinator shifts are enriched for pigment-state transitions;
- regulatory colour changes temporally coincide with changes in nectar/flower traits;
- models containing pollinator-state transitions explain colour-transition rates better than geography-only models.

This is the strongest eco-evolutionary hypothesis but currently the least resolved because historical pollinator states are poorly sampled.

## 5. Public-sequence meta-analysis that can be executed now

### Track A — petal pathway meta-transcriptomics

Use three publicly anchored datasets:

1. `SRP112181` — *C. nitidissima*, 15 flower libraries across five developmental stages;
2. `PRJNA1136134` — red *C. amplexicaulis*, yellow *C. petelotii*, white *C. oleifera*, 9 petal RNA-seq experiments;
3. other accessioned Sect. *Chrysantha* petal datasets as they pass provenance checks.

Map transcripts to orthogroups and calculate pathway-level scores for:

- anthocyanin: `DFR`, `ANS/LDOX`, glycosylation/transport regulators;
- flavonol: `FLS`, `F3'H`, `F3'5'H`, quercetin/kaempferol-associated branches;
- carotenoid: `PSY`, `PDS`, `ZDS`, `CRTISO`, `LCYB/LCYE`, `BCH/CrtZ`, `ZEP`;
- regulatory modules: MYB/bHLH/WD40, WRKY, candidate repressors.

Do not meta-analyse raw TPM across independently assembled transcriptomes. Use within-study standardized contrasts or orthogroup-level effect sizes and include study as a random effect.

### Track B — coding-integrity / gene-tree screen across yellow taxa

The 20-species golden-camellia leaf transcriptome dataset published in 2025 has individual SRA accessions listed in its Table 1. These data can support:

- ortholog recovery;
- coding-integrity checks;
- gene-tree comparisons for `FLS`, `DFR`, `ANS`, `MYB`, `WRKY`, and carotenoid genes.

Because tissue is leaf, absence of a transcript cannot be interpreted as gene absence without genome support.

### Track C — colour-transition reconstruction

Use nuclear species-tree sets from broad phylogenomics, not chloroplast-only trees. Fit:

- ER/SYM/ARD Mk models;
- hidden-state variants;
- stochastic character maps;
- root-state sensitivity;
- tree-set sensitivity;
- uncertain-tip states for polymorphic/poorly characterized taxa.

Run two trait representations:

1. visible phenotype (`white`, `yellow`, `red/pink`, mixed/unknown);
2. mechanistic pigment state with anthocyanin, flavonol, and carotenoid axes.

Report posterior distributions for event counts rather than one integer.

### Track D — phylogenetic pollination meta-analysis

Build one row per population × season, not merely one row per species. Main response variables:

- bird proportion of effective visits;
- insect proportion;
- exclusion log response ratio where available;
- pollen limitation / fruit-set response.

Candidate predictors:

- pigment-state axes and reflectance;
- nectar volume / concentration / sucrose ratio;
- flowering season;
- temperature / rainfall during flowering;
- sunbird range overlap;
- flower geometry;
- phylogenetic covariance.

Compare:

`history-only` vs `history + floral traits` vs `history + pollinator environment` vs `full interaction` models.

## 6. The most important unresolved questions

1. **When did yellow first appear?** No current study directly dates the first yellow-state transition. Sect. *Chrysantha* divergence dates are not equivalent to pigment-gain dates.
2. **How many independent yellow gains occurred?** Multiple phylogenetic trajectories exist, but gain count is not yet estimated on a nuclear tree with model/tree uncertainty.
3. **Was the ancestral white state molecularly latent?** White-visible ancestors are reconstructed, but ancestral pathway activity/availability has not been reconstructed.
4. **Are different yellow lineages biochemically homologous?** At least *C. nitidissima* uses both flavonols and carotenoids; the same mixture cannot be assumed for all yellow taxa.
5. **Did yellow-associated alleles arise repeatedly or introgress?** Reticulation makes these alternatives critical.
6. **Does pollination explain yellow distribution beyond shared ancestry and geography?** Existing yellow species show notable bird contribution, but comparative sampling is too sparse for a causal macroevolutionary claim.
7. **Is winter bird service the relevant selective dimension rather than flower hue itself?** Existing *Camellia* examples strongly motivate this test.

## 7. Proposed headline problem

> **Did Southeast Asian yellow camellias preserve an ancient pigment programme, repeatedly recruit a latent programme from white-flowered ancestors, or repeatedly acquire/retain yellow because winter pollinator environments favoured the same accessible region of floral phenotype space?**

The project should explicitly separate three histories:

`pigment-network history` × `species/biogeographic history` × `pollinator-history`.

Only their joint reconstruction can distinguish simple range persistence from repeated adaptive evolution.

## Primary-source anchors

- Fan M. et al. *Plant Biotechnology Journal* (2026). DOI `10.1111/pbi.70442`.
- Fan M. et al. *Industrial Crops and Products* 244:123200 (2026). DOI `10.1016/j.indcrop.2026.123200`.
- Zan et al. *Molecular Phylogenetics and Evolution* (2023). `Phylogenomic analyses of Camellia support reticulate evolution among major clades`.
- Xie Y-J. et al. *Scientific Reports* 15:699 (2025). DOI `10.1038/s41598-024-83004-3`.
- Liu Y. et al. *BMC Plant Biology* (2025). DOI `10.1186/s12870-025-07067-8`.
- Zhou X. et al. *Frontiers in Plant Science* 8:1545 (2017). DOI `10.3389/fpls.2017.01545`; SRA `SRP112181`.
- Wang Y. et al. *Plant Growth Regulation* (2025). DOI `10.1007/s10725-025-01335-1`; BioProject `PRJNA1136134`.
- Sun S-G. et al. *American Journal of Botany* 104:468–476 (2017). DOI `10.3732/ajb.1600428`.
- Chai S-F. et al. *Plant Species Biology* (2019). DOI `10.1111/1442-1984.12247`.
- *Flora* (2025). `Nectar characteristics and pollination ecology of Camellia perpetua in South China`. DOI `10.1016/j.flora.2025.152727`.
- Mori S. et al. *Phytochemistry* 207:113559 (2023). DOI `10.1016/j.phytochem.2022.113559`.
