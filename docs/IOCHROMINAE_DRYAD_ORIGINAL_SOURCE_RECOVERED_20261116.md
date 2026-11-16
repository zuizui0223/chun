# Iochrominae two original CC0 phylogeny archives: what was actually recovered (2026-11-16)

**Source-level recovery SUCCEEDED, but original 2018 Larter qPCR × HPLC matching remains HOLD.** Original provider archive files were actually downloaded through the [official Dryad version endpoints](https://datadryad.org/api/v2/versions/3567/download) and the [independent 2018 shape-study version](https://datadryad.org/api/v2/versions/22139/download), with CC0 verified from the original Dryad metadata, original deposited archive MD5 and SHA256 verified, and the original source members inspected using Biopython. This **materially resolves the earlier archive-access blocker** and should not be reported as a failed recovery. The exact original CC0 sources were preserved in [GitHub Actions #43893740478](https://github.com/zuizui0223/chun/actions/runs/43893740478), original artifact `iochrominae-verified-original-dryad-cc0-archives-20261116` (ID 14238002420). The frozen source-cohort audit is `results/iochrominae_original_cc0_archive_source_inventory_20261116.json`; CI must replay its **exact measured counts**.

## First original: Smith & Goldberg (2015), DOI 10.5061/dryad.0732g

Original Dryad v3567 file `ModeandTempoFlColor.zip`, 686,186 original bytes, provider MD5 `78957f5320749f5c022de78e8ad1ab32`, independently obtained SHA256 `2a7a92f600b0d92f874d636e90f5e2fcc3314876a7c4affc21b51e3c81701e5b`. The original deposited ZIP contains four floral-color clades; **Iochrominae** members:
- `IochBeast100.nex`: SHA256 `c2690a2b27d712684baab36be251e016904b98f60dd95156917a77a5a866c671`; **100 original posterior BEAST trees, each exactly 42 tips**, original dated chronograms, including original source outgroups and coded taxon labels.
- `ioch_data.csv`: SHA256 `6aacfaee4b5ef65afddf96e4e9d886d490d9bec59deafd70cc63440c26c06480`; **33 original labeled rows** for source **binary anthocyanin presence (1: 24, 0: 9)**, all 33 literal labels on the original posterior trees. **The first CSV line is a measured row, not a header.**

**Do not call the posterior 100-tree archive an original author-used MCC tree.** Larter et al. (2018; DOI 10.1093/molbev/msy117) describe their source tree as the previously published dated **MCC tree** for Iochrominae. The 2015 Dryad material recovered here includes 100 BEAST posterior trees but not an independently verified identical MCC file. These 100 trees may support a separately labeled posterior-tree sensitivity if the original 2018 assay matrices are obtained. They are **not** automatically Larter's original exact phylogeny.

## Second original: Smith & Kriebel (2018) floral shape and pollinators, DOI 10.5061/dryad.5jn7b

Original Dryad v22139 file `Smith_and_Kriebel_2018.zip`, 993,968 original bytes, provider MD5 `a4318f07ddd7e2dd1ce8297c057ead6b`, SHA256 `2a7f70c1e1db8e8308851b8317b90c112732661d288ec584219dd2d001a5bfe9`. Original source contents:
- `phylogenies/MCC_tree.nex`: SHA256 `80d4f39a9e7dba3f6337e0698473b1bcdd9027f853e82a072026204018076cec`, **one original 2018 shape-study MCC dated tree, 44 tips**.
- `phylogenies/126_trees.nex`: SHA256 `dac440674e8018e3a71b8147e46cb5c047486d7a8009725ce45d2165614c8e4d`, **126 original dated trees, each 44 tips**.
- `data/data.csv`: SHA256 `318637026410ef0c714ed225f4add7615aca3fe1e1d0908aa91295f777edff47`, **36 species**, *all 36 labels appear on the 44-tip 2018 MCC tree*; five original visible-flower-color classes: **purple 19, yellow 7, orange 5, white 3, red 2**. Original `main_pollinator` source labels: **hummingbird 12, insect 5, mixed 5, missing 14**.

The 2018 shape study's original tree is valuable for **independently source-backed visible-colour, floral shape and pollinator-category comparisons**, but it is **NOT an independently proven copy of the exact Larter et al. (2018) source tree**; this was a separate paper, phylogenetic tree and source sampling. Its categorical pollinator assignments are **not species-level pollination success measurements**, and no ecological selection causality follows from the source inventory.

## Taxon identity and representation are two separate gates

The 2015 **chemical anthocyanin presence** source uses specimen-like coded tip IDs such as `125IeduleWAXY`; the 2018 **visible flower color** data use binomials such as `Iochroma_edule`. Their phenotype CSV files have only **one literally identical name** (`Iochroma_tupayachianum`) before any curated synonym/specimen mapping. This does **not** mean there is only one biological species in common: it means an authoritative code→binomial mapping is required before a joint numeric analysis, with no automated suffix guessing.

The raw original **2015 binary biochemical state** (24 present, 9 absent, 33 source rows) and **2018 visible-colour state** (36 source rows) are different traits in different source cohorts. Comparing their positive/negative frequencies as if they were the same sample or calling white/yellow/orange identical to HPLC absence would be scientifically misleading.

## Source-data result and next admissible empirical step

The exact original original archive code and tests now permit **two independent data frame provenance audits**. Source-compatible posterior phylogenetic trees have been recovered from two papers. However, the *Larter 2018* measured **7-gene source qPCR matrix and quantitative floral anthocyanidin/flavonol HPLC matrix** are still **not recovered** from Oxford Academic or an original deposit. An independent same-tip transcript→metabolite predictive test **must remain on HOLD**, even though two related original phylogenetic datasets are now accessible.

No new gene/chemical causal effect, no new P value, no cross-radiation matched molecular replication, no pollen/UV/fitness analysis is claimed. Frozen Camellia AJB Paper 1, EL v0.3, and the original Petunieae 47-tip results are unchanged. Combined PR #414 remains Draft.

**Reproducibility:** `scripts/recover_iochrominae_official_source_20261116.py` contacts original Dryad by `datadryad.org/api/v2/versions/*/download` because direct `api.datadryad.org` DNS failed, then follows only the observed official archive backend. Original provider CC0 original data is SHA/MD5 authenticated and preserved as the GitHub Actions archive artifact. `scripts/audit_iochrominae_recovered_original_archives_v0_1.py` must validate source original member SHA, tree format/tip counts, raw 2015 headerlessness, original 2018 visible-color and pollinator missingness, and refuse cross-study same-name joins without original synonym evidence.
