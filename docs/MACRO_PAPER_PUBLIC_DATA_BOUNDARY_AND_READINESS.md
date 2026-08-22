# Macro paper — public-data boundary and readiness

## Decision

**Status: READY FOR MANUSCRIPT DRAFTING.**

The public-data analysis programme has reached its intended stopping point. The current results support a publishable **macroevolutionary/comparative paper**, provided the manuscript is framed around the contrast between **molecular accessibility** and **macroevolutionary constraint/persistence**, not as a demonstration of one ecological cause of Camellia flower-colour evolution.

No further literature mining or generic public-data analysis should be added to the main line merely to seek a preferred ecological story. The remaining causal questions require matched empirical data and should be handed to the next field/experimental study.

The one reviewer-critical topology concern was tested after the public-data boundary was reached: the main colour-conservatism result and the B011/B073 relationships persist on the independent 339-locus IQ-TREE/UFBoot/wASTRAL backbone. Therefore topology method is no longer a major unresolved obstacle to drafting.

---

## 1. The research story that the paper should tell

The paper should be written as a **hypothesis-updating sequence**, not as a retrospective story in which every analysis was designed to confirm one final model.

### Stage 1 — hypotheses from prior literature

Flower colour can respond to multiple classes of selection and constraint:

1. **abiotic protection** — anthocyanins can be associated with cold, irradiance, drought and oxidative stress;
2. **pollinator-mediated selection** — colour and sensory phenotypes can alter visitor attraction and reproductive service;
3. **historical/developmental constraint** — pigment chemistry and ancestry can limit which phenotypes are reached;
4. **molecular accessibility** — the flavonoid pathway provides multiple regulatory and structural routes to similar visible states.

These are literature-derived alternatives, not project conclusions.

### Stage 2 — first project tests reject the simplest ecological story

The first macro prediction was a simple direct-cold model: anthocyanin-like/red states should occupy colder environments.

The broad genus-level and history-controlled public occurrence/climate analyses did **not** support that model, while cold-tail estimates were strongly sensitive to occurrence provenance.

This negative result generated a new question:

> If direct climate does not explain the macro pattern, why are visible flower-colour states concentrated in particular evolutionary histories?

### Stage 3 — nuclear phylogeny rejects the strong A-specific lineage hypothesis

An independently reconstructed nuclear backbone was built without using flower colour.

A strong initial project hypothesis predicted that anthocyanin-like A states should be globally clustered in a uniquely permissive lineage background. That strong form was not supported.

Instead, the broader pattern is reproducible:

> **visible colour states as a whole are phylogenetically conserved.**

FastTree/ASTRAL sensitivity:

- same-state MPD permutation P = **0.00399**;
- nearest same-state P = **0.000620**.

Independent IQ-TREE/UFBoot/wASTRAL replication:

- same-state MPD P = **0.00346**;
- nearest same-state P = **0.000660**.

A-specific clustering remains weak/non-significant on both topologies.

This changes the question from **“which lineage permits red?”** to:

> **Why are multiple visible states history-dependent even though their molecular implementation is flexible?**

### Stage 4 — micro analyses reveal molecular flexibility

The micro literature/meta-analysis and sequence audit show that recurrent pigment responses cannot be reduced to universal reuse of one exact gene.

Key cases:

- **FLS:** a recurrent `CnFLS2_like_CSA008358` same-paralog lineage is resolved, while a later white-directed tea FLS is a different paralog;
- **DFR:** `C. japonica` is CsDFRa-like, whereas the tea white/pink source locus is CsDFRb2 — the same downstream module is implemented with different paralogs;
- **ANS/LDOX and ANR:** paralog/copy-specific directional heterogeneity means that a gene-family symbol does not have one universal evolutionary sign.

The supported micro interpretation is therefore **hierarchical molecular accessibility**:

`exact node < paralog lineage < family < biochemical module < pigment/sensory state`.

This creates the central paradox of the macro paper:

> **similar pigment states appear molecularly accessible through more than one implementation route, yet realized visible colour remains phylogenetically constrained.**

### Stage 5 — held-out rooted macro history identifies independent events

`Polyspora speciosa` was recovered using the same frozen marker universe and used to root the expanded nuclear sensitivity tree before colour was joined.

The sampled Camellia crown ancestor is most likely W:

- Fitch root state: **W only**;
- best model: ER in all four Mk treatments;
- model-averaged W posterior = **0.970–0.996** with ASTRAL branch lengths;
- W remains the top state with unit edges, but W/Y uncertainty is larger (**W 0.554–0.738**).

Therefore the paper should state **“W is favoured”**, not “the ancestor was certainly white”. This result is supporting context and is **not the novelty claim**, because Fan et al. 2026 already inferred a white Camellia ancestor.

Model-averaged branch reconstruction identifies exactly three strong robust endpoint transitions under the predeclared rule (same direction in all four treatments; minimum joint posterior >= 0.5):

- **B011:** W→A at the base of a 24-tip clade;
- **B073:** W→A to `C. brevistyla`;
- **B083:** W→A to `C. japonica`.

B011 and the `C. brevistyla`–`C. confusa` B073 relationship are retained on the stronger runtime91 wASTRAL tree. B083 cannot be assessed on runtime91 because `C. japonica` was added only in rooted94; it must remain explicitly a rooted94 result.

### Stage 6 — the new events are used to test causes, not to decorate the tree

The three events were then used as frozen targets for causal public-data tests.

#### Climate

B073 and B083 are both colder than their local sisters using exact-tip median BIO1/BIO6 values.

B011 also becomes colder if occurrence retrieval for the frozen `C. albogigas` sister is broadened to its accepted synonym `C. granthamiana`. Under that alias sensitivity all three branches are colder and the size-matched branch null is very strong.

However, the alias-derived cold tail differs from the existing exact-name provenance-clean boundary by **18.215°C**. Therefore the final status is:

**`public_data_unidentifiable_taxonomic_alias`**.

The correct interpretation is **suggestive branch-local cold association**, not proof of direct cold adaptation.

#### Pollination service

The literature contains strong within-lineage mechanistic evidence:

- `C. japonica` has bird-function, pollen-flow and sensory evidence;
- `C. reticulata` has controlled evidence for insect-mediated reproductive service;
- other Camellia studies motivate flowering-window reliability and pollinator-conflict hypotheses.

But **0/3** robust W→A branches have paired, branch-assignable direct service-quality evidence on both descendant and sister sides.

Final status:

**`public_data_unidentifiable`**.

This is an identifiability result, not evidence that pollinators are irrelevant.

#### Micro mechanism → macro transition

Only **B083 / C. japonica** currently has a terminal, branch-assignable paralog-resolved mechanism case (`CsDFRa_like_AB524885`, `CjMYB114`, `CjbHLH1`).

`C. reticulata` ANS/ANR/UFGT evidence lies inside the large B011 descendant clade and cannot be assigned to the basal event. B073 lacks a paralog-resolved public colour-mechanism cluster. The recurrent strict FLS micro predictor occurs in micro systems outside the three robust W→A branches.

Final status for macro hierarchical-reuse enrichment:

**`public_data_unidentifiable`**.

The micro molecular-accessibility result remains supported; what is unavailable is the independent macro recurrence test.

---

## 2. What is actually novel relative to current Camellia literature

### Not a novelty claim: a new Camellia phylogeny

Camellia nuclear phylogenomics is already well developed. Zan et al. (2023) used 1,481 low-copy genes and highlighted reticulation/gene-tree conflict; Yan et al. (2024) used 348 Angiosperms353 loci and showed extensive gene-tree heterogeneity and rapid radiation.

Our nuclear reconstruction is valuable because it is **independent, public, reproducible and colour-blind**, not because it supersedes those studies.

References:

- Zan et al. 2023, *Molecular Phylogenetics and Evolution*, DOI `10.1016/j.ympev.2023.107744`.
- Yan et al. 2024, *Molecular Phylogenetics and Evolution*, DOI `10.1016/j.ympev.2024.108089`.

### Not a novelty claim: a white Camellia ancestor

Fan et al. 2026 already analysed 237 Camellia accessions and inferred a likely white ancestor while identifying TE/SV-mediated regulatory changes associated with flower-colour diversification.

Reference:

- Fan et al. 2026, *Plant Biotechnology Journal*, DOI `10.1111/pbi.70442`.

Our root analysis should be presented as an **independent uncertainty-aware replication/supporting gate** used to define transition branches, not as the paper headline.

### Not a general novelty claim: multiple biochemical routes to convergent colour

Macroevolutionary work in other plant clades has already shown that similar flower colours can evolve through alternative pigment pathways and that pathway use can itself show phylogenetic signal. Ng & Smith’s Solanaceae work is an important precedent.

Reference:

- Ng & Smith 2016, *New Phytologist*, DOI `10.1111/nph.13576`.

Therefore the paper should not claim to discover the general idea that flower-colour convergence can use multiple biochemical routes.

### The defensible novelty

The current paper’s contribution is the combination of four points:

1. **paralog-resolved implementation:** recurrent Camellia pigment-module responses include both same-paralog reuse and within-module paralog substitution rather than only pathway-level categories;
2. **macro constraint despite micro accessibility:** visible Camellia colour is strongly phylogenetically conserved on two independently inferred nuclear topologies despite the demonstrated flexibility of molecular implementation;
3. **uncertainty-aware independent transition definition:** robust W→A events are selected only after tree/root/transition uncertainty is separated from ecological and molecular predictors;
4. **causal identifiability boundary:** public climate, pollination and paralog-resolved mechanism evidence are explicitly tested against those frozen branches, showing exactly which causal questions can no longer be resolved by further aggregation of heterogeneous public data.

The general contribution is therefore not “we found red flowers again”, but:

> **molecular accessibility and macroevolutionary persistence are different problems.**

---

## 3. Recommended central question and thesis

### Central question

> **Why are molecularly accessible flower-colour states evolutionarily constrained in Camellia?**

### Main thesis

A safe manuscript-level formulation is:

> **Public molecular evidence reveals multiple paralogous routes to related pigment states in Camellia, whereas independently reconstructed nuclear phylogenies show that realized visible colour remains strongly history-dependent. Uncertainty-aware reconstruction identifies a small set of robust W→A transitions, but current public ecological and branch-resolved molecular evidence cannot identify a single general cause for their persistence. These results separate molecular generation from macroevolutionary persistence and define the matched empirical tests needed to connect them.**

This thesis is supported by the current data.

### Claims that must not enter the title/abstract as established results

Do **not** claim:

- cold climate caused repeated W→A transitions;
- birds caused red/anthocyanin flower evolution across Camellia;
- macro W→A events preferentially reuse FLS/DFR/ANS/ANR modules;
- exact paralog reuse is rare on macro branches;
- B083 is independently validated on the runtime91 wASTRAL topology;
- ASTRAL branch lengths represent divergence time;
- W is the certain ancestral state.

---

## 4. Main-paper result structure

### Result 1 — molecular accessibility is hierarchical

Use the micro meta-analysis and sequence-resolved FLS/DFR/ANS/ANR audit.

Headline:

> recurrent module-level responses need not imply recurrent exact-gene implementation.

### Result 2 — visible flower colour is phylogenetically conserved

Use both nuclear topologies.

Headline:

> A-specific clustering is not robust, but colour-wide phylogenetic conservatism is.

This is a particularly useful hypothesis-revision result: the analysis rejects the stronger preferred story and supports a broader one.

### Result 3 — W is the favoured ancestral state, with explicit uncertainty

Use Fitch + Mk ER/SYM/ARD × branch-length × root-prior model averaging.

This is a transition-definition step, not the headline discovery.

### Result 4 — three W→A events survive model uncertainty

B011, B073 and B083 become the natural evolutionary replicates used in downstream tests.

### Result 5 — public data do not identify one universal ecological or molecular cause

Present the three branch-targeted gates together:

| causal layer | result | interpretation |
|---|---|---|
| annual thermal context | underidentified / alias-sensitive | B073/B083 colder; B011 taxon-concept instability prevents universal conclusion |
| pollination service | underidentified | strong case studies exist, but 0/3 branches have paired direct service data |
| paralog-resolved macro mechanism | underidentified | B083 linked; insufficient independent branch-resolved mechanisms for recurrence |

The positive conclusion is not “nothing explains colour”. It is:

> **the available evidence can identify macro events more reliably than it can identify their causes.**

That gap is itself the basis for a targeted empirical programme.

---

## 5. Figure plan

Keep the main text to approximately five major figures.

### Figure 1 — hypothesis-update cascade

Prior alternatives → project tests → rejected/revised hypotheses → current persistence question.

Visually distinguish:

- literature-derived hypothesis;
- project-generated hypothesis;
- supported result;
- falsified/weakened result;
- public-data boundary.

### Figure 2 — micro molecular accessibility hierarchy

FLS / DFR / ANS / ANR evidence displayed at:

- exact node;
- paralog lineage;
- family;
- module.

Highlight the FLS same-lineage case and DFR different-paralog case.

### Figure 3 — nuclear history and colour-wide conservatism

Show the colour-blind nuclear backbone with observed A/W/Y tips and the cross-topology permutation results.

Main numbers:

- FastTree/ASTRAL global same-state P=0.00399; nearest P=0.000620;
- IQ-TREE/UFBoot/wASTRAL global same-state P=0.00346; nearest P=0.000660;
- A-specific clustering not supported on the stronger tree.

### Figure 4 — rooted colour history and robust transition posterior

Show:

- W-favoured root posterior range rather than one hard ancestral state;
- B011, B073, B083;
- minimum and mean W→A posterior;
- explicit note that B083 is rooted94-only in the wASTRAL topology sensitivity.

### Figure 5 — public-data boundary and empirical handoff

Rows: B011 / B073 / B083.

Columns:

- climate;
- pollination service;
- paralog-resolved mechanism;
- next required measurement.

This should visually make the transition from Macro Paper to Empirical Study unavoidable rather than speculative.

### Supplementary core

- public-resource provenance/marker manifest;
- 339-locus occupancy and alignment gates;
- wASTRAL/runtime91 topology and rooted94 sensitivity;
- topology RF comparison;
- all Mk model fits/root priors;
- all 184 branch transition posteriors;
- climate provenance and `albogigas/granthamiana` alias sensitivity;
- pollination evidence hierarchy/coverage;
- orthology/paralogy ledgers and micro→macro coverage audit.

---

## 6. Suggested manuscript architecture

### Introduction

1. Flower colour is unusually tractable mechanistically but has multiple possible ultimate causes.
2. Molecular routes to colour can be labile, while macro phenotypes may still be historically constrained.
3. Camellia now has rich genomic and flower-colour literature, but the connection between molecular accessibility and persistence across independent macro transitions is unresolved.
4. Predeclare the sequence of questions rather than one favored causal hypothesis.

### Methods

1. systematic/public evidence synthesis;
2. paralog-aware molecular resolution;
3. colour-blind public nuclear reconstruction and sensitivity;
4. held-out colour join and phylogenetic-conservatism tests;
5. rooted model-averaged colour history;
6. robust transition definition;
7. branch-targeted climate, pollination and mechanism identifiability gates.

### Results

Follow the hypothesis-update sequence exactly. Negative results should generate the next test rather than being hidden.

### Discussion

1. **Generation is not persistence** — molecular accessibility can coexist with macro conservatism.
2. **Historical contingency operates above one exact gene** — connect paralog substitution to broader pathway/history constraints without claiming macro enrichment.
3. **No single ultimate cause is established by current public data** — distinguish annual climate, flowering-window service, pollinator conflict and latent sensory states.
4. **The missing data are now specific** — describe the empirical contrasts that can resolve the causal models.

---

## 7. Publication feasibility

### Current judgement

**Yes, the current work is sufficient to draft and submit a macro-comparative paper.**

It is strongest as a paper about **constraints, hypothesis revision and the separation of molecular accessibility from evolutionary persistence**. It is weaker if presented as a paper claiming to have discovered the ultimate ecological driver of Camellia flower colour.

### Realistic journal positioning

Current public-data-only version:

- **American Journal of Botany** — strong fit for floral colour evolution, comparative analyses and explicit evolutionary hypotheses;
- **Annals of Botany** — strong fit for integrative plant evolutionary biology;
- **Journal of Evolutionary Biology / Evolutionary Ecology** — plausible depending on final framing and methodological emphasis.

**New Phytologist** should be treated as a stretch target for the current public-data-only paper. A later version that directly measures matched pollination service + spectra/chemistry + paralog-specific expression across independent W→A contrasts would have a substantially stronger claim to that tier.

The manuscript should not compete with Fan et al. 2026 on genome/SV novelty. It should explicitly cite that study and define a different question: **what constrains persistence after molecular generation is possible?**

---

## 8. Stop rule for the Macro Paper

The main public-data analysis is now **closed**.

Further work belongs in the current Macro Paper only if it is one of:

- reproducibility/CI repair;
- figure generation;
- manuscript-table generation;
- a sensitivity test directly requested by the current claim architecture;
- correction of a demonstrated data/provenance error.

Do **not** add another ecological predictor simply because existing predictors are underidentified.

The next scientific work should instead move to matched empirical data.

---

## 9. Empirical Study 1 generated by the Macro Paper

### Empirical question

> **Do pollination-service quality and paralog-specific pigment deployment determine whether an accessible W→A state is maintained?**

### Priority evolutionary contrasts

#### Priority 1 — B073

`C. brevistyla` (A transition descendant) vs `C. confusa` (local W sister).

Why high priority:

- W→A posterior is extremely strong;
- local relationship is retained on wASTRAL;
- public pollination-service data are missing;
- public paralog-resolved mechanism data are missing;
- therefore new measurements have maximum information value.

#### Priority 2 — B083

`C. japonica` (A) vs `C. szechuanensis` (local W sister).

Why high priority:

- strong W→A posterior;
- `C. japonica` already has bird-function and paralog-resolved molecular evidence;
- the missing sister measurements can convert an isolated case study into a matched evolutionary contrast.

#### Priority 3 — B011

Resolve the `C. albogigas` / `C. granthamiana` taxon concept and the exact lineage represented in the nuclear tree before expensive ecological inference. Then choose phylogenetically informative descendant representatives close to the basal transition.

### One common measurement protocol

For each matched contrast collect:

1. guild-specific visitation through the full flowering window;
2. single-visit stigma pollen deposition;
3. pollen removal and pollen-transfer efficiency;
4. bird/insect exclusion and open-pollination controls;
5. fruit and seed set;
6. flowering-window temperature, precipitation, irradiance and wind at observation scale;
7. nectar volume and sugar concentration/composition;
8. calibrated UV–visible reflectance and, where relevant, fluorescence;
9. petal pigment chemistry;
10. paralog-specific FLS/DFR/ANS/ANR expression and sequence identity.

The design should include nearby W→W controls where feasible, so a W→A pair is not confounded with every lineage difference between two species.

### What the empirical study can finally discriminate

- direct abiotic adaptation vs flowering-window-mediated effects;
- pollinator abundance vs pollination-service quality;
- pollinator attraction vs pollinator conflict/avoidance;
- visible hue vs latent multidimensional sensory state;
- same-node reuse vs paralog substitution across independent macro transitions;
- molecular accessibility vs ecological persistence.

That is the correct scientific handoff from the Macro Paper.

---

## 10. Final claim boundary

The current public-data programme supports:

- hierarchical molecular accessibility and paralog substitution at micro scale;
- colour-wide phylogenetic conservatism on independent nuclear topologies;
- W as the favoured but uncertain Camellia crown state;
- three robust W→A macro endpoint transitions on the rooted94 sensitivity tree;
- B011/B073 local topology robustness on wASTRAL91;
- explicit public-data limits for direct climate, pollination-service and macro mechanism attribution.

It does **not** support one universal ecological cause or macro paralog-reuse enrichment.

That distinction should be treated as a feature of the paper, not a defect to be hidden with further opportunistic analyses.
