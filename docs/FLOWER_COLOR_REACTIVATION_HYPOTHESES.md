# Reversible floral pigment deployment in East Asian *Cirsium* and *Camellia*

## Working question

**Is repeated flower-colour evolution best understood as repeated invention/loss of pigments, or as repeated switching among latent, competing and tissue-specific deployments of conserved pigment pathways?**

This project starts from the East Asian *Cirsium* question — whether white-flowered states represent anthocyanin-pathway loss or petal-specific suppression, and whether later pink/purple states can represent re-deployment — and expands it to *Camellia*, where white, anthocyanin-rich red/pink and flavonol-rich yellow states recur across a broad East/Southeast Asian radiation.

The intended comparison is **mechanistic architecture**, not identical mutations. A convergent result would mean that different lineages repeatedly alter tissue-specific regulation and pathway flux while retaining much of the underlying flavonoid machinery.

## Why *Camellia* is an unusually useful comparison

Recent genomic work changes the problem from a simple colour-history exercise into a test of reversible pathway deployment.

Fan et al. (2026, *Plant Biotechnology Journal*, DOI: `10.1111/pbi.70442`) analysed 237 *Camellia* accessions and inferred the genus MRCA as likely white-flowered. Their early-diverging clade contains yellow, white and red phenotypes, whereas later-diverging clades lack yellow. The same study linked lineage-specific structural/TE variation to regulatory rewiring and experimentally implicated a TIR-associated change affecting **MYB60** and anthocyanin suppression.

Fan et al. (2026, *Industrial Crops and Products*, DOI: `10.1016/j.indcrop.2026.123200`) analysed 79 accessions, including 26 yellow camellias from China and 18 from Vietnam. Most yellow accessions fall into a major yellow lineage, but *C. cucphuongensis* and *C. flava* follow a distinct phylogenetic trajectory. Vietnamese and Yunnan accessions include early-diverging yellow lineages. This makes both **ancestral/relict retention** and **repeated yellow recruitment** explicit alternatives to test.

Yellow *Camellia* flowers are also mechanistically different from white flowers. In *C. nitidissima*, flavonol accumulation is strongly associated with yellow petals. FLS diverts shared dihydroflavonol precursors toward flavonols and away from anthocyanin production (Zhou et al. 2013, DOI: `10.1007/s12038-013-9339-2`; see also later multi-omics work on FLS regulation). Therefore yellow ↔ red evolution is potentially a **flux-allocation switch inside a shared flavonoid network**, not simply pigment loss versus gain.

## State representation

Do not force flower colour onto one ordered axis.

Maintain two linked data layers.

### Visible phenotype

- `white`
- `pink_red_purple`
- `yellow`
- `mixed_or_other`
- `unknown`

### Pigment state

When chemical or sufficiently strong molecular evidence exists:

- `W`: neither anthocyanin nor yellow flavonol strongly deployed in petals
- `A`: anthocyanin-dominant
- `Y`: flavonol-yellow dominant
- `AY`: both pigment classes demonstrably contribute
- `U`: unresolved

**Visible yellow must never be coded automatically as `anthocyanin = 0`.**

## Terminology gate

The central words have different evidential requirements.

### Retention
Use when a coloured state is ancestrally continuous across the relevant branch.

### Recruitment / gain
Use when a pigment appears in flowers after a white ancestral state, but prior floral activity of that pathway has not been demonstrated.

### Reactivation / re-expression
Use only when both conditions are supported:

1. phylogenetic evidence supports an earlier floral active state → intervening suppression/absence → later active state; and
2. molecular evidence supports retention of the underlying pathway during the suppressed interval.

A coloured descendant alone is **not** evidence of reactivation.

## Hypotheses

### H1. Latent anthocyanin-pathway hypothesis

White petals often retain an intact anthocyanin biosynthetic capacity that is transcriptionally, spatially or developmentally suppressed rather than genetically destroyed.

#### Predictions

- white lineages retain intact orthologs of `CHS`, `CHI`, `F3H`, `DFR`, `ANS` and major regulatory modules;
- petal expression and regulatory state distinguish white from coloured taxa better than structural-gene presence/absence;
- branches inferred to regain pink/red/purple pigmentation show re-use of retained machinery rather than wholesale reconstruction;
- flower-specific regulatory changes are more common than repeated coding-gene loss and recreation.

### H2. *Cirsium* Ryukyu reactivation alternatives

For the *C. brevicaule*–*C. irumtiense* contrast and nearby East Asian lineages, distinguish four histories rather than assuming one:

1. coloured ancestor → white-flower loss/suppression;
2. white ancestor → coloured recruitment;
3. ancestral colour polymorphism → differential sorting/fixation;
4. coloured ancestor → white suppression → later anthocyanin reactivation.

The fourth history earns the word **reactivation** only if the topology, ancestral-state model and pathway-retention evidence agree.

### H3. Flavonoid flux-switch hypothesis in yellow *Camellia*

Yellow petal evolution is primarily a change in allocation through a shared flavonoid network, not merely anthocyanin absence.

#### Predictions

- yellow states show elevated `FLS`/flavonol deployment and reduced flux through `DFR`/`ANS`/anthocyanin modules;
- regulatory changes involving WRKY/MYB/bHLH/WD40 modules are enriched around colour transitions;
- transitions between A and Y may require coordinated changes in competing branches or a shared upstream regulator;
- structural genes can remain conserved while regulatory state and metabolite flux change strongly.

### H4. White-bridge / accessible-state hypothesis

Direct transitions between anthocyanin-dominant (`A`) and flavonol-yellow (`Y`) states may be less accessible than transitions through a low-pigment/white (`W`) state.

This is inspired by broader flower-colour transition theory but must be tested independently in *Camellia*.

#### Model comparison

Compare at least:

- unrestricted `A <-> W <-> Y` plus direct `A <-> Y`;
- white-bridge model with direct `A <-> Y` prohibited;
- penalized direct-transition model;
- hidden-state model if simple Mk models fit poorly.

Use stochastic maps to estimate not only root state but also transition counts and locations.

### H5. Southeast Asian yellow-lineage alternatives

The concentration of early-diverging yellow *Camellia* lineages around southwestern China and Vietnam can arise through at least two histories.

#### H5a — relict retention
Yellow/flavonol deployment is an old state retained disproportionately in the southern China–Vietnam region and lost from later radiations.

#### H5b — repeated recruitment
Yellow/flavonol deployment evolved or was re-recruited multiple times, including phylogenetically distinct yellow trajectories such as those involving *C. cucphuongensis* and *C. flava*.

These are mutually testable alternatives. Do not describe yellow as ancestral or convergent until a taxonomically broad state reconstruction supports it.

### H6. Regulatory convergence across families

If independent transitions in *Cirsium* and *Camellia* repeatedly involve tissue-specific regulation, TE/SV-associated regulatory change or pathway-flux control while structural pigment genes remain intact, then a general mechanism is supported:

> **floral colour evolves repeatedly because conserved pigment machinery remains evolutionarily accessible and can be re-deployed.**

The convergence is predicted at the level of network architecture, not necessarily the same gene or mutation.

## Sampling frame

### East Asian *Cirsium*

Core focal taxa/complexes:

- *Cirsium brevicaule* — white
- *C. irumtiense* — pale pink to purple
- Taiwan *C. japonicum* complex — include white and blue-purple forms only where taxonomy/colour evidence is secure
- *C. morii* and other Taiwan/Ryukyu relatives as phylogenetic anchors
- continental and Japanese close relatives needed to polarize transitions

Expansion:

- *C. boninense* and other independent white-flowered island lineages

The first analysis should remain East Asian and phylogenetically defensible rather than expanding globally before transition direction is resolved.

### *Camellia*

Core data sources:

- broad 237-accession nuclear phylogenomic framework;
- dedicated 79-accession yellow-*Camellia* dataset with China/Vietnam coverage;
- yellow species with genomic/metabolomic evidence, including *C. longruiensis* and *C. nitidissima*;
- *C. cucphuongensis* and *C. flava* as tests of distinct yellow trajectories.

Geographic priority:

1. southwestern China;
2. Vietnam;
3. verified yellow lineages from the wider Southeast Asian distribution.

Myanmar/Thailand/Malaysia records should enter only after accepted-name, colour and sequence provenance checks. A colour-only species list without reliable phylogenetic placement is not sufficient.

Newly described taxa such as yellow *Camellia* from southern Yunnan are useful additions when nuclear sequence data and taxonomic evidence are available, but new names should not be allowed to destabilize the analysis silently; all additions must be versioned.

## Analysis plan

### Phase 1 — evidence matrix

Create a versioned table with at least:

```text
accepted_taxon
source_taxon_name
family
genus
region
country_or_island
visible_colour
anthocyanin_evidence
yellow_flavonol_evidence
pigment_state
chemical_evidence_level
rna_seq_available
genome_available
resequencing_available
nuclear_phylogeny_source
plastid_phylogeny_source
reticulation_flag
source_doi_or_accession
notes
```

Literature colour descriptions, chemistry and image observations must stay in separate evidence columns.

### Phase 2 — phylogenetic history

- prioritize nuclear species trees;
- retain alternative nuclear/plastid histories where discordance is known;
- fit ER/SYM/ARD Mk models;
- fit white-bridge and unrestricted transition graphs;
- use stochastic character mapping for transition counts/locations;
- repeat across plausible tree sets;
- report posterior/likelihood uncertainty instead of a single painted tree.

For yellow *Camellia*, plastid-only inference is not admissible as the main result because nuclear–plastid discordance and hybridization/introgression have been reported.

### Phase 3 — molecular mechanism

For candidate loss/recruitment/reactivation branches with public molecular data:

- structural-gene coding integrity;
- copy number and orthology;
- petal RNA-seq expression where available;
- `FLS` versus `DFR/ANS` branch deployment;
- MYB/bHLH/WD40 and WRKY regulatory candidates;
- TE/SV proximity to regulators in *Camellia*;
- signatures of pathway retention in white states.

For focal *Cirsium* field material, the decisive experiment is standardized petal pigment chemistry plus petal RNA-seq/qPCR across white and pink/purple relatives.

### Phase 4 — ecology after history

Only after transition direction is resolved, test whether independent pigment-state transitions covary with:

- pollinator guild / visual system;
- island versus continental setting;
- climate/light stress;
- habitat and elevation.

Ecology should explain why a transition may be selected or maintained, not be used to invent the direction of the transition.

## Falsification criteria

The central reversible-deployment hypothesis weakens if:

- white lineages repeatedly show irreversible loss/pseudogenization of key pathway components;
- apparent colour regains require independently reconstructed structural pathways;
- candidate reactivation events disappear across plausible trees;
- yellow states form one strongly supported origin with no evidence of repeated pathway recruitment and no meaningful regulatory flux shifts;
- regulatory changes do not explain colour-state differences better than coding-gene loss/gain.

## Minimum claim boundaries

Until the tests above are completed, the repository may claim:

> East Asian *Cirsium* and *Camellia* provide complementary systems for testing whether repeated flower-colour transitions arise through reversible regulation and pathway-flux shifts in conserved flavonoid networks.

It may **not** yet claim:

- that *C. irumtiense* is proven to be an anthocyanin reactivation;
- that yellow *Camellia* evolved multiple times;
- that yellow is ancestral in *Camellia*;
- that the same molecular mutation explains both genera;
- that pollinators caused any inferred transition.

## Initial literature anchors

- Fan M. et al. 2026. Transposable Element-Mediated Structural Variation Drives Flower Colour Diversification in *Camellia*. *Plant Biotechnology Journal*. DOI: `10.1111/pbi.70442`.
- Fan M. et al. 2026. A near telomere-to-telomere genome reveals yellow camellias evolution and flavonols biosynthesis. *Industrial Crops and Products* 244:123200. DOI: `10.1016/j.indcrop.2026.123200`.
- Zhou X-W. et al. 2013. Functional analyses of a flavonol synthase-like gene from *Camellia nitidissima* reveal its roles in flavonoid metabolism during floral pigmentation. *Journal of Biosciences* 38:593–604. DOI: `10.1007/s12038-013-9339-2`.
- Functional diversification work on *C. nitidissima* DFR and later multi-omics work on the FLS/flavonol module should be added to the evidence registry during Phase 1.
- Yellow-*Camellia* phylogenomic studies reporting nuclear/plastid discordance and introgression should be included before any ancestral-state claim is frozen.

## Tracking

The first implementation and data-acquisition tasks are tracked in **Issue #1**.