# Candidate-free RNA-seq run admission status v0.1

## Current boundary

All five short-timescale dependence clusters now have a public NCBI SRA route or an already frozen NCBI run manifest. The active bottleneck is no longer discovery of raw data; it is exact run-to-condition mapping plus reference/ortholog harmonization.

## Cluster status

### `CSIN_WHITE_PINK`

- accessions: `PRJNA597123`, `PRJNA597289`
- status: frozen run-level manifest already available
- design: pink versus white flowers across five matched developmental stages, three replicates per stage
- immediate role: candidate-free A/F/C/P module scoring with stage blocking

### `CJAPONICA`

- accessions: `PRJNA757193`, `PRJNA913600`
- status: frozen NCBI run-level manifests already available
- design: bud-sport colour series plus within-genotype red/pink petal sectors
- caveat: three control samples in the bud-sport dataset remain colour-unresolved and must remain excluded from colour-state contrasts unless provenance is recovered

### `CNITIDISSIMA`

- primary accession: `SRP112181`
- status: frozen 15-run developmental manifest already available
- secondary accession: `PRJNA909942`
- role: yellow-development multi-axis rescue; secondary dataset remains in the same dependence cluster rather than becoming a new evolutionary replicate

### `CRETICULATA`

- public raw runs: `SRR24413180` through `SRR24413206` (27 runs)
- GEO analysis accession: `GSE236364`
- published design: three cultivars (`MN`, `SZT`, `TZM`) across developmental contrasts, with three RNA-seq replicates per time point / region; mixed `MN` includes separately sampled red and white full-bloom regions
- status: exact run identities are known, but the run-to-condition mapping has not yet been frozen locally
- immediate role: highest-value within-genotype rescue of currently unresolved F/C axes
- rule: do not infer condition from SRR accession order

### `CPERPETUA`

- BioProject: `PRJNA981682`
- published design: 15 RNA-seq samples = five developmental stages x three biological replicates
- stages: young bud (`S1`), early bud (`S2`), yellowing (`S3`), expansion (`S4`), blooming (`S5`)
- sequencing: paired-end 150 bp Illumina; source study mapped to the *C. sinensis* reference genome `GCA_013676235.1`
- status: BioProject and complete experimental design are confirmed; exact run-to-stage mapping remains to be frozen
- immediate role: highest information-gain independent cluster because A/C/P are unresolved in the literature-coded micro matrix

## Consequence

The candidate-free test can now be treated as a harmonization problem rather than a literature-search problem. No additional mechanistic study discovery is required before attempting the predefined module reanalysis.

The strict execution order is:

1. quantify/validate modules in the already frozen `CSIN_WHITE_PINK`, `CJAPONICA`, and `CNITIDISSIMA` manifests;
2. freeze the `CRETICULATA` run-to-condition map from archive metadata;
3. freeze the `CPERPETUA` run-to-stage map from archive metadata;
4. apply the same predefined A/F/C/P module scoring to all five dependence clusters;
5. rerun the dependence-collapsed recurrence and ascertainment nulls;
6. only then evaluate the frozen representation on the `PRJNA1136134` external red/yellow/white holdout.
