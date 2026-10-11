# Erica 2019 published subspecies and 2025 IQ-TREE accession-choice diagnostic (2026-10-11)

**Status:** Source-level improvement: 11 → **14** one-candidate-tip taxon names, potential within-visible-hue pairs 20 → **31**. Strict direct-tip developmental-expression memory analysis remains **HOLD**.

## Original Methods clarifies seven qPCR sample taxa

Le Maitre, Pirie & Bellstedt (2019), DOI `10.3389/fpls.2019.01565`, *Materials and Methods* explicitly names the subspecies corresponding to the otherwise species-level spreadsheet labels. We recovered these seven independent **source-published taxon names** without inspecting any expression–tree relationship: *E. discolor* subsp. *speciosa*, *E. unicolor* subsp. *unicolor*, *E. coccinea* subsp. *coccinea*, *E. regia* subsp. *regia*, *E. abietina* subsp. *abietina*, *E. viscaria* subsp. *longifolia*, and *E. stagnalis* subsp. *stagnalis*.

Original paper: https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2019.01565/full (Methods, selected close-relative comparison sets).

The names were tied to the 2025 IQ-TREE accession **prefixes** using explicit exact anchors only, e.g. `discolor_spe_`, `unicolor_uni_` and `stagnalis_sta_`. This is a stronger morphological taxon candidate identifier, **not proof of identical voucher/flower individual**. The 2019 flowers and 2025 DNA tips are still different sample collections.

## Verified effect on effective comparison support

On all three 2025 molecular trees, the candidate source cohort remains **22 of 27** single-colour taxa, but the species/subspecies filtering removes multiple unrelated 2025 accession-prefix candidates for three original source taxa.

| Cohort | Taxa with one source-tip candidate | Within-hue pair combinations |
|---|---:|---:|
| Species-stem alone (previous) | 11 | 20 |
| Original published subspecies prefix (new) | **14** | **31** |
| Previous strict primary design requirement | 20 | 40 |

New strict one-tip candidates: red **7**, pink **5**, white **1**, yellow **1**. Five original 2019 qPCR taxa have no tree-prefix candidate. Eight source taxa still have 2–4 candidate DNA vouchers each (including `cerinthoides`, `prolata`, `monadelphia`, `coccinea`, `regia`, `abietina`, `viscaria`, and `vestita`). Do not select one according to tree topology, expression correlation, pollinator context, or visual hue.

Source results are frozen in `results/erica_2019_subspecies_to_2025_voucher_prefix_gate_v0_1.json`; hosted regression replay used the original 2019 Table 2 crosswalk and three archived 2025 molecular-tree accession inventories and passed 4 tests. The original **2016 TreeBASE** phylogeny stays inaccessible and is never silently replaced.

## Distance-choice uncertainty (source-only)

As a separate source-quality diagnostic, use *all* frozen 2025 DNA accession candidates for every pair of original 2019 named taxa, without selecting any representative. For each pair, the min/max/mean patristic distances across voucher pairs are recorded. This **does not use any qPCR expression outcome or compute a biological evolutionary-memory P value**.

The exact archived-2025 molecular tree replay recorded:

| Tree | 83 within-hue candidate pairs sensitive to voucher choice | Fraction of 3,403 unordered pair-of-pair comparisons with disjoint distance ranges |
|---|---:|---:|
| Combined | 52 | 87.3% |
| Nuclear | 52 | 85.8% |
| Plastid | 52 | 84.8% |

All 31 single-voucher source candidates form within-hue pairs with fixed molecular distances; the other 52 pairs have nonzero voucher choice ranges. This is a **rank-uncertainty diagnostic conditional on the source-defined candidate labels**; disjoint source intervals are not posterior confidence intervals, and this metric is not statistical support for retained developmental expression memory.

Scripts:
- `scripts/audit_erica_2019_subspecies_to_2025_voucher_prefix_v0_1.py`
- `scripts/audit_erica_voucher_choice_phylogenetic_distance_bounds_v0_1.py`

Hosted replays:
- Subspecies: https://github.com/zuizui0223/chun/actions/runs/38107275542
- Voucher-choice tree distance envelope: https://github.com/zuizui0223/chun/actions/runs/38107379892

### Inferential distinction

The **original direct-tip** Erica test remains unavailable (14 candidate taxa and 31 potential pairs fail 20/40 support). A *separate new retrospective taxon-name-level* analysis that averages across all molecular accession candidates may be explored as a **different estimand** in its own proposal, but cannot be called an independently matched exact chemical-state replication of Petunieae or a replacement for the frozen Erica primary.

The Camellia AJB Paper 1 and Evolution Letters v0.3 submission freezes remain untouched.
