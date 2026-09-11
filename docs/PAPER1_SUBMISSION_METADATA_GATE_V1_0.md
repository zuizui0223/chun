# Paper 1 submission metadata gate v1.0

Checked: 2026-09-11.

## Purpose

Paper 1 science is closed. The only active first-submission gate is Issue #85. This gate turns the remaining human submission inputs into one explicit, machine-readable contract without inferring missing author information.

Input file: `submission/PAPER1_SUBMISSION_METADATA_V1_0.json`.

## Phase 1 — author identity

Required before any metadata-complete manuscript regeneration:

- final ordered author list;
- each author's affiliation IDs;
- full affiliation institution names and unabbreviated addresses;
- corresponding-author name, email, postal address, and ORCID.

The corresponding author must match one ordered author. ORCID must use the `0000-0000-0000-0000` form. No missing value is inferred from repository history, account metadata, prior drafts, or model memory.

Current state is `AWAITING_PHASE1_AUTHOR_IDENTITY`.

## Phase 2 — declarations

After Phase 1, record only author-approved values:

- acknowledgments;
- funding status and sources;
- CRediT roles for every author;
- conflict-of-interest declaration;
- originality / no simultaneous submission confirmation;
- all-author approval of submitted version and order;
- preprint status/details;
- final generative-AI disclosure after reviewing the then-current journal/Wiley policy.

The validator uses the standard 14-role CRediT vocabulary and will not invent roles.

## Phase 3 — archive

After a permanent versioned archive is minted, record:

- archive DOI;
- archive version;
- archive URL.

A GitHub tag or release alone is not treated as a DOI. The DOI remains an external archival action until actually minted.

## Validator behavior

Run:

```bash
python scripts/validate_paper1_submission_metadata_v1_0.py \
  --input submission/PAPER1_SUBMISSION_METADATA_V1_0.json \
  --summary build/paper1_submission_metadata_gate_v1_0.json
```

This command succeeds for a structurally valid but incomplete metadata file and reports the exact missing fields. It fails on schema drift, malformed supplied values, inconsistent author/affiliation references, or any attempt to mark the stored state more advanced than the supplied metadata support.

Use `--require-phase1` before inserting author identity into manuscript/cover-letter outputs, and `--require-complete` before generating a final metadata-complete submission bundle.

## Scientific firewall

This metadata gate must not modify:

- science v0.2.2;
- framing v0.3.4;
- candidate-free recurrence estimates;
- yellow-development estimates;
- macro-pattern or event-identifiability results;
- main figure inputs or reference registries.

Only author/declaration/archive/presentation fields may advance under this gate.
