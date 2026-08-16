# Camellia flower-colour mechanism meta-synthesis v0.2

## Status

This is a **dependence-aware directional synthesis**, not yet a pooled effect-size meta-analysis.

The v0.2 evidence table contains 12 mechanistic study records grouped into 8 independence clusters so that repeated studies on the same focal biological system (especially *C. japonica* and *C. reticulata*) are not silently counted as independent evolutionary replicates.

Three descriptive layers are frozen:

1. all literature study records;
2. records whose raw sequence resource is currently publicly resolvable/admissible;
3. independence-cluster consensus.

The authoritative inputs/outputs are:

- `data/camellia_flower_color_mechanism_meta_v0_2.csv`
- `scripts/summarize_camellia_flower_color_mechanism_meta_v0_2.py`
- `data/camellia_flower_color_mechanism_meta_summary_v0_2.csv`
- `data/camellia_general_colour_admitted_sample_manifest_v0_1.csv`

## Results

### 1. Anthocyanin abundance tracks the red/pink direction

Among study records that make a directional comparison, **10/10** report higher anthocyanin in the more red/pink state.

The same direction is retained when restricted to currently public/resolvable raw studies (**7/7**) and after collapsing dependent records to independence clusters (**6/6 informative clusters**).

This is the strongest current recurrent result.

It does not imply that all red flowers have the same chemistry. The genus-wide and cultivar studies show variation in cyanidin/delphinidin composition, acylation and concentration. The recurrent claim is only about movement toward stronger anthocyanin deployment in redder states.

### 2. The downstream anthocyanin branch repeatedly strengthens in redder states

For studies that directly resolve this direction, **6/6 study records**, **4/4 currently public/resolvable raw records**, and **4/4 informative independence clusters** report stronger downstream anthocyanin-side deployment in the more red state.

The recurrent nodes include `DFR`, `ANS/LDOX`, glycosylation steps and associated transcriptional regulators, although not every study measures the same genes.

### 3. Less-red, white or yellow states repeatedly strengthen competing deployment

Among directly interpretable comparisons, **6/6 study records**, **4/4 currently public/resolvable raw records**, and **5/5 informative independence clusters** report stronger deployment of at least one competing branch in the less-red/white/yellow direction.

Examples include:

- higher `FLS` deployment in white relative to pink *C. sinensis*;
- increased `ANR`/proanthocyanidin-side diversion in white petal regions or developmental fading;
- flavonol-rich and carotenoid-rich deployment in yellow flowers.

The exact competing branch is not universal. The recurrent signal is **flux redistribution**, not one universal white/yellow pathway.

### 4. Regulatory or pathway-flux explanations recur across all current systems

All 12 included study records and all 8 independence clusters contain evidence for regulatory or pathway-allocation differences associated with visible colour. Among the eight study records whose raw resource is currently public/resolvable, all eight also point in this direction.

This category includes different evidence classes:

- expression changes in structural genes;
- transcription-factor differences;
- cis-regulatory/TE/SV candidates;
- within-flower spatial switches;
- developmental switches;
- metabolite-flux redistribution.

Because the literature is enriched for successful mechanism studies, `12/12` should not be interpreted as an unbiased estimate of how often regulation causes colour evolution in nature. It is evidence that regulatory accessibility is a repeatedly observed mechanism across distinct biological scales.

### 5. No current study requires structural-gene loss to explain its focal colour contrast

Only a subset of studies directly informs this question. At the study-record level, four are directly informative and all four code `no`; at the independence-cluster level, three are directly informative and all three code `no`. The remaining clusters are `no_evidence`, not evidence of absence.

The genus-wide 2026 genomic study is particularly important because it reports broad retention of core flavonoid structural genes across colour groups and places major candidate differences in regulatory/TE/SV contexts.

The correct current claim is:

> **There is repeated positive evidence for regulatory/flux change, while the current synthesis contains no positive evidence that wholesale structural-gene loss is required for the focal colour contrasts.**

It is not valid to claim that structural-gene loss never contributes to *Camellia* flower-colour evolution.

## Why within-genotype studies matter

The v0.2 table includes several contrasts that occur without deep phylogenetic divergence:

- *C. japonica* bud sports spanning white to dark red;
- red/pink sectors of a single *C. japonica* cultivar;
- red/white sectors of *C. reticulata*;
- developmental pink-to-white fading within *C. reticulata*;
- developmental yellow-pigment accumulation within *C. nitidissima*.

These do **not** estimate natural macroevolutionary transition rates. Their role is different: they demonstrate that large visible colour changes are mechanistically reachable by changing regulation/deployment in an already existing genetic background.

This is the key mechanistic bridge to the `accessible-state` hypothesis.

## Revised central hypothesis

The strongest current working model is:

> **Much of *Camellia* flower-colour evolution occurs within an evolutionarily accessible pigment network. White, pink/red and yellow phenotypes can be produced by repeated changes in pathway activation, repression and substrate allocation while much of the underlying biosynthetic machinery remains retained.**

This model predicts that macroevolutionary transitions should repeatedly reuse network positions that are also labile within cultivars, petal sectors and developmental stages.

## Competing explanations still open

The directional synthesis does not distinguish among:

1. repeated independent regulatory recruitment;
2. retention of ancient regulatory programmes followed by repeated suppression/loss;
3. introgression of colour-associated regulatory alleles;
4. different molecular routes producing the same visible phenotype.

Those alternatives require the phylogenetic and raw-data layers below.

## Public-data admission achieved for the NCBI subset

The NCBI-accessible colour datasets have now been resolved to concrete run-level metadata and frozen in `data/camellia_general_colour_admitted_sample_manifest_v0_1.csv`.

Current admitted/resolved NCBI subset:

- `SRP112181`: 15 *C. nitidissima* flower-development runs;
- `PRJNA597123`: 15 pink *C. sinensis* runs (five stages × three replicates);
- `PRJNA597289`: 15 white *C. sinensis* runs (five stages × three replicates);
- `PRJNA757193`: 15 *C. japonica* bud-sport runs (five groups × three replicates; three control-colour samples remain explicitly unresolved);
- `PRJNA913600`: six *C. japonica* petal-sector runs (pink three + red three);
- `PRJNA1136134`: nine cross-species runs (red, white and yellow, three replicates each).

That is **75 run-level RNA-seq records**. Seventy-two currently have explicit colour-state mappings; three control samples in the bud-sport study remain colour-unresolved rather than being guessed.

The oil-camellia paper states `PRJNA859399`, but live NCBI SRA resolution returns zero RunInfo rows as of the audit date. This is recorded as provenance conflict `META007` and that study remains usable at literature level but is excluded from raw-read pooling until the archive issue is resolved.

## Next quantitative layer: standardized raw-data meta-transcriptomics

The next goal is to replace directional votes with comparable effect sizes derived from public raw data.

For each admissible petal RNA-seq dataset:

1. freeze run/sample metadata and tissue/colour/stage labels;
2. map to a common ortholog set;
3. calculate pre-defined pathway module scores;
4. obtain within-study standardized contrasts;
5. fit a multilevel meta-analysis with study, taxon and contrast scale as moderators.

Primary modules:

- anthocyanin structural module: `CHS/CHI/F3H/F3'H/F3'5'H/DFR/ANS/UFGT`;
- flavonol branch: `FLS` and supporting steps;
- proanthocyanidin/procyanidin diversion: `ANR/LAR` where homologs and expression are defensible;
- selected MYB/bHLH/WD40/WRKY regulatory modules;
- carotenoid module for yellow systems.

CRA/GSA/GEO resources remain provider-specific and must be admitted through separate provenance routes rather than being forced through NCBI SRA tooling.

## Exploratory exact sign synthesis

A dependence-collapsed exact sign analysis is frozen in `data/camellia_direction_sign_meta_v0_1.csv`.

Under a symmetric 50:50 directional null:

- higher anthocyanin in the more-red state: 6/6 informative independence clusters, exact two-sided `P = 0.03125`;
- stronger downstream anthocyanin deployment in the more-red state: 4/4, `P = 0.125`;
- stronger competing-branch deployment in the less-red/white/yellow state: 5/5, `P = 0.0625`;
- regulatory/flux evidence associated with the colour contrast: 8/8, `P = 0.0078125`;
- structural-gene loss not required: 3/3 informative clusters, `P = 0.25`.

These P-values quantify **directional recurrence in this selected literature**, not the natural frequency of mechanisms and not an unbiased publication-level meta-effect.

## Next phylogenetic layer

The second major result must quantify **how many times colour states changed**.

The target outputs are distributions such as:

- `P(N_red_or_pink_gains = k)`;
- `P(N_white_gains = k)`;
- `P(N_yellow_gains = k)`;
- posterior/bootstrapped support for direct versus white-mediated transitions;
- branch-level probability of retention, recruitment, suppression or true reactivation.

This must be repeated across nuclear-tree and model uncertainty (ER/SYM/ARD and, if needed, hidden-state models). A plastid topology is not admissible as the sole origin-count backbone in a reticulate genus.

## Remaining gaps

1. The molecular state of the inferred white MRCA is unknown.
2. A machine-readable, locally reproducible 237-accession nuclear tree with branch lengths has not yet been frozen from the 2026 genus-wide study.
3. Public raw RNA-seq now has a frozen NCBI run-level subset, but ortholog/expression harmonization is not yet complete and CRA/GSA/GEO provider-specific inputs remain to be admitted.
4. Wild macroevolutionary transitions and horticultural/mechanistic accessibility must remain separate inferential levels.
5. Pollinator studies are not yet numerous/standardized enough for a simple colour-category pooled effect; spectrum/UV, nectar and season must be incorporated.
6. Identical visible yellow or red states can have different pigment composition, so visible-colour and mechanistic-state analyses must be run separately.

## Claim boundary for v0.2

Supported as a working meta-synthesis:

> Across multiple *Camellia* systems and biological scales, redder states consistently show stronger anthocyanin deployment, while less-red/white/yellow states repeatedly show alternative pathway allocation. This recurrence is compatible with regulatory accessibility of a conserved pigment network.

Not yet supported:

- a numerical frequency of regulatory versus coding causes in wild evolution;
- a definitive number of independent red, white or yellow origins;
- proof that the genus ancestor's white state retained every modern pigment pathway;
- proof that white is a required evolutionary intermediate;
- proof that pollinators caused the reconstructed colour transitions.
