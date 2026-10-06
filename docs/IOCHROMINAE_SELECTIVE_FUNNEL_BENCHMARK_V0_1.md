# Iochrominae selective-funnel benchmark v0.1

## Current advance

Iochrominae is promoted from a generic coloured-ancestor control to the first **direct cross-timescale benchmark** for the atlas.

The reason is not its ancestral blue/delphinidin state. It is that the same clade has data at three nested scales:

1. segregating acyanic morphs within normally pigmented species;
2. fixed white/yellow species;
3. reconstructed macroevolutionary pigment transitions across the clade.

The linked molecular measurements include floral flavonoid chemistry and anthocyanin-pathway gene expression.

## Published seed rows

Larter et al. 2019 (`10.1002/dvdy.82`) reports six polymorphic species. The estimated acyanic morph frequencies range from **0.9% to 57%**, with molecular sampling of both pigmented and acyanic morphs. One acyanic morph is yellow rather than white (*I. parvifolium*), so the atlas keeps visible state distinct from anthocyanin absence.

These six summary rows are now encoded as a published-table seed. They are not substitutes for the individual-level Dryad rows.

## Raw-data source

Dryad `10.5061/dryad.p5dq84v` exposes:

- `Larter et al 2019 Dvdy Iochrominae development evolution DATA.rar` (~3.05 MB);
- a README (~4.07 KB).

The archive is remotely verified but not yet ingested in the active runtime. No checksum is exposed in the indexed metadata, so none is invented.

An optional sequence-level companion exists at Dryad `10.5061/dryad.49rs8` for Chi/F3h/Dfr alignments from 22 Iochrominae species.

## Benchmark to reproduce

The atlas must independently reconstruct the published qualitative scale contrast from row-level observations:

- white/yellow morphs and fixed white species both lack colourful anthocyanins;
- fixed white species occupy a characteristic low downstream-expression state (especially DFR/ANS);
- acyanic morphs generally remain closer in expression space to their pigmented conspecifics than to fixed white species.

The group labels may be used as biological-scale metadata, but the published conclusion may not be used to alter feature selection, normalization, or molecular-target coding.

## Why this matters

This is an empirical warning against treating present polymorphism as a literal snapshot of the mechanism that will later become fixed. A visible endpoint can be accessible through a broad short-timescale mechanism space while long-term lineage-level differences occupy a narrower developmental route.

The atlas will test whether this contraction generalizes across clades, not whether Iochrominae itself shows it—the latter is already established prior art.

## Next gate

1. ingest the Dryad archive and README;
2. inventory every table/script/file and compute local checksums;
3. normalize individual rows into `taxon × morph × display organ × biochemical state × molecular module × provenance`;
4. reproduce published morph-frequency and sample-count metadata;
5. reconstruct a blind scale classifier/contrast using frozen expression and flavonoid variables;
6. only after reproduction, compare funnel metrics with other clades.

Paper 1 remains unchanged and closed.
