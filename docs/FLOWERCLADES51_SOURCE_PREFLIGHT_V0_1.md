# Flower-clades-51 source preflight v0.1

## Terminal preflight state

`HOLD_SOURCE_ACCESS_OUTCOMES_UNOPENED`

The standardized 51-clade resolution-profile rule was frozen on `main` before CHUN opened species-level `flower_color` values. This preflight resolves the exact Dryad dataset version and expected source files, but machine retrieval of the published bytes is intercepted by Dryad's Anubis validation page.

This is an access hold, not a source-data mismatch, biological negative, or profile result.

## Frozen source identity

Dataset DOI: `10.5061/dryad.r4xgxd2sc`

Version id: `402189`

| file | Dryad file id | bytes | SHA-256 |
|---|---:|---:|---|
| `final_dataset.csv` | 4411881 | 118867 | `a253308785e4cbd0e361b3ca04cdfdae29c523eefa843375cebf8030ee0874af` |
| `trees.zip` | 4411880 | 80326 | `ae5c82945e5bf9c29bcabc52d6029acd8d4f5be1fe9141fad95918eacb4f674d` |

The public file-stream endpoints returned HTTP 200 with a 4329-byte HTML `Validating...` page rather than the source bytes. The diagnostic identifies the Anubis proof-of-work interstitial. Therefore the earlier digest mismatch was a client-side source-access classification error, not evidence that Dryad's published digest is wrong.

## Outcome firewall

At this terminal preflight state:

- species-level `flower_color`: not opened or emitted;
- `fruit_color`: not opened or emitted;
- clade colour frequencies: not computed;
- coarse/intermediate/fine states: not materialized;
- AUCs: not computed;
- profile winners: not computed;
- identifier/tree crosswalk: not frozen;
- resolution-profile result directory: absent.

## Next gate

Resume only after exact `final_dataset.csv` and `trees.zip` bytes matching the frozen SHA-256 digests are available through a legitimate source path. The first resumed analysis remains identifiers/tree-only: freeze clade-to-tree mapping, normalized species crosswalk, duplicate handling, and join diagnostics before opening `flower_color`.

No anti-bot mechanism is bypassed and no alternative dataset version is substituted.

Camellia Paper 1 remains unchanged and closed.
