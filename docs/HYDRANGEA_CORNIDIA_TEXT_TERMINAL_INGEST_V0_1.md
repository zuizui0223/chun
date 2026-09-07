# Hydrangea sect. Cornidia source-text terminal recovery v0.1

## Status

This is the first non-template terminal-state recovery for the Hydrangea sect. Cornidia cross-clade falsification system. It is deliberately partial: explicit source-text colour statements are admitted, but no accession-level phylogeny-tip mapping or atlas ancestral-state reconstruction is claimed.

## Source

Primary source: Granados Mendoza et al. 2021, DOI `10.3389/fpls.2021.661522`.

The paper defines the flower-colour character as purple, red or white, referring to sepals of enlarged marginal flowers and petals of reduced flowers. Therefore these rows retain `SOURCE_TYPED_DISPLAY_PERIANTH` rather than silently assigning a single botanical organ across all taxa.

## Explicitly recovered white terminals

### Clade A — 3 taxa

The phylogenetic-results text identifies clade A as containing all sampled Hydrangea serratifolia, two H. seemannii accessions and H. integrifolia. The discussion then explicitly states that these three species have white flowers.

Recovered species-level rows:

- Hydrangea serratifolia
- Hydrangea seemannii
- Hydrangea integrifolia

### Clade I — 7 taxa

The results identify clade I as containing H. tapalapensis, H. sousae, H. steyermarkii, H. breedlovei, H. nahaensis, H. nebulicola and H. otontepecensis. The discussion explicitly states that species within clade I have white flowers and lack enlarged marginal flowers.

Recovered species-level rows:

- Hydrangea tapalapensis
- Hydrangea sousae
- Hydrangea steyermarkii
- Hydrangea breedlovei
- Hydrangea nahaensis
- Hydrangea nebulicola
- Hydrangea otontepecensis

## Admission boundary

All 10 rows are source-backed species-level colour recoveries, but all retain:

- `phylogeny_tip = UNRESOLVED_TO_EXACT_ACCESSION_TIP`;
- `include_macro = 0`;
- unresolved population/polymorphism status.

This prevents a species statement from being projected onto an exact accession tip without evidence. It also prevents partial white-only recovery from biasing an ancestral-state reconstruction.

## Source inconsistency held out

A later discussion sentence describes the majority of Cornidia species as showing a single coloration, parenthetically `red`, despite the paper elsewhere stating that more species exhibit white than red and explicitly identifying white clades A and I. This sentence is therefore not used to mass-code unnamed red terminals. It is retained as a source inconsistency requiring figure/supplement/taxon-level reconciliation.

## Executed result

The frozen validator requires:

- exactly 10 unique recovered taxa;
- exactly 3 clade-A and 7 clade-I taxa;
- all 10 states = WHITE;
- all rows tied to the primary DOI;
- all rows explicit source-text assertions;
- no invented accession-tip mapping;
- zero rows admitted to macro ASR.

Thus `terminal_matrix_status = PARTIAL_SOURCE_RECOVERY`, not `READY`.

## Next empirical gate

Recover the study's full sampled-tip list and terminal flower-colour coding from Supplementary Material/Figure 5 or an equivalent auditable source. Then:

1. reconcile accepted species names to individual accessions/tips;
2. add explicit red, purple, polymorphic and unknown terminals;
3. quantify attempted-tip provenance coverage and require >=80%;
4. only after that set `include_macro=1` for eligible rows and fit the common ER/SYM/ARD model set.

Until that gate passes, the published 3.38 return-to-white / gain-from-white ratio remains a falsification QC target rather than an atlas estimate.

Paper 1 remains unchanged.
