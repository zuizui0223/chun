# Epimedium provenance and historical-event gate — v0.2

## Decision

**Second mechanistic anchor: HOLD / FAIL-CLOSED for historical recurrence estimation.**

The eight-species molecular study (`10.3389/fpls.2023.1133616`) is a valuable comparative experiment on floral anthocyanin deployment, but its A+/A− observations are measurements of **garden accessions transplanted from unspecified wild populations**. They are not documented as the same accessions/populations used in the 2023 GBS phylogeny (`10.3389/fpls.2023.1234148`), and they cannot currently be assigned to independent historical colour-transition events.

This gate does not reject the molecular result. It prevents an accession-level phenotype from being silently promoted to a species-level evolutionary event.

## What the molecular paper actually establishes

Eight Epimedium species grown in the Wuhan Botanical Garden specialist nursery were sampled in spring 2011. All plants were reported as transplanted from wild populations and grown under a common environment, but the main article does not provide the exact source population or an accession crosswalk.

The sampled floral tissues separate cleanly into four anthocyanin-positive accessions (A+) and four anthocyanin-negative accessions (A−). HPLC and qPCR show:

- detectable cyanidin/delphinidin in A+ floral samples and no detectable anthocyanins in A− samples;
- ANS strongly reduced in all four A− samples;
- DFR reduced in the A− samples except *E. lishihchenii*;
- additional CHS/FLS differences in subsets of A− samples;
- retained coding function for tested *E. sagittatum* F3'H/DFR products in heterologous functional assays.

The defensible molecular conclusion is therefore **convergent-looking regulatory reduction at the functional-module level**, not four identified independent historical pigment-loss events.

## Why species-tip promotion is unsafe

### 1. Known intraspecific colour polymorphism

Xu et al. 2019 (`10.3897/phytokeys.118.30268`) used population-level field surveys and documented substantial intraspecific flower-colour polymorphism in five Epimedium species, including **both *E. acuminatum* and *E. leptorrhizum***. Those two species are A+ in the eight-species molecular paper.

Thus `molecular accession A+` is demonstrably not equivalent to `species fixed A+` for at least part of the molecular panel.

### 2. Missing source-population crosswalk

The molecular paper states only that nursery plants were transplanted from wild populations. No exact wild-population source or sample/accession identifier has been recovered that allows the sampled 2011 plants to be linked to a GBS accession, population trait row, or reconstructed transition branch.

### 3. Rapid radiation, ILS and introgression

The 2023 phylogenomic study sampled 57 accessions and found two major clades plus multiple supported subclades, but also topology differences among de-novo/reference/coalescent analyses and extensive reticulation. It explicitly reports rapid Pleistocene radiation, incomplete-lineage-sorting concerns, and introgression. The historical independence of molecular samples therefore cannot be inferred safely from traditional series membership or one convenient topology.

## Current status of the eight molecular samples

The authoritative row-level status is `data/epimedium_molecular_provenance_gate_v0_2.csv`.

Rules:

1. A+/A− remains a valid **sample/accession observation**.
2. A+/A− must not fill a species-level terminal colour state when population colour is unresolved or polymorphic.
3. No A− sample counts as an independent historical loss until a defensible accession/population-to-tree/event crosswalk exists.
4. The number of independent loss/gain events represented by the eight samples is currently **UNRESOLVED**, not four.
5. The molecular panel can still be used as a functional-module benchmark, provided the estimand is accession/species comparative expression and not macroevolutionary recurrence.

## Implication for the cross-clade atlas

Epimedium remains highly valuable, but its role changes:

- **retain:** organ-aware functional-module benchmark;
- **retain:** explicit current-polymorphism ↔ evolutionary-history bridge;
- **retain:** test case showing why accession-level state, species-level state and historical event are separate quantities;
- **hold:** second independent mechanistic-recurrence anchor requiring >=3 identified historical transitions.

This is not a failure of the atlas. It is a cross-clade replication of the core identification lesson from Camellia: measurement resolution can be stronger than historical event resolution.

## Reopen criterion

Promote Epimedium to a second historical mechanistic anchor only if at least one of the following closes the event identity gap:

- exact wild-source/accession crosswalk for the eight molecular plants becomes available and maps >=3 samples/contrasts onto defensibly independent transitions;
- new population-resolved colour molecular data are generated/released across >=3 independent lineages;
- a new multi-species study supplies molecular phenotype, terminal population state and phylogenetic event identity under one auditable sampling design.

Until then, the recurrence estimator must not treat the four A− samples as four independent losses.

## Paper-1 boundary

This is post-Paper-1 programme development only. It changes no Camellia science v0.2.2, framing v0.3.4, AJB v1.0 output or scientific-closure decision.
