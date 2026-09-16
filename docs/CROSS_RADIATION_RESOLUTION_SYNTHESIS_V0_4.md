# Cross-radiation resolution synthesis — v0.4

## Central claim

> **Flower-colour evolution has no universal biological resolution at which phylogenetic predictability is maximized. Resolution profiles vary among biological units even under standardized estimators, and the first completed biochemical cross-representation profile also selects fine rather than intermediate resolution.**

This retains the v0.3 conclusion while adding one completed cross-representation anchor and one subsequently executed biochemical applicability test. It does **not** establish that biochemical representations generally favour fine resolution.

## Evidence sequence

### 1. Discovery produced a falsifiable intermediate-resolution rule

Earlier conditional-hierarchy analyses suggested that biologically meaningful organization could emerge below a very coarse colour boundary. That motivated the stronger unconditional prediction that predictability might peak at an intermediate resolution across radiations.

### 2. Iris prospectively falsified a universal intermediate optimum

The fourth-radiation Iris test was frozen before row-level outcome ingestion and terminated `FAIL`:

- coarse AUC = `0.4617285166`;
- intermediate AUC = `0.4543945669`;
- fine AUC = `0.4870504419`.

Intermediate was below 0.5 and below fine; the frozen fail-side fine-over-intermediate test was significant (`P = 0.0486`). This rejects a universal intermediate optimum without converting fine into a successful Iris signal.

### 3. A standardized many-clade visible-colour batch shows heterogeneous profiles

Under one visible-colour ontology and one exact pipeline, 28 Flower-clades units completed the three-resolution profile:

| terminal class | completed clades |
|---|---:|
| `PROFILE_SIGNALLED_COARSE` | 3 |
| `PROFILE_SIGNALLED_INTERMEDIATE` | 0 |
| `PROFILE_SIGNALLED_FINE` | 3 |
| `PROFILE_SIGNALLED_TIED` | 6 |
| `PROFILE_NO_PHYLOGENETIC_SIGNAL` | 16 |

Twenty-three additional clades stopped at the frozen insufficient-frame/state-variation HOLD.

Thus even within one representation and source protocol, the profile is heterogeneous rather than a single preferred scale.

### 4. Simple tree geometry does not predict the heterogeneity

Four outcome-independent one-predictor candidates — log tip number, pair-distance CV, branch-length CV and root-to-tip CV — were required to improve leave-one-clade-out RMSE over intercept-only for both independent profile contrasts. Zero of four qualified.

The negative result means the tested simple tree geometry does not explain the profile differences. It does not prove that no biological moderator exists.

### 5. Petunieae provides the first completed biochemical cross-representation anchor

A separate three-resolution biochemical hierarchy was frozen on the already-audited Wheeler et al. Petunieae source before this profile AUC was computed:

- coarse = any of six anthocyanidins present vs none;
- intermediate = PEL/CYA/DEL anthocyanidin-class presence pattern;
- fine = exact six-compound presence pattern.

This analysis is **retrospective standardized training**, not a new prospective replication, because the underlying source values had previously been inspected for a different molecular-subspace estimand.

After applying the frozen rare-fine-state rule, 47 tips remained. On that common frame, coarse and intermediate collapsed to the same binary partition (6 absent / 41 present), whereas fine retained six common compound patterns.

Result:

- coarse AUC = `0.518925563507132`, signal p = `0.1985`;
- intermediate AUC = `0.518925563507132`, signal p = `0.1985`;
- fine AUC = `0.6995630849367751`, signal p = `0.0001`;
- fine minus runner-up = `0.18063752142964307`, joint-permutation p = `0.0001`;
- terminal class = **`PROFILE_SIGNALLED_FINE`**.

The scientific point is narrow but important: when the phenotype state space is defined biochemically rather than as human-visible colour, fine compound composition can carry strong phylogenetic same-state structure that is lost by coarser presence summaries.

This strengthens representation dependence but does **not** justify a general `biochemical -> fine` rule from one completed biochemical radiation.

### 6. Solanaceae tests the same programme boundary but does not yield a second completed biochemical profile

The red-flowered Solanaceae candidate was preregistered before its Table S1 chemistry outcomes were opened. After the frozen source/tree gate was solved using archived TreeBASE study S16617, 25 exact source/tree matches were available and 24 had complete chemistry required for the hierarchy.

The fine representation was the preregistered joint state `(CAROTENOID_PRESENT, PELARGONIDIN_PRESENT, CYANIDIN_PRESENT, DELPHINIDIN_PRESENT)`. Ten fine states were observed, with support counts from 1 to 4 taxa. Because the frozen primary rule required at least 5 taxa per fine state before constructing the identical common frame, **all ten states were excluded and the retained frame contained 0 tips**.

Terminal class:

`HOLD_INSUFFICIENT_COMMON_FRAME_OR_STATE_VARIATION`

No AUC, permutation p-value, or winner was computed. This is not a biochemical negative and it does not become a second completed biochemical observation. Relaxing the threshold or merging states after seeing the chemistry would be post-hoc rescue and is excluded from the primary programme.

This result adds an applicability boundary: representation granularity is constrained not only by biology but also by whether the source contains enough replicated state support for the predeclared estimator.

### 7. Representation type is variable but not yet predictively identifiable

The exact-profile universe still contains **30 completed biological units**:

- 28 standardized visible-colour clades;
- 1 biochemical-composition unit (Petunieae);
- 1 mixed pigment/hue prospective unit (Iris).

This is enough total replication but not enough replication of representation classes. In an honest leave-one-out fold with Petunieae held out, the training set contains zero completed biochemical observations. The Solanaceae HOLD supplies no response value and cannot fill that fold.

A biochemical-vs-visible category effect therefore cannot be learned and then used to predict the held-out biochemical unit. Accordingly CHUN does **not** fit a representation-type moderator yet. Iris is not relabelled as biochemical simply to manufacture a second biochemical observation.

### 8. Applicability and source boundaries remain informative

- **Solanaceae red 27** — source/tree recovery succeeded, but the frozen common-frame gate terminated `HOLD_INSUFFICIENT_COMMON_FRAME_OR_STATE_VARIATION`; no AUC or winner.
- **Iochrominae** — exact frozen Dryad source bytes remain unavailable through the tested anonymous routes.
- **Gesnerioideae** — remains `HOLD_SCHEMA_SOURCE_AXES_NOT_NESTED`: its available pigment chemistry and visible/reflectance layers do not instantiate one outcome-independent nested ladder.
- **Ruellia** — has a frozen biochemical hierarchy and HPLC source but lacks the authoritative 2023 ddRAD tree required by the author analysis.
- **Rhododendron** — has a frozen biochemical hierarchy and primary-tree metadata but remains source-access blocked before chemistry opening.

These holds are not biological negatives.

## Integrated inference

The strongest current statement is:

> **Evolutionary predictability of flower-colour phenotypes is representation dependent, but no universal optimal resolution is supported. A preregistered intermediate-resolution rule failed prospectively in Iris; a standardized visible-colour batch produced coarse, fine, tied and no-signal profiles with zero unique intermediate winners; simple tree geometry failed to predict those differences; an independently standardized biochemical Petunieae profile selected fine compound composition rather than coarser biochemical summaries; and a second preregistered biochemical candidate stopped at its frozen support gate rather than being post-hoc rescued.**

What is still unresolved is whether representation class itself predicts the profile. One completed biochemical observation is insufficient for that test.

## Novelty boundary

Do not claim:

- a universal fine-resolution optimum;
- that biochemical representations generally favour fine resolution;
- that the Solanaceae HOLD is evidence against a biochemical profile;
- that Petunieae is a new prospective replication;
- that tree geometry can never explain resolution profiles;
- that every flower-colour system admits a single nested hierarchy.

The stronger empirical contribution is the disciplined sequence of hypothesis generation, prospective falsification, standardized many-unit replication, failed moderator qualification, cross-representation extension, and preservation of a failed support gate without post-hoc upgrading.

## Updated figure spine

1. Discovery and hierarchy distinction.
2. Iris prospective falsification.
3. Standardized 28-clade visible-colour profile map.
4. Visible-colour terminal-class summary: 3 coarse / 0 intermediate / 3 fine / 6 tied / 16 no signal.
5. Tree-geometry moderator failure.
6. Petunieae biochemical profile: coarse/intermediate collapse versus fine AUC `0.6996`.
7. Solanaceae applicability panel: 25 exact matches → 24 chemistry-complete → 10 fine states, each n=1–4 → 0 retained at frozen n>=5 support rule → structural HOLD.
8. Representation-identifiability panel: visible `n=28`, biochemical completed `n=1`, mixed `n=1`; categorical moderator blocked until a second non-visible exact-profile system is completed.
9. Remaining Iochrominae/Ruellia/Rhododendron boundary and next-gate panel.

## Working title

**No universal scale of predictability in flower-colour evolution**

Alternative:

**The informative scale of flower-colour evolution depends on phenotypic representation**

## Next gate

Do not open another held-out profile merely to increase n and do not post-hoc rescue Solanaceae. The next information-bearing milestone is a **second independent completed biochemical or otherwise non-visible exact-profile system** that survives its frozen common-frame/state-variation gate.

Iochrominae, Ruellia and Rhododendron remain the bounded source-faithful routes if their currently missing authoritative inputs become available. Only after that second completed replication exists should representation type be evaluated as a one-predictor moderator under leave-one-out validation and, if it qualifies, used to freeze a new held-out prediction.

Camellia Paper 1 remains unchanged.
