# Cross-radiation Evolution Letters submission metadata gate v0.1

## Current state

The scientific manuscript and journal-format checks are already at:

`SCIENCE_AND_JOURNAL_FORMAT_READY_METADATA_HOLD`

This gate does not change the science, the cross-radiation claim registry, the Evolution Letters v0.2 manuscript, or Camellia Paper 1.

Current metadata state:

`AWAITING_PHASE1_AUTHOR_IDENTITY`

## Phase 1 — author identity

Human-confirmed input is required before this phase can pass. The repository must not infer these fields from Git commits, account names, prior conversations, or institutional context.

Required:

- final ordered author list;
- each author's full affiliation assignment;
- full affiliation/institution addresses;
- each author's ORCID;
- corresponding author identity, email, postal address, and ORCID.

Once Phase 1 is complete, the validator advances automatically to `AWAITING_PHASE2_DECLARATIONS`.

## Phase 2 — declarations and CRediT

Required after Phase 1:

- acknowledgments text, or an explicit `None.`;
- funding status (`funded` or `none`) and, when funded, the funding-source/grant text;
- CRediT roles for every ordered author;
- conflict-of-interest declaration.

The current scaffold retains the manuscript's existing conflict-of-interest sentence but does not infer the other human declarations.

## Phase 3 — archive identifier

Required only after Phases 1 and 2:

- submission-specific archive DOI;
- archive version;
- archive URL.

A DOI or archive identifier must not be fabricated before a real persistent archive exists.

## Terminal state

The final state is:

`READY_FOR_FINAL_BUNDLE`

only when all three phases pass the machine validator.

## Validation

```bash
python scripts/validate_cross_radiation_el_submission_metadata_v0_1.py \
  --input submission/CROSS_RADIATION_EL_SUBMISSION_METADATA_V0_1.json
```

The validator reports missing fields by phase and enforces `do_not_infer_missing_human_metadata=true`.
