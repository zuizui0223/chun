# Ruellia 51-species source preflight v0.1

## Terminal pre-outcome state

`HOLD_TREE_SOURCE_OUTCOMES_UNOPENED`

The HPLC source required by the frozen Ruellia resolution-profile preregistration is publicly recoverable and its exact identity is now fixed. The exact timed phylogeny used by the author analysis is not present in the public Figshare v2 file manifest or in the public author-code Git tree checked here, so CHUN stops before identifier crosswalk and before row-level HPLC outcome ingestion.

This is a tree-source availability hold, not a biological negative and not a resolution-profile result.

## Frozen Figshare source identity

Figshare article id: `30282448`

Version: `10.6084/m9.figshare.30282448.v2`

| file | file id | bytes | MD5 | role |
|---|---:|---:|---|---|
| `raw_data.csv` | 58502635 | 130680 | `0e3b9830abb1378f9546cd7d07ae1f97` | **primary six-compound HPLC source** |
| `anthocyanins_spectra.csv` | 58502632 | 468339 | `bb76b658952017e1c30bc5b488068f63` | processed HPLC + reflectance companion |
| `ruellia_occurrences.csv` | 58520542 | 1210527 | `e1eeb161db7a735d88f5c016a15167f2` | occurrence companion |

Exact bytes for the two HPLC CSVs were downloaded and hash-verified, but the diagnostic parsed **header rows only**. No data row was read.

`raw_data.csv` contains the identifiers `hplc_id`, `tissue`, `species`, `spec_ID`, `phylo_ID`, and the six preregistered original compound columns: Pelargonidin, Cyanidin, Peonidin, Delphinidin, Petunidin, Malvidin. It is therefore frozen as the primary HPLC source. Prederived binary or pathway-branch columns from the processed companion are not used to define the primary CHUN states.

## Tree contract

At author-code commit `38bb511da1390bdd525a15ea8738bcc3f016fb59`, the phylogeny is read as:

`color data/color data/phylogeny/03-Ruellia_phylo.timed.tre`

The Figshare v2 manifest exposes only the three CSV files listed above. The author GitHub commit tree contains the analysis scripts but not `03-Ruellia_phylo.timed.tre`.

CHUN therefore does **not** substitute another Ruellia tree. A related topology, an untimed tree, or a reconstruction made after opening HPLC outcomes would change the frozen source contract.

## Outcome firewall

At this stop:

- row-level HPLC values used for CHUN profile: **no**;
- six-compound presence patterns: **not materialized**;
- PEL/CYA/DEL branch patterns: **not materialized**;
- state frequencies: **not computed**;
- AUCs: **not computed**;
- 9,999 permutations: **not run**;
- profile winner: **not assigned**;
- species-to-tree crosswalk: **not frozen**.

## Next gate

Resume only after exact `03-Ruellia_phylo.timed.tre` bytes, or an authoritative public object demonstrably identical to that author-code tree, is recovered. Then freeze tree identity/hash, tip labels, branch lengths, sample-to-species handling and identifier-only species-to-tree crosswalk before opening HPLC rows.

Camellia Paper 1 remains unchanged and closed.
