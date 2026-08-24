# C. japonica Joy Kendrick candidate-free RNA-seq pilot v0.1

## Purpose

This is the first real raw-data test of the candidate-free pigment-module pipeline. It is deliberately chosen as a within-genotype contrast so that deep phylogenetic divergence is absent.

The pilot asks a narrow question:

> When the same predefined A/F/C/P modules are quantified without using the source paper's nominated candidate genes, which module differences are recoverable between red and pink petal regions of the same *Camellia japonica* cultivar?

It is not a macroevolutionary transition test.

## Frozen samples

BioProject: `PRJNA913600`.

Pink region:

- `SRR22904726` — `Pink1` — `SAMN32301769`;
- `SRR22904725` — `Pink2` — `SAMN32301770`;
- `SRR22904724` — `Pink3` — `SAMN32301771`.

Red region:

- `SRR22904723` — `Red1` — `SAMN32301772`;
- `SRR22904722` — `Red2` — `SAMN32301773`;
- `SRR22904727` — `Red3` — `SAMN32301774`.

Archive sample names directly encode region and replicate, so condition labels are not inferred from run order.

## Frozen contrast

`CJ_JK_PINK -> CJ_JK_RED`.

All four primary axes A/F/C/P are evaluated. Positive signed Hedges' g means higher module score in the red target region.

No expected biological direction is a CI pass condition. A, F, C or P may increase, decrease or remain unresolved.

## Reference

Pilot reference: *Camellia sinensis* assembly `GCA_013676235.1`.

The reference is fixed before expression inspection. The same reference has precedent for cross-Camellia transcriptomic analysis and provides a practical common annotation scaffold, but cross-species mapping adequacy must be evaluated rather than assumed.

Before RNA-seq interpretation, the reference-only workflow reports how many preregistered gene families and primary modules can be identified from annotation alone.

## Family assignment

The frozen family mapper searches gene, transcript, CDS product and RNA-FASTA annotations for preregistered names/synonyms of 19 pigment gene families.

All annotation-matched transcript paralogs are retained. Differential expression, petal colour and source-paper candidate status are not used to select family members.

If annotation does not identify enough families for a module, that module remains unscorable rather than being rescued by hand-selecting expected genes.

## Pilot read depth

The workflow uses the first **1,000,000 SRA spots per run** as a deterministic computational pilot.

This is not claimed to be an unbiased random subsample of each library and is not the final effect-size dataset. It is used to test:

1. whether the fixed reference maps the *C. japonica* reads adequately;
2. whether preregistered pigment families receive enough reads for stable family-level quantification;
3. whether the complete candidate-free scoring pipeline executes on real data;
4. which axes are clearly resolvable versus technically underpowered.

Any biological direction from this subsampled pilot must be confirmed at full depth, or by a prespecified depth-sensitivity analysis, before becoming a final manuscript effect.

## Quantification

1. Salmon transcript-level quantification against the fixed transcript reference;
2. technical gate: mapping percentage must be at least 15% for every run in the current pilot contract;
3. sum TPM across all annotation-matched transcripts within each gene family;
4. transform family abundance as `log2(sumTPM + 1)`;
5. z-standardize each gene family within dataset;
6. module score = mean available family z-scores;
7. require at least 50% of predefined families for that module;
8. compute target-minus-source Hedges' g on replicate-level module scores.

The 15% mapping threshold is a technical preregistration, not a biological success criterion. If the cross-species reference fails it, the remedy is to change/reference-test the quantification scaffold transparently, not lower the threshold until the expected result appears.

## Failure interpretation

### Reference annotation fails

If too few preregistered families are identifiable from `GCA_013676235.1`, the annotation scaffold is inadequate. Move to a more defensible orthology/reference strategy before interpreting expression.

### Mapping fails

If one or more Joy Kendrick runs map below the technical threshold, cross-species sequence divergence/reference mismatch is the leading explanation. Do not treat the corresponding module result as a biological null.

### Module completeness fails

If a module has <50% resolved families, report the axis as technically unresolved. Do not infer it from visible red/pink colour.

### Candidate-free direction disagrees with the published candidate narrative

Retain the result. This is a primary reason for the reanalysis and is not a pipeline failure.

### Candidate-free direction agrees

Agreement is evidence that the reported direction survives candidate-gene selection, but one within-genotype system is not an independent macroevolutionary replicate.

## Promotion to final analysis

The pilot becomes manuscript-grade for this biological system only after:

1. reference/family identifiability is defensible;
2. all six run labels pass provenance checks;
3. full-depth or prespecified depth-sensitivity quantification confirms the pilot conclusion;
4. effect directions are frozen without expected-direction assertions;
5. the result is subsequently collapsed with other `CJAPONICA` systems at the dependence-cluster level for cross-system inference.
