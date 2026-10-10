# Hoekstra 2025 Erica molecular tree / 2019 flower-colour expression source gate — final v0.1 (2026-10-10)

**Concluded source-first check: phylogenetic data RECOVERED; safe species/collection-unit integration HOLD.**

## Real data recovered and verified

Hoekstra et al. (2025), DOI `10.3897/phytokeys.257.139457`, supplement DOI `10.3897/phytokeys.257.139457.suppl3`, Zenodo record 15606575. The exact archived ZIP `oo_1344866.zip` was retrieved, file MD5 `d4363c6e604784b58c91d8a1d824a1f1` matched. The archive contains reproducible molecular alignments and IQ-TREE branch-length trees (combined 771 DNA accessions, nuclear 749, plastid 744); it is not a PDF-to-tip transcription or a synthetic taxonomic supertree.

Hosted proof: [source archive/tip-name replay](https://github.com/zuizui0223/chun/actions/runs/38062290346), and [original archived ZIP monophyly replay](https://github.com/zuizui0223/chun/actions/runs/38062647910). This second replay downloads the **already checksum-verified source artifact** rather than relying on another external network fetch.

## Key source-level distinction

The independent 2019 Le Maitre / Pirie / Bellstedt RT-qPCR sample (DOI `10.3389/fpls.2019.01565`) already supplies 630 numeric pathway-expression values and published four-class visible flower colour across 27 source taxa represented by one colour. The 2025 DNA tree tips have voucher-like names such as `abietina_aur_MP717` or `viscaria_mac_MP808`, not the exact 2019 source individuals.

A **name-stem-only** audit of the 27 source taxa gives 22 candidate names on all three trees (red 12; pink 6; white 2; yellow 2). The tempting **83 potential same-visible-colour pairs** are NOT source-admitted observations, because 11 of the 22 matched names have 2–12 accession or subspecific tips. The exact 2019 qPCR voucher/sample identity is not available from its named source matrix.

To diagnose whether treating these 11 groups as one phylogenetic tip could be justified, we computed the MRCA of each prefix-matched group in each original 2025 Newick tree and compared all actual descendants with the group. **All 11 multi-tip name-stem sets were nonmonophyletic under this strict definition in all three molecular trees.**

| Source tree | Matched name-stem candidates | Multiple-voucher sets | Sets monophyletic as labelled | One-candidate-tip sets |
|---|---:|---:|---:|---:|
| Combined | 22 | 11 | 0 / 11 | 11 |
| Nuclear | 22 | 11 | 0 / 11 | 11 |
| Plastid | 22 | 11 | 0 / 11 | 11 |

Important: this is **a finding about these string-defined sample sets on the given molecular tree**, not taxonomic proof that *Erica abietina* or all 11 biological species are evolutionarily polyphyletic. Some source stem matches combine published subspecies and potentially heterogeneous colour traits; independent taxonomic/voucher admission is required.

## Hard biological-support result

Restricting to the candidate taxa with exactly one possible tree tip yields **11 taxa (red 5, pink 5, white 1, yellow 0)** and **20 theoretical within-colour unordered pairs** (10 red + 10 pink). Even these taxa are only *lexical candidate taxon matches*, not proven identical DNA/RT-qPCR collection individuals.

The experiment design was fixed earlier (`data/erica_predeclared_visible_colour_developmental_gene_memory_design_v0_1.json`) with `≥20` independently admitted taxa, `≥40` same-visible-colour pairs and ≥2 visible-colour states with ≥3 taxa. The strict source set therefore **fails two required source-support criteria**. We do not calculate Spearman rho, run permutations, lower the thresholds, select a favourable accession, infer an evolutionary-time half-life, or claim a successful/failed independent memory replication.

**Status: `HOLD_MULTIPLE_TIP_IDENTITY_NONMONOPHYLY_AND_PREDECLARED_PAIR_SUPPORT`.**

## Implication for the research programme

The new **2019 floral expression × 2025 evolutionary phylogeny** bridge now has quantitative source evidence on both sides. Its remaining obstacle is not the absence of public molecular phylogenies. It is whether the 2019 floral samples can be placed in the 2025 phylogeny at an appropriately matched species/subspecies/collection scale; an alternative species-level distance model over all accessions would be a **new estimand** rather than a replay of the predeclared test.

The biologically exciting question—whether floral developmental gene-expression trajectories retain finer ancestry after visible flower colour is fixed—remains legitimate but **unanswered**. The earlier retrospective Petunieae chemical-state conditional result remains a one-radiation positive; it is not augmented by an *Erica* second-radiation memory P value.

Source replay files:
- `scripts/audit_erica_hoekstra2025_supp3_tree_crosswalk_v0_1.py`
- `scripts/audit_erica_hoekstra2025_voucher_monophyly_v0_1.py`
- `results/erica_hoekstra2025_source_tree_lexical_and_voucher_support_v0_1.json`
- `results/erica_hoekstra2025_voucher_monophyly_source_gate_v0_1.json`
- source tests and two dedicated GitHub Actions workflows.

The proposal remains on Draft PR #420 stacked on #419/#418/#417/#414. Frozen *Camellia* AJB and Evolution Letters v0.3 first-submission assets are unchanged.
