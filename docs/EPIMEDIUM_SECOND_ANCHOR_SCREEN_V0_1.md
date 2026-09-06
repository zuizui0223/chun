# Epimedium second-anchor screen — v0.1

## Question

Can *Epimedium* sect. *Diphyllon* serve as a second mechanistic anchor for the Camellia result that repeated flower-colour endpoints show hierarchical, module-level molecular repeatability rather than one invariant whole programme?

Two gates are deliberately separated:

1. **common-panel mechanistic gate** — do A− species measured under the same candidate panel share some modules but not one complete implementation?
2. **historical event-independence gate** — can the A− species be assigned to >=3 defensibly independent colour-transition events across competing phylogenetic evidence?

The first can pass while the second fails.

## Common observation regime

Mi et al. 2023 (`10.3389/fpls.2023.1133616`) measured eight species grown in a common garden. Four were classified A+ and four A−. Floral material included petaloid sepals and spur-like petals. HPLC and one transferred 12-gene anthocyanin-pathway qRT-PCR panel were applied across species.

This is **not candidate-free RNA-seq**. It is a common, candidate-defined observation regime. Its strength is that all eight species were interrogated with the same predefined panel; its limitation is that unmeasured pigment-network modules remain outside the observation space.

The paper spelling `E. epstenii` is normalized to the accepted name *E. epsteinii*.

## Mechanistic result

Across the four A− species (*E. sagittatum, E. lishihchenii, E. franchetii, E. wushanense*):

- detectable floral anthocyanins: **0/4**;
- ANS significantly lower than A+ species: **4/4**;
- DFR significantly lower than A+ species: **3/4**; *E. lishihchenii* is the explicit exception;
- explicit A−-specific CHS suppression: **2/4**, but at different copies — CHS2 in *E. franchetii* and CHS1 in *E. wushanense*;
- increased FLS associated with low DFR: **2/4** (*E. franchetii*, *E. wushanense*);
- *E. sagittatum* DFR/F3'H coding products retain catalytic activity in Arabidopsis complementation assays, supporting a regulatory rather than simple coding-null explanation for that species.

At a broad qualitative module level, *E. franchetii* and *E. wushanense* share the same pattern `ANS low / DFR low / CHS-family low / FLS diversion high`, so the maximum broad-signature recurrence among the four A− species is **2/4**. Once CHS copy identity is retained, those two signatures separate (`CHS2` vs `CHS1`), and no complete copy-aware qualitative signature is shared by more than one A− species.

This is a diagnostic summary of one common candidate panel, not a formal estimate of evolutionary event recurrence.

## Interpretation

The panel supports a strong external version of the Camellia hierarchy:

`same anthocyanin-depleted endpoint`

`-> highly recurrent core module (ANS 4/4)`

`-> partially recurrent downstream module (DFR 3/4)`

`-> heterogeneous flux/upstream implementation (CHS/FLS species-specific)`.

Thus endpoint recurrence does not imply one invariant full molecular programme even when all species are measured under the same assay panel.

## Historical event-independence gate

This gate is **FAIL / HOLD** at v0.1.

Reasons:

- the 2014 AFLP analysis separates *E. sagittatum* into a Brachycerae-dominated clade while *E. franchetii, E. lishihchenii,* and *E. wushanense* occur in the broad clade-1 context;
- plastome analyses instead recover geographically structured relationships and can place *E. sagittatum* near *E. lishihchenii/E. wushanense*;
- the 45-plastome analysis reports dispersed/non-monophyletic populations for *E. sagittatum* and weak support around several relevant species;
- modern GBS work shows extensive topology conflict and introgression within sect. *Diphyllon*;
- recent species-delimitation work reports non-monophyly in sampled *E. franchetii* and *E. sagittatum*;
- several relevant species belong to historically difficult taxonomic complexes.

Therefore the four A− species must **not** be promoted to four, three, or any fixed number of independent historical loss events from the present evidence. Direction itself is also not frozen: use `A− endpoint` rather than `anthocyanin loss event` until ancestral state and event identity are robust.

## Verdict

- **External common-panel mechanistic validation:** PASS.
- **Second independent historical-transition anchor:** FAIL / HOLD.
- **Role retained for the atlas:** high-value molecular endpoint panel plus organ-aware macro system.

This is useful rather than disappointing: it independently reproduces the pattern/event distinction central to Camellia Paper 1. A mechanistic pattern can be strong while event identity remains weak.

## Next step

1. extract the 699-individual organ-resolved macro trait table;
2. retain this eight-species panel as a common-measurement molecular layer;
3. do not estimate event-level recurrence from these four A− species unless a topology/event gate later passes;
4. continue searching for a white-like ancestral clade with both robust repeated events and >=3 molecular contrasts.

Paper 1 remains unchanged and closed.
