# Evolution Letters v0.3 submission readiness — v0.1

## Current state

EL_V0_3_AUTOMATED_SUBMISSION_CHECKS_PASS_HUMAN_METADATA_HOLD

The science candidate remains frozen and unchanged.

The current Evolution Letters author guidelines were rechecked on 2026-09-29. The current Letter guidance is approximately 5,000 words, title 30 words or fewer, abstract 300 words max, up to 10 keywords, teaser text up to 150 words, required end matter, individual figure files, and alt text for all figures.

## Automated manuscript checks

- title: 11 words / 30 max
- teaser: 66 words / 150 max
- abstract: 246 words / 300 max
- keywords: 8 / 10 max
- approximate main text: 3,770 words / ~5,000-word Letter guide
- required end-matter headings: all present
- main figures: 5
- figure alt texts: 5

All automated content-format checks pass.

## Figure submission layer

The frozen science figure builder is not modified.

A separate exporter imports the frozen builder and writes the same five figure objects as individual vector PDF files for submission. This avoids changing any scientific input or plot construction while producing a journal-accepted vector format.

The original frozen PNG builder remains preserved.

## Remaining holds

Only human/external submission metadata remain:

### Phase 1 — author identity

- final author list and order
- full affiliations and addresses
- corresponding author name
- corresponding author email
- corresponding author postal address
- author ORCIDs

### Phase 2 — declarations

- CRediT roles for every author
- funding status and grant information, or explicit none
- acknowledgements, or explicit none

Conflict of interest is already populated as no conflicts.

### Phase 3 — archive

- submission-specific CHUN archive DOI
- archive version
- archive URL

No author identity, funding, CRediT role, acknowledgement, or DOI is inferred from repository history or model context.

## Next action after human metadata

Once Phase 1 and Phase 2 are supplied, populate the existing submission metadata scaffold, create the persistent archive identifier, then render the line-numbered final manuscript bundle.

No additional science is required for the current Evolution Letters v0.3 submission route.
