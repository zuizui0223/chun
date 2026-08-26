# Repository scope and project handoff

## Active boundary

`chun` owns the *Camellia* micro-to-macro programme:

1. pigment-state and pathway accessibility at developmental, within-lineage and comparative scales;
2. sequence-aware orthology/paralog resolution;
3. accepted-taxonomy and wild-colour macro patterns;
4. the identifiability boundary between molecular accessibility, transition realization and ecological persistence.

East Asian *Cirsium* phylogenomics, flower-colour history, population structure and molecular mechanism are outside this repository's active scope and belong to [EAzami](https://github.com/zuizui0223/EAzami).

## Why Cirsium appeared here

The repository was expanded on 2026-08-16 as a cross-family scaffold: *Cirsium* supplied a phylogenetically informative but mechanism-poor contrast, while *Camellia* supplied stronger experimental pigment-pathway evidence. That comparison was useful for generating hypotheses, but it duplicated EAzami's established Cirsium Aim 3/4 scope and obscured ownership.

## Handoff rule

- No Cirsium accession, sample manifest, topology constraint, phenotype matrix row, validator or CI gate is an active `chun` input.
- Stable Cirsium results should be developed and frozen in EAzami.
- Any future cross-family synthesis must consume versioned outputs from `chun` and EAzami rather than maintaining a second Cirsium analysis inside `chun`.
- The removed comparative scaffold remains recoverable from Git history; no scientific provenance was rewritten or silently reassigned.
