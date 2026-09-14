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

## Decision logic

- If README/archive bytes are blocked, freeze a source-access HOLD rather than treating it as a biological negative.
- If exact bytes are recovered, inspect schema/member names and only then decide whether a deterministic nested biochemical representation can be frozen before computing a new profile AUC.
- No substitute tree or hand-transcribed phenotype table is admitted merely to create a second biochemical observation.

## Scientific boundary

Iochrominae has been used previously as retrospective mechanistic evidence, so any future exact-profile result from this source will be **retrospective standardized cross-representation training**, not a prospective replication.

The current representation-moderator gate remains blocked until an independent second non-visible exact-profile unit is actually completed. This source preflight alone does not increment that count.

Camellia Paper 1 remains unchanged.
