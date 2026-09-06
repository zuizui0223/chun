# Epimedium CRA014550 ingestion — v0.1

## Purpose

Freeze the expected biological design and source identity **before** reading deposited run-level outcomes or expression values.

The primary source is Xu et al. 2024 (`10.1186/s12870-024-05480-z`), which assigns the cross-species colour RNA-seq experiment to GSA accession `CRA014550` and maps reads to the chromosome-level *Epimedium pubescens* reference genome `GWHBECS00000000`.

## Expected biological design from the paper

Primary flower state groups:

### Petals
- *E. pseudowushanense* — magenta;
- *E. acuminatum* — magenta;
- *E. jinchengshanense* — yellow;
- *E. baojingense* — green.

### Sepals
- *E. hunanense* — red;
- *E. baojingense* — green;
- *E. acuminatum* — white.

Secondary non-floral context:
- *E. pubescens* green leaf;
- *E. pubescens* magenta leaf.

The Methods report three biological replicates per state, each biological replicate pooled from three individuals. Therefore the pre-ingestion expectation is:

- `7 flower groups × 3 biological replicates = 21` flower biological libraries;
- `2 leaf groups × 3 biological replicates = 6` secondary leaf biological libraries.

These are **design expectations**, not assertions about the number of deposited GSA runs. The deposited metadata must be reconciled to this expectation before any expression analysis is admitted.

## Fail-closed metadata rule

`data/epimedium_cra014550_sample_manifest_template_v0_1.csv` deliberately contains only a header. No run accession, sample accession, FASTQ filename or checksum is invented from publication order or figure labels.

A real run enters the analysis only after all of the following are verified from repository metadata or downloaded files:

1. run/sample accession;
2. species identity;
3. organ identity;
4. visible-state group;
5. biological replicate mapping;
6. raw filename(s);
7. checksum where supplied, or a locally computed checksum after download;
8. mapping to one and only one frozen biological group.

If deposited metadata cannot reconcile the 21-flower-library design, the discrepancy is recorded and the affected group remains unresolved. We do not repair missing libraries by duplicating runs, guessing accession order or borrowing leaf samples.

## Reference contract

Primary common reference:
- species: *Epimedium pubescens*;
- Genome Warehouse: `GWHBECS00000000`;
- source genome project: `PRJCA006303`;
- corresponding NCBI raw-support project: `PRJNA747870`.

Reference and annotation versions must be pinned before expression inspection. Module completeness is evaluated before any direction or state-similarity result is used.

## Primary analysis boundary

The primary estimator uses flower samples only and keeps PETAL and SEPAL separate.

The planned functional modules are frozen in `data/epimedium_second_anchor_module_contract_v0_2.csv`:
- phenylpropanoid gateway;
- anthocyanin core;
- flavonol competition;
- prespecified secondary regulatory/diversion modules if annotation completeness passes.

Visible yellow and green remain `CHEMISTRY_UNRESOLVED` unless direct chemical evidence supports a typed pigment mechanism. Visible state never fills a missing molecular module.

## What CRA014550 can test

After successful ingestion and standardized remeasurement, this resource can test:

1. organ-specific multivariate molecular states across red/magenta/yellow/green/white displays;
2. whether the two magenta petal taxa occupy similar molecular states under one outcome-independent measurement rule;
3. whether candidate-selected PAL/DFR/ANS framing overstates or understates whole-state similarity relative to the standardized module space.

It **cannot**, by itself, identify independent historical transition branches. Cross-sectional species differences remain current-state contrasts until a separate event-identifiability gate is passed.

## Claim ceiling

Until real GSA metadata and raw binaries are ingested:
- `CRA014550` is `REMOTE_VERIFIED_NOT_INGESTED`;
- expected library counts are design expectations only;
- no standardized expression result exists;
- no historical transition vector is inferred;
- no cross-clade generality claim is promoted.

Camellia Paper 1 remains unchanged and scientifically closed.
