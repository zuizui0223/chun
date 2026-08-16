# Camellia flower-colour meta-analysis: current identifiability ceiling

## Purpose

This document answers one question before the programme asks for more data:

> **What can the existing Camellia literature and current `chun` re-analyses already establish, and which questions remain non-identifiable without additional evidence?**

Three evidence classes are kept separate:

1. **meta-resolved preliminary conclusions** — current literature synthesis is sufficient for a bounded directional statement;
2. **public-data extension** — no new field experiment is required, but common raw-data or nuclear-tree re-analysis is still needed;
3. **new primary measurement required** — the target parameter cannot be estimated from the current heterogeneous literature, even if the existing papers are summarized more aggressively.

The machine-readable gate is `data/meta_analysis_identifiability_ceiling_v0_1.csv`.

## 1. Literature expansion without independence inflation

The v0.3 mechanism table adds four flower studies while preserving dependence structure:

- Feng et al. 2024, *C. nitidissima*: admitted inside the existing `CNITIDISSIMA` cluster because it adds multi-omics and functional CnFLS2 evidence from the same focal biological system rather than a new independent colour origin;
- Zhang et al. 2024, *C. japonica*: admitted inside `CJAPONICA` as functional CjMYB114/CjbHLH1 -> CjDFR evidence;
- Zhu et al. 2024, *C. perpetua*: admitted as a new independent yellow-flower developmental cluster (`CPERPETUA`), with public RNA-seq PRJNA981682;
- *C. huana* 2025 golden/red-petal study: admitted as a new independent flower-colour cluster (`CHUANA`) because it adds a carotenoid-dominated colour axis rather than another anthocyanin-only contrast.

A 23-golden-Camellia flavonol survey / CnFLS1 functional study is retained as auxiliary yellow-state chemistry rather than forced into the red-versus-less-red sign synthesis. A 2025 *C. tachangensis* purple study is excluded from the flower meta-analysis because its focal tissues are tea buds/leaves.

The decisions are frozen in `data/camellia_mechanistic_literature_expansion_decisions_v0_1.csv`.

## 2. What the expanded mechanistic meta-analysis now supports

The expanded v0.3 table contains 16 study records collapsed to **10 independence clusters**.

### 2.1 Regulatory/flux accessibility is the strongest result

At independence-cluster level:

- regulatory/pathway-flux evidence: **10/10**, exact two-sided sign P = **0.00195312**;
- more-red/pink state has more anthocyanin: **6/6 interpretable**, P = **0.03125**;
- stronger downstream anthocyanin branch in the more-red state: **4/4 interpretable**;
- stronger competing branch in the less-red/yellow/white direction: **6/6 interpretable**, P = **0.03125**.

This remains true under two important anti-circularity restrictions:

**Micro-only, excluding the genus-scale Fan 2026 record**

- regulatory/flux: **9/9**;
- anthocyanin direction: **5/5**;
- downstream anthocyanin direction: **3/3**;
- competing branch: **5/5**.

**Public-raw-only cluster consensus**

- regulatory/flux: **6/6**;
- anthocyanin direction: **4/4**;
- downstream anthocyanin direction: **3/3**;
- competing branch: **5/5**.

Therefore the short-scale accessibility result does not require the macro phylogenomic result to be present in the evidence set.

### 2.2 The direction is not driven by one focal taxon cluster

Leave-one-independence-cluster-out analysis retains:

- anthocyanin direction: yes fraction 1.0 in every run;
- downstream anthocyanin direction: 1.0 in every run;
- competing branch direction: 1.0 in every run;
- regulatory/flux evidence: 1.0 in every run.

This does **not** remove publication/ascertainment bias, but it shows that the directional result is not numerically dependent on one of the admitted independence clusters.

### 2.3 Regulatory lability spans comparison scales

Cluster-consensus regulatory/flux evidence is present in:

- developmental / mosaic / bud-sport systems: **5/5 clusters**;
- within-species genotype/cultivar comparisons: **4/4**;
- between-taxon/species comparisons: **3/3**.

Clusters can contribute to more than one scale category, so the categories are not independent replicates. The valid conclusion is **scale coverage of mechanistic lability**, not a formal test that transition rates are equal across scales.

## 3. What the meta-analysis does not support, even after expansion

### 3.1 Structural-gene loss frequency remains underidentified

No explicitly informative focal cluster requires structural-gene loss, but only **3/10** clusters directly discriminate loss-versus-no-loss; the remaining seven have `no_evidence`.

Therefore:

> **Supported:** whole-pathway structural loss is not required to explain the currently informative focal contrasts.

> **Not supported:** structural-gene loss is generally rare across Camellia macroevolution.

The latter requires coding-sequence presence/absence, pseudogenization, copy-number and synteny auditing across independently reconstructed transition lineages.

### 3.2 Micro accessibility is not macro origin frequency

The v0.3 mechanism result establishes that regulatory/flux states are repeatedly reachable in studied systems. It does not establish that A or Y evolved independently many times.

This distinction is especially important because the full species table shows:

- A: 25 species in 4/17 traditional sections, with 22/25 in sect. Camellia;
- Y: 17 species in 4/17 sections, with 13/17 in sect. Chrysantha.

The same extant concentration can arise from repeated gains, lineage-gated gain, differential loss/persistence, one/few origins followed by radiation, or reticulation.

No further re-counting of the current papers can identify those histories.

### 3.3 Pollination literature rejects deterministic hue-function mapping but cannot estimate event frequency

The primary-evidence pollination seed has seven taxa. A and Y each contain more than one broad pollinator-function class, and 2/3 multi-taxon visible states show functional heterogeneity. The exact global hue-function association is unresolved (P = 0.4857).

This is sufficient to reject the model `one visible hue -> one fixed reproductive function`.

It is **not** sufficient to estimate whether reproductive/sensory niche shifts are more frequent than climatic niche shifts because the seven taxa are literature-ascertained and study designs/effect sizes are heterogeneous.

### 3.4 Present-day correlations cannot identify reactivation causality

The current literature can establish that:

- regulatory re-deployment is mechanistically plausible and recurrent;
- pathway competence can be retained in low-pigment states;
- climate, season and pollinator environment can all plausibly affect floral function;
- a universal visible-red/cold model is not supported.

It cannot establish a Camellia-specific adaptive `active -> low -> active` event without an ordered branch history plus retained-pathway evidence. It cannot assign selection pressure without ecological ordering and fitness/persistence evidence.

## 4. The exact boundary between public-data work and genuinely new data

### 4.1 Can still be advanced without new field measurements

These are **not** field-data blockers:

- common-effect-size re-analysis of public petal RNA-seq / metabolome datasets (M1/M2/M7);
- node-level micro-accessibility scores using a common ortholog/module definition;
- provenance-safe nuclear species-tree reconstruction from public sequence resources;
- stochastic visible/latent state histories once a defensible tree set is admitted;
- gain-versus-loss/persistence hazard decomposition from those histories;
- reticulation-sensitive alternative histories where public data permit.

These should be exhausted before asking for new sampling.

### 4.2 Requires standardized primary trait measurements if literature coverage does not improve

The current species seed has strong structured missingness: pollinator regime is much better covered than UV/reflectance, carotenoid chemistry, reward and comparable phenology.

A genus-level test of `H_SELECTION_TARGET` or `H_REPRODUCTIVE_NICHE` therefore needs the **same species set** measured for:

- petal reflectance spectra including UV;
- anthocyanin / flavonol / carotenoid / proanthocyanidin chemistry on comparable scales;
- nectar volume/concentration/composition and other reward traits where relevant;
- flowering phenology;
- effective pollinator contribution, not visitor lists alone.

Without this matched matrix, latent-state models and visible-hue models cannot be compared fairly.

### 4.3 Adaptive reactivation requires stronger evidence than comparative meta-analysis

To call a branch an **adaptive reactivation**, require all of:

1. an ordered active -> low/suppressed -> active history;
2. retained pathway machinery through the low state;
3. a heritable regulatory/coding change associated with renewed deployment;
4. temporal alignment with a candidate climate/light/pollinator regime change;
5. evidence that the reactivated phenotype improves fitness, reproductive success or persistence under the candidate regime;
6. history/introgression/ancestral-polymorphism alternatives tested.

Items 1-3 may often be approachable with public phylogenomic/genomic/transcriptomic data. Item 5 will commonly require new field, common-garden or experimental fitness data.

## 5. Revised research sequence

The programme should now proceed in this order:

1. **finish public-data meta/transcriptomic quantification** — convert directional recurrence into comparable module effect sizes;
2. **admit nuclear histories** — estimate independent origin/gain/loss events rather than infer them from extant section counts;
3. **separate generation from persistence** — test the accessibility-persistence paradox directly;
4. **build the matched latent ecological phenotype matrix** — only then compare sensory/reproductive versus climatic filtering;
5. **promote candidate regains to reactivation only after the history + retention gate**;
6. **collect new fitness/selection data only for branches that survive all previous gates**.

This avoids collecting broad trait data before the meta-analysis has identified which branches and variables are actually diagnostic.

## Current strongest statement

> **Camellia flower-colour variation is repeatedly generated through regulatory and pathway-flux reallocation across several short-scale biological contexts, but the extant macro distribution of coloured states is far more lineage-concentrated than this mechanistic accessibility alone predicts. Existing meta-analysis can establish this accessibility–realization mismatch; it cannot identify whether the macro bottleneck lies in generation, persistence/loss, one/few-origin radiation or reticulation, nor can it attribute adaptive reactivation without branch histories and matched ecological/fitness evidence.**
