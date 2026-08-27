# Micro accessibility v0.2 — formal-database ascertainment update

## Trigger

The reproducible OpenAlex/Crossref/PubMed search completed in run `33039509237` recovered one previously omitted independent directed flower-colour literature system: Jiang et al. 2025, red versus white *Camellia semiserrata* (DOI `10.1007/s10722-025-02606-6`).

The study compares petals of red *C. semiserrata* with the white form `albiflora` using transcriptomic and chemical evidence. Six anthocyanins were reported in red flowers and none in white flowers, and eleven anthocyanin-biosynthesis structural genes were strongly downregulated in white flowers. Under the pre-existing canonical orientation white -> red, this supports **A = up**. F/C/P transcript-state directions remain unresolved.

No public raw RNA-seq accession was located in the 2026-08-27 database/open-web audit. CSEMISERRATA is therefore admitted to the **literature observation/accessibility layer only** and is not added to the frozen candidate-free standardized arm.

## Frozen analysis

The existing dependence-aware analysis script `scripts/analyze_micro_accessibility_v0_1.py` was rerun without algorithm changes using `data/micro_accessibility_edge_registry_v0_2.csv`. Hosted run: **`33040242009`**.

The validator `scripts/validate_micro_accessibility_v0_2.py` passed all precomputed numerical contracts.

## Updated literature ascertainment

### System level

- biological systems: **11** (old 10)
- A/F/C/P coverage: **9 / 4 / 1 / 3** (old 8 / 4 / 1 / 3)
- exact axis-symmetric null assignments: **21,233,664**
- exact P(A enrichment): **0.002788543701171875**
- exact P(any axis imbalance): **0.008607652452256944**

The formal-database addition therefore strengthens the evidence that published molecular observation is anthocyanin-heavy.

### Dependence-cluster level

- dependence clusters: **6** (old 5)
- A/F/C/P coverage: **5 / 3 / 1 / 2** (old 4 / 3 / 1 / 2)
- exact axis-symmetric null assignments: **2,304**
- exact P(A enrichment): **0.046875**
- exact P(any axis imbalance): **0.14583333333333334**

The important change is that anthocyanin enrichment now remains detectable after dependence collapse. The general maximum-minus-minimum imbalance statistic remains non-significant after collapse.

## Signature recurrence sensitivity

The same registry update also changes the older Simpson signature-recurrence sensitivity:

- system-level observed recurrence = **0.256198347107438**, permutation P = **0.0458954104589541**;
- dependence-collapsed observed recurrence = **0.2222222222222222**, permutation P = **0.198980101989801**.

The system-level result is descriptive because multiple systems share biological dependence backgrounds. The dependence-collapsed result remains the appropriate primary version and does **not** support a strong recurrent complete mechanism signature.

## What does not change

The candidate-free matched comparison remains exactly the same five public raw-data systems:

- `CJAPONICA`
- `CRETICULATA`
- `CSIN_WHITE_PINK`
- `CNITIDISSIMA`
- `CPERPETUA`

Therefore the Paper 1 common-set recurrence values do not change:

- anthocyanin gain candidate-free exact-signature recurrence = **0.333 exactly**;
- anthocyanin gain pairwise concordance = **0.333–0.5**;
- yellow candidate-free exact-signature recurrence = **0.5 exactly**;
- yellow pairwise concordance = **0.75 exactly**.

No macro phylogeny, wild-colour, topology, local-conservatism, or event-identifiability result changes.

## Revised inference

The database-backed literature expansion strengthens the observation-regime layer rather than weakening the main Paper 1 conclusion:

> **The published Camellia mechanism literature is nonuniformly anthocyanin-resolved even after dependence collapse, while the standardized five-system common-set analysis still rejects one invariant whole A/F/C/P package.**

The distinction is essential: broader literature coverage can update the observation-process estimate without silently changing the matched candidate-free biological comparison.

## Boundary

- Do not treat CSEMISERRATA as candidate-free until public raw reads are located and audited.
- Do not impute F/C/P from visible red/white colour or metabolite presence.
- Do not reinterpret the dependence-collapsed recurrence P=0.19898 as support for a repeated complete mechanistic signature.
- Do not alter any macro branch-causal gate from this literature-only update.
