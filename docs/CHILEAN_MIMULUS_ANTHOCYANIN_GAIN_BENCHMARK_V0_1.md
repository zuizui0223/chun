# Chilean Mimulus anthocyanin-gain benchmark v0.1

## Why this system matters

The Chilean *Mimulus luteus* group provides a three-event positive benchmark for repeated floral pigment gain from a non-white ancestral baseline.

Classical genetic work reconstructed the yellow monkeyflower phenotype as ancestral and identified three independent gains of petal-lobe anthocyanin pigmentation in:

- *M. luteus* var. *variegatus*;
- *M. cupreus*;
- *M. naiandinus*.

The gains are genetically simple at the focal petal-lobe anthocyanin trait but are not one exact-locus replay.

## Hierarchy of repeatability

### High-level module

All three gains map to genomic regions containing duplicated anthocyanin-regulating R2R3-MYB transcription factors. At the atlas ontology level all three therefore resolve to:

`PATHWAY_SPECIFIC_REGULATOR`.

This yields high module-level repeatability: **3/3 events**.

### Genomic region

- *M. cupreus*: `pla1`;
- *M. naiandinus*: `pla1`;
- *M. l. variegatus*: `pla2`.

Thus the maximum exact-region recurrence is **2/3**. Pairwise region concordance is **1/3** because only the *cupreus–naiandinus* pair matches.

### Exact causal gene

Only the *M. l. variegatus* event is currently resolved to a functionally demonstrated gene at the required standard: `MYB5a/NEGAN` (`10.1093/genetics/iyaa036`). The other two remain unresolved within the `pla1` R2R3-MYB cluster in the frozen evidence.

Therefore exact-gene recurrence is **not estimable** and must not be imputed from genomic-region overlap.

## Biological interpretation

This system is an important control for the white-baseline hypothesis. Strong module-level recurrence in pigment gain occurs from an ancestrally yellow context as well as in white/colorless systems.

The cross-clade prediction should therefore not be:

`white ancestry -> modular recurrence`.

A stronger test is:

> **Repeated gains of floral pigmentation are biased toward reusable regulatory modules across ancestral baseline states, while exact locus/gene replay is less complete.**

Whether white-like ancestry changes the probability, direction or persistence of gains remains a separate comparative question.

## Ecological note

Field studies found no simple shift to a new pollinator corresponding to the three anthocyanin gains. This makes the group useful for separating recurrent pigment generation from a deterministic pollination-syndrome explanation.

## Claim ceiling

Do not claim:

- that all three events have an identified exact causal gene;
- that `pla1` recurrence means the same mutation or same paralog was reused;
- that the ancestral state was white;
- that pollinators caused the repeated gains;
- that the three-event benchmark alone establishes a general angiosperm rule.

## Atlas role

`YELLOW_BASELINE_REGULATORY_GAIN_BENCHMARK`

This is currently the cleanest >=3-event positive benchmark for the atlas hierarchy:

`module repeatability > exact-region repeatability > exact-gene identifiability`.
