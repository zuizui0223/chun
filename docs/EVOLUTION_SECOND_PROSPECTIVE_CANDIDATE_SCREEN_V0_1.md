# Evolution second prospective candidate screen v0.1

Checked: 2026-09-11

## Purpose

After the first genuinely prospective Petunieae cross-level test returned `PETUNIEAE_PROSPECTIVE_BRIDGE_MIXED`, screen a finite set of plausible independent flower-colour radiations for a **second prospective full two-axis test** without weakening the Petunieae admission rule after seeing its result.

This is an admission screen, not an empirical reanalysis. No candidate's outcome distribution is inspected to choose a favourable threshold.

## Frozen admission rule

A candidate can advance to a new pre-result analysis gate only if the currently recoverable public evidence plausibly supports all of the following in one radiation:

1. **>=30 matched taxa** across the analysis frame, preserving the Petunieae coverage scale rather than lowering n after the MIXED result;
2. a direct source-defined **pigment amount/depletion** phenotype axis;
3. a direct source-defined **hue/hydroxylation or comparable pathway-branching** phenotype axis;
4. molecular measurements on the same taxon frame sufficient to define **>=3 prespecified molecular subspaces**;
5. a usable branch-length phylogeny for the matched taxa;
6. enough uninspected source values that phenotype definitions, transforms, molecular grouping and PASS/MIXED/FAIL thresholds can still be frozen before the decisive analysis.

Failure of any item is `HOLD`, not a biological negative result.

## Bounded candidate set

The screen is deliberately limited to six candidates identified before result-oriented source expansion:

- *Ruellia*;
- *Rhododendron*;
- Gesnerioideae;
- Antirrhineae;
- *Mimulus*;
- *Aquilegia*.

Iochrominae and Cape Erica are excluded because their cross-level patterns were already inspected retrospectively. Petunieae is the completed first prospective test and is not eligible to serve as its own replication.

## Results

| Candidate | Strong phenotype/phylogeny layer | Molecular layer | Admission verdict |
|---|---|---|---|
| *Ruellia* | 51-species reflectance + floral anthocyanin chemistry + phylogeny | colour-expression/co-expression panel is about 10 species | **HOLD** — same >=30 taxa are not matched across phenotype and molecular subspaces |
| *Rhododendron* | 30-species colour + quantitative anthocyanin chemistry | direct transcriptomic colour contrasts are concentrated in three *R. sanguineum* varieties or a few exemplars | **HOLD** — molecular frame is too small and not the 30-species phenotype frame |
| Gesnerioideae | 156 species / 180 samples with reflectance, anthocyanin chemistry and phylogeny | no recovered radiation-wide matched expression/functional panel spanning >=3 molecular subspaces | **HOLD** — no matched molecular bridge |
| Antirrhineae | large source trait/tree system; 169-taxon phylogenetic analysis and later repo reanalysis | auditable colour RNA-seq is concentrated in *Antirrhinum majus* and dependence-collapses to one lineage architecture | **HOLD** — existing molecular admission screen already fails |
| *Mimulus* | broad phylogenetic and flower-colour resources | strong functional/transcriptomic mechanisms exist, but they are species-, population- or event-focused | **HOLD** — no single >=30-taxon matched two-axis molecular panel |
| *Aquilegia* | phylogeny plus a 13-species anthocyanin-expression panel | depletion/late-pathway axis is direct; blue/red branching axis lacks a matched radiation-wide direct molecular panel | **HOLD** — existing PR #211 verdict retained |

Machine-readable ledger: `data/evolution_second_prospective_candidate_screen_v0_1.csv`.

## Source anchors

### Ruellia

The recent colour-space study (`10.1002/ajb2.70149`) characterises reflectance, floral anthocyanin concentrations and evolutionary history for 51 neotropical *Ruellia* species. The earlier co-expression study (`10.1186/s12862-021-01955-x`) provides colour-relevant transcriptomic/co-expression evidence and a hybrid transcriptome–RADseq phylogeny for only 10 species. This is valuable mechanistic evidence but not the same >=30-taxon matched frame.

### Rhododendron

The 30-species chemistry study (`10.1111/plb.12649`) directly quantifies colour and seven anthocyanins. The *R. sanguineum* complex transcriptome study (`10.1186/s12870-021-02977-9`) directly joins reflectance and RNA-seq, but only for three coexisting varieties. These datasets do not provide one common >=30-taxon molecular/phenotype frame.

### Gesnerioideae

`10.3389/fpls.2020.604389` provides 180 samples representing 156 species with reflectance, detailed anthocyanin chemistry and a phylogenetic framework. It is an excellent phenotype/biochemistry radiation but does not supply the matched radiation-wide gene-expression/functional panel required by the current bridge definition.

### Antirrhineae

The repository already contains `docs/ANTIRRHINEAE_MOLECULAR_ADMISSION_SCREEN_V0_1.md`. Its strict gate is `FAIL / HOLD`: two auditable colour RNA-seq contrasts are concentrated in the same *A. majus* regulatory architecture, with zero direct colour contrasts recovered outside *A. majus*. The strong macro layer therefore cannot be promoted into the required molecular bridge by reusing correlated systems.

### Mimulus

`10.1111/nph.12968` and related work provide strong functional and transcriptomic dissection of anthocyanin regulation across selected monkeyflower systems. Those studies establish mechanisms, not one radiation-wide >=30-taxon matched amount+hue+expression dataset. Event-level evidence is retained in its current benchmark role rather than relabelled as the decisive prospective radiation.

### Aquilegia

`10.1111/j.1365-294X.2006.03114.x` measures expression of six structural anthocyanin-pathway loci across 13 species and strongly supports late-pathway down-regulation in independent pigment-loss lineages. PR #211 already applied the two-axis bridge rule: depletion passes, while a matched direct blue/red hue molecular axis is unavailable. That HOLD is retained.

## Decision

**No candidate passes the frozen second-prospective admission rule.**

Status:

`NO_SECOND_PROSPECTIVE_FULL_BRIDGE_CANDIDATE_ADMITTED_UNDER_FROZEN_SCREEN`

Consequences:

1. **Do not lower the >=30 matched-taxon criterion** to make Ruellia, Aquilegia or another small molecular panel pass after Petunieae returned MIXED.
2. **Do not combine different taxon panels within a radiation** and call the result a matched cross-level test.
3. **Do not convert retrospective Iochrominae/Cape Erica evidence into prospective replication.**
4. **Do not reopen the Camellia Paper 1 AJB route on the basis of this screen.** Evolution escalation remains HOLD.
5. Reopen this search only when a newly available dataset plausibly meets all six admission items before its decisive values are inspected.

## What is still scientifically positive

The absence of an admitted second prospective dataset does not erase the existing programme result. The current strongest general statement remains:

> The molecular subspace associated with floral colour variation depends on the phenotype dimension being resolved: hue/hydroxylation repeatedly concentrates on pathway-branching machinery across retrospective radiations and a strong prospective Petunieae hue test, whereas pigment amount/depletion is less stable and response-definition sensitive.

That result is stronger than the original Camellia-only AJB package but is not yet the clean prospective two-axis replication required to authorize an *Evolution* first-submission architecture.

## Stop rule

This candidate screen is closed after the six named candidates. Further database searching is **not** justified merely because the current set produced zero admissions. Reopen only for a newly published/released dataset, a previously unavailable public dataset becoming accessible, or a concrete source already known to satisfy every admission field above.

Paper 1 remains unchanged.
