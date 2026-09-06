# White-baseline atlas normalized ingestion — v0.3

## Current advance

The atlas no longer treats `flower colour` as one universal scalar. The first real source audit shows that homologous-looking visible states can be attached to different floral display organs and different pigment systems. The normalized observation unit is therefore:

`taxon × floral display organ × visible/pigment state × provenance`

rather than `taxon × one colour label`.

This is a direct generalization of the observation-regime lesson from Camellia Paper 1.

## Why organ typing is necessary

### Epimedium

The reproductive dataset in Zhang et al. 2023 (`10.3389/fpls.2023.1234148`) contains 699 individuals from 41 species plus one unknown taxon. It explicitly separates:

- inner sepal colour: white / yellow / red / purple;
- petal/spur colour: white / yellow / red / purple / brown.

These cannot be collapsed to one hue. A species may combine differently coloured floral organs; the article itself describes *E. davidii* as having red inner sepals and yellow petals. The atlas therefore freezes two separate Epimedium display-organ rows.

### Hydrangea sect. Cornidia

The showy floral colour state is associated with display sepals rather than being silently treated as a petal state. The atlas records the organ as `FLORAL_DISPLAY_SEPAL`.

### Antirrhineae / Iochrominae / Linoideae

Their main comparative colour unit is closer to corolla/perianth pigmentation, but the source organ is still explicit in the contract so that future cross-clade models can test organ-homologous and display-function-homologous subsets separately.

## Polymorphism rule

Current polymorphism must never be converted to a majority colour before the temporal analysis.

- taxon-level source polymorphism remains `POLYMORPHIC` or a multistate observation;
- individual-level data are retained through an individual-to-taxon aggregation layer;
- within-population coexistence, among-population differentiation and uncertain taxonomic alternatives remain distinct provenance classes;
- a pooled macro state is created only under a prespecified sensitivity rule.

This preserves the future connection between the `fcp` spatial arm and the `chun` temporal arm.

## First extraction-ready systems

### Antirrhineae

The ISTA object `10.15479/AT:ISTA:34` is CC0 and exposes the archive `IST-2016-34-v1+1_tellis_flower_colour_data.zip` (4.47 MB; MD5 `950f85b80427d357bfeff09608ba02e9`). It contains flower-colour data and NEXUS phylogeny files. This is the cleanest first machine-readable ingestion.

### Epimedium sect. Diphyllon

The open supplement contains a 699-individual reproductive morphometric dataset (Supplementary Table S4), and the published phylogenomic analysis provides the taxon/tree framework. The extraction must preserve individual variation and the two display-organ colour axes.

## Rebuild systems

### Linoideae

The terminal 112-species colour matrix must be reconstructed with row-level provenance because a standalone source table has not been recovered. This becomes a primary original derived-data component.

### Hydrangea sect. Cornidia

Wild display-sepal colour states must likewise be rebuilt from article/field/taxonomic evidence before a common transition model is fitted.

## Cross-clade state hierarchy

The normalized trait table keeps visible states and molecular functions separate.

Visible/display layer:
- organ-typed colour state;
- polymorphism status;
- wild/cultivar status;
- provenance and uncertainty.

Functional molecular layer (later phase):
- `ANTHOCYANIN_DEPLOYMENT`;
- `COPIGMENT_FLAVONOL`;
- `YELLOW_PIGMENT` with typed chemistry;
- `SHARED_FLUX_DIVERSION`;
- `REGULATORY_STATE`;
- `SENSORY_STATE` where available.

A visible yellow observation does not automatically imply carotenoid deployment; a white display organ does not imply absence of pigment machinery.

## Gate after v0.3

`pooled_analysis` remains blocked until real normalized rows exist.

The next finite gate is:
1. ingest Antirrhineae into the common schema;
2. extract Epimedium individual-level colour rows and produce species-level uncertainty-preserving summaries;
3. rebuild at least one of Linoideae or Hydrangea to >=80% of the target phylogeny tips, counting explicit unresolved rows in the denominator;
4. run identical taxonomy/provenance/organ validators;
5. only then fit cross-clade transition models.

Paper 1 remains unchanged and closed.
