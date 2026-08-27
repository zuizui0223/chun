# Paper 1 bibliographic database search — 2026-08-27

## Status

A reproducible API-backed bibliographic search was completed on 2026-08-27 across **OpenAlex, Crossref, and PubMed** using 12 frozen conceptual query families (`data/paper1_bibliographic_db_queries_v0_1.csv`). All **36 database queries completed successfully** in GitHub Actions run `33039509237`.

This pass materially changes the previous saturation verdict: it identified **one new independent molecular literature cluster that meets the directed flower-colour transcriptomic evidence criteria**, *Camellia semiserrata* red versus white flowers (Jiang et al. 2025, DOI `10.1007/s10722-025-02606-6`).

Therefore the earlier open-web saturation statement `new eligible independent A/F/C/P cluster = 0` is superseded. The formal database search is doing useful scientific work rather than simply documenting search completeness.

## Reproducible search contract

- query registry: `data/paper1_bibliographic_db_queries_v0_1.csv`
- exact hit-count snapshot: `data/paper1_bibliographic_db_query_counts_2026-08-27.csv`
- runner: `scripts/run_paper1_bibliographic_db_search_v0_1.py`
- workflow: `.github/workflows/paper1-bibliographic-db-search-v0-1.yml`
- hosted run: `33039509237`
- artifact: `paper1-bibliographic-db-search-v0-1`
- artifact SHA256: `047ba1e7083e7dde79d0ef80e86c45dfe101bd76489c3546e54ef26c2485f5c9`
- search timestamp: `2026-08-27T04:28:24+00:00`

The runner recorded exact database hit counts, retrieval counts and retrieval-cap flags; deduplicated DOI-bearing records; compared external DOIs against the existing repository DOI corpus; and emitted new DOI/no-DOI candidate files for screening.

## Search-volume result

The 36 queries all returned counts successfully. PubMed retrieval was uncapped for all 12 query families. OpenAlex was uncapped for the more targeted molecular/yellow/historical/species queries but capped at 1000 records for several broad queries. Crossref `query.bibliographic` was extremely broad (tens to hundreds of thousands of hits) and therefore capped at 1000 retrieved records for every query family.

This means:

- **hit counts are reproducibly frozen for all three databases**;
- PubMed candidate retrieval is complete for the frozen queries;
- several OpenAlex candidate sets are complete, while broad OpenAlex sets are capped;
- Crossref provides a useful independent count/discovery channel but its current broad bibliographic queries are not an exhaustive screenable corpus.

The database search therefore improves reproducibility but still does not justify a PRISMA-complete claim.

## High-priority candidate screen

The external retrieval produced many false-positive records because OpenAlex/Crossref broad text search is permissive. A focused high-priority screen was performed for Camellia flower/petal pigment-mechanism and pollination titles and is frozen in `data/paper1_bibliographic_priority_screen_v0_1.csv`.

### New molecular cluster: CSEMISERRATA

Jiang et al. 2025 compared red *Camellia semiserrata* with the white form `albiflora` using petals, transcriptomics and chemical analysis (DOI `10.1007/s10722-025-02606-6`). The published evidence reports:

- six anthocyanins in red flowers and no anthocyanins in white flowers;
- cyanidin-3-O-glucoside as the major red-petal anthocyanin;
- eleven anthocyanin-biosynthesis structural genes strongly downregulated in white flowers;
- a directed within-species red/white comparison independent of the existing CJAPONICA, CRETICULATA, CSIN_WHITE_PINK, CNITIDISSIMA and CPERPETUA dependence clusters.

Canonical orientation from white to red therefore supports **A = up**. F/C/P transcript-state directions are left unresolved until the full gene-level evidence is audited; visible colour and chemical presence are not used to impute them.

The white form is treated taxonomically as a form/synonym within *C. semiserrata*, which is compatible with the current micro-evidence architecture because it already admits within-species genotype, sector and developmental contrasts as biological systems.

### Raw-data gate

No public SRA/BioProject accession for the Jiang et al. 2025 red/white RNA-seq was located in the current open search. Consequently:

- **admit it to the literature observation / accessibility matrix**;
- **do not add it to the candidate-free standardized arm unless raw reads are located and audited**;
- the existing three-cluster anthocyanin candidate-free common-set result remains unchanged for now.

## Immediate statistical consequence

Adding one A-resolved independent system changes the literature ascertainment layer:

### System level

Old A/F/C/P coverage: `8/4/1/3`

Updated coverage: **`9/4/1/3`**

Under the same exact axis-symmetric null conditional on row-wise resolved-axis counts:

- old exact P(A enrichment) = `0.00836181640625`
- updated exact P(A enrichment) = **`0.002788543701171875`**
- old exact P(any axis imbalance) = `0.023948386863425927`
- updated exact P(any axis imbalance) = **`0.008607652452256944`**

### Dependence-cluster level

Old A/F/C/P coverage: `4/3/1/2`

Updated coverage: **`5/3/1/2`**

- old exact P(A enrichment) = `0.140625`
- updated exact P(A enrichment) = **`0.046875`**
- old exact P(any axis imbalance) = `0.4166666666666667`
- updated exact P(any axis imbalance) = **`0.14583333333333334`**

Thus the newly recovered independent study **strengthens**, rather than weakens, the paper's observation-regime result: anthocyanin-heavy literature ascertainment now survives dependence collapse at the prespecified exact test level.

## Other molecular candidates

The priority screen recovered additional useful evidence, but none currently adds another independent A/F/C/P transcript-state recurrence cluster:

- *C. impressinervis* genome / flower-colour resources: useful auxiliary genomics, no matched directed petal contrast;
- *C. reticulata* 'Tongzimian' physiology: useful, but same CRETICULATA background and not a new transcript-state cluster;
- *C. nitidissima* proteomics and preprints: same CNITIDISSIMA cluster or duplicate prepublication versions;
- *C. oleifera* differently coloured petal metabolomics: independent chemistry evidence but not the prespecified transcript-state matrix;
- historical anthocyanin/flavonol/yellow-pigment studies: important priority/state evidence but not comparable transcript-state direction signatures.

## Ecology candidates

The search also recovered additional Camellia pollination literature, including insect effectiveness, landscape bird-mediated pollen flow, volcanic-disturbance studies and a 2026 range-shift model for *C. oleifera* and specialist wild bees. These strengthen the interpretation of pollination as a context-dependent establishment/persistence filter. They do **not** provide a robust branch-specific flower-colour selection test and therefore do not change the event-identity stop rule.

## Revised completeness verdict

The literature state is now:

> **high-recall evidence audit + reproducible three-database hit counts + explicit priority screening, with one scientifically relevant omission recovered and integrated.**

This is stronger than the previous saturation pass, but still not PRISMA-complete because:

1. broad OpenAlex/Crossref retrievals hit the 1000-record screening cap;
2. a title/abstract/full-text ledger over the entire deduplicated corpus is not complete;
3. CNKI/Wanfang remain outside the API-backed database set;
4. grey-literature policy remains incomplete.

The key scientific response is not to hide the newly found study but to reopen the literature-ascertainment layer, update its statistics, and keep the candidate-free common-system recurrence result frozen until public raw data justify expansion.
