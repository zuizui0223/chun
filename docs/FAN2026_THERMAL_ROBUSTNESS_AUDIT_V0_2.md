# Fan 2026 Camellia thermal robustness audit v0.2

## What this audit adds

The initial species-scale thermal analysis admitted 51 GBIF-linked taxa. Two independent robustness checks were then run:

1. **taxonomy exactness:** require GBIF `rank=SPECIES`, `matchType=EXACT`, and a unique accepted usage key;
2. **occurrence provenance:** retain only preserved specimens/material samples/material citations rather than the broader wild-like occurrence set.

These checks test whether the A(red/pink)-versus-W(white) null result was created by fuzzy taxonomy, duplicate synonyms, observations, or residual cultivation records.

## 1. Exact-taxonomy result

The live GBIF audit rejected exactly one admitted name:

- `Camellia kissi` → FUZZY match to accepted *C. kissii* (same usage key).

Final independent taxon sample:

- total = **50 species**;
- A = **14**;
- W = **34**;
- Y = **2**.

Frozen result: `data/fan2026_chelsa_exact_taxon_tests_v0_2.csv`.

### A versus W

- BIO1 median: A−W = **+0.178 °C**, two-sided **P=0.7846**;
- BIO6 median: A−W = **−0.526 °C**, **P=0.5544**;
- BIO6 q05 cold tail: A−W = **−0.638 °C**, **P=0.6968**;
- BIO1 IQR breadth: A−W = **−0.185 °C**, **P=0.6265**.

Thus exact taxonomy does not reveal a hidden thermal separation between anthocyanin-like red/pink and white species.

The coarse section-block sensitivity also remains non-directional: the two sections containing both A and W states split direction for BIO1/BIO6 position metrics; exact sign `P=1.0`.

## 2. Specimen-only sensitivity

The specimen-only run retains `PRESERVED_SPECIMEN`, `MATERIAL_SAMPLE`, and `MATERIAL_CITATION` records after the same country/geospatial filtering.

Frozen result: `data/fan2026_chelsa_specimen_sensitivity_v0_1.csv`.

A versus W:

- BIO1 median: **P=0.7462**;
- BIO6 median: **P=0.5857**;
- BIO6 q05: **P=0.5273**;
- BIO1 IQR: **P=0.7479**.

The null A–W result therefore persists when human observations and other non-specimen occurrence classes are removed.

## 3. Robust conclusion

Across the main 51-species screen, the exact-taxonomy 50-species audit, the specimen-only sensitivity, and the close *C. japonica–C. rusticana* counterexample:

> **Visible anthocyanin-like red/pink versus white floral state does not explain a general shift to colder thermal niches in Camellia.**

This is now substantially more defensible than the original hypothesis that anthocyanin might generally enable cold-climate expansion.

The result does **not** show that anthocyanin has no cold/UV physiological function. It shows that whatever such functions exist do not translate into a simple genus-wide mapping from visible red/pink flower state to colder species climatic niche.

## 4. What survives

The surviving cross-scale model is:

`molecular accessibility -> recurrent pigment phenotype generation -> ecological/historical filtering -> persistence`

This model is supported by the contrast between:

- very strong micro/mechanistic recurrence of pigment regulatory/flux changes; and
- weak/conditional macro climatic association.

Yellow remains different: Data S1 shows strong southern geographic confinement, and the small GBIF-admitted Y subset is warmer-centred in BIO6. However only two Y species survive the direct thermal gate, both in Sect. Chrysantha/South China, so the current robust result is **yellow historical/geographic restriction**, not a demonstrated yellow adaptive thermal optimum.

## 5. Remaining phylogenetic question

The next unresolved question is no longer whether A and W differ in present-day thermal niche; this analysis says they do not detectably differ.

The remaining evolutionary question is whether **particular transition branches** show transient or lineage-specific niche shifts that disappear in genus-wide averages. That requires a machine-readable nuclear tree/chronogram and event-centred modelling.

Any DateLife/OpenTree analysis is treated only as a secondary sensitivity because it is a synthetic chronogram, not the primary 405-gene Camellia nuclear tree.
