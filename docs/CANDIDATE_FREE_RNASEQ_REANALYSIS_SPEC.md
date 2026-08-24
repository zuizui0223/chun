# Candidate-free public RNA-seq reanalysis — preregistered specification v0.1

## Purpose

The literature-coded micro-accessibility matrix is anthocyanin-heavy and has substantial missingness on F/C/P axes. The next analysis therefore re-quantifies predefined pigment modules from public petal RNA-seq without selecting genes because the source paper nominated them.

## Primary question

After uniform multi-axis quantification, do independent *Camellia* dependence clusters converge on recurrent multivariate pigment-state transitions more strongly than the current literature-coded matrix?

## Fixed module panel

Primary modules are frozen in `data/candidate_free_pigment_module_schema_v0_1.csv` before expression results are inspected.

- A core: CHS, CHI, F3H, F3'H, F3'5'H, DFR, ANS/LDOX, UFGT/3GT;
- F branch: FLS;
- P branch: ANR, LAR;
- C core: PSY, PDS, ZDS, CRTISO, LCYB, LCYE, BCH, ZEP.

MYB/bHLH/WD40/WRKY modules are secondary/exploratory because regulatory orthology and functional direction are less portable across species.

## Raw-data targets

Targets and provider/readiness status are frozen in `data/candidate_free_rnaseq_target_registry_v0_1.csv`.

The fitting set is restricted to short-timescale systems belonging to the five dependence clusters in the micro registry. `PRJNA1136134` is reserved as an external between-species state-classification check and is not used as an independent micro-accessibility edge.

## Quantification rule

For each dataset:

1. resolve run/sample/tissue/colour/stage metadata without guessing unresolved labels;
2. quantify transcripts/genes with one documented pipeline per reference type;
3. assign genes to predefined ortholog families independently of source-paper candidate lists;
4. use log2(TPM + 1) or a count-model-derived normalized expression scale only within dataset;
5. z-standardize each ortholog family within dataset before module aggregation;
6. calculate a sample-level module score as the mean available standardized family values within the frozen module;
7. record module completeness for every sample and dataset.

A module is not scored when fewer than 50% of its predefined gene families are defensibly resolved. Missing families remain missing rather than being imputed from visible colour.

## Within-study contrasts

### Matched developmental colour series

For paired colour genotypes observed at the same developmental stages, estimate the colour-state effect with stage as a blocking factor. Report stage-specific contrasts plus one study-level marginal contrast.

### Within-genotype petal sectors

Use replicate-level red/pink or red/white sector contrasts. These are high-value accessibility tests because deep phylogenetic divergence is absent.

### Ordered cultivar/bud-sport series

Treat colour intensity as an ordered predictor only when ordering is defined independently from the expression outcome. Also report endpoint contrasts.

### Yellow developmental series

Estimate module change across developmental stage and predefine the biologically relevant early-to-golden contrast from source metadata, not from whichever stage maximizes expression separation.

## Effect-size layer

Primary cross-system quantities are within-study standardized module contrasts, not raw TPM differences across studies.

For replicate-based two-state contrasts, use Hedges' g of the sample-level module score when assumptions are adequate. Preserve signed direction on the fixed A/F/C/P axes.

For repeated developmental stages, do not treat stage contrasts as independent studies. Obtain one cluster/study-level contrast through a blocked model or covariance-aware aggregation.

## Dependence handling

Two outputs are mandatory:

1. biological-system level sensitivity;
2. dependence-cluster-collapsed primary analysis.

Repeated *C. japonica*, *C. reticulata* and *C. nitidissima* studies do not become independent macroevolutionary replicates merely because they use different cultivars or experiments.

## Primary validation

After module directions are frozen from raw-data reanalysis:

1. replace literature-coded `unknown` axes only where candidate-free module results resolve direction;
2. rerun the cross-axis recurrence permutation null;
3. rerun the mechanistic-axis ascertainment audit;
4. compare literature-coded and candidate-free transition signatures;
5. activate the mechanistic-state graph only if source and target node states are sufficiently complete.

## External check

Use `PRJNA1136134` only after the micro model is frozen. Ask whether module-state differences learned from short-timescale systems correctly order the red/yellow/white between-species samples on the predicted latent A/F/C/P axes.

This is a held-out evaluation of state representation, not evidence that the three species constitute independent short-timescale transitions.

## Falsification outcomes

The accessibility hypothesis is weakened if any of the following occurs:

- literature directional recurrence disappears under candidate-free quantification;
- F/C/P modules vary as often as A but were simply under-reported;
- dependence-collapsed multivariate recurrence remains null after missing-axis rescue;
- external samples cannot be classified better than null using the frozen latent module representation.

## Claim boundary

Even a positive candidate-free recurrence result does not by itself establish macroevolutionary transition rates. The branch-level micro-to-macro prediction test remains gated on an admitted nuclear phylogeny with defensible wild-species mechanistic states.
