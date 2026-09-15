# Iochrominae biochemical exact-profile source access recheck — v0.2

## Goal

Recheck the exact public Dryad objects already frozen for the Iochrominae second-biochemical-anchor candidate without changing the biological admission rule or opening any archive data rows.

Source: `10.5061/dryad.p5dq84v`.

Required exact objects:
- README file id `108458`, 4,072 bytes;
- `Larter et al 2019 Dvdy Iochrominae development evolution DATA.rar`, file id `108456`, 3,054,999 bytes.

The expected digests remain those published by the Dryad file metadata and frozen in the v0.1 preflight receipt.

## Recheck rule

Use the same anonymous routes as v0.1:
1. Dryad public `stash/downloads/file_stream/{id}`;
2. Dryad REST `/api/v2/files/{id}/download`.

No credentials are added in this gate. No alternate/mirrored data file may be accepted unless exact object identity can be verified against the frozen file metadata.

## Outcome firewall

This recheck may inspect only dataset/file metadata and whether exact bytes pass size/digest checks. It must not:
- list DATA.rar member names unless both exact source objects are recovered;
- read archive data rows;
- define a new profile state mapping;
- compute profile states, patristic distances, AUCs, permutations, or a winner.

## Decision

If both exact objects are recovered, the next gate is README plus archive-member-name inspection before any outcome mapping is frozen.

If either remains inaccessible, retain source-access HOLD. A transport failure is not a biological negative.
