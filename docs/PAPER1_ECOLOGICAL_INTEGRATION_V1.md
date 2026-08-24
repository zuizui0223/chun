# Paper 1 ecological integration after meta-analysis v2

## Revised story

Paper 1 should now make a three-scale argument rather than a two-scale argument.

1. **Molecular generation is flexible.** Similar pigment states can be produced through different paralog implementations; exact-gene recurrence is weaker than pathway/module recurrence.
2. **Macroevolutionary colour is locally conservative.** Accepted-species wild-colour states show repeatable nearest-same-colour phylogenetic structure across trait and topology sensitivities, although broad MPD clustering is topology-sensitive.
3. **Ecological filtering has quantitative support at the service level.** Pollinator access/reliability repeatedly changes fruit set, pollen limitation and effective pollen delivery, and climate/season repeatedly changes the conditions under which that service is delivered. However, current accepted-species colour data do not identify robust transition branches to which these ecological effects can be causally assigned.

The resulting question is no longer only why molecularly accessible colours are not evolutionarily labile. It is:

> How can flexible molecular generation coexist with local phylogenetic conservatism when reproductive-service filtering is strong but macroevolutionary transition events remain poorly identifiable?

## Authoritative ecological numbers

- Cross-species pollinator-service fruit-set effects: 3 independent species, A/W/Y represented, 3/3 positive, RR range 2.29–6.35, equal-weight geometric mean RR = 3.53, leave-one-out RR = 2.64–4.39.
- *C. oleifera* within-species replication: bird access RR = 2.29; *Apis cerana* cage introduction RR = 2.56; geometric mean RR = 2.42; secondary open-field honey-bee RR = 4.31.
- Pollinator reliability gradients: 5/5 registered effects in the expected direction.
- *C. pubipetala* pollen supplementation: RR = 3.50, reconstructed SE(lnRR) = 0.586, approximate 95% RR interval 1.11–11.03.
- Climate/season mediation: 5 studies across 4 taxa.
- Direct abiotic floral-pigment manipulation: 1 independent experiment, cold and darkness confounded; no formal pooling.
- Same-visible-red sensory contrast: *C. rusticana* vs *C. japonica* bumblebee visit RR ≈ 23.45.

## Revised AJB structured abstract candidate — 237 words

### Premise of the study

Flower-colour states can be generated through multiple pigment-pathway routes, but molecular accessibility need not imply macroevolutionary lability. We asked whether molecular routes to colour are repeatable, whether wild flower colours remain phylogenetically constrained, and which ecological processes repeatedly affect reproduction.

### Methods

We combined sequence-aware synthesis of *Camellia* pigment mechanisms with a 339-locus Angiosperms353 nuclear framework, accepted taxonomy, audited wild-colour states, and phylogenetic permutations. We also synthesized study-level ecological effects for pollinator service, pollen limitation, climate/season mediation, sensory choice, and floral pigment manipulation without pooling incompatible outcomes.

### Key results

Molecular recurrence did not require one exact gene: FLS showed same-lineage recurrence, whereas independent DFR clusters used different paralog subclasses. Nearest-same-colour conservatism persisted across trait and topology sensitivities; on the UFBoot topology, *P* = 0.00116 (strict) and *P* = 0.000080 (dominant), while broad mean pairwise-distance clustering was topology-sensitive. Bird access increased fruit set 2.29–6.35-fold across three independent A, W, and Y systems (geometric mean RR = 3.53). Independent *Camellia oleifera* experiments replicated strong bird and bee service effects, and five reliability-gradient effects all matched prediction. Climate or season altered pollination conditions in five studies across four taxa, whereas direct abiotic floral-pigment evidence remained limited to one confounded experiment. No accepted-species colour-transition branch was robust to both trait scenarios.

### Conclusions

Flexible molecular implementations coexist with local phylogenetic conservatism, while reproductive-service filtering has quantitative support across *Camellia*. Public data support this ecological mechanism but cannot assign it causally to individual macroevolutionary colour transitions.

## Claim boundary

### Can state

- reproductive-service/reliability effects are quantitatively large and repeat across independent *Camellia* systems;
- those effects are not restricted to red/A visible states;
- climate/season repeatedly changes pollination conditions and therefore provides a plausible mediator of reproductive-service filtering;
- visible hue is an inadequate deterministic ecological-state variable;
- direct abiotic control of floral pigment is much less replicated than reproductive-service evidence.

### Cannot state

- pollinator-service filtering caused a specific accepted-species colour transition;
- bird pollination is a red/A-specific syndrome across *Camellia*;
- cold adaptation directly caused A/red flower evolution;
- current ecological data justify one omnibus random-effects meta-analysis across heterogeneous outcome families.

## Manuscript integration implemented

1. Ecological-effect extraction, independence, and non-pooling rules are added to Methods.
2. A Results subsection reports the v2 service/reliability numbers after the macro colour-conservatism result.
3. Discussion and Conclusions treat ecological service filtering as quantitatively supported at the mechanism level while preserving the accepted-species branch-identifiability boundary.
4. The Introduction separates the study-level ecological-effect question from branch-specific historical assignment.
5. The AJB abstract, citations, manuscript, revised Fig. 6, Appendix S4, and final upload bundle are regenerated through the v0.5 workflow.

## Figure and Supporting Information contract

- Main Figs 1–5 retain the frozen molecular, taxonomy, topology, and colour-conservatism layers.
- Main Fig. 6 is rebuilt directly from `ecological_driver_effect_size_registry_v0_2.csv` and a regenerated v2 summary; effect values are not duplicated as script constants.
- `paper1_main_figure_manifest_v0_2.csv` replaces the former Fig. 6 dependency rows while preserving the v0.1 manifest as historical provenance.
- Appendix S4 joins all 17 admitted study rows to all 25 effect rows and retains variance status, independence units, source locators, admission status, and claim ceilings.
- The earlier AJB v0.4 bundle remains an immutable pre-ecological snapshot; the ecological manuscript/figure/table integration is versioned as v0.5.
