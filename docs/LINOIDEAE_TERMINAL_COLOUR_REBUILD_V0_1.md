# Linoideae terminal flower-colour rebuild v0.1

## Why rebuild instead of copy

Villalvazo-Hernández et al. 2022 (`10.3390/plants11121579`) state that flower colour was recorded for 112 Linoideae species from herbarium data, systematic/taxonomic studies, regional floras and a database. They explicitly avoided assuming one colour for all species in a genus and coded terminals into yellow, blue, white, purple, red and pink.

However, the published supplement exposes GenBank accessions, divergence-time estimates and phylogenetic/ancestral-state figures, but not a standalone machine-readable 112-tip flower-colour table. Therefore the cross-clade atlas must rebuild the terminal states rather than digitize the authors' reconstructed nodes or copy a painted tree.

## Frozen source universe

The source paper cites eight evidence groups for its 112-species flower-colour coding: references 5, 6, 13, 54, 130, 131, 132 and 133. These are recorded in `data/linoideae_colour_rebuild_sources_v0_1.csv` and define the first-pass source universe.

The rebuild may add a newer taxonomic source only for name resolution or when a cited source is inaccessible/ambiguous. Any added colour evidence must be flagged as `ATLAS_ADDITION` rather than silently substituted for the source-study evidence.

## Row-level coding

One row corresponds to one accepted taxon mapped to one target phylogeny tip.

Allowed visible states for the first pass:
- `YELLOW`
- `BLUE`
- `WHITE`
- `PURPLE`
- `RED`
- `PINK`
- `POLYMORPHIC`
- `UNKNOWN`

Do not use the source paper's composite phrase `yellow-white` as a terminal state unless the underlying species description is genuinely ambiguous between yellow and white. `yellow-white` is an ancestral-node interpretation in the published narrative, whereas terminal tips were described as six discrete categories.

## Evidence hierarchy

Priority for a terminal state:
1. species-level wild description or herbarium-derived description in a cited flora/revision;
2. species-level colour explicitly reported in a systematic study;
3. species-level database description with a frozen access date;
4. figure inspection only as a last-resort QC, never as the sole source when text exists.

Cultivar-only flower colour cannot fill a wild species state.

## Multiple sources

If two independent sources agree, retain one state and list both source IDs.

If sources disagree:
- retain `POLYMORPHIC` only if biological variation is explicitly documented;
- otherwise mark `UNRESOLVED_CONFLICT` and exclude from the strict macro analysis;
- do not choose the source that best matches the published ancestral reconstruction.

## Taxonomy

Historical `Linum` names and segregate genera must be mapped to a pinned accepted taxonomy before modelling. Source names are retained verbatim in `source_taxon_name`; accepted names go in `accepted_taxon`.

## Coverage gate

The first usable rebuilt matrix requires >=80% of the target Linoideae phylogeny tips to have either:
- a resolved colour state;
- documented polymorphism; or
- an explicit `UNKNOWN` row with attempted source recovery.

Coverage is therefore a provenance-completeness criterion, not a demand to impute missing colour.

## Reconstruction gate

Only after the terminal matrix passes coverage/taxonomy checks will ancestral states be re-estimated under the common cross-clade model set. The published S-DIVA/Mesquite result is a comparison target, not the atlas estimator.

This is a substantive original derived-data component of the atlas and remains separate from the frozen Camellia Paper 1.
