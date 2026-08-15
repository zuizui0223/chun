# Range-tail provenance and estimator uncertainty before macroevolutionary boundary inference

## Current position

The initial Tuberculatae cold-edge candidate did not survive record-level audit. Extending the audit to the whole exact 50-species Fan2026 × GBIF × CHELSA matrix exposed a broader problem than a single outlier:

> **An occurrence-derived climatic boundary is not an error-free species trait. It is an inferred observation whose value depends on taxonomic/georeferencing provenance, sample size and the lower-tail estimator.**

The required analysis hierarchy is now:

`occurrence provenance -> estimator reliability -> boundary uncertainty -> latent pigment/sensory state -> primary nuclear branch history -> ecological lead/lag`

This layer must be resolved before asking whether pigment deployment preceded, followed or enabled a climatic boundary shift.

## 1. Tuberculatae false cold edge

The original exact matrix contained:

- *Camellia rhytidocarpa*: `n=18`, BIO6 q05 `-14.105 C`;
- *C. tuberculata*: `n=12`, BIO6 q05 `-16.415 C`.

Both taxa contained the same extreme coordinates:

| taxon | GBIF key | basis | latitude | longitude | BIO6 |
|---|---:|---|---:|---:|---:|
| *C. rhytidocarpa* | 4044189601 | preserved specimen | 42.900000 | 125.140000 | -20.65 C |
| *C. rhytidocarpa* | 2250665548 | material sample | 38.073254 | 104.691140 | -12.95 C |
| *C. tuberculata* | 4043637661 | preserved specimen | 42.900000 | 125.140000 | -20.65 C |
| *C. tuberculata* | 2250664859 | material sample | 38.073254 | 104.691140 | -12.95 C |

The `42.9 N` records are internally inconsistent with their GBIF `stateProvince=Guizhou` metadata. The `38.073254 N, 104.691140 E` records are GenBank-mined material samples and the corresponding BOLD records identify the coordinate as a **country-centroid** georeference.

Removing only those four record instances changes q05 by:

- *C. rhytidocarpa*: `-14.105 -> +1.425 C` (`+15.53 C`);
- *C. tuberculata*: `-16.415 -> +0.400 C` (`+16.815 C`).

The former section-level cold-tail result disappears. The current Tuberculatae `H_EDGE_EPISODIC` candidate is rejected as biological evidence.

## 2. Provenance contamination is genus-dataset scale, not a single-species exception

The exact 50-species matrix contains 1842 climate points before the new explicit provenance exclusions.

The record ledger `data/camellia_tail_provenance_flags_v0_1.csv` separates three sensitivity classes.

### S1 — documented nonlocal/generic records

- `38.073254, 104.691140` occurs in **27 exact Camellia taxa** and is explicitly documented in BOLD as a country-centroid coordinate;
- `36.519977, 103.891767` occurs in four exact taxa and is associated with an NHM area-polygon georeferencing protocol rather than a precise collecting locality;
- the two Tuberculatae `42.9, 125.14` records have internal administrative-coordinate conflict.

### S2 — generic China-centre proxy sensitivity

- `35.86, 104.20` occurs in five exact taxa from the same institution without locality detail. It is treated as a declared generic-centre **sensitivity flag**, not as a proven error class.

### S3 — seven hard cold-edge conflicts

Seven additional records in *C. saluenensis, C. semiserrata, C. cordifolia, C. subintegra, C. sinensis, C. cuspidata,* and *C. chekiangoleosa* conflict with administrative metadata and/or strong current native-range evidence and are removed only in the strongest declared sensitivity.

Raw GBIF-derived points remain unchanged; exclusions are always traceable to the versioned ledger.

## 3. Staged provenance sensitivity reverses apparent lower-tail significance

`data/camellia_tail_provenance_scenario_tests_v0_1.csv` applies the exclusion stages cumulatively.

- **S0 original:** q05 A-W `-0.638 C`, `P=0.696`; q01 `-2.568 C`, `P=0.212`; min `-2.886 C`, `P=0.223`.
- **S1 documented nonlocal removed:** q05 `-1.553 C`, `P=0.116`; q01 `-3.831 C`, `P=0.0165`; min `-4.595 C`, `P=0.0507`.
- **S2 generic-centre proxy also removed:** q05 `-1.484 C`, `P=0.125`; q01 `-4.100 C`, `P=0.00622`; min `-4.865 C`, `P=0.0352`.
- **S3 additional hard conflicts removed:** q05 `-0.484 C`, `P=0.553`; q01 `-1.326 C`, `P=0.227`; min `-1.547 C`, `P=0.308`; median `-0.583 C`, `P=0.509`.

The deepest lower-tail tests become significant only at intermediate cleaning stages and return to null when additional clearly problematic cold records are removed.

**Interpretation:** the transient significance is a sensitivity result, not evidence that A/red lineages have a colder evolutionary boundary.

## 4. H_TAIL_PROVENANCE — supported at genus-dataset scale

> **Occurrence provenance can dominate the inferred lower climatic boundary and can change both effect size and statistical significance.**

The Tuberculatae example alone moved q05 by `15.53–16.82 C`, while the wider staged audit shows the same issue changes genus-level A-W tail inference.

A country-only native filter and ordinary GBIF geospatial flags are therefore insufficient for narrow-ranged *Camellia* boundary inference.

## 5. H_TAIL_ESTIMATOR — q05 uncertainty is sample-size dependent

Even after the S3 provenance screen, q05 remains unstable for low-n species.

Across 50 taxa:

- Spearman correlation between retained `n_points` and maximum absolute leave-one-record-out q05 change: `rho=-0.52047`, `P=0.0001069`.

Maximum leave-one-record-out q05 change by n-bin:

| retained n | species | median max change | mean max change | 90th percentile |
|---|---:|---:|---:|---:|
| 5–9 | 10 | 0.610 C | 0.994 C | 2.241 C |
| 10–19 | 13 | 0.670 C | 1.151 C | 2.249 C |
| >=20 | 27 | 0.285 C | 0.351 C | 0.707 C |

The worst S3-cleaned example, *C. confusa* (`n=10`), moves by as much as `4.96 C` after one point is removed.

Thus q05 should be represented as an uncertain observation, not as an exact branch trait.

## 6. Equalizing occurrence n does not recover a robust A-W cold-edge effect

Among the 27 A/W species with at least 20 S3-cleaned points (A=11, W=16), 20 points/species were sampled without replacement for 5000 replicates.

- q05: mean A-W `-0.535 C`, 95% resampling interval `[-1.438, +0.292]`;
- lower-20%-mean: `-0.566 C`, interval `[-1.398, +0.254]`;
- min: `-0.695 C`, interval `[-2.742, +1.430]`.

The direction is often A-lower, but every interval crosses zero. Current data do not establish a robust visible-A cold-boundary expansion.

## 7. H_BOUNDARY_ASCERTAINMENT — hard quality gates solve one problem and create another

Two **diagnostic, non-final** admission tiers quantify the tradeoff.

### provisional minimum gate

`n >= 20` and `max |LOO q05 change| <= 1 C`

- A: `10/14` pass;
- W: `16/34` pass;
- Y: `0/2` pass;
- total: **26/50**.

Within admitted A/W taxa, q05 A-W is `-0.156 C`, `P=0.879`.

### provisional strong gate

`n >= 40` and `max |LOO q05 change| <= 0.5 C`

- A: `6/14` pass;
- W: `11/34` pass;
- Y: `0/2` pass;
- total: **17/50**.

Within admitted A/W taxa, q05 A-W is `-0.703 C`, `P=0.591`.

These thresholds are not proposed as universal ecological standards. They expose the structural problem:

> **Complete-case quality filtering can remove roughly half the taxa and all currently climate-admitted yellow species, so the supposedly high-quality branch dataset can become selected by data availability, lineage and trait state.**

Therefore uncertainty-weighting/missingness modelling is preferable to simply discarding every unstable boundary.

## 8. Boundary observation model required before phylogenetic lead/lag

The primary macroevolutionary analysis should separate three layers.

### Layer A — occurrence provenance

1. accepted name/taxon confidence;
2. dataset/institution/catalogue provenance;
3. collecting locality versus centroid/polygon/geocoded proxy;
4. independent native-range plausibility;
5. cross-taxon coordinate reuse;
6. administrative-coordinate consistency.

### Layer B — estimator reliability

1. number of retained spatially thinned points;
2. q05/q01/min/lower-tail alternatives;
3. leave-one-record and leave-one-locality leverage;
4. equal-n resampling/bootstrap uncertainty;
5. support by multiple localities/collections.

### Layer C — macroevolutionary observation uncertainty

Instead of a binary `edge=observed/not observed` complete-case table, the branch model should receive:

- boundary estimate;
- uncertainty interval or reliability weight;
- provenance status;
- missingness/admission probability.

Only then should pigment-first, niche-first, pollinator-first or synchronous histories be compared.

## 9. Consequence for the flower-colour problem

The current macro question is no longer simply:

> `Does red colour correlate with colder occurrence values?`

It becomes:

> **When a validated ecological boundary shift occurs, did an accessible latent pigment/sensory state change before it, after it, or independently—and how certain are we that both events were actually observed?**

That formulation connects molecular accessibility to genuine evolutionary events without allowing occurrence artefacts or unstable quantiles to define those events.

## 10. Claim boundary

Supported now:

- the Tuberculatae cold-edge candidate is artefactual/provenance-sensitive;
- provenance problems occur across the genus-scale occurrence matrix;
- lower-tail estimates have strong sample-size-dependent instability;
- staged record cleaning can generate and erase apparent colour-state significance;
- after the strongest current provenance screen and sample-size sensitivities, no robust A-W cold-edge difference remains;
- hard quality filtering sharply reduces taxon coverage and creates an ascertainment problem that must be modelled.

Not yet supported:

- a final universal threshold for accepting a range boundary;
- that every S3-retained point is correct;
- a complete probability model for provenance/error/missingness;
- a validated *Camellia* branch on which pigment deployment demonstrably precedes a true climatic boundary shift.

## 11. Reproducible assets

- `data/camellia_tail_provenance_flags_v0_1.csv`
- `data/camellia_tail_provenance_scenario_tests_v0_1.csv`
- `data/camellia_tail_sample_size_sensitivity_v0_1.csv`
- `data/camellia_q05_estimator_stability_summary_v0_1.csv`
- `data/camellia_boundary_admission_tiers_v0_1.csv`
- `data/camellia_boundary_admission_summary_v0_1.csv`
- `data/camellia_fixed_n20_tail_resampling_v0_1.csv`
- `scripts/audit_gbif_tail_provenance.py`
- `scripts/analyze_tail_provenance_sensitivity.py`

The Fan2026 GBIF × CHELSA workflow runs both point-level provenance audit and staged provenance/estimator sensitivity and retains outputs as workflow artifacts.
