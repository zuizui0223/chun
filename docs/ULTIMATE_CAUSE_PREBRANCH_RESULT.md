# Ultimate-cause pre-branch test result

This analysis tests ecological hypotheses **without inspecting the newly reconstructed nuclear topology**. The runtime91 roster is rebuilt from the frozen Wu v0.3 provenance manifest, the Fan 2026 visible-colour/section seed is rebuilt from public Data S1, and all null tests use 100,000 deterministic permutations (seed 20260820).

## Result

### H1 / ecological filtering: preliminary support

Among the 43 runtime91 taxa with stable visible-colour and unambiguous traditional-section labels, the anthocyanin-like A state has only 7 taxa but occupies only **2 sections**, versus **4.81092** expected under count-preserving random allocation. Breadth P = **0.00412**. A-state section HHI is **0.75510**, versus **0.25995** expected; HHI P = **0.00045**.

The macro realization of A is therefore strongly history-proxy concentrated. This supports ecological filtering / historical contingency, but traditional sections are not a substitute for the independent nuclear tree.

### H2 / simple direct cold adaptation: not supported

On the exact A/W + climate overlap (A=5, W=22):

- BIO1 median: A-W = **+0.475 C**, two-sided P = **0.86279**.
- BIO6 median: A-W = **-2.225 C**, two-sided P = **0.15738**. A colder one-sided P = **0.03168** before historical blocking.
- After section-block permutation, the BIO6 cold-direction P rises to **0.37350**.
- Within-section standardized climate distance is **2.19516** for different-colour pairs versus **2.29773** for same-colour pairs; different-minus-same = **-0.10256**, one-sided P for greater climate divergence = **1.0**.

Thus a weak apparent coldest-month signal is not robust once historical background is preserved. The simple model `anthocyanin-like visible colour -> direct cold adaptation` is rejected as a general explanation in this screen. This does **not** reject an indirect `climate -> reproductive niche/pollinator -> floral phenotype` model.

### H3 / molecular memory and pathway retention: compatible, supported at the accessibility level

Seven independent mechanistic clusters contain a white state. Across them:

- structural pathway loss required: **0/7**;
- explicit evidence that structural loss is not required: **2/7**;
- no evidence that structural loss is required: **5/7**;
- reversible within-genotype/developmental white-colour switches: **2 independent clusters**.

The evidence is therefore consistent with white states retaining access to pigment machinery and with colour being switched by regulation/flux rather than obligatory pathway deletion. This supports the molecular-memory/accessibility premise, but ancestral macroevolutionary reactivation is not yet demonstrated.

### H4 / lineage permissivity: preliminary support

The same A-state concentration statistic supports the idea that some historical backgrounds are more permissive for A realization/persistence than others. The decisive test is to replace traditional section with independently inferred nuclear branches after the species tree is admitted.

### H5 / yellow history dependence: unresolved in runtime91

Only 3 Y taxa occur in the runtime91 labelled subset: 2 sections observed versus 2.61529 expected; breadth/HHI P = **0.36194**. This subset is underpowered and does not supersede the broader Fan 2026 full-section concentration result.

## Current causal interpretation

The evidence now favors the following ordering of explanations:

1. **Molecular accessibility is broad**: colour changes can be produced repeatedly without requiring structural pathway deletion.
2. **Macroevolutionary realization is historically concentrated**: A states occur in far fewer historical backgrounds than expected by count alone.
3. **Simple direct climate adaptation is insufficient**: coarse visible-colour divergence does not robustly track thermal divergence after historical blocking.
4. Therefore the next falsifiable target is **lineage-specific permissivity plus ecological/reproductive filtering**, rather than a universal `cold -> anthocyanin` rule.

Final branch-level tests remain gated on the independent nuclear species tree and outgroup rooting. Pollinator-first / climate->pollinator->pigment ordering remains under-sampled until ecological anchor taxa are added to the frozen339 backbone.
