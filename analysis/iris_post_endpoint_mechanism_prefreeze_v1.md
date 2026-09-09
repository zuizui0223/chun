# Iris post-endpoint mechanism stage — prospective pre-freeze v1

Freeze status: **FROZEN BEFORE ANY IRIS MECHANISM SEARCH OR MECHANISM-EVIDENCE ADMISSION FOR THIS STAGE**.

## Ordering contract

The cross-radiation discovery set is fixed as **Linoideae + Angraecinae + Antirrhineae**. The canonical prospective fourth-radiation phenotype test is **Iris**.

Iris Stage A was frozen before phenotype endpoint computation in commit `6cd82af7733e9dd2a0d8074fd9a7de4163424435` (`analysis/iris_fine_state_falsification_prefreeze_v1.md`) and later returned `MIXED`. Stage A is closed: no mechanism result may change its colour coding, coarse partition, taxon admission, statistic, sensitivity set, threshold, or final `MIXED` classification.

**No Iris molecular/mechanistic source may be selected, screened for concordance, or interpreted for Stage B until this file is committed.** Literature already known in other clades is not an Iris Stage-B observation.

## Stage B question

Given the frozen Iris Stage-A phenotype result, does independently observed Iris molecular differentiation resolve at the **same phenotype granularity** rather than only at a coarse pigment-class level?

This is a prospective phenotype-to-mechanism alignment test. It is not a search for a preferred gene, and it is not allowed to rescue or refute the Stage-A macro result.

## Frozen mechanism ontology

Code direct Iris molecular observations only into these functional levels, without naming candidate genes in advance:

1. `PIGMENT_DEPLOYMENT` — molecular state associated with presence/absence or total deployment of a major floral pigment system;
2. `PIGMENT_CLASS` — molecular differentiation separating major pigment classes such as anthocyanin versus carotenoid/no-major-pigment;
3. `FINE_HUE_BRANCH` — molecular differentiation among fine states inside one major pigment class;
4. `CAROTENOID_FINE_AXIS` — differentiation among carotenoid-associated fine states, only if a directly matched Iris observation regime exists.

A source may populate more than one level only when its own measurements support those levels independently. Do not infer a fine-level mechanism from visible colour alone.

## Frozen evidence admission

A Stage-B source is admissible only if all are true:

- it contains **direct molecular observations** from Iris floral tissue or a directly comparable floral organ (e.g. metabolite/pigment chemistry, expression, genotype linked to measured molecular phenotype, enzyme/function assay);
- sampled Iris taxon identities can be mapped one-to-one to the Stage-A source taxonomy or to a predeclared taxonomic crosswalk independent of the mechanism result;
- the molecular variable is measured rather than inferred solely from flower colour, pollinator syndrome, phylogenetic reconstruction, or narrative review;
- wild taxa/species-level biological material can be separated from horticultural/cultivar-only evidence when the latter is not representative of the Stage-A taxon;
- taxon inclusion is not chosen because it agrees with the Stage-A pattern.

Narrative-only statements and single-species functional studies may be retained as context but cannot satisfy the comparative alignment gate.

## Frozen comparative gate

Promote Stage B beyond `HOLD_MECHANISM_OBSERVATION_REGIME` only if the admitted direct evidence jointly provides:

1. at least **20 Iris taxa** with Stage-A colour-state mapping and direct molecular observations; and
2. at least one Stage-A coarse class containing **at least two distinct fine colour states**, with **at least 5 directly measured taxa in each of two fine states**; and
3. a molecular observation regime comparable across those taxa (same molecular layer or a prespecified harmonizable measurement family), rather than a patchwork of unrelated one-off genes; and
4. no result-dependent removal of discordant taxa.

If these gates fail, stop at `HOLD_MECHANISM_OBSERVATION_REGIME`. Do not relax n, fine-state replication, or comparability after seeing the sources.

## Frozen alignment tests

If the comparative gate passes, evaluate two nested questions on the same admitted taxon set:

### B1 — coarse molecular alignment
Does molecular state discriminate the frozen Stage-A coarse pigment grouping better than a taxon-label permutation null?

### B2 — residual fine-state molecular alignment
After conditioning on the same frozen Stage-A coarse grouping, does molecular state retain association with fine Stage-A colour state?

The exact statistical form may depend on the recovered direct molecular object (continuous multivariate measurements versus categorical functional states), but it must be selected **from the source data type before looking at colour-concordance results** and recorded in a source-specific analysis freeze. Permutations must preserve the Stage-A coarse grouping for B2.

## Frozen Stage-B classification

- `PROSPECTIVE_PHENOTYPE_MECHANISM_ALIGNMENT`: comparative gate passes, B2 supports residual fine-state alignment, and no required admissible sensitivity materially contradicts it;
- `COARSE_ONLY_ALIGNMENT`: B1 supports but B2 does not support residual fine-state alignment;
- `MIXED_MECHANISM_ALIGNMENT`: admitted molecular layers or predeclared sensitivities materially disagree;
- `ADVERSE_MECHANISM_ALIGNMENT`: adequate direct matched evidence shows neither stable coarse nor fine alignment across the frozen tests;
- `HOLD_MECHANISM_OBSERVATION_REGIME`: direct matched comparative evidence is insufficient or incomparable.

`ADVERSE_MECHANISM_ALIGNMENT` is **not** a refutation of Stage A. It refutes only a proposed cross-level mechanistic extension under this observation regime.

## Prohibited post-search moves

After Iris mechanism search begins, do not:

- add a new ontology level because a discovered gene fits it better;
- choose genes or pathways based on agreement with the Stage-A phenotype pattern;
- change the Stage-A coarse or fine colour coding;
- lower the 20-taxon or 5-per-fine-state gates;
- combine incomparable molecular assays merely to reach n;
- replace wild-taxon evidence with cultivar-only evidence to fill a desired state;
- treat multiple genes from one taxon comparison as independent evolutionary replications;
- revise the Stage-A `MIXED` result.

## Counting boundary

Iris contributes one prospective fourth-radiation phenotype test through Stage A. Stage B, if admitted, is a **cross-level follow-up within the same radiation**, not a fifth independent radiation. Iochrominae, Erica, Epimedium and Aquilegia remain retrospective/previously inspected mechanism systems and cannot be used to claim that Iris mechanism was prospectively selected.
