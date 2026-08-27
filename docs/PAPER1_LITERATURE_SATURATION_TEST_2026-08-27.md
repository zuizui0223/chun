# Paper 1 literature saturation test — 2026-08-27

## Purpose

This test asks a narrower question than a formal systematic review:

> After the high-recall prior-art and Camellia literature audits were already expanded, do additional species-specific, pigment-specific, ecology-specific, and Chinese-language open-web search families add a **new independent biological system eligible for the frozen A/F/C/P recurrence architecture**?

The answer in this pass is **no**.

This is evidence of search saturation for the current recurrence architecture. It is **not** evidence that every Camellia paper ever published has been retrieved.

## Search design

The additional pass deliberately varied the vocabulary and taxonomic entry points rather than repeating one generic query. Search families included:

- genus-wide Camellia flower-colour transcriptome/metabolome/mechanism searches;
- *C. japonica*, *C. reticulata*, *C. sasanqua*, *C. oleifera*, *C. amplexicaulis*, golden-Camellia/*C. nitidissima*, and *C. chrysantha* searches;
- anthocyanin, flavonol, carotenoid, yellow-pigment and hybrid-inheritance vocabulary;
- bird/bee/pollination and sensory-colour ecology;
- Chinese-language open-web queries for 山茶花色, 金花茶色素/转录组, and 油茶/山茶传粉.

The query-family decisions are frozen in `data/paper1_literature_saturation_search_log_v0_1.csv`.

## What the pass recovered

The strongest molecular hits were already represented in the evidence architecture. Examples include:

- integrated *C. japonica* transcriptome/metabolome colour-diversity work;
- integrated *C. reticulata* red/pink/white transcriptome/metabolome work;
- the four-colour *C. oleifera* petal transcriptome/metabolome study (DOI `10.1186/s12870-023-04699-6`);
- Ai et al. 2025 red/yellow/white three-species transcriptome/metabolome comparison (DOI `10.1007/s10725-025-01335-1`);
- *C. nitidissima* developmental transcriptome and later flavonol multi-omics/functional studies;
- the historical *C. chrysantha* flavonol/carotenoid hybrid literature;
- the aluminium–flavonoid yellow-colour mechanism (DOI `10.2503/jjshs1.77.402`).

These were already admitted, merged into an existing dependence cluster, or explicitly screened as auxiliary/excluded evidence.

## Why no new recurrence replicate was added

A literature hit is not automatically a recurrence replicate. The current Paper 1 estimator requires a biological system that can support a canonical flower/petal contrast on the prespecified A/F/C/P transcript-state representation and, for the standardized arm, sufficiently interpretable public raw RNA-seq data.

The additional hits failed to create a new eligible independent cluster for one or more already-frozen reasons:

- they belonged to an existing taxon/dependence cluster;
- they were between-species or horticultural comparisons that did not define a clean independent transition-class replicate;
- they supplied pigment chemistry or heterologous functional evidence rather than a matched A/F/C/P transcript-state direction signature;
- their public archive/taxon mapping was not clean enough for the frozen candidate-free standardization;
- they were ecological/sensory studies and therefore belonged to the persistence/filtering layer rather than the molecular recurrence estimator.

No eligibility rule was changed after seeing these search results.

## Ecology saturation result

The added ecology searches again recovered the already-important conclusion that coarse human-visible red is not a unique pollination state. In particular, the *C. japonica* / *C. rusticana* comparison combines similar human-visible red flowers with sharply different UV/fluorescence properties and bee responses. This reinforces, rather than overturns, the current ecological boundary:

`visible A/W/Y -> not a sufficient sensory/reproductive state`

The search did not supply evidence that would justify assigning a pollinator or climate cause to any accepted-species colour-transition branch that failed the event-identity gate.

## Saturation verdict

After the earlier high-recall audit plus this additional orthogonal search pass:

- **new eligible independent A/F/C/P recurrence clusters added: 0**;
- **new result-changing ecological evidence added: 0**;
- the same direct competitors and historical/auxiliary studies were repeatedly recovered under different query families.

This increases confidence that the current molecular recurrence result is not an artifact of one narrow keyword family.

It does **not** upgrade the review to PRISMA-complete.

## What still blocks the word “systematic”

The following are still required for a formal systematic-review claim:

1. named bibliographic databases with frozen search dates, exact queries and hit counts;
2. cross-database deduplication;
3. title/abstract and full-text screening flow with exclusion reasons;
4. dedicated CNKI/Wanfang or equivalent Chinese bibliographic-database screening rather than open-web Chinese queries;
5. explicit thesis/conference/grey-literature policy;
6. a reproducible forward/backward citation-chasing ledger.

Until then, the correct methodological language remains **high-recall evidence audit**, **targeted evidence synthesis**, or **literature-conditioned mechanism matrix**.

## Consequence for Paper 1 novelty

The saturation test does not support a “first ever” claim. It supports the narrower statement already frozen by the novelty audit:

> Within the literature recovered under multiple independent search families, no direct match was found for the empirical combination of same-public-system observation standardization, explicit incomplete A/F/C/P recurrence bounds, topology/coding-robust macro pattern testing, and a separate event-identity stop rule in *Camellia*.

That contribution should remain application-specific and evidence-bounded.
