# Paper 1 backward/forward citation-chase audit — 2026-08-27

## Purpose

Keyword and database searches can miss biologically relevant studies whose titles do not expose the focal taxon. Paper 1 therefore adds a separate citation-chasing layer anchored on eight current review/direct-competitor papers.

## Frozen seeds

`data/paper1_citation_chase_seeds_v0_1.csv` contains eight seeds spanning:

- current Camellia molecular synthesis;
- genus-scale Camellia colour phylogenomics;
- flower-colour pollinator-selection review;
- alternate biochemical and pathway-level convergence;
- pathway-wide expression evolution;
- broad flower-colour transition review;
- Chinese pollination-ecology review.

The runner resolves each seed in Crossref and OpenAlex, records Crossref backward references, retrieves OpenAlex forward citations, and compares DOI-bearing candidates with the DOI corpus already present in the repository.

## First hosted retrieval

Hosted run `33042972863` completed without API failures and recovered:

- seeds resolved: **8/8**;
- backward reference records: **846**;
- forward citation records: **685**;
- new priority DOI candidates: **189**;
- new priority DOI candidates with Camellia in the title: **22**;
- new priority no-DOI candidates: **27**.

These counts are provenance for that retrieval date, not immutable expectations for future reruns because forward citation counts can grow.

## Manual biological screen

`data/paper1_citation_chase_priority_screen_v0_1.csv` freezes the 22 Camellia-title DOI candidates plus one high-impact general-title candidate recovered during biological screening.

Outcome:

- newly discovered independent directional A/F/C/P cluster: **0**;
- newly admitted candidate-free public-RNA-seq system: **0**;
- one literature-side result update: **Luo et al. 2016**, DOI `10.3389/fpls.2015.01257`, assigned to the existing `CJAPONICA` dependence cluster.

Luo et al. is the important exception to a Camellia-title-only screen. Its title is cross-plant, but the study directly compares red and white *C. japonica* expression. It reports CjDFR higher in red and CjFLS higher in white, resolving literature-side `CJAPONICA` as A=up and F=down under the already frozen white-to-red orientation.

The corresponding Paper 1 literature layer was therefore reopened and rechecked with the existing estimator. The successful corrected hosted recheck is run `33045356947` and is documented in `docs/PAPER1_LUO2016_LITERATURE_RECHECK_RESULT.md`.

## Other high-value recoveries

Citation chasing also recovered additional Camellia evidence that does not create independent recurrence replicates, including:

- *C. nitidissima* CnCHI4 functional/developmental evidence;
- yellow-Camellia petal RNA-seq involving *C. nitidissima*-derived hybrids;
- *C. nitidissima* DFR functional evidence;
- *C. nitidissima* stamen transcriptome/pigment evidence;
- *C. sinensis* multi-colour flower metabolomics;
- historical Camellia anthocyanin chemistry.

These records are classified as same-background auxiliary evidence, chemistry-only evidence, non-petal/non-flower evidence, or otherwise outside the frozen directional transcript-state recurrence estimator.

## Claim boundary

Citation chasing materially improved coverage: it found a study that changed a literature-side A/F/C/P cell and weakened the earlier dependence-collapsed A-ascertainment headline. It did **not** add an independent evolutionary origin or candidate-free system.

Therefore the current literature claim is:

> Paper 1 uses database-counted high-recall search plus reproducible backward/forward citation chasing and explicit biological screening. The search is not called PRISMA-complete because a full CNKI/Wanfang export, one unified cross-database deduplication/screening flow, and a closed forward-citation stopping rule are still absent.

The scientific consequence of Luo 2016 is handled in the versioned science freeze; the citation-chase infrastructure itself never auto-admits evidence into the recurrence estimator.
