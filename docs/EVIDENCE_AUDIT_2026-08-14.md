# Evidence audit — 2026-08-14

## Purpose

This audit separates what can already be tested from public data from what remains a hypothesis. It also records the evidence conflicts that would otherwise allow a visually plausible flower-colour story to outrun the molecular data.

## 1. East Asian *Cirsium*: strong public phylogenomic input, weak petal-mechanism evidence

### What is already usable

Chang et al. (2026; DOI `10.1186/s12870-026-08097-6`) provide a phylotranscriptomic scaffold for the Taiwanese *Cirsium japonicum* complex and the Ryukyu taxa, with raw sequence data under `PRJNA1311153`.

The focal visible-colour observations include:

- *C. brevicaule*: white corolla;
- *C. irumtiense*: bluish-purple corolla;
- *C. japonicum* var. *albescens*: white;
- var. *takaoense*: white and bluish-purple morphs within the same named taxon;
- var. *australe*: bluish-purple in the sampled treatment;
- var. *fukienense*: purple with reported paler variation.

The same study reports reticulation within the Taiwanese complex, especially around var. *australe* and var. *fukienense*. The nuclear scaffold is therefore much more appropriate than a plastid-only colour history.

### Critical limitation

The public RNA-seq tissue described in the study is **leaf**, not petal. These reads can support:

- orthology and coding-integrity checks for anthocyanin-pathway genes;
- species-tree reconstruction;
- detection of obvious gene loss/pseudogenization where coverage permits.

They cannot directly support:

- petal-specific pathway activation;
- differential anthocyanin expression between white and purple morphs;
- causal pollinator preference.

The article abstract/conclusion state that flower-colour polymorphism in var. *takaoense* was linked to anthocyanin expression and pollinator preference, but the searchable main Methods/Results do not document a petal-expression or pollinator experiment. This claim remains **quarantined** until the supplementary/source evidence is recovered and checked.

### Highest-value *Cirsium* target

The two colour morphs of var. *takaoense* are particularly valuable because colour differs within one taxonomic lineage while broad morphology is reported as very similar. This gives a cleaner test of regulatory colour switching than a comparison between deeply diverged species.

However, the current public leaf RNA-seq samples are not demonstrated to be colour-morph-linked petal material. Therefore the branch may be labelled a **candidate regulatory switch**, but not a demonstrated anthocyanin reactivation.

## 2. *Camellia*: broad nuclear colour history plus experimentally resolved regulatory mechanisms

### Broad phylogenomic framework

Fan et al. (2026; DOI `10.1111/pbi.70442`) analysed 237 accessions and 11 de novo genomes. Their nuclear SNP framework inferred the *Camellia* MRCA as likely white-flowered. Early-diverging clades include white, yellow and red phenotypes, whereas later clades lack yellow in their sample.

The same work experimentally links a TIR structural variant near **MYB60** to increased MYB60 expression and anthocyanin suppression in yellow Sect. *Chrysantha* material.

This makes *Camellia* suitable for distinguishing:

- a visible-colour transition;
- suppression of anthocyanin;
- deployment of a separate yellow-pigment pathway.

### Public-data limitation

A complete public raw-data package sufficient to reproduce the 237-accession phylogeny has not yet been recovered in this audit. Until that changes, its ancestral-colour reconstruction is a **published reference result**, not yet a locally reproducible project result.

## 3. Yellow *Camellia* is not one biochemical state

### *Camellia nitidissima*

The 2017 flower transcriptome/pigment study (DOI `10.3389/fpls.2017.01545`) provides public flower RNA-seq under `SRP112181` and reports that golden-yellow petals contain both:

- carotenoids; and
- flavonol glycosides.

The 2013 CnFLS1 functional study (DOI `10.1007/s12038-013-9339-2`) shows that FLS can redirect shared dihydroflavonol substrates toward flavonols while reducing anthocyanin accumulation.

The 2024 multi-omics/functional study (DOI `10.1186/s12870-024-05332-w`) further supports petal-stage-specific flavonol accumulation and CnFLS2 regulation.

Therefore the earlier simplified `Y = flavonol-yellow` state is superseded. The project now tracks **anthocyanin, flavonol and carotenoid evidence independently**.

### *Camellia longruiensis* and southern China–Vietnam yellow lineages

Fan et al. (2026; DOI `10.1016/j.indcrop.2026.123200`) analysed 79 accessions including 26 yellow camellias from China and 18 from Vietnam. Most yellow accessions belong to a major yellow lineage, but *C. cucphuongensis* and *C. flava* follow a distinct trajectory with *C. krempfii* and *C. vidalii*.

The same study provides functional evidence that WRKY23 can activate **FLS** and promote flavonol accumulation in *C. longruiensis*.

This creates a direct test between:

1. old/relict retention of a yellow deployment state; and
2. repeated recruitment of yellow-pigment deployment in phylogenetically distinct lineages.

But the chemistry of the distinct *C. cucphuongensis* / *C. flava* trajectory must be established before claiming that the same molecular yellow state evolved repeatedly.

## 4. What can be analysed immediately

### Track A — *Cirsium* public nuclear/coding screen

Using `PRJNA1311153`:

1. recover sample metadata and taxon mapping;
2. reproduce or import the supported nuclear topology;
3. identify orthologs for `CHS`, `CHI`, `F3H`, `F3'H/F3'5'H`, `DFR`, `ANS/LDOX`, `UFGT` and key MYB/bHLH/WD40 regulators where transcript coverage permits;
4. test for gross coding loss, truncation or missing orthologs in white versus coloured lineages;
5. treat non-detection in leaf transcriptomes as **missing expression evidence**, not gene absence, unless genome/orthology evidence independently supports loss;
6. map visible colour only after the topology and taxon identities are frozen.

This track can falsify a strong irreversible-loss model in some branches, but cannot by itself prove petal reactivation.

### Track B — *C. nitidissima* public flower transcriptome reanalysis

Using `SRP112181`:

1. recover the 15 flower/developmental samples and stage metadata;
2. quantify anthocyanin-, flavonol- and carotenoid-pathway expression through development;
3. reproduce the direction of `FLS` versus `DFR/ANS` deployment;
4. build a pathway-level expression score rather than a visible-colour classifier;
5. use the result as a mechanistic reference for what a true pigment-flux switch looks like.

### Track C — published *Camellia* transition scaffold

Until the broad raw phylogenomic data are recovered:

1. encode the 237-accession published topology/state result as literature evidence only;
2. encode the 79-accession yellow-lineage result separately;
3. do not merge them into one synthetic tree without provenance;
4. search for deposited tree/SNP/genome resources and accession-level identifiers;
5. run ancestral-state models only after the phylogenetic input becomes reproducible or is explicitly accepted as a published-tree digitisation with uncertainty.

## 5. Priority hypotheses after the audit

### Priority 1 — regulatory accessibility

Do white flower states retain enough intact pigment machinery that later coloured states can arise mainly through regulatory redeployment?

The immediate *Cirsium* coding-integrity screen and *Camellia* functional references address opposite halves of this question.

### Priority 2 — biochemical non-equivalence of visible yellow

Do phylogenetically distinct yellow *Camellia* lineages use the same pigment mixture and regulatory route?

This must be answered before calling repeated visible yellow either convergence or reactivation.

### Priority 3 — transition accessibility

After biochemical states are assigned, compare whether transitions between anthocyanin-rich and yellow profiles occur directly or disproportionately through low-pigment/white states.

The previous `A/W/Y` visual simplification is not admissible for this mechanistic test.

## 6. Current public anchors

| System | Public anchor | Tissue/data | Immediate use |
|---|---|---|---|
| *Cirsium* | `PRJNA1311153` | leaf RNA-seq | nuclear/coding-integrity screen |
| *C. nitidissima* | `SRP112181` | flower developmental RNA-seq | pigment-pathway developmental reanalysis |

These are the first two reproducible raw-data tracks for the repository.

## 7. Claim status

### Supported now

- flower-colour polymorphism in East Asian *Cirsium* is not cleanly congruent with the reported nuclear lineage structure;
- *Camellia* contains repeated visible white/red/yellow states in a broad nuclear phylogenomic framework;
- at least one yellow *Camellia* species (*C. nitidissima*) uses both flavonol and carotenoid components;
- regulatory suppression/reallocation of conserved pigment pathways is experimentally plausible in *Camellia*.

### Not supported yet

- *C. irumtiense* as a proven anthocyanin reactivation;
- var. *takaoense* purple as a proven reactivation rather than retention/recruitment;
- a single biochemical state underlying all yellow *Camellia*;
- repeated independent origins of the same yellow mechanism;
- a causal pollinator explanation for any reconstructed transition.

## Next execution gate

The next computational milestone is reached when both public anchors have machine-readable sample manifests and the *Cirsium* pathway-gene coding screen plus the *C. nitidissima* developmental pathway-expression reanalysis can run reproducibly from accession metadata.