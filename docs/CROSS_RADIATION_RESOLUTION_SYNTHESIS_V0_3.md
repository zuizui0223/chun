# Cross-radiation resolution synthesis — v0.3

## Central claim

> **Flower-colour evolution has no universal biological resolution at which phylogenetic predictability is maximized. Resolution profiles vary among radiations even when phenotype ontology, estimator, permutation scheme and source methodology are standardized.**

This replaces the rejected universal `coarse < intermediate > fine` hypothesis and sharpens the v0.2 claim that the best resolution is radiation dependent.

## Evidence sequence

### 1. Retrospective discovery generated a resolution hypothesis

Earlier cross-radiation work showed recurrent hierarchical organization but weak universal transition direction. That discovery stage motivated a stronger, falsifiable prediction: intermediate biological resolution might maximize predictability across radiations.

### 2. Iris prospectively falsified the universal intermediate optimum

The fourth-radiation Iris test was frozen before row-level outcome ingestion and terminated `FAIL`:

- `AUC_coarse = 0.4617`;
- `AUC_intermediate = 0.4544`;
- `AUC_fine = 0.4871`;
- intermediate was below 0.5 and below fine;
- the frozen fail-side fine-over-intermediate test was significant (`P = 0.0486`).

This prospective result rejected a universal intermediate optimum; it did not reject the separate conditional-hierarchy claim.

### 3. A standardized 51-clade batch shows heterogeneity under one ontology

The Sinnott-Armstrong et al. flower-clade dataset was preregistered before CHUN opened row-level `flower_color` values. The exact source files, 51 clade-to-tree mappings, 2960/2960 species crosswalk and a lexical source-schema erratum were frozen before AUC calculation.

The same estimator was then applied to every clade:

- common retained-tip frame across all three resolutions;
- fine states with fewer than 5 tips removed before all resolutions;
- minimum 20 retained tips and minimum 2 states at each resolution;
- negative patristic distance predicting same-state pairs;
- ROC AUC;
- 9,999 joint triplet permutations with seed `20260913` per clade.

Terminal result:

| class | clades |
|---|---:|
| `HOLD_INSUFFICIENT_COMMON_FRAME_OR_STATE_VARIATION` | 23 |
| `PROFILE_NO_PHYLOGENETIC_SIGNAL` | 16 |
| `PROFILE_SIGNALLED_TIED` | 6 |
| `PROFILE_SIGNALLED_COARSE` | 3 |
| `PROFILE_SIGNALLED_INTERMEDIATE` | **0** |
| `PROFILE_SIGNALLED_FINE` | 3 |

The unique coarse winners are *Ilex*, *Maytenus* and *Symplocos*. The unique fine winners are *Passiflora*, *Rosa* and *Solanum*.

The key result is not merely that intermediate failed again. Under one visible-colour ontology and one analysis pipeline, **different biological clades support coarse, fine, tied or no-signal profiles, while none supports a uniquely dominant intermediate profile**.

### 4. Simple pre-outcome tree geometry does not explain the profile differences

After the standardized batch crossed the numerical `n >= 5` moderator gate, four outcome-independent one-predictor models were evaluated:

- log tree-tip count;
- pairwise patristic-distance CV;
- branch-length CV;
- root-to-tip CV.

A predictor had to improve leave-one-clade-out RMSE over intercept-only for both independent profile contrasts:

1. `AUC_intermediate - AUC_coarse`;
2. `AUC_fine - AUC_intermediate`.

No predictor qualified. All four also worsened LOO RMSE for the derived `AUC_fine - AUC_coarse` contrast. Therefore the observed resolution heterogeneity is not rescued as a simple consequence of tree size or basic tree geometry.

This is a negative moderator result, not evidence that no biological moderator exists.

### 5. Gesnerioideae defines an applicability boundary

Gesnerioideae was preregistered as another profile replication, but the source phenotype layers did not instantiate one outcome-independent nested ladder across pigment chemistry and visible/reflectance colour. The analysis therefore stopped pre-outcome at `HOLD_SCHEMA_SOURCE_AXES_NOT_NESTED`.

This boundary matters conceptually: some radiations may not possess a single biologically defensible coarse-to-fine representation spanning the available phenotype dimensions.

## What survives from the earlier hierarchy result

The conditional hierarchy programme remains distinct:

> after fixing a coarse state, finer phenotype identity can retain non-random phylogenetic organization.

That result is supported in the existing Linoideae, Angraecinae and Antirrhineae analyses. It is a different estimand from the unconditional three-resolution AUC profile used in Iris and the 51-clade batch.

Therefore both statements can be true:

1. phenotype state spaces are often hierarchical;
2. there is no universal resolution at which the strongest unconditional evolutionary signal must occur.

## Revised integrated inference

The strongest current synthesis is:

> **Flower-colour predictability is representation-dependent but not governed by one universal optimal scale. A preregistered intermediate-resolution rule failed prospectively in Iris, and a standardized 28-clade exact-profile batch produced coarse, fine, tied and no-signal outcomes with zero unique intermediate winners. Simple pre-outcome tree geometry failed to predict these differences, while some systems do not admit a single nested cross-axis hierarchy at all.**

## Novelty boundary

Do not claim that this is the first demonstration that trait evolution can be resolution dependent. That broad idea has prior art.

The stronger empirical contribution is the sequence:

1. derive a cross-radiation resolution rule;
2. freeze it before a new radiation;
3. prospectively falsify it;
4. expand to a standardized many-radiation exact estimator;
5. show that heterogeneity persists after standardization;
6. fail a pre-outcome tree-geometry moderator gate rather than post-hoc explain the heterogeneity.

## Main-paper figure spine

1. **Discovery / hierarchy panel** — how the intermediate-resolution prediction arose while conditional hierarchy remained distinct.
2. **Iris prospective falsification** — frozen timeline and three AUCs.
3. **51-clade standardized profile map** — per-clade coarse/intermediate/fine AUCs and terminal classes.
4. **Winner summary** — 3 coarse / 0 intermediate / 3 fine / 6 tied / 16 no signal among completed clades.
5. **Moderator qualification** — LOO change relative to intercept for the four tree-only candidates, all failing the joint profile gate.
6. **Applicability boundary** — Gesnerioideae schema HOLD illustrating that a nested ladder itself can fail to exist.

## Working title

**No universal scale of predictability in flower-colour evolution**

Alternative:

**The scale of evolutionary predictability varies among flower-colour radiations**

## Next gate

Do not open another held-out resolution-profile outcome merely to accumulate examples. The next prospective test requires either:

- additional exact-estimand training that varies representation type, especially a biochemical hierarchy such as Ruellia after exact tree recovery; or
- a separately preregistered outcome-independent moderator that passes the full-profile LOO qualification rule.

Camellia Paper 1 remains unchanged.
