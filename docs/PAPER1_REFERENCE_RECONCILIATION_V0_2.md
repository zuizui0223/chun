# Paper 1 v0.2 reference reconciliation

## Status

Reference reconciliation is now separated from scientific-result governance. The authoritative bibliography seed is `data/paper1_reference_registry_v0_2.csv`; references are admitted only when article/dataset identity and DOI or stable archive locator are resolved.

## What the v0.2 manuscript currently cites explicitly

The current v0.2 Introduction explicitly cites the genus-scale phylogenomic context (`Wu 2022; Zan 2023; Zhang 2023; Yan 2024; Fan 2026`). Those five entries already existed in the v0.1 verified core set, except that Fan 2026 still had provisional pagination. Final pagination is now verified as *Plant Biotechnology Journal* 24: 1725–1739.

## Missing source citations identified by this audit

The candidate-free Methods describe five frozen public RNA-seq systems but did not yet attach formal author-year citations to those source datasets. The source articles are now frozen as follows:

| candidate-free cluster | frozen biological system | primary source | DOI |
|---|---|---|---|
| `CJAPONICA` | Joy Kendrick pink vs red petal regions | Yu et al. 2023, *Forests* 14:69 | `10.3390/f14010069` |
| `CRETICULATA` | Manao full-bloom white vs red petal regions | Qu et al. 2024, *BMC Plant Biology* 24:18 | `10.1186/s12870-023-04655-4` |
| `CSIN_WHITE_PINK` | matched white vs pink flower developmental series | Zhou et al. 2020, *Molecules* 25:190 | `10.3390/molecules25010190` |
| `CNITIDISSIMA` | S1–S5 yellow-flower development | Zhou et al. 2017, *Frontiers in Plant Science* 8:1545 | `10.3389/fpls.2017.01545` |
| `CPERPETUA` | S1–S5 yellow-flower development | Zhu et al. 2024, *Horticulture Advances* 2:29 | `10.1007/s44281-024-00052-5` |

These citations should be attached directly to the corresponding Methods sentences. This is source provenance, not evidence selected after expression outcomes.

## Background citations to restore from the verified v0.1 core

The v0.2 opening paragraphs currently make general claims about flower-colour mechanism, ecological selection, and mechanistic scale with little citation support. The following already-verified v0.1 references can be restored without expanding the claim set:

- Rausher 2008 — evolutionary transitions in floral colour;
- Wessinger & Rausher 2012 — mechanistic targets and levels of flower-colour evolution;
- Trunschke et al. 2021 — evidence and limits of pollinator-mediated flower-colour selection;
- Berardi et al. 2026 — current synthesis framing flower-colour evolution as multicausal and mechanistically plural.

## Taxonomy dataset citation

The pinned accepted-taxonomy input should be cited as the World Flora Online Consortium, *World Flora Online Plant List June 2026*, Zenodo version 2026-06, DOI `10.5281/zenodo.20782718`. The exact version must remain explicit because taxonomy normalization is an analytical input rather than a generic website lookup.

## References that should not automatically migrate from v0.1

The old v0.1 bibliography also contains references tied only to superseded micro-node framing, ecological screens, or Supplement-level analyses (for example FLS/DFR source papers). They should migrate only if the v0.2 Main text or final Supplement actually cites them. A reference being present in v0.1 is not by itself an admission criterion for v0.2.

## Current unresolved editorial items

- Convert the frozen registry to the journal's final Literature Cited punctuation/style at submission formatting time.
- Check whether AJB requires all authors or permits truncation for long author lists; do not preserve provisional `et al.` strings from working notes if full authors are required.
- Keep repository PR numbers and workflow-run IDs in Data Availability/Supplement provenance, not as substitutes for formal literature citations.

## Gate

The scientific reference identities needed for the v0.2 Main argument are now resolved. Remaining bibliography work is formatting and insertion, not source discovery.
