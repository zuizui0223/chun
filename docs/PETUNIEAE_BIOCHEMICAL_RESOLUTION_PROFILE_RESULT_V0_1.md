# Petunieae biochemical resolution profile result v0.1

## Terminal class

`PROFILE_SIGNALLED_FINE`

This is a standardized retrospective cross-representation training result. It is **not** a new prospective replication because the underlying OSF source values had already been inspected for a different cross-level estimand before this resolution-profile analysis was frozen.

## Frozen provenance

The biochemical profile estimand was frozen in main before profile AUC computation. A pre-AUC source-key erratum then corrected only the literal source outgroup key from the descriptive label `BROWALLIA_AMERICANA_BROW` to the audited processed-data key `BROW`; no biological state, threshold, estimator, permutation rule or decision rule changed.

Hosted terminal execution:
- workflow run `34845624684`
- job `103980743277`
- artifact `10347352800`
- artifact digest `sha256:adda5a9b9e53412c6fe37745158a2a710ee9aa5dc2f7b757e7fff5ff8d7b5856`
- source transport on the successful run: `live_osf`
- all frozen inner source hashes reverified before analysis

Frozen source hashes:
- processed HPLC/expression table: `5843d4cd4eb253046f97349fa6bd285ca77e43e7a9c3aaa0e78fae3e8e391edd`
- dated tree: `95b4a688d3d71417b712b37a2b04cdc22a9431be3172d6509def4435f5fd8614`

## Primary frame

The source contains 60 rows including the source-defined `BROW` outgroup. After excluding `BROW`, 59 Petunieae taxa remain. Applying the frozen rare fine-state rule (<5 tips) leaves 47 eligible tips.

On that common frame:
- coarse states: 6 absent / 41 present;
- intermediate states: 6 `000` / 41 `001`;
- fine retained six-bit patterns: `000000` (6), `000010` (6), `000011` (6), `000100` (10), `000110` (6), `000111` (13).

The coarse and intermediate partitions therefore collapse to the same binary partition on the retained frame. This is a source/data property, not a post-hoc recoding.

## Result

Using negative patristic distance to predict same-state pairs, the frozen rank-based ROC AUC estimator, 9,999 joint triplet permutations and seed `20260913`:

- coarse AUC = `0.518925563507132`, one-sided signal p = `0.1985`;
- intermediate AUC = `0.518925563507132`, one-sided signal p = `0.1985`;
- fine AUC = `0.6995630849367751`, one-sided signal p = `0.0001`.

Fine minus runner-up = `0.18063752142964307`; joint-permutation p = `0.0001`.

The frozen decision rule therefore returns `PROFILE_SIGNALLED_FINE`.

## Interpretation boundary

This result supports a specific statement: within this Petunieae biochemical state space, exact six-compound composition carries substantially stronger phylogenetic same-state structure than presence alone or the three-class presence representation on the retained common frame.

Do not relabel this as a prospective replication. Do not use it to infer universal superiority of fine resolution, universal causal genes, common ecological drivers, or a universal biochemical hierarchy. It is one additional standardized training radiation showing that the informative resolution can differ from the intermediate optimum originally hypothesized.

Camellia Paper 1 science remains unchanged.
