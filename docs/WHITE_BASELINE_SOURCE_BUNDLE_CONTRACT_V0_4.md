# White-baseline atlas source bundle contract — v0.4

## Purpose

Freeze the identity of the first external source bundles before raw extraction so that a later download cannot silently substitute a different attachment/version.

## Antirrhineae

Verified remote record: `10.15479/AT:ISTA:34`.

The repository page reports:
- filename: `IST-2016-34-v1+1_tellis_flower_colour_data.zip`;
- display size: 4.47 MB;
- MD5: `950f85b80427d357bfeff09608ba02e9`;
- license: CC0 1.0;
- contents described as flower-colour data and phylogeny (NEXUS) files.

The raw bundle is not yet committed or ingested. The source identity is verified; the remaining blocker is binary retrieval into an execution environment that can inspect the archive.

## Epimedium sect. Diphyllon

Verified article/supplement context: `10.3389/fpls.2023.1234148`.

Open article and PMC metadata identify a supplementary XLSX attachment with reported display size 157.3 KB. The article states that Supplementary Table S4 is the reproductive dataset with 699 individuals from 41 species plus one unknown taxon and includes separate inner-sepal and spur/petal colour variables.

The exact attachment filename/checksum is not exposed in the currently indexed metadata, so the contract deliberately records no invented checksum. It will be frozen only after the actual XLSX is retrieved.

## Fail-closed rule

A remote source is not `INGESTED_VERIFIED` until:
1. the binary is available to the analysis environment;
2. a published checksum is matched where one exists, otherwise a local SHA256 is computed and recorded as project provenance;
3. archive/sheet contents are inventoried;
4. the expected terminal trait and phylogeny content is found;
5. normalized output passes the v0.3 organ/polymorphism contract.

Until then, the source is `REMOTE_VERIFIED_NOT_INGESTED` and cannot contribute rows to pooled analyses.

This source gate is post-Paper-1 and does not alter the frozen Camellia manuscript.
