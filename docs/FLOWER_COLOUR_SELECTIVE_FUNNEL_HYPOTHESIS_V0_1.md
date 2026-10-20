# Flower-colour selective funnel hypothesis v0.1

## Programme advance

The cross-clade atlas should not be organized only around whether a clade has a white-like ancestral state. A stronger programme-level question links the spatial/current variation arm (`fcp`) to the evolutionary-time arm (`chun`):

> **How much of the flower-colour variation that is molecularly possible and segregating now survives the filters required to become a persistent lineage-level state through evolutionary time?**

The proposed architecture is:

`current segregating variation`

`-> developmental / biochemical possibility space`

`-> ecological + pleiotropic + demographic filtering`

`-> fixed population/species differences`

`-> long-term recurrent macroevolutionary states`.

This is called the **selective funnel** here as programme shorthand.

## Prior-art boundary

The selective-funnel idea itself is not new and must not be claimed as such.

- Sobel & Streisfeld (2013) explicitly distinguished segregating flower-colour polymorphisms from fixed differences and predicted different mutation spectra after selective filtering.
- Wu et al. (2013; `10.1371/journal.pone.0081173`) identified a rare white *Mimulus lewisii* morph caused by a coding frameshift and argued that segregating flower-colour variation spans a broader mutational spectrum than fixed differences.
- Larter et al. (2019; `10.1002/dvdy.82`) directly compared white morphs within pigmented Iochrominae species with fixed white species. They were biochemically convergent but developmentally non-convergent: white species showed characteristic downstream pathway downregulation, whereas white morphs remained closer in expression space to their pigmented conspecifics.

Therefore the atlas novelty cannot be `short-term and long-term flower-colour mechanisms differ`.

## Retained new test

The atlas can make a stronger, explicitly cross-clade test by rebuilding observations under a common hierarchy rather than comparing narrative case studies.

### H-F1 — possibility-space contraction

The diversity of molecular perturbations associated with segregating within-species colour variation is greater than the diversity of molecular modules associated with persistent fixed differences.

Operationally, compare entropy/effective-number of observed molecular target classes after conditioning on direction and pigment system:

`H_molecular(within) > H_molecular(fixed)`.

Do not pool gene names directly across clades; map them to a hierarchical ontology (structural coding change, structural cis-regulation, pathway-specific regulator, broad regulator, branch enzyme, downstream deployment module, yellow-pigment module, other).

### H-F2 — late/specific module enrichment through time

Persistent fixed transitions are enriched for changes expected to reduce pleiotropic cost (for example tissue-specific regulators, branch enzymes or late pathway deployment) relative to transient/segregating variation.

This is a directional prediction but not a universal rule; clades such as Iochrominae and Mimulus provide benchmark evidence, not priors to force the outcome.

### H-F3 — phenotype convergence can increase while mechanism space contracts

The same visible state may occur frequently at both within-population and macro scales, while the set of molecular routes that persist through time becomes narrower.

Thus visible recurrence and mechanistic recurrence are separate axes.

### H-F4 — micro ecological associations need not scale to macro persistence

Ecological correlates of morph frequency within polymorphic species need not predict the long-term distribution of colour states across species. Monkeyflower work provides a direct benchmark where abiotic associations at the micro scale did not reproduce as phylogenetically controlled macroevolutionary association.

### H-F5 — current polymorphism is not automatically an incipient fixed state

A present-day morph is a sample from the accessible phenotype space, not necessarily a snapshot of the mechanism that will later fix. Iochrominae is the key empirical benchmark: similar white endpoints above and below the species level can have different developmental implementations.

## Evidence roles

The first frozen systems have complementary roles rather than one forced common estimator:

- **Iochrominae** — direct same-clade selective-funnel benchmark: six polymorphic species, fixed white species, 28-species molecular comparison, open Dryad data.
- **Mimulus lewisii** — mutation-spectrum benchmark for a rare segregating white morph versus known fixed pigment-intensity differences.
- **Antirrhineae** — macro bridge between extant polymorphism categories and long-term transition corridors; molecular independence gate currently fails.
- **Lysimachia monelli/arvensis** — counterexample/control in which similar trans-specific colour polymorphisms have strongly shared biochemical and expression mechanisms.
- **Monkeyflowers (Erythranthe/Diplacus)** — ecological micro-to-macro scale-dependence control.
- **Silene littorea** — within-species molecular possibility-space reference.

## Relation to the white-baseline atlas

Ancestral baseline and selective funnel are orthogonal dimensions.

A clade can be:

1. white-like ancestral or coloured ancestral; and
2. informative about within-to-between-timescale filtering or not.

This prevents the study from selecting only clades that fit a `white -> colourful` narrative.

The cross-clade table should therefore carry both:

- `ancestral_baseline_class`; and
- `timescale_evidence_role`.

## What would be original data

The new contribution would be a harmonized observation dataset in which each published event/morph is recoded under the same rules for:

- biological scale: within population / geographic fixed difference / species fixed difference / macro transition;
- display organ;
- visible state;
- pigment chemistry;
- molecular target ontology;
- mutation/regulation class;
- evidence type and raw-data availability;
- topology/event-identifiability status;
- ecological association/effect where available.

The pooled result is not allowed until row-level evidence is rebuilt with provenance. Literature conclusions are QC targets, not data rows.

## Claim ceiling

Do not claim:

- that all current polymorphisms are evolutionary intermediates;
- that selection alone creates the funnel;
- that pleiotropy is the only filtering mechanism;
- that white ancestry is required for funneling;
- that a within-species molecular route is ancestral to a fixed species route without historical evidence.

The intended general question is narrower:

> **Does the observable molecular possibility space of flower-colour variation contract systematically across evolutionary timescales, and which functional modules disproportionately survive into persistent lineage-level differences?**
