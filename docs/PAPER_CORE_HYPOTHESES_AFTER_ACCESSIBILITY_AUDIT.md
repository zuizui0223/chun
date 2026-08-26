# Paper core after accessibility, ascertainment and nuclear-realization audits

## Central question

Where does predictability break between short-timescale floral pigment feasibility, recurrent molecular mechanism, and long-term evolutionary realization in *Camellia*?

The paper now separates five empirically distinct quantities:

1. **demonstrated feasibility** — a state change can occur within genotype, development, bud sport, or a close cultivar system;
2. **observation regime** — which pigment axes and gene families a study chooses or is able to measure;
3. **identified mechanistic recurrence** — how strongly independent systems share the same multivariate A/F/C/P transition package after observation is standardized;
4. **macroevolutionary realization pattern** — whether visible states are locally clustered or broadly distributed across accepted-species nuclear history;
5. **persistence/filtering** — ecology, mating system, lineage history, introgression or other processes affect establishment, retention or loss after a feasible state is generated.

The central empirical lesson is that these quantities cannot be collapsed into one `accessibility` variable.

## H1 — substantial flower-colour changes are demonstrably feasible on short timescales

### Current status: supported as an existence-level statement

Multiple within-genotype, developmental and close-cultivar systems demonstrate that substantial visible colour changes can be generated without deep phylogenetic divergence or wholesale pathway deletion.

### Boundary

The literature does not provide a standardized denominator of perturbations, so it does not estimate a natural generation probability or a variational-bias distribution.

## H2 — independent red/pink-gain systems repeatedly reuse one multivariate anthocyanin-up transition package

### Current status: **not supported by the first standardized two-cluster remeasurement**

The literature-only matrix is weakly identified because pigment axes are measured unevenly. At biological-system level A/F/C/P coverage is 8/4/1/3, with exact conditional P(A enrichment) = **0.0083618164** and P(any imbalance at least as large) = **0.0239483869**; dependence collapse weakens A enrichment to P = **0.140625**.

After canonical orientation, the literature-only `anthocyanin_gain` class has three dependence clusters and broad recurrence bounds:

- exact-signature recurrence: **0.3333–1.0**;
- pairwise A/F/C/P concordance: **0.25–1.0**.

The decisive standardized test uses the same two independent common clusters that now have frozen candidate-free raw-RNA-seq results:

- `CJAPONICA`;
- `CSIN_WHITE_PINK`.

### Same-cluster literature regime

Five cluster × axis cells remain unresolved, giving 243 exact completions:

- exact-signature recurrence: **0.5–1.0**;
- pairwise concordance: **0.25–1.0**;
- pairwise identified-set width: **0.75**.

### Same-cluster candidate-free regime

Only one cluster × axis cell remains unresolved, giving three exact completions:

- exact-signature recurrence: **0.5 exactly**;
- pairwise concordance: **0.25–0.5**;
- pairwise identified-set width: **0.25**;
- width reduction relative to the literature regime: **0.50**.

Thus standardized measurement does not merely tighten the literature estimate around strong recurrence. It removes complete multivariate concordance from the admissible set.

### Direct observation-regime conflicts

Across the three cells independently resolved in both observation regimes:

- agreement = **1/3**;
- conflicts = **2/3**.

Both conflicts are the A axis:

- `CJAPONICA`: literature `A=up`, candidate-free `A=down`;
- `CSIN_WHITE_PINK`: literature `A=up`, candidate-free `A=down`.

For *C. sinensis* white -> pink specifically, the five frozen stage contrasts give:

- A: mean Hedges' g **-2.8595**, 5/5 same sign, down;
- F: **-0.3679**, 4/5 same sign, down;
- C: **+0.8820**, 4/5 same sign, up;
- P: **-0.7558**, 3/5 same sign, unresolved.

All 30 prespecified runs were present before scoring; mapping was 77.55–84.29%, mean 81.16%. No expected biological direction or P-value threshold was used as a success gate.

The authoritative result is `docs/CANDIDATE_FREE_ACTUAL_RECURRENCE_RESULT_V0_1.md`.

### Interpretation boundary

This result does **not** show that anthocyanin is irrelevant or that candidate-gene studies are generally wrong. The frozen A score is a pathway-wide transcript module across DFR, ANS/LDOX and UFGT/3GT families. Specific paralogs, upstream regulators, spatial expression, substrate flux, enzyme activity, post-transcriptional control and metabolites can diverge from the module direction.

The supported conclusion is narrower:

> **the published anthocyanin-up recurrence narrative is materially observation-regime dependent, and the first standardized two-cluster remeasurement supports mechanistic heterogeneity rather than one repeated whole-module package.**

## H3 — all demonstrably feasible visible states share the same macroevolutionary realization pattern

### Current status: rejected at the root-independent nuclear pattern level

The primary macro evidence is accepted-species wild-colour clustering on two public nuclear topology pipelines:

1. WFO55 FastTree gene trees -> ASTRAL;
2. WFO53 IQ-TREE LG+G4 + 1000 UFBoot gene trees -> ASTRAL-IV.

Both use 100,000 count-preserving label permutations and unrooted topology distances.

### Global local-conservatism result

Nearest-same-state phylogenetic distance is shorter than null under both trait scenarios and both topologies:

- FastTree strict P = **0.00212**;
- FastTree dominant P < **1e-5**;
- UFBoot strict P = **0.00116**;
- UFBoot dominant P = **0.0000800**.

Thus a reproducible local phylogenetic pattern exists even though individual transitions are not robustly identifiable.

### State-specific result

- **Y:** clustered under strict and dominant coding on both nuclear topologies; strongest state-specific macro pattern.
- **A:** clustered on both topologies only under dominant-colour sensitivity; strict A is a singleton and cannot be tested.
- **W:** not individually clustered under either trait scenario on either topology.

Therefore visible states that are all demonstrably generable on short timescales do not share one accepted-species nuclear realization pattern.

### Pattern-versus-event boundary

Accepted-species branch-transition analysis gives:

- strict wild scenario: zero strong robust branches;
- dominant scenario: one W->A candidate branch;
- strict × dominant cross-scenario gate: **zero robust accepted-species transitions**.

The macro result is therefore a **pattern without identifiable events**. No branch-specific molecular, climate or pollinator cause is assigned.

Traditional-section concentration remains supplementary sensitivity only.

## H4 — ecology acts primarily as a conditional reproductive-service/persistence filter rather than a deterministic hue generator

### Current status: supported at reproductive-service level, not at branch-causal level

The ecological meta-analysis supports large and repeatable reproductive-service effects and climate/season mediation, while rejecting deterministic coarse-hue rules such as universal `red -> bird`.

The strongest current causal chain is:

`molecular feasibility -> latent pigment/spectral/reward phenotype -> flowering-window environment + pollinator availability/effectiveness -> reproductive success -> persistence`.

### Boundary

Accepted-species branch-specific colour-transition causes remain unidentifiable. Ecology cannot yet be assigned as the cause of individual macroevolutionary colour changes.

## H5 — published mechanism and standardized mechanism can be treated as interchangeable observations of one latent state

### Current status: rejected as a default assumption

The actual two-cluster anthocyanin-gain comparison gives only 1/3 agreement in independently resolved cells and opposite A-axis directions in both common clusters. Meanwhile the `CNITIDISSIMA` yellow-development control agrees 4/4 between literature and candidate-free measurement.

Therefore the observation process is **system/class dependent**: it is neither harmless nor uniformly distorting.

This creates the paper's strongest methodological-biological interface. Literature-derived mechanism should be modeled as an observation of biology, not silently equated with biology itself.

## Primary novelty claim after the actual-result gate

Do not claim novelty for any of the following in isolation:

- developmental or mutational bias can shape macroevolution;
- flower-colour pathways constrain transitions;
- spontaneous variation differs from fixed substitutions;
- candidate-gene literature is biased;
- public flower-colour RNA-seq can be reanalysed;
- partial identification is a general statistical idea.

The strongest surviving contribution is now empirical as well as conceptual:

> **In the same biological systems, published candidate-selected mechanistic observations and a frozen pathway-wide candidate-free remeasurement produce different identified recurrence spaces. Standardized measurement contracts the anthocyanin-gain concordance set from 0.25–1.0 to 0.25–0.5 and reverses the published A-axis direction in both independently remeasured clusters.**

This is embedded in a broader identification framework that separately measures:

`feasibility -> observation -> identified recurrence -> macroevolutionary realization -> persistence/filtering`.

A second independent contribution remains:

> **a macroevolutionary pattern can be robustly identifiable even when the individual historical events and their causes are not.**

## Next decisive work

The main question is no longer whether the first two-cluster test exists; it is complete. The next work is generalization and falsification:

1. add a third defensible independent `anthocyanin_gain` candidate-free cluster if public raw data permit, to test whether the two-cluster attenuation persists;
2. add a second independent `yellow_development` candidate-free cluster before claiming class-level yellow recurrence;
3. preserve the current negative/heterogeneous result if additional systems restore, weaken or reverse it;
4. keep mechanistic-state phylogeny gated until taxon-level A/F/C/P coverage is sufficient; visible hue cannot impute missing molecular axes.
