# Pollinator-filter study-level direction consistency v0.1

## Question

Does the pollinator-service/reliability layer depend on one large study or on counting multiple correlated effect rows from the same study?

This is a CHUN-generated diagnostic built from the frozen ecological effect registry. It does **not** estimate a biological support frequency and it does not correct publication or study-selection bias.

## Independence rule

Each independent study contributes exactly one vote.

- Kunitake 2004 — *C. japonica* bird access vs exclusion;
- Sun 2017 — *C. petelotii* bird access vs exclusion;
- Zhang 2024 — *C. oleifera* bird access vs exclusion;
- Liu 2025 — independent *C. oleifera* honeybee cage experiment;
- Chai 2019 — *C. pubipetala* pollen supplementation vs open pollination;
- Xie 2013 — *C. oleifera* legitimate visit density vs pollen limitation;
- Li 2021 JAE — *C. oleifera* wild-bee abundance / nest-distance gradients.

Li 2021 contains four registered coefficients across two years. Those four coefficients are **not four votes**: the study receives one vote only if all four coefficients have the predeclared service-limitation direction.

The exact frozen contract is `data/pollinator_filter_direction_contract_v0_1.csv`.

## Result

All **7/7 independent study clusters** have the predicted direction.

Under a diagnostic 0.5 sign null, the one-sided exact value is:

- **P = 0.0078125**.

Leave-one-study-out is also complete:

- every deletion leaves **6/6** studies in the predicted direction;
- the corresponding one-sided exact sign value is **P = 0.015625** for every deletion.

## Interpretation

The ecological-filtering evidence is not being driven by one study or by within-study coefficient multiplication. Pollinator availability/access or pollen delivery repeatedly covaries with reproductive service in the predicted direction across independent designs and four represented taxa.

This strengthens the **service/reliability** part of the causal chain. It does not strengthen the sensory-state link directly, and it does not establish that pollinators caused a particular historical flower-colour transition.

## Claim ceiling

Use this only as a directional reproducibility diagnostic. The study set is literature-ascertained, publication bias is not estimated, and 7/7 must not be written as a genus-wide biological frequency. Historical transition causation remains governed by the zero-shared-event gate.
