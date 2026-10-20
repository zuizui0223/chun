# Epimedium second mechanistic anchor — v0.2

## Current verdict

Epimedium remains the strongest second mechanistic anchor after Camellia, but the inferential route must be split into two non-interchangeable questions.

### Route A — historical-transition recurrence
The 2023 eight-species HPLC/qPCR study compares four anthocyanin-positive and four anthocyanin-negative species. The four A- terminals cannot be counted as four independent losses. Current nuclear/plastid/mitochondrial evidence allows broad non-independence among `sagittatum / lishihchenii / wushanense`, whereas `franchetii` is separated in older AFLP structure. The conservative transition-cluster count is therefore treated as an **identified set of 2–4**, not a point estimate.

The preregistered `>=3 robust independent historical transitions` gate is **not yet met**, because the lower bound is only 2 and rapid radiation/introgression make single-tree branch assignment unsafe.

### Route B — raw current-state remeasurement
Xu et al. 2024 (`10.1186/s12870-024-05480-z`) independently generated floral RNA-seq across Epimedium species with distinct organ-specific colours. The floral raw-data accession is `CRA014550`.

Primary flower samples:
- petals: `E. pseudowushanense` magenta; `E. acuminatum` magenta; `E. jinchengshanense` yellow; `E. baojingense` green;
- sepals: `E. hunanense` red; `E. baojingense` green; `E. acuminatum` white.

The source reports three biological replicates per state, each biological replicate pooling three individuals. The raw data are therefore suitable for a new, outcome-independent remeasurement once binary/sample metadata are ingested.

This route tests **current molecular-state repeatability**, not historical transition vectors.

## Observation intervention

The literature-side candidate-selected layer is the 2023 HPLC/qPCR study (`10.3389/fpls.2023.1133616`), which emphasizes anthocyanin-pathway genes and concludes convergent regulatory reduction of DFR/ANS in A- flowers.

The standardized layer will instead use the raw `CRA014550` reads and one frozen reference/annotation rule. No family is admitted because its observed direction matches the literature.

Primary functional modules:
1. `PHENYLPROPANOID_GATEWAY` — PAL;
2. `ANTHOCYANIN_CORE` — CHS/CHI/F3H/F3'H/F3'5'H/DFR/ANS;
3. `FLAVONOL_COMPETITION` — FLS.

Secondary modules are regulatory MYB/bHLH/WD40 and LAR/ANR diversion if reference annotation completeness passes a frozen threshold.

Yellow and green visible states remain chemically unresolved until direct pigment evidence identifies the relevant chemistry. They are not coded as carotenoid or anthocyanin absence by colour alone.

## Why this is useful even if Route A remains blocked

`E. acuminatum` and `E. pseudowushanense` provide a repeated magenta-petal state in different parts of the radiation, while the full cohort spans magenta/yellow/green petals and red/green/white sepals. A standardized state-space analysis can therefore ask:

> Does the same visible state occupy a similar multivariate molecular state after outcome-independent remeasurement?

This is a direct external test of the Camellia observation-regime result, while remaining agnostic about historical event identity.

## Claim ceiling

Until Route A passes, Epimedium cannot be described as three-or-more independent molecularly measured anthocyanin-loss events. Until CRA014550 is ingested and reprocessed, the raw standardized result does not exist. A successful Route B would establish cross-clade reproducibility of the **measurement/state-space** result, not by itself a general law of historical molecular recurrence.

## Next finite steps

1. ingest CRA014550 sample/run metadata and raw reads;
2. freeze E. pubescens reference/annotation and module completeness before expression outcomes;
3. process petal and sepal samples separately;
4. quantify the repeated-magenta pair and all organ-typed state distances;
5. compare literature-selected versus standardized module-state similarity;
6. keep Route A historical transition recurrence blocked unless >=3 robust dependence clusters survive topology sensitivity.
