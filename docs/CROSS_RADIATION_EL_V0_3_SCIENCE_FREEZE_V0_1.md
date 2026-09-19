# Evolution Letters v0.3 science freeze — v0.1

## State

`EL_V0_3_SCIENCE_FROZEN`

Current first-submission candidate:

**Flower-color evolutionary memory is transient but lacks a universal phenotypic scale**

The science state is frozen from main commit:

`64943a1a1dda98c8863d9b2fcd7b70715e9cda4b`

## What is frozen

Twenty science-bearing assets are pinned by exact Git blob SHA, including:

- the v0.3 manuscript;
- science validator and figure builder;
- claim and reference manifests;
- *Iris* prospective result;
- 51-clade standardized profile results;
- tree-moderator result;
- Petunieae biochemical result;
- relative-divergence persistence result and curve inputs;
- half-depth result;
- v0.2 format gate and v0.3 promotion gate.

The freeze validator recomputes Git blob SHA from checkout bytes and fails on any missing or changed protected asset.

## What may still change

Only submission administration remains open:

- final author list and order;
- affiliations and ORCIDs;
- corresponding-author contact;
- CRediT roles;
- funding;
- acknowledgements;
- persistent archive DOI/version/URL;
- submission-system metadata.

The v0.3 metadata scaffold remains intentionally outside the science freeze.

## Rule for new science

Any new biological analysis, moderator, subgroup result, changed numerical result, or expanded claim must **not** be merged into the frozen v0.3 candidate in place.

It must instead open:

- `v0.4` or later, or
- a separate extension/project.

This prevents post-hoc result accumulation while the manuscript is already submission-ready.

## Fallback

Evolution Letters v0.2 remains the validated representation-centered fallback and is not altered by this freeze.

Camellia Paper 1 remains unchanged.
