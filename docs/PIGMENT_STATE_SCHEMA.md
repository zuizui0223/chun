# Pigment-state schema

## Purpose

Visible flower colour is not a biochemical state. The project therefore stores phenotype and pigment evidence separately and derives transition states only when chemistry or sufficiently strong molecular evidence exists.

## Visible phenotype layer

Allowed coarse states:

- `white`
- `pink_red_purple`
- `yellow`
- `mixed_or_other`
- `unknown`

Visible colour can be entered from a taxonomic treatment or study photograph, but it must never by itself create a pigment-mechanism claim.

## Independent pigment axes

### Anthocyanin axis

- `detected`
- `low_or_suppressed`
- `not_detected`
- `inferred_only`
- `unknown`

### Flavonol / yellow-flavonoid axis

- `high`
- `detected`
- `low_or_not_detected`
- `unknown`

### Carotenoid axis

- `detected`
- `low_or_not_detected`
- `unknown`

The carotenoid axis is mandatory because *Camellia nitidissima* golden-yellow petals contain both carotenoids and flavonol glycosides. A yellow phenotype therefore cannot be represented faithfully by a single `flavonol-yellow` variable.

## Derived profiles

Derived profiles are convenience labels, not raw observations:

- `A` — anthocyanin-supported
- `F` — flavonol-supported yellow deployment
- `C` — carotenoid-supported yellow deployment
- `F+C` — both flavonol and carotenoid contribution supported
- `A+F`, `A+C`, `A+F+C` — mixed deployment where supported
- `W` — low-pigment/white only when chemistry supports the absence or very low deployment of the focal pigment classes
- `U` — unresolved

A visible white flower with no chemistry is `U`, not `W`.

## Evidence levels

### E0 — visual/taxonomic phenotype only
No pigment mechanism can be assigned.

### E1 — chemistry or expression association
Pigment/metabolite or expression evidence exists, but causal regulation is not demonstrated.

### E2 — functional mechanism
Perturbation, transient expression, enzyme assay, or equivalent evidence supports a pathway mechanism.

### E3 — evolutionary mechanism
Functional evidence is connected to a phylogenetically supported transition on an independently justified species-tree history.

Only E3 can support a strong evolutionary `reactivation` claim.

## Reactivation vocabulary gate

- `retention`: coloured state is ancestrally continuous.
- `recruitment/gain`: pigment deployment appears after a reconstructed low/absent state, but prior activity and latent retention are not demonstrated.
- `reactivation`: active ancestral deployment -> suppressed/absent floral deployment -> active descendant deployment **plus** evidence that underlying pathway capacity persisted through the suppressed interval.

## Consequence for transition models

The first phylogenetic analyses should be run twice:

1. **visible-colour model** for broad taxonomic coverage;
2. **pigment-profile model** restricted to taxa with biochemical evidence.

If the two histories disagree, the pigment-profile result has mechanistic priority while the visible-colour reconstruction is retained as a broader phenotype analysis.

Do not fit an ordered white -> yellow -> red axis.