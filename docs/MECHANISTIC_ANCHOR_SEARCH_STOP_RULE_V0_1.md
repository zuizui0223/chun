# Mechanistic anchor search stop rule v0.1

## Decision

Do not keep searching indefinitely for a second clade that duplicates the full Camellia Paper 1 design.

The current finite candidate screen shows a recurring trade-off:

- white-like ancestral clades with strong macro colour histories often lack comparable floral molecular data or robust event identity;
- clades with excellent molecular repeatability data often begin from a coloured ancestral state or address pigment loss rather than white-to-colour gain;
- forcing these systems into one estimator would require weakening independence, topology or measurement rules.

The atlas therefore adopts a **role-based comparative design** rather than an exact-clone design.

## Current strict screen

A full second mechanistic anchor would need all of the following:

1. a defensible ancestral baseline;
2. at least three independent historical colour-transition events of the same frozen class;
3. flower-tissue molecular measurements at comparable functional resolution for those events;
4. event identity robust enough that the molecular contrasts can be assigned without post-hoc tree choice;
5. no visible-hue imputation of missing molecular state.

Under the current screened evidence:

- *Epimedium* fails criterion 2 after conservative dependence collapse;
- Petunia has excellent mechanistic regain evidence but only two independent colour regains;
- Linoideae has a strong dated macro history but insufficient comparable floral molecular evidence;
- Hydrangea sect. Cornidia has strong transitions but lacks section-matched molecular colour data;
- Polygonatum has relevant colour phenotypes but tissue/metadata mismatch in available omics;
- Indian *Jasminum* has a white-to-yellow macro history but no matched evolutionary colour molecular set recovered;
- modern *Linanthus* evidence no longer supports treating the main system as a simple white-root colour-gain radiation;
- older Leptosiphon white-root claims are not admitted without a current auditable published trait reconstruction;
- Nicotiana is a network/hybridization system rather than a simple white-root radiation.

None is promoted by relaxing a criterion.

## Positive benchmarks retained

The absence of a white-like exact clone does not prevent external testing of the Camellia interpretation.

### Chilean *Mimulus luteus* group

An ancestrally yellow system contains three independent gains of petal-lobe anthocyanins. All three resolve to a pathway-specific R2R3-MYB regulatory module, but genomic-region replay is incomplete (`pla1`, `pla1`, `pla2`) and exact-gene identity is only fully resolved for one event at the frozen standard.

Role: `YELLOW_BASELINE_REGULATORY_GAIN_BENCHMARK`.

### Iochrominae

An ancestrally delphinidin/blue system contains four independent pigment losses and a direct same-clade comparison between segregating acyanic morphs and fixed white species.

Role: `DIRECT_SELECTIVE_FUNNEL_AND_PATHWAY_BENCHMARK`.

### Petunia

A recent colorless long-tube ancestor is followed by two independent colour regains with sharply different regulatory implementations.

Role: `WHITE_BASELINE_REGAIN_MECHANISTIC_BENCHMARK`.

These systems allow tests of whether hierarchical/module-level repeatability is general **without conditioning the result on white ancestry**.

## Why the role-based design is stronger

The atlas can now distinguish two questions that were previously conflated:

### Ancestral-baseline question

Does a white-like, yellow or anthocyanic ancestral state alter the direction/rate of visible colour transitions or the probability of regain?

### Mechanistic-repeatability question

Conditional on a transition class, at what molecular level does recurrence occur: exact gene, genomic region, regulatory module, biochemical branch or only visible phenotype?

The first requires many clades. The second can use high-resolution benchmark systems even when their ancestral colours differ.

## Stop rule

For the current project phase, stop exact-clone searching after this finite screen and allocate effort to row-level data reconstruction/ingestion.

Reopen the exact-white-anchor search only if a new candidate is identified that plausibly satisfies **all five** strict criteria, or if new public data change a failed criterion in an existing candidate.

This is not an exhaustive statement that no such plant clade exists. It is a project-level anti-fishing rule based on the current screened candidate set.

## Immediate work allocation

1. reproduce the Iochrominae within-to-fixed scale contrast from open data;
2. ingest the three Chilean Mimulus gain events into the common ontology;
3. reconstruct Linoideae and Hydrangea terminal trait matrices with provenance;
4. retain Epimedium and Petunia as mechanistic partial benchmarks;
5. only after row-level harmonization fit cross-clade models.

Camellia Paper 1 remains scientifically closed.
