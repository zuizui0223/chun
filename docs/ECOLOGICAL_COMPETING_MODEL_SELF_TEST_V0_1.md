# Ecological competing-model self-test v0.1

## Aim

This is a `chun`-generated reanalysis of already frozen repository outputs. It does not add historical colour-transition branches and it does not treat literature-study counts as biological frequencies.

The question is deliberately narrower:

> **When the same repository evidence is forced through explicit competing predictions, which ecological explanation survives its own negative controls?**

Three models are compared:

1. `M_DIRECT_ANNUAL_CLIMATE` — coarse anthocyanin-like visible colour is directly tied to annual thermal niche;
2. `M_VISIBLE_HUE_SYNDROME` — coarse human-visible A/W/Y is itself the relevant pollination state;
3. `M_POLLINATOR_FILTER` — flowering-window environment modifies pollinator/reward conditions, latent floral sensory states affect pollinator behaviour, and effective service changes reproductive success.

The frozen decision rules are in `data/ecological_competing_model_contract_v0_1.csv`. Constraint counts are **not** interpreted as independent probabilities or a formal Bayes factor.

## Negative control 1 — coarse A/W colour does not improve climatic prediction

The provenance-clean A/W climate model table contains four preselected metrics:

- BIO1 median;
- BIO6 median;
- BIO6 q05;
- BIO1 IQR.

For each metric the self-test compares the frozen `colour` model directly against the `null` model by AIC. The rule is intentionally permissive: `M_DIRECT_ANNUAL_CLIMATE` gets credit if visible colour beats the null on even **one** of the four metrics.

Observed result:

> **colour AIC wins = 0/4.**

The independent history-aware diagnostic also fails the predicted direct-cold pattern:

- section-block cold-direction P = **0.37350**;
- within-section prediction that different-colour pairs are more climatically divergent: one-sided P = **1.0**, with the observed difference in the opposite direction.

### Additional history-conditioned AIC check

A second self-check asks a still more direct question: after a traditional-section history proxy is already in the model, does adding visible A/W colour improve fit?

Across the same four frozen metrics, `section+colour` is compared against `section` alone. Adding colour improves AIC in:

> **0/4 metrics.**

This check is intentionally descriptive because traditional section is only a coarse history proxy. Its value is that the same conclusion is recovered from model comparison rather than only from the permutation tests: coarse visible colour does not add detectable annual-climate information after the current history proxy is present.

Thus the direct annual-climate model fails a null-model prediction, a history-blocked directional test, and a history-conditioned AIC sensitivity. This does not reject flowering-window climate acting upstream through pollinators.

## Negative control 2 — visible hue is not a deterministic pollination state

The frozen seven-taxon primary pollination seed gives:

- exact hue × broad-pollinator-function association P = **0.485714**;
- **2/3** visible states represented by multiple taxa contain more than one broad pollinator-function class.

The exact P value is treated as unresolved association, not evidence of independence, because the seed is small and literature-ascertained. The deterministic proposition is nevertheless falsified by direct same-hue functional collisions.

Therefore `A/W/Y -> one pollination syndrome` does not survive as the ecological state representation.

## Positive self-test — pollinator-mediated filtering

The same fixed rules are then applied to the branch-safe causal-chain registry.

### PF1 — flowering-window environment -> pollinator/reward conditions

Supported.

The admitted layer contains **5 studies across 4 taxa**, exceeding the predeclared replication rule of at least two independent taxa.

### PF2 — latent/spectral state -> pollinator choice

Supported, but currently the weakest link.

Two independent Camellia behavioural studies are admitted: Mori et al. 2023 and Chen et al. 2020. They show strong pollinator-response differences despite the contrasted flowers remaining within the same coarse human-visible red class.

However, leave-one-study-out validation exposes the weakness cleanly: deleting either sensory study leaves only one study, so the two-study replication criterion fails in **2/2 leave-one-out deletions**.

Thus the latent-sensory link is replicated but not yet robustly over-replicated.

### PF3 — pollinator service -> reproductive success

Supported and leave-one-out robust.

Three independent wild Camellia systems spanning A/Y/W all show fruit-set RR > 1 under pollinator access:

- *C. japonica*: RR ≈ **6.35**;
- *C. petelotii*: RR ≈ **3.04**;
- *C. oleifera*: RR ≈ **2.29**.

The equal-weight geometric mean is **RR = 3.533**. Removing any one service evidence row still leaves at least two taxa with positive service effects under the frozen replication rule.

### PF4 — same-taxon environment/service bridge

Supported.

At least *C. petelotii* and *C. oleifera* occur in both the environment/reliability layer and the reproductive-service layer. This creates a branch-safe bridge without inventing an ancestral colour-transition event.

### PF5 — full same-system ecological chain

Unresolved.

No admitted taxon currently closes all three components:

`environment -> sensory/pollinator response -> fruit/seed fitness`.

This remains the decisive empirical gap.

## Leave-one-out result

The self-test removes one admitted evidence unit at a time and re-applies the minimum replication rules.

- environment -> pollinator reliability: **0** deletion failures;
- sensory state -> pollinator choice: **2/2** deletion failures;
- pollinator service -> reproductive success: **0** deletion failures.

The result is useful because it identifies the exact weak point instead of merely declaring the whole pollinator model “supported.”

## Competing-model verdict

Under the frozen constraint contract:

- `M_DIRECT_ANNUAL_CLIMATE`: **0 supported / 2 not supported**;
- `M_VISIBLE_HUE_SYNDROME`: **0 supported / 1 not supported / 1 unresolved**;
- `M_POLLINATOR_FILTER`: **4 supported / 0 not supported / 1 unresolved**.

The additional history-conditioned 0/4 AIC check is an orthogonal sensitivity and is not counted as an extra pseudo-independent constraint in those totals.

These counts are descriptive constraint survival, not a statistical model probability.

The strongest current `chun`-generated conclusion is therefore:

> **The repository data discriminate against a direct coarse-hue annual-climate model and against a deterministic visible-hue pollination syndrome. A context-dependent pollinator-mediated filter survives four independent component tests, but its latent-sensory link remains only two-study deep and no Camellia system yet closes sensory state -> pollinator response -> reproductive fitness in one causal chain.**

## Biological consequence

The current causal architecture should be written as:

`molecular accessibility`

`-> latent pigment / UV / fluorescence / reward phenotype`

`-> flowering-window environment x pollinator availability/effectiveness`

`-> reproductive success`

`-> differential persistence`

This is now stronger than a literature-motivated hypothesis because the competing coarse models fail repository-level negative controls and the surviving model has explicit leave-one-out diagnostics.

It still does **not** identify the cause of a particular accepted-species historical colour-transition branch. Paper 1's zero-shared-event ceiling remains unchanged.

## Next decisive self-test

Do not spend the next cycle adding more annual thermal points. The weakest-link analysis says the highest-value new evidence is another independent, preferably wild-system test that links a measured spectral/biochemical floral contrast to pollinator effectiveness and then to fruit or seed production.
