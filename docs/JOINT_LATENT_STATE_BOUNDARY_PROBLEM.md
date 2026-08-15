# Joint latent flower-colour state and ecological-boundary problem

## Current position

Two independent robustness analyses now invalidate the simplest macroevolutionary data model.

1. **Flower colour is not directly observed as one biological state.** Human-visible W/A/Y merges distinct pigment flux, spectral signals and pollination functions.
2. **Climatic range boundaries are not directly observed as one biological value.** GBIF provenance, low sample size and the lower-tail estimator create substantial observation uncertainty.

Therefore the usual analysis

`observed W/A/Y -> observed q05 -> PGLS / ancestral-state correlation`

is structurally too simple for the central biological question.

The new problem is:

> **Can pigment-network accessibility and ecological filtering be separated when both the floral state and the ecological boundary are latent, incompletely observed quantities?**

This is the next modelling target. It is a project problem statement, not a claim that a latent-variable statistical framework is itself novel.

## 1. Why the predictor is latent

The current *Camellia* evidence already falsifies a deterministic map from human-visible hue to one ecological/mechanistic state.

- red *C. japonica* is bird-associated;
- red *C. rusticana* is insect/bee-associated and has different UV/fluorescence cues;
- white/less-red states are produced through several documented regulatory/flux routes rather than one pathway deletion;
- yellow *C. nitidissima* combines flavonol and carotenoid contributions.

The current 8-taxon latent-state seed therefore keeps separate axes for anthocyanin, flavonol, carotenoid, procyanidin diversion, UV/fluorescence, pollinator regime, thermal context and pathway retention.

Visible W/A/Y is an **observation layer** generated from those states, not the latent state itself.

## 2. Why the ecological response is latent

The exact 50-species GBIF × CHELSA analysis originally treated BIO6 q05 as a species trait. Record-level audit shows that this can be badly wrong.

- Two implausible records moved *C. rhytidocarpa* q05 by `+15.53 C` after removal.
- Two analogous records moved *C. tuberculata* q05 by `+16.815 C`.
- A documented BOLD country-centroid coordinate occurs in 27 exact *Camellia* taxa.
- Intermediate provenance-cleaning stages can create significant A-W q01/min differences that disappear under the stronger current provenance screen.

After the current S3 provenance sensitivity, no robust visible-A cold-edge difference remains.

The q05 estimator also remains sample-size dependent even after provenance screening: retained occurrence n is negatively associated with leave-one-record-out q05 instability (`Spearman rho=-0.52047`, `P=0.0001069`).

Thus the true ecological boundary is another **latent quantity** observed with taxon-specific error.

## 3. Preliminary uncertainty propagation

`data/camellia_boundary_observation_uncertainty_v0_1.csv` propagates q05 observation uncertainty after the S3 provenance screen.

Observed A-W q05 difference:

- `-0.4837 C` (A colder).

When within-species occurrence-resampling error is propagated while conditioning on the observed species set:

- centered 95% diagnostic interval: **`-1.390 to +0.192 C`**;
- fraction of replicates with A lower: `0.91`.

When non-phylogenetic species resampling is added:

- diagnostic interval: **`-2.206 to +1.140 C`**;
- fraction A lower: `0.700`.

The point direction can therefore look fairly consistent while its magnitude is not resolved away from zero once observation/taxon-sampling uncertainty is represented.

This is not a formal confidence interval for a phylogenetic evolutionary effect. It is a diagnostic that the error-free-species-trait assumption is untenable for the current data.

## 4. Hard filtering is not a complete solution

A provisional minimum boundary gate (`n>=20` and max leave-one-record-out q05 change <=1 C) retains only:

- A: `10/14`;
- W: `16/34`;
- Y: `0/2`;
- total: `26/50`.

A stronger gate retains 17/50 species and again no yellow taxa.

The A-versus-W differences in pass rate are not statistically established in the current sample, but the complete loss of the two climate-admitted Y taxa illustrates a more general problem: **quality filtering changes which evolutionary states and lineages can enter the analysis.**

Therefore the final solution should not be `discard every uncertain taxon and run PGLS on the remainder`.

## 5. Additional macro check: A is not a general niche-displacement state

A section-relative niche-displacement screen provides another negative result at the coarse visible-state level.

Within the two traditional sections shared by A and W taxa (Camellia and Paracamellia):

- core thermal niche displacement without the tail: A-W mean displacement `-0.356`, within-section permutation `P=0.287`;
- adding the provenance-clean cold-tail: A-W `-0.211`, `P=0.269`.

So visible A is not supported as a general state of stronger niche displacement within these coarse historical blocks either.

This makes it less useful to keep inventing new A-versus-W macro correlations. The state and event observation models need to change first.

## 6. New primary inference structure

A minimally adequate model should have four linked layers.

### Layer 1 — floral observation model

Observed evidence:

- human-visible hue;
- pigment chemistry;
- petal transcript/expression modules;
- UV/visible spectra and fluorescence;
- pathway-retention evidence.

Latent target:

`Z_pigment(taxon, branch, time)` = biochemical/sensory deployment state.

### Layer 2 — ecological observation model

Observed evidence:

- provenance-audited occurrences;
- CHELSA/environment values;
- sample size;
- q05/min/lower-tail estimators;
- leave-one-record/locality influence;
- bootstrap/resampling uncertainty.

Latent target:

`B_env(taxon, branch, time)` = biological environmental boundary or niche-limit state.

### Layer 3 — phylogenetic transition/event model

On admitted nuclear topologies:

- pigment-state transition events;
- ecological-boundary shifts;
- pollinator/sensory regime shifts;
- white-root uncertainty;
- topology/branch-length uncertainty.

### Layer 4 — ordering/causal-pattern comparison

Compare event histories such as:

1. pigment-first / ecological enabler;
2. environment-first / pigment follower;
3. pollinator-first mediation;
4. approximately synchronous transition;
5. independent recurrence under lineage-specific permissivity.

The goal is not to force one global sequence but to estimate which ordering classes recur across independent branches.

## 7. New hypotheses generated by the combined problem

### H_DUAL_LATENT

> Both the flower-colour state and the ecological boundary are noisy observation layers; treating either as error-free systematically overstates the precision of macroevolutionary associations.

Current status: **supported as a modelling requirement by separate empirical failures on both sides**, but a full joint model is not yet fitted.

### H_EVENT_ORDER_HETEROGENEITY

> The same accessible pigment network can participate in different branch histories: trait-first, environment-first, pollinator-first or recurrence without a major niche shift.

Current status: open. This replaces the assumption that one genus-wide correlation represents one evolutionary mechanism.

### H_INFORMATION_BOTTLENECK

> The limiting factor in testing micro-to-macro accessibility is not only sample size; it is the mismatch between rich molecular/sensory states and sparse/uncertain species-level ecological boundary evidence.

Current preliminary support:

- latent pigment seed has strongly structured missingness;
- boundary quality gates retain only 26/50 under the mild diagnostic gate and 17/50 under the strong gate;
- both climate-admitted Y species fail the n-based boundary gate.

### H_VISIBLE_HUE_MACRO_NULL

> Once provenance and within-lineage structure are respected, coarse visible A/W hue may carry little direct information about thermal niche evolution even though pigment-network deployment is highly labile mechanistically.

Current preliminary support:

- raw and provenance-clean A-W thermal means/tails are null;
- fixed-n tail resampling intervals cross zero;
- observation-uncertainty propagation crosses zero;
- section-relative niche-displacement tests are null.

This is stronger than saying `red is not cold-adapted`: it predicts that the biologically relevant macro signal, if present, lies in latent pigment/sensory dimensions or event ordering rather than visible hue itself.

## 8. Decisive next implementation

1. Expand the species-level pigment/sensory evidence matrix with explicit uncertainty/missingness rather than complete-case deletion.
2. Convert the environmental boundary table from one q05 value per species to estimate + uncertainty + provenance fields.
3. Recover/admit primary nuclear *Camellia* topologies and branch lengths.
4. Fit visible-hue and latent-state observation models on exactly the same admitted branches.
5. Compare event-order classes while integrating boundary observation error.
6. Model data availability/admission so missing yellow/rare lineages are not treated as random missingness.
7. Only then ask whether specific pigment-network nodes are reused on branches with validated ecological or pollinator shifts.

## 9. Claim boundary

Supported now:

> The project has empirical evidence that both sides of the intended macroevolutionary association are observed with biologically important compression/error. Coarse W/A/Y is not a unique functional state, and occurrence-derived climatic boundaries are provenance- and sample-size-sensitive. The current visible A-W macro signal remains unresolved/null under stronger checks.

Not yet supported:

- a fitted joint latent phylogenetic model;
- causal event ordering on any *Camellia* branch;
- superiority of one particular latent-state parameterization;
- a genus-wide absence of ecological selection on pigments;
- statistical-method novelty of the joint latent framework itself.
