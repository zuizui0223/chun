# Epimedium molecular dependence screen v0.1

## Question

Can the eight-species molecular comparison in Mi et al. 2023 (`10.3389/fpls.2023.1133616`) supply at least three defensibly independent anthocyanin-loss transitions for a second `Camellia`-style mechanistic recurrence test?

## Molecular observations

The molecular study sampled eight wild-derived species grown in one common garden. Four were anthocyanin-positive (`A+`):

- *E. acuminatum*;
- *E. leptorrhizum*;
- *E. epsteinii* (spelled `epstenii` in the molecular article);
- *E. zhushanense*.

Four were anthocyanin-negative (`A-`):

- *E. franchetii*;
- *E. lishihchenii*;
- *E. sagittatum*;
- *E. wushanense*.

All four A- taxa show strongly reduced ANS expression; DFR is also reduced in most, while coding-function assays in *E. sagittatum* support retained catalytic capacity. This is strong evidence for repeated regulatory association with pigment loss, but it does not by itself establish four independent historical losses.

## Dependence collapse

### 1. *franchetii* + *lishihchenii*

These cannot be counted as independent evolutionary replicates under a strict rule. The current taxonomic literature treats them as part of the same difficult *E. franchetii* complex and reports morphologically transitional populations. They are collapsed as `LOSS_FRC_COMPLEX`.

### 2. *wushanense* + *sagittatum*

The nuclear GBS history and plastid history are not fully concordant. In the 2023 GBS analyses, *E. wushanense* is placed away from the stable E2 lineage and can occur near the E3 boundary in SVD topologies. Plastid studies, however, recover *E. wushanense* close to *E. lishihchenii* and *E. sagittatum*, while the *E. sagittatum* complex itself is taxonomically and phylogenetically difficult. Therefore a third loss event obtained by separating *wushanense* from *sagittatum* is not topology-robust from the evidence currently frozen.

They are conservatively collapsed as `LOSS_EAST_AMBIGUOUS` for the lower-bound independence test.

## Result

The current evidence therefore supports:

- observed A- taxa = **4**;
- conservative topology/taxonomy-robust loss clusters = **2**;
- a nuclear-tree-only interpretation may permit more clusters, but that is not robust enough for the preregistered >=3 independent-transition gate.

**Second mechanistic anchor gate = FAIL / HOLD.**

This does not invalidate the biological result of Mi et al. 2023. It means that the eight-species dataset is excellent evidence for repeated regulatory association with anthocyanin loss, but is not yet a clean set of >=3 independent historical transitions under the atlas event-identity rule.

## Retained role of Epimedium

Epimedium remains exceptionally valuable for the atlas because it supplies:

1. a white plesiomorphic inner-sepal state with repeated colour diversification;
2. organ-resolved present-day colour data for 699 individuals;
3. a direct eight-species molecular comparison showing ANS/DFR regulatory convergence;
4. rapid radiation, parallel evolution, atavism and introgression as an explicit stress test for event identity.

Its role changes from `SECOND_MECHANISTIC_ANCHOR_CONFIRMED` to `MECHANISTIC_SUPPORT_WITH_EVENT_IDENTITY_LIMIT`.

## Reopen condition

Promote Epimedium to a full recurrence anchor only if one of the following becomes available:

- a trait-mapped nuclear tree that robustly resolves >=3 independent A+↔A- transitions among the molecularly sampled species across topology sensitivities;
- additional molecularly measured species that add independent transition clusters;
- population/genomic evidence that separates the ambiguous A- histories without post-hoc choice of topology.

## Programme consequence

The atlas should not require every white-like ancestral clade to reproduce the Camellia design. Instead use complementary clade roles:

- `Camellia`: full matched molecular observation intervention;
- `Epimedium`: regulatory-convergence evidence under reticulate/event-identity uncertainty;
- `Hydrangea-Cornidia`: directional-transition falsification case;
- `Linoideae`: original terminal-trait reconstruction and dated macro history;
- `Antirrhineae`: temporal–spatial polymorphism bridge;
- `Iochrominae`: coloured-ancestor molecular benchmark.

This role-based atlas is stronger than forcing weakly independent systems into one recurrence estimator.
