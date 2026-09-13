# Gesnerioideae source-access resolution — v0.2

## Decision

**`HOLD_SOURCE_ACCESS` is resolved. `HOLD_SCHEMA_SOURCE_AXES_NOT_NESTED` remains terminal.**

On 2026-09-13 the exact Dryad tree bytes were supplied externally and checked against the source manifest frozen before outcome inspection.

Verified object:

- canonical Dryad filename: `Gesne_Ago8_simple_combined_CA.tre`;
- Dryad DOI: `10.5061/dryad.m7589`;
- file id: `72407`;
- expected and observed size: `668933` bytes;
- expected and observed MD5: `94d6f267f5c123d6d875170da1783ffa`;
- observed SHA256: `0aac94ddfad56cff759eb0352aeaebb61b5bd4ebb60fa8c0db857b7f93ab0d50`;
- NEXUS declaration: `ntax=595`.

Machine-readable receipt: `data/gesnerioideae_source_access_resolution_receipt_v0_2.json`.

## Why the fifth-radiation analysis does not reopen

The source-access failure was only one gate. Before row-level outcome ingestion, the independent source-schema gate had already terminated the frozen same-estimand analysis as:

`HOLD_SCHEMA_SOURCE_AXES_NOT_NESTED`

The source defines pigment chemistry and visible/reflectance colour as cross-cutting biological dimensions, not as nested refinements of one state ladder. The preregistered test explicitly required a nested coarse → intermediate → fine representation without outcome-dependent recoding.

Therefore access to the correct phylogeny cannot authorize a later rescue hierarchy. Doing so would change the estimand after the schema conflict was known.

## Firewall status

At closure:

- exact phylogeny bytes: **verified**;
- source-access hold: **cleared**;
- row-level phenotype outcome values opened for this test: **no**;
- profile AUCs computed: **no**;
- 9,999-permutation test run: **no**;
- resolution winner computed: **no**;
- fifth-radiation biological verdict: **none**.

Gesnerioideae remains a **pre-outcome schema HOLD**, not a negative replication.

## Cross-radiation consequence

The prospective record now contains two distinct boundary results that must not be collapsed:

1. **Iris:** a valid same-estimand prospective test that falsified the universal `coarse < intermediate > fine` ordering.
2. **Gesnerioideae:** a pre-outcome demonstration that some flower-colour datasets do not admit one common nested resolution ladder because pigment chemistry and visible colour are different phenotype dimensions.

The stronger programme-level statement is therefore not an intermediate-resolution optimum. It is that phylogenetic predictability depends on **which phenotype dimension is represented and how its state space is defined**; a single universal visible-colour/pigment hierarchy is unsupported.

Camellia Paper 1 remains unchanged.
