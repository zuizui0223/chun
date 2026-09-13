# Continuous pigment quantity prospective gate — v0.1

## Status

**Frozen before inspection of target-class outcomes in any unused fourth radiation.**

This gate follows the cross-radiation phenotype-dimension correction. The old `PIGMENT_AMOUNT_OR_DEPLETION` category has been split because continuous pigment quantity and discrete pigment loss are different biological traits. Pigment loss already has strong exact-regulator counterexamples, so the next high-information test targets **continuous pigment quantity** only.

## Question

> In an unused independent radiation, does continuous floral pigment quantity map most strongly to an intermediate-resolution **output-control** molecular target family?

The prediction is not an exact-gene law. It is an intermediate-resolution target-class prediction.

## Frozen target classes

- `EARLY_CORE`: CHS, CHI, F3H.
- `BRANCH_COMPOSITION`: F3'H, F3'5'H.
- `LATE_OUTPUT`: DFR, ANS, UFGT/3GT, GST/transport.
- `PATHWAY_REGULATION`: R2R3-MYB, bHLH, WD40.

The predicted family is:

`OUTPUT_CONTROL = LATE_OUTPUT OR PATHWAY_REGULATION`

The competing classes are `EARLY_CORE` and `BRANCH_COMPOSITION`.

This resolution is deliberately intermediate: broader than an exact gene, narrower than a whole pigment programme.

## Calibration context — not validation evidence

Two previously inspected systems motivated the gate:

- Iochrominae: continuous pigment intensity maps to a late-pathway coexpression module;
- Petunieae: the frozen raw total-anthocyanin response does not identify a stable primary molecular subspace, although a source-method log sensitivity favors late output.

These systems are calibration context only and cannot count as the prospective fourth-radiation test.

## Candidate admission

A candidate is admitted only if all conditions are satisfied before project-side target-class outcome fitting.

1. The radiation is unused for this target-class validation and is not one of the already outcome-inspected programme systems listed in the JSON gate.
2. At least **20 matched taxa** have phenotype, molecular data and a branch-length phylogeny.
3. The phenotype is a **continuous numeric total floral pigment quantity**, not an ordinal colour score and not binary pigment presence/absence.
4. There are at least **10 unique phenotype values** and no more than **20% exact zeros**.
5. Molecular data come from flower/petal tissue and cover all four target classes on the same taxa:
   - EARLY_CORE: >=2 genes;
   - BRANCH_COMPOSITION: >=1 gene;
   - LATE_OUTPUT: >=2 genes;
   - PATHWAY_REGULATION: >=2 genes.
6. A branch-length phylogeny and public numeric phenotype/molecular data are available.
7. The project has not inspected/recomputed the decisive target-class association before admission.

Failure of admission is `UNQUALIFIED`, not biological negative evidence.

## Candidate search firewall

At most **20 source publications** may enter the bounded screening universe.

Before admission, screening may use only source identity, radiation, taxon count, tissue, whether continuous pigment quantity exists, whether a molecular matrix and required target classes exist, whether a branch-length tree exists, and whether public numeric data are accessible.

Project-recomputed target-class fits, AICc values and best-target outcomes are forbidden before admission.

If multiple sources pass, selection is deterministic:

1. largest matched taxon count;
2. earliest publication year;
3. lexicographically smallest DOI.

No threshold relaxation is allowed after screening starts.

## Primary phenotype and transformation

Primary response = the source-reported continuous total pigment quantity on the **raw source scale**, z-standardized across matched taxa.

No log, square-root, Box–Cox or outcome-chosen transformation can alter the primary classification.

One rank-based sensitivity is allowed because it was declared here before outcome inspection. It can describe robustness but **cannot upgrade** FAIL or MIXED to PASS.

## Molecular summaries

Within each gene, values are z-standardized across matched taxa.

For a target class containing multiple genes, use PC1. Orient the PC1 sign so that the sum of loadings is non-negative. A single-gene class, if allowed by the frozen minimum, uses its z-score directly.

Orthology/gene-class mapping must be frozen before fitting the pigment response.

## Model

For one fixed matched taxon set and one fixed branch-length tree, fit:

- NULL;
- EARLY_CORE;
- BRANCH_COMPOSITION;
- LATE_OUTPUT;
- PATHWAY_REGULATION.

Each molecular model is a single-predictor PGLS with Brownian covariance. Compare by AICc. No effect direction is predeclared.

## Frozen classification

### PASS

All admission gates pass; the best non-null model is `LATE_OUTPUT` or `PATHWAY_REGULATION`; it improves on NULL by at least 2 AICc; and the best OUTPUT_CONTROL model beats the best non-output model by at least 2 AICc.

### MIXED

Coverage passes but OUTPUT_CONTROL has less than 2 AICc separation from NULL or the best non-output class, including ties.

### FAIL

Coverage passes and either:

- `EARLY_CORE` or `BRANCH_COMPOSITION` beats the best OUTPUT_CONTROL model by at least 2 AICc; or
- NULL beats every molecular model by at least 2 AICc.

### UNQUALIFIED

Any admission condition fails. This does not count as evidence against the biological prediction.

## No-rescue rules

After candidate screening starts:

- do not redefine continuous pigment quantity;
- do not merge/split molecular target classes;
- do not lower the 20-taxon threshold;
- do not promote the rank sensitivity to the primary endpoint;
- do not replace continuous quantity with discrete pigment loss;
- do not hunt additional candidates because the first admitted outcome is adverse.

## Why this is now the highest-information test

Hue/composition already has several heterogeneous cross-system controls concentrated on anthocyanin branch-control architecture. Continuous pigment quantity has only two direct radiation-scale systems and they disagree at the primary endpoint.

Therefore an unused radiation can genuinely discriminate between:

- a reusable intermediate-resolution output-control rule; and
- a clade-specific Iochrominae result / non-general Petunieae sensitivity.

## Claim boundary

A PASS would support one prospectively validated target-family rule for continuous pigment quantity. It would not establish a universal exact gene, a universal flower-colour law, or event-for-event correspondence with macroevolutionary transitions.

A FAIL would falsify the frozen output-control prediction for the admitted radiation; it would not invalidate the broader phenotype-dimension ontology.

Camellia Paper 1 remains unchanged and closed.
