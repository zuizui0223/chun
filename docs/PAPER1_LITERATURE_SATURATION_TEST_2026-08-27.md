# Paper 1 literature saturation test — 2026-08-27

## Status: superseded as a final saturation verdict

This document records the **open-web orthogonal saturation pass** that preceded the formal API-backed database search.

The open-web pass added 13 species-, pigment-, ecology-, and Chinese-language query families and, within that pass, recovered no new independent biological system eligible for the frozen A/F/C/P recurrence architecture.

That local result was correct for the open-web pass, but it must **not** be used as the final literature-completeness claim.

A subsequent reproducible OpenAlex/Crossref/PubMed search (`docs/PAPER1_BIBLIOGRAPHIC_DB_SEARCH_2026-08-27.md`; run `33039509237`) recovered a previously omitted eligible literature system:

- Jiang et al. 2025, red versus white *Camellia semiserrata*, DOI `10.1007/s10722-025-02606-6`.

The study is an independent within-species petal transcriptomic + chemical contrast and supports canonical white→red **A = up**. It therefore reopens the literature-ascertainment layer. Public raw RNA-seq accession has not yet been located, so it is not currently admitted to the candidate-free standardized arm.

## Historical open-web search design

The original pass deliberately varied vocabulary and taxonomic entry points rather than repeating one generic query. Search families included:

- genus-wide Camellia flower-colour transcriptome/metabolome/mechanism searches;
- *C. japonica*, *C. reticulata*, *C. sasanqua*, *C. oleifera*, *C. amplexicaulis*, golden-Camellia/*C. nitidissima*, and *C. chrysantha* searches;
- anthocyanin, flavonol, carotenoid, yellow-pigment and hybrid-inheritance vocabulary;
- bird/bee/pollination and sensory-colour ecology;
- Chinese-language open-web queries for 山茶花色, 金花茶色素/转录组, and 油茶/山茶传粉.

The original decisions remain frozen in `data/paper1_literature_saturation_search_log_v0_1.csv` as provenance.

## What remains useful from this pass

The pass repeatedly recovered already-known modern and historical evidence, including:

- *C. japonica* and *C. reticulata* colour transcriptome/metabolome work;
- the four-colour *C. oleifera* petal study;
- Ai et al. 2025 red/yellow/white multispecies comparison;
- *C. nitidissima* developmental and flavonol multi-omics evidence;
- historical *C. chrysantha* pigment/hybrid studies;
- aluminium–flavonoid yellow-colour chemistry;
- Camellia sensory/pollination studies showing that coarse visible hue is not a unique reproductive-function state.

These repeated recoveries remain evidence that the prior architecture was not driven by one keyword family. They are **not** evidence that the literature corpus was complete.

## Revised saturation verdict

The correct current statement is:

> The open-web pass showed local saturation, but the later database-backed search falsified a global `no additional eligible cluster` claim by recovering *C. semiserrata*. Literature ascertainment must therefore be updated before Paper 1 is re-frozen.

The review remains a **high-recall evidence audit**, now supplemented by exact OpenAlex/Crossref/PubMed hit counts and an explicit candidate-screening ledger. It is not PRISMA-complete.

## Remaining formal-review gaps

1. broad OpenAlex/Crossref retrievals still require narrower screenable queries or complete pagination beyond the current 1000-record retrieval cap;
2. a full cross-database deduplication + title/abstract/full-text screening flow is not complete;
3. CNKI/Wanfang or equivalent Chinese bibliographic databases remain outside the API-backed set;
4. thesis/conference/grey-literature policy remains incomplete;
5. forward/backward citation chasing needs a fully enumerated ledger.

See `docs/PAPER1_BIBLIOGRAPHIC_DB_SEARCH_2026-08-27.md` for the current database-counted result and the scientific consequence for literature ascertainment.
