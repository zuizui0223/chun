# Gesnerioideae source acquisition / schema gate — v0.1

## Goal

Acquire the source supplementary workbooks for the already-preregistered fifth-radiation resolution-profile test without opening row-level outcome values before the state-mapping contract is frozen.

## Frozen upstream analysis

The scientific test is already fixed in:

- `data/gesnerioideae_resolution_profile_prereg_v0_1.json`;
- `docs/GESNERIOIDEAE_RESOLUTION_PROFILE_PREREG_V0_1.md`.

Source DOI: `10.3389/fpls.2020.604389` (Ogutcen et al. 2020).
PMCID: `PMC7767864`.

The preregistration defines a common-frame coarse/intermediate/fine same-state AUC analysis with joint permutation and explicitly requires a schema HOLD rather than outcome-dependent recoding if three nested levels cannot be instantiated defensibly.

## Acquisition route

The workflow resolves the current article-version prefix from the NIH/NLM PMC Article Datasets public S3 bucket (`pmc-oa-opendata`) and downloads only XLSX objects under that version. The selected prefix and every object key/size/ETag are recorded.

This uses the post-August-2026 PMC Article Dataset structure; no retired PMC OA API/FTP route is used.

## Outcome firewall

This stage may inspect only:

- article-version/object metadata;
- workbook filenames and checksums;
- worksheet names;
- workbook dimensions;
- the first plausible header row within rows 1–12.

Cells below the detected header row are not inspected or emitted. No species-level hue, anthocyanin composition, sample frequency, phylogenetic AUC, permutation result or winning resolution is calculated here.

## Next gate

After the schema artifact is recovered:

1. identify which workbook/sheet contains the terminal trait table;
2. freeze the semantics-only mappings for coarse, intermediate and fine states using column names and source definitions;
3. separately acquire/freeze the branch-length tree and taxon crosswalk;
4. only then open row values and run the preregistered same-estimand analysis.

If the schema cannot support the three nested levels without arbitrary outcome-dependent recoding, return `HOLD_SCHEMA` and stop.

## Paper boundary

Post-Paper-1 work only. Camellia Paper 1 science and submission bundle remain unchanged.
