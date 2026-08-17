# C. sinensis white/pink reported-effect pilot

## Current result

The public PMC supplement for Zhou et al. 2020 was recovered successfully after following the current PMC deprecated OA-package fallback. The package checksum is frozen in the workflow artifact. Tables S6, S8 and S9 contain reported expression values that can be used before downloading all 30 raw FASTQ runs.

## Provenance conflict: Table S6 must not be used naively

Cross-table identity checks reveal that Table S6 assigns the same numeric expression triplets to the opposite BTP/ZJW headers relative to Tables S8 and S9.

Example 1, `CSNG38209` / DFR, stage 5:

- Table S8: ZJW = `11.749097, 13.202141, 11.02931`; BTP = `51.847836, 91.943451, 70.945137`; reported log2FC = `+2.519595`.
- Table S6 contains the exact same triplets but labels the low triplet BTP51/52/53 and the high triplet ZJW51/52/53.

Example 2, `CSA019984` / LAR, stage 2:

- Table S8 and Table S9 agree: ZJW = `7.44081, 6.026519, 8.048627`; BTP = `56.15473, 49.184815, 27.702047`; Table S8 log2FC = `+2.595145`.
- Table S6 again assigns the two triplets to the opposite genotype headers.

**Decision:** quarantine Table S6 for genotype-effect estimation. Use the mutually consistent S8/S9 orientation until the original source header provenance is independently resolved.

## Stage-resolved effect pattern from Table S8

The reported effects support a more nuanced version of the flux-reallocation hypothesis.

### Anthocyanin-side DFR

- stage 2: DFR `+1.872` log2FC (BTP pink > ZJW white);
- stage 3: two DFR loci `+2.081`, `+1.853`;
- stage 4: `+2.323`, `+2.370`;
- stage 5: `+2.520`, `+2.647`.

Thus the DFR red-direction effect strengthens and persists through later stages in this study.

### Flavonol-side FLS is stage/paralog dependent

- stage 2: `CSA008358/FLS` is **higher in pink** (`+1.352`);
- stage 3: `CSA006950/FLS` is **higher in white** (`-1.394`);
- stage 4: `CSA006950/FLS1` `-1.558`;
- stage 5: `CSA006950/FLS` `-1.375`.

Therefore the source does not support a simple stage-invariant rule `pink = DFR up / white = FLS up`. Instead it supports **paralog- and stage-specific flux redistribution**.

### Proanthocyanidin-side LAR/ANR

At stage 2, multiple LAR loci and ANR are also higher in BTP pink (`+1.78` to `+2.60` for admitted LAR; ANR `+2.18`). Two LAR loci remain higher in pink through stages 3–5.

This means the pink state is not described by a one-dimensional anthocyanin-versus-PA antagonism either. Multiple downstream branches can be co-activated, with their relative allocation changing through development.

## Annotation conflict

`CSA011508` is labelled `LAR`, `FLAR`, and `LAR` in different S8 stage sheets, while KEGG/Swiss-Prot annotations point to K05277/leucoanthocyanidin dioxygenase/ANT17 (ANS-like). It is quarantined from LAR/ANS module scores until common orthology is validated.

## Connection to the current meta-analysis

This pilot strengthens, but also sharpens, `H_ACC`:

- strong recurrent regulatory/flux accessibility remains supported;
- DFR red-direction deployment is quantitatively clear in this white/pink system;
- the biologically useful unit is a **stage- and paralog-resolved module state**, not one gene name or one visible colour label;
- common raw/processed reanalysis must validate sample orientation and orthology before calculating pooled module effect sizes.

The result therefore supports the project's move from qualitative vote counting to a common module effect model, while preventing a false simplification of `anthocyanin branch versus FLS/PA branch`.

## Next analysis gate

1. validate BTP/ZJW orientation against archive sample metadata and source methods;
2. use S8/S9, not S6 headers, for the reported-effect seed;
3. establish a common ortholog map for DFR, FLS, ANS, UFGT, LAR and ANR;
4. compute stage-matched module effects with stages nested within the `CSIN_WHITE_PINK` independence cluster;
5. then repeat the same extraction for other public processed/raw datasets.

No macroevolutionary causal claim is changed by this pilot.
