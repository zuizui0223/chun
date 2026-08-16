# Reactivation selection pressure: preliminary synthesis

## Scope and inference rule

This document keeps three layers separate.

1. **Published conclusions** are results demonstrated in individual source studies. They are inputs, not `chun` discoveries.
2. **`chun` preliminary results** are patterns produced by repository reanalysis, dependence-aware synthesis, provenance auditing, or count-controlled tests.
3. **`chun` hypotheses** are explanations generated from those preliminary results. A paper's discussion/future-work statement is not sufficient to create a `chun` hypothesis.

The target question is no longer simply whether flower colour can be regained. Genuine floral-pigment regain/reactivation has precedent outside *Camellia*. The target is:

> **When a retained pigment programme becomes active again, what ecological change selects and preserves that re-deployment, and why does a molecularly accessible state become macroevolutionarily persistent only in particular lineages?**

---

## I. What the literature already establishes

### L1 — regulatory flower-colour evolution is common in Camellia

Fan et al. 2026 (`10.1111/pbi.70442`) reconstructed white as the most likely ancestral **visible** flower colour in their 237-accession nuclear analysis and identified TE/SV-associated regulatory rewiring, including an experimentally supported MYB60-associated anthocyanin-suppression mechanism.

This establishes that large visible-colour divergence can arise from regulatory architecture. It does **not** establish that an ancestral white lineage had a particular latent biochemical state, nor what ecological selection pressure caused any later regain.

### L2 — anthocyanin loss can remain molecularly reversible

In Iochrominae, Ho & Smith 2016 (`10.1186/s12862-016-0675-3`) found intact anthocyanin-pathway coding regions after repeated losses of floral pigmentation. Smith et al. 2018 (`10.1093/molbev/msy117`) reported convergent late-pathway expression losses and a candidate regain of floral anthocyanin after a prior loss.

Therefore pathway retention can preserve evolutionary reversibility. This is not a *Camellia*-specific discovery.

### L3 — true colour regain can be selected during pollinator reversal

Esfeld et al. 2018 (`10.1016/j.cub.2018.10.019`) demonstrated a particularly strong case in *Petunia secreta*: a two-base-pair deletion restored the reading frame of the previously non-functional `AN2` regulator, re-establishing anthocyanin production during a reversal toward bee pollination.

Thus the general concept `retained/repairable pigment machinery -> regained floral colour -> pollinator-associated selection` already has an empirical precedent.

### L4 — human-visible hue is not the full pollination phenotype

Mori et al. 2023 (`10.1016/j.phytochem.2022.113559`) showed that red *C. japonica* and red *C. rusticana* use different spectral strategies and recruit different pollinators. *C. rusticana* has bee-relevant UV reflectance/fluorescence and is insect-associated, whereas *C. japonica* is bird-associated and relatively inconspicuous to bees.

This establishes that the selection target can differ within one coarse visible-colour state.

### L5 — climate/season can change pollinator reliability in Camellia

Sun et al. 2017 (`10.3732/ajb.1600428`) showed in yellow *C. petelotii* that bird exclusion reduced fruit and seed set by 64%, while honeybee visitation decreased under cloudy/rainy conditions.

The 2025 *C. perpetua* study (`10.1016/j.flora.2025.152727`) found greater bird visitation and reproductive success in winter than summer together with large seasonal changes in nectar volume and sugar composition.

These studies show that climate/weather/season can alter the ecological weighting of pollinator functional groups. They do not reconstruct flower-colour evolution.

### L6 — direct abiotic filtering of floral pigments is possible, but not universal across scales

Koski & Ashman 2016 (`10.1111/nph.13921`) found that UV-absorbing floral pigmentation across 177 Potentilleae species covaried with altitude, temperature and UV-B.

By contrast, Short et al. 2021 (`10.3389/fpls.2021.636133`) found environmental associations with anthocyanin within polymorphic monkeyflower species but no phylogenetically corrected joint evolution of flower colour and environmental affinity across two radiations.

The literature therefore already warns that a micro-scale stress response does not automatically become a macroevolutionary trait-niche pattern.

---

## II. What chun's own analyses have found

### C1 — molecular accessibility is much more repeatable than one climatic outcome

The dependence-aware *Camellia* mechanism synthesis contains 12 study records grouped into 8 independence clusters:

- regulatory/pathway-flux evidence: **8/8** informative clusters;
- higher anthocyanin in the more-red/pink state: **6/6** informative clusters;
- stronger downstream anthocyanin deployment in the more-red state: **4/4**;
- stronger competing branch in the less-red/white/yellow direction: **5/5**;
- no positive informative case currently requires wholesale structural-pathway loss.

This is a `chun` cross-study result: molecular routes into and out of visible pigmentation repeatedly use a limited regulatory/flux architecture.

### C2 — a universal anthocyanin/cold-expansion model fails in Camellia

After the occurrence-provenance audit, exact A(red/pink-like) versus W(white) tests remain non-directional:

- BIO1 median: `P ~ 0.805`;
- BIO6 median: `P ~ 0.526`;
- BIO6 q05 cold tail: `P ~ 0.252`;
- BIO1 IQR: `P ~ 0.705`.

Therefore current *Camellia* data do not support `anthocyanin-rich visible state -> generally colder niche` as a genus-wide rule.

### C3 — visible W/A/Y categories alias multiple functional states

The current latent-state seed already contains exact same-hue collisions:

- red *C. japonica* vs red *C. rusticana*: different pollinator weighting, spectral/UV function and thermal context;
- yellow/golden species: different bird/bee weighting and seasonal pollinator regimes;
- yellow *C. nitidissima*: combined flavonol and carotenoid deployment rather than a one-axis yellow mechanism;
- white *C. oleifera* and white *C. sinensis*: retained flavonoid/pathway activity rather than demonstrated pathway absence.

The deterministic proposition `one visible hue = one ecological/biochemical state` is therefore rejected by the current evidence audit.

### C4 — anthocyanin-like A is strongly lineage-concentrated after controlling for sample size

A new count-controlled permutation screen uses the exact-taxonomy 50-species *Camellia* niche table and traditional sections as a coarse history proxy. State labels are shuffled 100,000 times while preserving A/W/Y species counts.

Observed results:

- `A`: 14 species occupy **2 sections**; expected breadth `6.59279`; lower-tail `P = 0.00003`;
- `A` section Shannon entropy `0.2573`; expected `1.6942`; lower-tail `P < 0.00001`;
- `W`: 34 species occupy 9 sections; expected `9.12673`; breadth `P = 0.651` and entropy `P = 0.413`;
- `Y`: only 2 species in the exact climate subset, so its count-controlled breadth test is underpowered.

This changes the interpretation of the raw section breadth. White's 9/10-section occupancy is not unusually broad once its larger sample size is respected. Instead, the striking result is that **A is much more historically concentrated than expected despite its high molecular accessibility**.

This is a new `chun` micro-to-macro asymmetry.

### C5 — environmental-edge signals can be provenance artefacts

The Tuberculatae audit showed that four shared extreme-coordinate GBIF records generated implausibly cold q05 tails and an apparently strong section-level cold-tail result. Removing those coordinates shifted *C. rhytidocarpa* and *C. tuberculata* q05 temperatures upward by roughly 15–17 °C and removed the nominal section signal.

Therefore a putative `environmental shift -> reactivation` event is inadmissible until the environmental event itself passes provenance and range-plausibility checks.

### C6 — the current information bottleneck is functional phenotype, not more thermal points

In the 8-taxon latent-state audit:

- pollinator regime: 6/8 informative;
- anthocyanin axis: 5/8;
- flavonol axis: 4/8;
- pathway retention: 5/8;
- carotenoid axis: 1/8;
- UV/fluorescence axis: 1/8;
- procyanidin diversion: 0/8.

The next high-value evidence is therefore spectral/UV and biochemical phenotype coverage, not merely denser occurrence sampling.

---

## III. Problems generated by the chun results

### Problem 1 — accessibility–persistence paradox

> **If anthocyanin deployment is repeatedly easy to generate at the molecular scale, why is the A visible state so strongly concentrated in particular historical sections?**

This is stronger than asking whether anthocyanin is adaptive. It asks why **evolvability is broad but macro persistence is narrow**.

### Problem 2 — selection-target problem

> **When pigment re-deployment is selected, what is actually being selected: visible hue, anthocyanin concentration, flavonol/carotenoid allocation, UV reflectance/fluorescence, or a correlated nectar/phenology syndrome?**

The current same-hue collisions make W/A/Y too coarse for causal selection-pressure attribution.

### Problem 3 — trigger-versus-enabler ordering

> **Does environmental/pollinator change first select a reactivated pigment phenotype, or does pigment reactivation first permit expansion into a new ecological niche?**

Present-day trait-environment correlation cannot distinguish these histories.

### Problem 4 — ecological recurrence versus niche novelty

> **Does reactivation enable a genuinely new niche, or does it restore a previously useful signal when an ancestral-like pollinator/light environment recurs?**

This distinguishes `novel adaptation` from `ecological return + molecular memory`.

### Problem 5 — lineage permissivity

> **Which lineage properties convert an easy molecular state into a stable macroevolutionary state?**

Candidates include regulatory background, pathway pleiotropy, floral morphology, phenology, pollinator fauna, ancestral range and introgression opportunity.

### Problem 6 — event validity

> **Is the inferred ecological shift real?**

Range-tail events must pass taxonomic/provenance/native-range/coordinate-reuse sensitivity before they enter a selection analysis.

---

## IV. Hypotheses generated from chun preliminary results

### H-R1 — lineage-permissivity filter (new primary hypothesis)

**Hypothesis:** molecularly easy anthocyanin deployment becomes macro-persistent only in particular genetic/historical backgrounds.

**Generated from:** C1 + C4.

**Prediction:** after stochastic mapping on multiple nuclear trees, A gains and/or persistence will be over-concentrated in particular ancestral backgrounds even after the number of transition opportunities is controlled.

### H-R2 — latent selection target (new primary hypothesis)

**Hypothesis:** ecological selection acts more directly on biochemical/spectral latent phenotype than on human-visible hue.

**Generated from:** C2 + C3.

**Prediction:** models using anthocyanin/flavonol/carotenoid module scores plus UV/visible reflectance explain effective pollination and niche persistence better than W/A/Y labels.

### H-R3 — environment-first reactivation

**Hypothesis:** a climate/light niche shift occurs first, after which a retained pigment programme is selected back on.

**Prediction:** validated environmental shifts systematically precede reactivation branches.

### H-R4 — trait-first niche enabling

**Hypothesis:** a heritable reactivation occurs first and increases access to/persistence in a previously inaccessible niche.

**Prediction:** pigment reactivation precedes cold/UV/drought or other niche-edge expansion and is followed by increased persistence/range occupancy.

The current genus-wide A-W thermal null weakens a universal version but does not exclude branch-specific cases.

### H-R5 — climate-mediated pollinator reactivation

**Hypothesis:** climate is upstream but selects pigment re-deployment mainly by altering pollinator reliability, seasonality or community composition.

**Generated from:** C2 plus the source-level *C. petelotii* weather response and *C. perpetua* seasonal pollinator shift.

**Prediction:** `climate/season -> pollinator regime -> latent spectral/pigment state` outperforms `climate -> visible hue`.

### H-R6 — dual-function reactivation

**Hypothesis:** the same flavonoid deployment is retained because it contributes simultaneously to reproductive-tissue stress protection and pollinator signalling.

**Prediction:** the strongest reactivation branches align with both abiotic change and sensory/pollination change, and biochemical state outperforms hue alone.

### H-R7 — ecological recurrence / molecular memory

**Hypothesis:** some reactivations occur when an ecological regime similar to an ancestral regime reappears, making a retained former signal advantageous again.

**Generated from:** recurrent pathway accessibility, external proof that colour regain can accompany pollinator reversal, and Camellia same-hue functional collisions.

**Prediction:** ecological distance between the post-reactivation regime and the pre-loss ancestral regime is smaller than expected under a novel-niche model.

### H-R0 — historical/neutral recurrence

Apparent regain can also result from ancestral polymorphism, introgression, lineage sorting or drift without a new selective optimum.

This remains a strong alternative because *Camellia* shows marked colour-history structure and reticulation. It must be beaten before calling a branch adaptive reactivation.

---

## V. Preliminary ranking after the current analyses

### Weakened as a general explanation

**Direct universal abiotic selection on visible redness.** Provenance-clean *Camellia* A/W thermal comparisons are null, and macro literature contains both support and counterexamples.

### Strong background explanation

**Historical/lineage filtering.** Full Fan-table section-colour dependence is strong, and the new count-controlled exact-subset analysis shows A is much more section-concentrated than expected.

### Best ecological candidate at present

**Pollinator/sensory filtering, potentially mediated by climate/season.** This is favored as a *candidate*, not established as the macro cause, because *Camellia* already contains same-hue pollinator-function collisions and direct seasonal/weather effects on pollinator weighting.

### Most important unresolved causal contrast

**Environment-first/follower versus reactivation-first/enabler.** This cannot be settled without a dated/admitted nuclear transition history.

---

## VI. Decisive analysis sequence

1. **Admit a primary nuclear species tree** and retain multiple alternative nuclear trees for reticulation/topology sensitivity.
2. **Map mechanistic states, not only W/A/Y**, carrying state uncertainty.
3. Identify candidate `active -> low/suppressed -> active` histories and require pathway retention before calling them reactivation candidates.
4. Validate occurrence-based environmental edge events with the range-tail provenance gate.
5. Reconstruct branch changes in climate/light, flowering season and pollinator regime.
6. Compare explicit temporal models: `environment first`, `reactivation first`, `pollinator first`, `climate -> pollinator`, `ecological recurrence`, and `no ecological alignment`.
7. Test whether post-reactivation persistence/range expansion exceeds matched non-reactivation branches.
8. Test whether micro-accessibility and lineage background interact to predict macro reuse/persistence.

## Current claim ceiling

Supported now:

> *Camellia* flower-pigment states are highly accessible through recurrent regulatory/flux changes, but visible anthocyanin-like states are not universal cold-niche enablers and are unexpectedly concentrated in a small subset of traditional sections. Visible hue also aliases distinct ecological functions. These results generate a lineage-permissivity and latent-selection-target problem: ecological/historical filters determine which readily generated pigment states become persistent macroevolutionary states.

Not yet supported:

- a branch-specific adaptive reactivation in *Camellia*;
- direct climate causation of a regain;
- pollinator causation of a regain;
- a universal white-state evolutionary hub;
- a particular lead-lag direction between colour and niche change.
