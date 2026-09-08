# Epimedium same-radiation endpoint bridge v0.1

## Result

The existing source-audited reproductive table and the existing eight-species common molecular panel overlap for **6 species**.

Among those six:

- three A+ species have source joint organ codes `2:2` or `3:3`;
- three A− species (*E. franchetii*, *E. lishihchenii*, *E. wushanense*) all have the same source joint organ code `1:1`;
- within the three A− taxa, `ANS` is low in **3/3**, `DFR` is low in **2/3**, and the CHS implementation is different in every taxon: no A−-specific CHS change / `CHS2_LOW` / `CHS1_LOW`.

Thus the endpoint-level result is:

> `SAME_SOURCE_ENDPOINT_CODE_WITH_RECURRENT_CORE_AND_HETEROGENEOUS_MOLECULAR_IMPLEMENTATION`

This independently matches the general pattern that a coarse visible endpoint can hide molecular heterogeneity while retaining a recurrent core.

## Strict boundaries

This is **not** an event-level recurrence estimate.

- Historical transition direction is not established.
- The three A− taxa are not counted as three independent losses.
- Exact molecular individuals are not matched to the 699-individual reproductive records.
- The source reproductive colour codes remain nominal: `source_code_to_hue = UNRESOLVED_CODEBOOK_NO_HUE_IMPUTATION`.
- *E. acuminatum* and *E. leptorrhizum* carry external colour-variation warnings in the existing audit.

The historical event-independence gate therefore remains `FAIL / HOLD`.

## Relation to Iochrominae

Iochrominae provides a same-radiation phenotype-dimension bridge: pigment presence/intensity and hue map to different molecular subspaces.

Epimedium provides a different, complementary endpoint bridge: the same source-level endpoint among overlapping A− taxa retains a common core (`ANS`) but separates at lower molecular resolution (`DFR`, CHS copy, FLS allocation).

These are **not exchangeable replicates of one estimator**. Together they justify a mechanistic compatibility statement, not a pooled recurrence proportion or universal molecular law.

Paper 1 remains unchanged.
