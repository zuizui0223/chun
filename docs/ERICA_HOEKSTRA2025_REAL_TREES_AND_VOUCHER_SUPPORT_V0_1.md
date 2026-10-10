# Erica phylogeny recovered; voucher/taxon identity gate is the remaining blocker (2026-10-10)

**Status: real independent molecular phylogeny source recovered (PASS); linked developmental-expression ancestry inference (HOLD).**

## New verified source

Hoekstra et al. (2025), *PhytoKeys* 257, DOI `10.3897/phytokeys.257.139457`, published **Supplementary Material 3: Full phylogenetic data and results**, DOI `10.3897/phytokeys.257.139457.suppl3`. Exact ZIP `oo_1344866.zip` was retrieved from the source-published Zenodo record `15606575`, `https://zenodo.org/records/15606575/files/oo_1344866.zip?download=1`; downloaded file MD5 exactly matched `d4363c6e604784b58c91d8a1d824a1f1`.

The archive contains explicit IQ-TREE Newick result files, independent alignment files, and other model and provenance assets. Bio.Phylo parsed the three genuine `.treefile` entries (not partition schemes or plots):

| Newick result | Original tips | Tips with branches | **Unverified lexical taxon candidates** | Maximum within-colour pairs among candidates |
|---|---:|---:|---:|---:|
| Combined molecular tree | 771 | 771 | 22 | 83 |
| Nuclear tree | 749 | 749 | 22 | 83 |
| Plastid tree | 744 | 744 | 22 | 83 |

These are three **correlated trees from one 2025 study**, not three independent radiations. The distances on the IQ-TREE outputs are molecular branch lengths, **not millions of years**.

Reproduction: source and parser tests, SHA/MD5-fixed retrieval and archive-member inventory in `scripts/audit_erica_hoekstra2025_supp3_tree_crosswalk_v0_1.py`, [hosted run 38061975401](https://github.com/zuizui0223/chun/actions/runs/38061975401), and re-run [38062290346](https://github.com/zuizui0223/chun/actions/runs/38062290346). Original ZIP and full source audit JSON were uploaded as Actions artifacts.

## Crucial biological-unit correction

The 2019 qPCR source contains **30 original floral sample labels** (630 gene/stage numeric fold changes) of which 27 belong to taxa showing only one visible flower colour in that dataset. The 2025 phylogeny has labels like `abietina_aur_MP717`, `coccinea_uni_EO12849`, `viscaria_mac_MP808`, etc. These represent **different sequenced accessions or subspecific groups**, not the 2019 floral expression specimens.

Matching published/qPCR name stems plus voucher suffixes (including differences between original printed and qPCR spellings) yields 22 candidate named lineages: red 12, pink 6, white 2, yellow 2. The **83 unordered same-colour combinations are only maximum hypothetical sample pairs** before exact species/subspecies/voucher admission.

**Eleven of these 22 taxa have multiple candidate phylogenetic tips (from 2 to 12 accessions).** For example, the broad published `Erica_abietina` source name maps to 12 genetically sequenced subspecific/voucher names. Automatically taking the first match or pooling all accessions as independent species would be unjustified.

A strict no-arbitrary-voucher-choice subset contains **11 names with exactly one candidate tip each** (red 5, pink 5, white 1, yellow 0), offering just **20 possible within-visible-colour unordered pairs**. This fails the previously frozen minimum for inferential admission (**20 taxa and 40 within-colour pairs**), even before taxonomic synonym, voucher and direct-sequence checks. The correct classification is **`HOLD_SOURCE_IDENTITY_SUPPORT`**, **not** a negative biological memory result.

The five qPCR taxa with no candidate matches in any of these three trees are `Erica_sparmanii`, `Erica_plukenetii_breviflora`, `Erica_mammosa`, `Erica_filipendula`, `Erica_annectans`. Some apparent name differences (`cerenthoides` vs printed `cerinthoides`; `hematocodon` vs `haematocodon`; `verticiliata` vs `verticillata`) have independently traceable printed name evidence but **do not alone prove the same collection vouchers**.

## Forward route without inferential leakage

1. Resolve the 11 multi-accession species by exact **subspecies and voucher provenance**, or develop and preregister a **species-level phylogenetic uncertainty model** that averages over all observed sequenced accessions *without* selecting a topology or sample based on the expression outcome. Such an alternative must explicitly change the estimand and be separately evaluated, not silently rescue the frozen 21-feature test.
2. Confirm tree-tip labels against original sequence alignments and specimen metadata; do not infer that a species-level name match is a same-individual match.
3. Freeze a taxon-by-tree source admission table and actual pair support before accessing any new developmental-expression statistic.
4. Retain source chemistry and visible phenotype distinctions: *Erica* red/pink classes differ from Petunieae's measured identical anthocyanidin-presence signatures.

**Manuscript decision:** No independent positive/negative regulatory-memory result is added. Preserve the original *Camellia* AJB Paper 1 and EL v0.3 submission freezes, and keep integrated PR #414 Draft. This recovered tree source and its explicit 11/20 support ceiling are genuine new contributions to source feasibility, not proof of molecular-memory causality.
