# ANS/LDOX conservative sequence-resolution result

## Decision

The ANS/LDOX family now has **two reference-lineage-anchored independence clusters** (`CSIN_WHITE_PINK` and `CRETICULATA`), but **zero species-native strict cross-species exact-node recurrences**.

The main new result is not that one universal ANS gene changes in the same direction. In the 2022 *C. reticulata* contrast, distinct tea-reference copies assigned to the ANS/LDOX family move in opposite directions:

- `gene-LOC114274940` is a canonical-like ANS/LDOX reference copy: protein identity `0.997183`, query coverage `1.0`, subject coverage `0.997191`; it is red-directed (`red - white log2FPKM = +0.857082`) and follows `red > pink > white`.
- `gene-LOC114288034` is a divergent ANS-family reference copy: protein identity `0.842254`, query coverage `0.965625`, subject coverage `0.853933`; it is white-directed (`red - white log2FPKM = -3.109402`).
- `gene-LOC114295638` matches admitted ANS references too weakly (`0.341772` identity; `0.729231` query coverage) and is excluded from strict ANS sequence evidence.
- `novel.12638` remains a white-directed de novo ANS-family annotation whose source transcript sequence has not been recovered.

Thus the current data support **copy/paralog-specific deployment within the same biochemical module**. They do not support collapsing all source `ANS`/`K05277` labels into one interchangeable evolutionary node.

## CrANS primer link

The published `CrANS` ORF primer pair produces one unique exact 1,068-bp amplicon against the canonical-like tea reference feature `gene-LOC114274940`. The exploratory output contained RNA and CDS representations of the same amplicon; these are deduplicated to **one** reference-model link.

This is strong reference-lineage and functional-assay evidence, but it is **not** recovery of a deposited species-native *C. reticulata* nucleotide sequence. Therefore `species_native_sequence_recovered = no` and the strict-node predictor remains zero.

## Conservative gates

A recovered reference feature is admitted as canonical-like only when:

- protein identity is at least `0.95`;
- query coverage is at least `0.95`;
- subject coverage is at least `0.90`.

A divergent ANS-family candidate requires:

- protein identity at least `0.70`;
- query coverage at least `0.80`;
- subject coverage at least `0.80`.

Features below these thresholds remain source-reported family annotations rather than sequence-resolved ANS nodes.

## Evidence ledger consequence

- ANS family recurrence clusters: `3`.
- Reference-lineage-anchored clusters: `2`.
- Species-native strict-node clusters: `0`.
- Strict cross-species exact recurrence: `0`.
- First held-out macro test level: family/module or state-vector.
- Strict-node predictor: `0`, not ready.

This strengthens `H_HIERARCHICAL_REUSE` and `H_PARALOG_SUBSTITUTION`: convergence can be expressed at module level while individual copies differ by lineage and direction. It does not yet establish how often this occurs on independent macroevolutionary colour-transition branches.

## Reproducible assets

- `data/creticulata_ans_reference_feature_effects_v0_1.csv`
- `data/ans_ldox_source_feature_decisions_v0_1.csv`
- `data/ans_ldox_primer_linkage_deduplicated_v0_1.csv`
- `data/ans_ldox_conservative_summary_v0_1.json`
- `data/pigment_node_source_id_crosswalk_v0_2.csv`
- `data/orthology_resolution_by_feature_v0_2.csv`
- `data/micro_accessibility_node_score_harmonized_v0_2.csv`
- `scripts/summarize_ans_ldox_conservative.py`
- `.github/workflows/ans-ldox-conservative-resolution.yml`

The workflow re-downloads the frozen public sequence sources, reruns the exploratory resolver, applies the conservative gates, compares every admitted output against the frozen result, and checks the authoritative ANS ledger values.

## Claim boundary

Supported:

- sequence classification of two tea-reference ANS/LDOX-family copies used by the 2022 *C. reticulata* mapping analysis;
- opposite red/white directions for the canonical-like and divergent reference copies;
- one deduplicated exact CrANS primer-bounded link to a canonical-like tea reference model;
- two reference-lineage-anchored ANS clusters.

Not supported:

- a deposited species-native *C. reticulata* `CrANS` sequence;
- species-native orthology for the 2022 tea-reference targets;
- strict cross-species exact-node recurrence;
- duplication age, macro transition enrichment, or adaptive selection.

## Authority note

The pre-existing v0.1 ledgers and exploratory workflow are retained as historical recovery products. For ANS/LDOX decisions after PR #21, the v0.2 ledgers and conservative workflow listed above are authoritative.
