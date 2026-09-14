# Resolution-profile training inventory — v0.4

## Current exact-estimand count

The unconditional three-resolution AUC estimator has now been completed in **30 biological units**:

- **Iris** — 1 prospectively tested radiation; the preregistered universal intermediate-ordering rule terminated `FAIL`.
- **Flower-clades-51 batch** — 28 completed clades under one standardized visible-colour ontology; 23 additional clades remain pre-defined `HOLD_INSUFFICIENT_COMMON_FRAME_OR_STATE_VARIATION`.
- **Petunieae biochemical profile** — 1 completed retrospective standardized cross-representation unit; terminal class `PROFILE_SIGNALLED_FINE`.

The numerical replication floor is therefore not limiting. The limiting factor is now **representation-level identifiability**.

## Petunieae cross-representation anchor

The Petunieae profile uses the same unconditional exact-profile estimator but a different phenotype representation from the 28 visible-colour clades:

- coarse: any of six anthocyanidins present vs none;
- intermediate: PEL/CYA/DEL anthocyanidin-class presence pattern;
- fine: exact six-compound presence pattern.

After the frozen rare-fine-state rule, 47 tips remain. Coarse and intermediate collapse to the same retained binary partition (6 absent / 41 present), while the fine representation retains six states.

Terminal result:

- coarse AUC = `0.518925563507132`, p = `0.1985`;
- intermediate AUC = `0.518925563507132`, p = `0.1985`;
- fine AUC = `0.6995630849367751`, p = `0.0001`;
- fine minus runner-up = `0.18063752142964307`, joint-permutation p = `0.0001`;
- terminal class = **`PROFILE_SIGNALLED_FINE`**.

This is **not** a new prospective replication. The source values had previously been inspected for a different cross-level molecular-subspace analysis. It is admitted only as standardized retrospective cross-representation training.

## Representation composition of the current training universe

| representation role | completed units | use |
|---|---:|---|
| standardized visible-colour ontology | 28 | within-representation replication and tree-geometry qualification |
| biochemical composition hierarchy | 1 (Petunieae) | first cross-representation anchor |
| mixed pigment/hue hierarchy | 1 (Iris) | prospective falsification; not exchangeable with the biochemical category |

The total count of 30 must **not** be interpreted as 30 exchangeable radiation-level moderator observations. The 28 visible-colour clades share one source/ontology, Petunieae is the only completed biochemical hierarchy, and Iris uses a distinct mixed hierarchy.

## Moderator status after Petunieae

Current decision remains:

`NO_MODERATOR_QUALIFIED_CURRENT_TRAINING`

The earlier four tree-only predictors remain unqualified under leave-one-clade-out evaluation. Petunieae supplies representation variation, but it does **not** make a representation-type moderator estimable under honest leave-one-out validation:

- the biochemical category has exactly one completed observation;
- in the fold holding out Petunieae, the training data contain zero biochemical observations;
- therefore a biochemical-vs-visible representation effect cannot be learned and used to predict the held-out biochemical unit without extrapolating an unidentified category coefficient.

No representation-type regression is fit, no probability over the next held-out winner is frozen, and no existing held-out outcome is opened to rescue this limitation.

## Current blocked systems

- **Gesnerioideae** — `HOLD_SCHEMA_SOURCE_AXES_NOT_NESTED`; source access was resolved, but the available phenotype axes do not form one outcome-independent nested ladder.
- **Ruellia HPLC** — biochemical ladder and identifiers frozen; `HOLD_AUTHORITATIVE_2023_TREE_BYTES_OR_EXACT_RECONSTRUCTION_SOURCE_UNAVAILABLE_OUTCOMES_UNOPENED`.
- **Rhododendron30** — biochemical ladder preregistered; exact primary-tree metadata frozen, but Wiley Table S3 and Dryad tree bytes are currently source-access blocked. Chemistry outcomes remain unopened.
- **Linoideae / Angraecinae / Antirrhineae conditional hierarchy analyses** — different conditional-null estimand; do not count toward the unconditional exact-profile total.

## Next gate

The highest-information next step is **not another visible-colour clade and not a larger moderator model**. The representation-moderator gate reopens only after at least one additional independent completed exact-profile unit with a biochemical or otherwise non-visible nested representation is available.

Preferred unblock paths:

1. recover the authoritative Ruellia 2023 ddRAD tree and execute the already-frozen biochemical profile; or
2. recover exact Rhododendron Table S3 + frozen primary-tree bytes, freeze the species/tree crosswalk, and only then open chemistry outcomes.

Only after a second non-visible exact-profile system exists should CHUN test whether representation class predicts the two independent profile contrasts under leave-one-out validation.

Camellia Paper 1 remains unchanged.
