# Iochrominae 2018 raw-data admission — resolved provenance and actual blocker (2026-11-14)

**Decision: HOLD raw 2018 same-tip HPLC × qPCR × dated-tree inference.** No new independent radiation-level prediction was run.

The original paper [Larter et al. 2018, DOI 10.1093/molbev/msy117](https://doi.org/10.1093/molbev/msy117) reports floral HPLC pigment profiling across 28 species, qPCR of seven anthocyanin-pathway genes, and the dated Smith–Goldberg 2015 Iochrominae tree. The journal's [supplementary PDF](https://oup.silverchair-cdn.com/oup/backfile/Content_public/Journal/mbe/35/9/10.1093_molbev_msy117/1/msy117_supp.pdf) was located, but its bytes were not recovered during this audit (web cache miss); its numerical tables cannot be treated as source-verified. The [2015 original tree Dryad DOI](https://doi.org/10.5061/dryad.0732g) was also located, but its original dated tree file has not been recovered and hashed.

**Important discovery:** this is not the first CHUN source-recovery attempt. Existing `docs/IOCHROMINAE_CROSS_LEVEL_BRIDGE_V0_1.md` already records **three GitHub-hosted Dryad retrieval attempts**, all blocked by delivery-layer **HTTP 401/403** (including historical file id **21811**). It also already records the author-reported biological phenotype-module pattern:
- four independent losses of ancestral delphinidin pigmentation coincide with reduced late `F3'5'H, DFR, ANS` expression;
- pigment-hue shifts coincide with branch `F3'H, F3'5'H` changes;
- upstream `CHS, CHI, F3H` remain comparatively conserved.

**These are published source results already present in CHUN, not a new discovery or raw source replication.** Repeating the same failed historical Dryad endpoint without a changed access route is not useful.

A connected-repository check of `zuizui0223/anto` identified independently published **Larter 2019** Table 2 five-model AIC values and **Ho–Smith 2016** 22-taxon gene accession mappings, plus a **2025 within-species Iochroma backcross** RNA study. None is the missing **2018 per-species quantitative HPLC × qPCR table or author-used dated tree**. Mixing the three publication years or treating accession metadata as 2018 measured expression would be invalid.

## Specific next executable source gates

1. Retrieve the original 2018 supplement using a working publisher/CDN or author-hosted mirror, and verify whether the PDF includes numerical per-species HPLC and seven-gene qPCR tables (not only plots and figure legends).
2. Retrieve the original Smith–Goldberg 2015 dated tree from Dryad using a verified accessible archive, or a verifiable author-hosted original identical topology/branch-length file.
3. Record SHA256, original names, species×HPLC and species×qPCR intersections and missingness. **Only then** fix a second-radiation outcome contrast and run it.

If the publisher supplement contains only summary figures and not the original species×quantitative matrices, **do not digitize plot bars as though they were raw original measurements**; hold for author data.

**Current scientific conclusion:** repeated pathway-level mechanisms are supported by the published Iochrominae source, but a new independent phylogeny-controlled quantitative prediction test is **not supported by currently accessible source bytes**. Petunieae remains the only fully verified matched multilayer radiation in this CHUN program. AJB Camellia Paper 1, EL v0.3 and integrated Draft #414 remain unchanged.
