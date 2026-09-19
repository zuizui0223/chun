# Rhododendron30 source-access recheck — v0.3

## Current result

`HOLD_SOURCE_ACCESS_STILL_BLOCKED_OUTCOMES_UNOPENED`

The source identities themselves are publicly verifiable:

- Plant Biology Table S3: `plb12649-sup-0002-TableS3.docx`, listed as 35.9 KB;
- Dryad primary tree: `1_WP_RAxML.tre`, listed as 13.10 KB.

The 2026-09-19 hosted recheck nevertheless could not recover exact bytes.

### Species-identity supplement

All five frozen Wiley routes returned HTTP 403. No genuine DOCX was admitted and no Table S1 chemistry was opened.

### Primary tree

The frozen Dryad file is still file id 1853438 with expected SHA-256:

`784011d0e2e17df9ea21eb22d31197bad29219a37ac213fda013766e29b51362`.

Current route diagnostics:

- Dryad API file download: HTTP 401;
- stash file-stream route: HTTP 200 but non-tree HTML payload.

No payload matched the frozen digest.

## Outcome firewall

Still unopened:

- Table S1 chemistry;
- row-level anthocyanin values;
- flower color and CIELAB outcomes;
- compound-presence states;
- state frequencies;
- AUCs, permutations and winner.

## Decision

Do not substitute another tree, infer species identities from chemistry rows, or weaken the source gate.

Rhododendron30 remains a valid future held-out biochemical candidate if exact transport becomes available, but it is not executable now.

Frozen EL v0.3 and Camellia Paper 1 remain unchanged.
