# Linoideae target coverage contract v0.2

## Purpose

The row-level Linoideae rebuild must use the phylogenetic sampling frame, not only the subset for which the source paper reported flower colour.

Villalvazo-Hernández et al. 2022 (`10.3390/plants11121579`) report:

- 451 accessions representing **113 Linoideae species** in the phylogenetic analysis;
- flower colour recorded for **112 Linoideae species**;
- three outgroups outside the Linoideae colour denominator;
- six terminal flower-colour categories: yellow, blue, white, purple, red and pink.

Thus the source study itself implies one Linoideae target tip without a reported terminal colour state.

## Frozen denominator

`target Linoideae tips = 113`

The atlas creates one terminal-trait row for every target tip. The source-study colour subset is not allowed to redefine the denominator to 112.

Expected source-study colour coverage is therefore:

`112 / 113 = 0.9911504425`

The missing source-study tip remains an explicit `UNKNOWN` row after attempted recovery. It is not silently deleted and is not imputed from genus, section, neighbour state or published ancestral reconstruction.

## Coverage gate

The existing atlas provenance-completeness threshold remains 0.80.

For 113 target tips this means at least:

`ceil(113 × 0.80) = 91`

rows must contain a resolved state, documented polymorphism, or an explicit attempted-but-unresolved `UNKNOWN` state with provenance.

This is a documentation/attempt-coverage gate, not a requirement to invent colour for unresolved species.

## Outgroups

The three source-study outgroups are:

- *Hugonia busseana*;
- *Phyllanthus emblica*;
- *Ixonanthes chinensis*.

They may remain in the phylogenetic source bundle where needed for rooting, but they are excluded from the 113-tip Linoideae terminal-colour denominator and from white-baseline transition counts.

## Next ingestion gate

1. recover the exact 113 Linoideae tip names from the supplementary accession table/tree;
2. instantiate 113 rows in the rebuild matrix before assigning colour;
3. reconcile the source paper's 112 recorded colours against those 113 tips;
4. identify the single source-study uncoloured tip explicitly;
5. fill terminal states only from the frozen source universe or flagged `ATLAS_ADDITION` evidence;
6. run taxonomy/provenance validators before any ancestral-state reconstruction.

## Boundary

This is post-Paper-1 atlas work. It does not change Camellia Paper 1 science, framing or AJB v1.0.
