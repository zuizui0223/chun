# Paper 1 authoritative result registry

## Purpose

Paper 1 has reached a public-data identifiability boundary. From this point onward, the manuscript must not drift back toward older legacy-tip, provisional-trait, or topology-sensitive claims simply because they are visually convenient or narratively stronger.

The machine-readable contract is:

- `data/paper1_authoritative_results_v0_1.csv` — all current Paper 1 results, including explicit negative/sensitivity results and superseded historical claims;
- `data/paper1_main_figure_manifest_v0_1.csv` — every Main Fig 1–6 panel and the exact result IDs it is allowed to display;
- `scripts/validate_paper1_result_registry.py` — CI gate that prevents superseded/excluded results from re-entering Main figures.

## Current headline

The manuscript is **not** a causal adaptation paper and is **not** a new Camellia phylogeny or ancestral-colour paper.

The current integrative claim is:

> Camellia pigment states show flexible molecular implementation but limited macroevolutionary lability: accepted wild flower colour retains topology-robust local phylogenetic conservatism, while current public species-level hard-state data do not identify robust branch-specific colour events that can be assigned ecological or molecular causes.

## Results retained in the Main text

### Molecular accessibility

1. FLS includes a resolved same-lineage recurrence mode (`M01_FLS_SAME_LINEAGE`).
2. DFR shows a resolved different-paralog implementation of the same pathway module (`M02_DFR_PARALOG_SUBSTITUTION`).
3. ANS/LDOX and ANR copy-aware directional heterogeneity remain supporting evidence, not strict macro-node recurrence.

### Ecological screening

4. Current climate screens do not support a universal visible A/W -> colder niche chain (`E01_UNIVERSAL_COLD_CHAIN_NOT_SUPPORTED`).
5. Coarse human-visible hue is not a deterministic pollinator-function state in the current primary-evidence synthesis (`E02_VISIBLE_HUE_POLLINATOR_ALIASING`).

### Taxonomy and trait evidence

6. The legacy nuclear panel contains 93 Camellia tips but only 55 WFO Plant List 2026-06 accepted Camellia species (`T01_WFO_ACCEPTED_TAXONOMY`).
7. Wild/floristic evidence reduces 35 provisional hard colour states to a strict 24-species seed; the dominant-colour sensitivity contains 30 species (`T02_WILD_COLOUR_AUDIT`).

### Nuclear topology and macro pattern

8. FastTree- and IQ-TREE/UFBoot-derived accepted-species topologies share 46/50 nontrivial splits on 53 common species (normalized RF 0.08; `P01_NUCLEAR_TOPOLOGY_CONCORDANCE`).
9. The robust macro pattern is **local nearest-same-colour conservatism**, which survives strict/dominant trait scenarios and the stronger UFBoot topology (`P03_LOCAL_COLOUR_CONSERV_UFBOOT`).
10. Broad/global same-colour MPD clustering is topology-sensitive and is therefore a negative robustness result, not a headline (`P04_GLOBAL_MPD_TOPOLOGY_SENSITIVE`).
11. A-specific lineage permissivity is not a strict accepted-species result (`P05_A_SPECIFIC_PERMISSIVITY_NOT_STRICT`).

### Identifiability boundary

12. No accepted-species branch transition is robust to both strict wild-colour and dominant-colour assumptions (`B01_NO_ROBUST_ACCEPTED_BRANCH_EVENTS`).
13. Therefore branch-specific climate, pollinator, or micro-to-macro causal enrichment must stop with current public hard-state data (`C02_PUBLIC_DATA_IDENTIFIABILITY_BOUNDARY`).

## Results retained only as sensitivity/background

- ANS/LDOX and ANR copy-specific directional heterogeneity;
- accepted-species ancestral state, where W is favoured but W/Y uncertainty remains;
- FastTree local-conservatism result as a sensitivity complement to the UFBoot result.

## Superseded results that must not return to Main figures

- legacy A-specific lineage-permissivity headline;
- legacy/global same-colour MPD headline as if topology-independent;
- definitive/novel white-ancestor framing;
- the three legacy 93-tip W->A branches as secure macro events.

These remain useful provenance and may be described in Supplementary sensitivity history where necessary.

## Main figure contract

- **Fig 1** — literature alternatives -> falsification/refinement -> cross-scale mismatch -> public-data boundary.
- **Fig 2** — micro implementation modes: FLS same-lineage, DFR paralog substitution, ANS/ANR copy-aware uncertainty.
- **Fig 3** — data audit: 93 legacy tips -> 55 accepted species; 35 provisional hard states -> strict 24 / dominant 30.
- **Fig 4** — nuclear topology sensitivity: 46/50 shared accepted-species splits, normalized RF=0.08.
- **Fig 5** — local nearest-same-colour permutation results across trait and topology sensitivities, with the failed global-MPD headline shown explicitly as a robustness failure.
- **Fig 6** — pattern-without-identifiable-events boundary and measurements required for Empirical Study 1.

## Stop rule

Do not add new branch-specific climate, pollination, or molecular-causation models unless a genuinely new data source changes the accepted-species trait identifiability boundary.

The next Paper 1 work is figure generation, provenance audit, and manuscript freezing. The next scientific causal work belongs to Empirical Study 1.
