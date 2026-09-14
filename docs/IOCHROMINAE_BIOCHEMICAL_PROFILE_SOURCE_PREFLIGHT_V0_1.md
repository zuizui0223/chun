# Iochrominae biochemical profile source preflight v0.1

## Purpose

Test whether the existing Iochrominae Dryad package can supply a second independent non-visible exact-profile system without inventing a new source or changing the current resolution-profile estimator.

This step is source/schema preflight only. It does **not** calculate a new Iochrominae resolution profile.

## Source

Primary package:

- Larter et al. 2019, *Developmental control of convergent floral pigmentation across evolutionary timescales*;
- Dryad DOI `10.5061/dryad.p5dq84v`;
- expected archive `Larter et al 2019 Dvdy Iochrominae development evolution DATA.rar`;
- expected README `README_for_Larter et al 2019 Dvdy Iochrominae development evolution DATA.txt`.

The source article reports HPLC measurement of anthocyanidins and related flavonoids and a phylogenetic comparative framework. Related Iochrominae work distinguishes pelargonidin-, cyanidin- and delphinidin-derived anthocyanins, including unpigmented species and minor pigments.

## Allowed operations in this preflight

1. Resolve Dryad version/file metadata and exact file identities.
2. Attempt ordinary public download routes without bypassing access controls.
3. If exact README bytes are available, retain/read the README.
4. If exact archive bytes are available, list archive member **names only**.
5. Do not extract or parse row-level HPLC/expression values in this step.

## Hosted preflight result

Terminal state:

`HOLD_SOURCE_ACCESS_README_AND_ARCHIVE_PROFILE_UNCOMPUTED`

Dryad metadata resolved both expected objects exactly:

- README: file id `108458`, 4,072 bytes, MD5 `2e4a251725ad4c13975fc09481da302d`;
- archive: file id `108456`, 3,054,999 bytes, MD5 `76b46e384fb7c9bf1ef3fbd7d1e5d2f0`.

Neither ordinary public file-stream nor API download yielded exact source bytes in the hosted environment. Exact filename/digest web search found no independent mirror. Therefore README interpretation, archive-member inspection and profile state mapping remain unopened.

Hosted evidence:

- workflow run `34848769129`;
- job `103991099017`;
- artifact `10348639063`;
- artifact digest `sha256:d82ac9dfd37cb74b5a25d4210258f4177a516cfe0be5460d2f9a0029d4b6aa66`.

## Decision logic

- The current state is a **source-access HOLD**, not a biological negative.
- The source is not counted as a second biochemical exact-profile unit.
- No substitute tree, hand-transcribed pigment table or figure-derived approximation is admitted merely to create representation replication.
- Resume only from exact README/archive bytes matching the frozen identities above; then inspect README plus archive member names before freezing any profile state mapping.

## Scientific boundary

Iochrominae has been used previously as retrospective mechanistic evidence, so any future exact-profile result from this source will be **retrospective standardized cross-representation training**, not a prospective replication.

The current representation-moderator gate remains blocked until an independent second non-visible exact-profile unit is actually completed. This source preflight alone does not increment that count.

No archive data rows, profile states, patristic distances, AUCs, permutations or winner class were computed in this preflight.

Camellia Paper 1 remains unchanged.
