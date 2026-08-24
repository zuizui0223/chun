# Ecological-driver meta-analysis — Paper 1 v0.5 integration complete locally

The ecological-driver layer has been carried through v2 quantitative synthesis and propagated into a versioned AJB v0.5 build contract. The deterministic local build passes the manuscript claim gate, AJB style gate, revised ecological Fig. 6 generation, ecological Appendix S4 materialization, and final bundle checksum audit. No further ecological search is required before submission unless a study supplies missing sampling variances for the three cross-species bird-access effects.

## Resolved question

Which ecological processes have quantitatively repeatable effects on reproductive performance in *Camellia*?

## Quantitative result

1. **Cross-species pollinator service:** three independent bird-access/exclusion systems (*C. japonica*, *C. petelotii*, *C. oleifera*) all increase fruit set, spanning A/Y/W visible states. Equal-weight geometric-mean RR = **3.53**; leave-one-out RR = **2.64–4.39**. This is a magnitude synthesis, not inverse-variance pooling, because defensible sampling variances remain unavailable for all three effects.
2. **Within-species replication:** independent *C. oleifera* bird-exclusion and managed-*Apis cerana* experiments give RR = **2.29** and **2.56**, respectively; the latter also has a correlated open-field RR = **4.31**. Wild-bee abundance, nesting distance and *Andrena* visit-density gradients independently point in the expected pollinator-service direction.
3. **Pollen limitation:** *C. pubipetala* supplementation gives RR = **3.50** (approx. 95% RR interval 1.11–11.03), while *C. petelotii* reports no supplementation effect. Service contribution and pollen limitation are therefore context dependent and not interchangeable.
4. **Climate/season mediation:** admitted systems in *C. hainanica*, *C. perpetua*, *C. petelotii* and *C. oleifera* support flowering-window environment -> pollinator/reward conditions -> reproduction. Outcomes are heterogeneous and are not pooled on one scale.
5. **Direct abiotic floral pigment:** still under-replicated. The cleanest admitted *Camellia* flower experiment is the Berruti *C. japonica* cold+dark treatment, which confounds temperature and darkness. Additional searches mainly recover leaf anthocyanin experiments, observational petal comparisons, or extraction-temperature studies rather than independent whole-flower ecological manipulations.
6. **Sensory aliasing:** same-visible-red *C. rusticana* vs *C. japonica* differs by ~23.46-fold in bumblebee visitation, reinforcing that coarse visible hue is not a deterministic ecological state.

## Revised ecological model

`molecular accessibility -> latent pigment/spectral/reward phenotype -> flowering-window environment + pollinator availability/effectiveness -> reproductive success -> evolutionary persistence`

The strongest evidence is for the middle of this chain: reproductive-service/reliability filtering and its climate/season dependence. The data do **not** support a universal `red -> bird` or `red -> cold` syndrome.

## Remaining public-data boundary

The ecological filtering mechanism is quantitatively supported at the service/reliability level, but accepted-species branch-specific colour-transition causes remain unidentifiable after taxonomy and wild-polymorphism audit. Direct abiotic floral-pigment effects also remain too sparse/confounded for formal meta-analysis.

## Paper 1 integration result

- AJB structured abstract: 237 words;
- Literature Cited: 32 entries, alphabetized and style-gated;
- Main figures: frozen Figs 1–5 plus registry-backed ecological Fig. 6;
- Supporting Information: nine appendices, with Appendix S4 carrying 17 studies and 25 registered ecological effects plus variance and claim-ceiling fields;
- final local bundle audit: 6 main figures, 9 appendices, 47 files, one archive-DOI placeholder, SHA256 manifest generated.

Submission metadata and archive DOI work remains paused until the v0.5 branch is reviewed and the regenerated bundle passes hosted CI. The remaining scientific boundary is unchanged: mechanism/service-level filtering is supported, but accepted-species branch-specific historical causation is not identified.
