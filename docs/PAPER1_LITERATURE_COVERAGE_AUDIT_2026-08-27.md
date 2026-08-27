# Paper 1 literature coverage audit — 2026-08-27

## Current verdict

The project now has a **database-counted, high-recall evidence audit** that is substantially broader than the Paper 1 journal reference list. It should still **not** be called PRISMA-complete, exhaustive, or a formal systematic review.

What is now defensible is:

> **A database-counted, high-recall evidence audit with explicit admission/exclusion rules, formal OpenAlex/Crossref/PubMed query counts, targeted Chinese-language/thesis screening, prior-art citation chaining, and standardized reanalysis of public systems that meet the frozen molecular criteria.**

The central methodological distinction remains that the manuscript reference list is not the literature corpus, and a relevant paper is not automatically an independent recurrence replicate.

## Evidence architecture

The broader literature evidence is distributed across:

- `data/camellia_flower_color_mechanism_meta_v0_3.csv` — mechanism-focused study systems and independence clusters;
- `data/camellia_mechanistic_literature_expansion_decisions_v0_1.csv` — explicit admit/exclude decisions from the first expansion;
- `data/camellia_mechanistic_literature_additional_screen_v0_1.csv` — historical/current high-recall molecular screen;
- `data/paper1_bibliographic_db_queries_v0_1.csv` — frozen formal OpenAlex/Crossref/PubMed query families;
- `data/paper1_bibliographic_priority_screen_v0_1.csv` — priority decisions from the formal database retrieval;
- `data/paper1_chinese_grey_literature_screen_v0_1.csv` — Chinese-language, thesis, and adjacent grey-literature decisions;
- `data/ecological_driver_study_registry_v0_2.csv` and `data/paper1_ecological_primary_references_v0_1.csv` — ecology evidence;
- `data/paper1_novelty_prior_art_registry_v0_1.csv` and `data/paper1_novelty_search_log_v0_1.csv` — prior-art and novelty-search decisions.

The journal-facing `data/paper1_reference_registry_v0_4.csv` is a 22-reference submission contract, not the search database.

## Formal English-language bibliographic database pass

A reproducible hosted search used **12 frozen conceptual query families across OpenAlex, Crossref, and PubMed**:

- **36/36 database queries completed successfully**;
- hosted search run: **`33039509237`**;
- DOI-bearing records were deduplicated against the repository corpus before priority screening.

This search invalidated the earlier open-web saturation statement that no additional eligible independent molecular cluster existed. It recovered Jiang et al. 2025, a red-versus-white *Camellia semiserrata* transcriptomic/chemical system (DOI `10.1007/s10722-025-02606-6`).

That record was admitted as the literature-only `CSEMISERRATA` dependence cluster with canonical white→red **A=up** and F/C/P unresolved. No auditable public raw RNA-seq accession was located, so it does not enter the candidate-free standardized arm.

The formal-database consequence is frozen in Paper 1 science v0.2.1:

- literature biological systems: **11**;
- dependence clusters: **6**;
- system A/F/C/P coverage: **9/4/1/3**;
- exact system-level A-axis enrichment: **P=0.0027885437**;
- dependence-collapsed coverage: **5/3/1/2**;
- exact dependence-collapsed A-axis enrichment: **P=0.046875**;
- dependence-collapsed complete-signature recurrence remains unsupported: **P=0.1989801**.

Thus broader formal database coverage strengthened the observation-process result while leaving the matched five-system candidate-free recurrence estimator unchanged.

## Molecular literature coverage

### Modern omics layer

The current mechanism architecture includes the major public flower-colour transcriptomic/metabolomic systems recovered by the audit, including:

- white/pink *C. sinensis*;
- multiple *C. japonica* colour systems;
- red/pink/white and spatial/developmental *C. reticulata* systems;
- *C. sasanqua* colour diversity;
- yellow developmental *C. nitidissima* and *C. perpetua*;
- multispecies red/yellow/white comparisons;
- genus-scale colour phylogenomics;
- literature-only red/white *C. semiserrata* from the formal database pass.

Only systems satisfying the frozen public-raw-data and contrast criteria enter the candidate-free arm. Formal retrieval breadth therefore does not redefine the estimator after outcomes are seen.

### Historical pigment and functional layer

The audit extends well before the RNA-seq era. Explicitly screened examples include:

- Endo 1958 — anthocyanin/leucoanthocyanin chemistry in *C. japonica*;
- Miyajima et al. 1985 and Scogin 1986 — yellow-pigment chemistry in *C. chrysantha*;
- Saito et al. 1987 — cyanidin derivatives across red *Camellia* species/cultivars;
- Sakata et al. 1987 — anthocyanins of wild Section *Camellia* forms;
- Hwang et al. 1992 — yellow-pigment inheritance in *C. chrysantha* hybrids;
- Nakayama et al. 2008 — aluminium–flavonoid interaction in deep-yellow *C. chrysantha*;
- Zhou et al. 2013 — functional CnFLS1 evidence.

These papers matter for biological interpretation and priority, but most do **not** supply an independent canonically oriented A/F/C/P transcript-state signature.

## Chinese-language and grey-literature indexed pass

A dedicated indexed-source/thesis pass is frozen in:

- `data/paper1_chinese_grey_literature_screen_v0_1.csv`;
- `docs/PAPER1_CHINESE_GREY_LITERATURE_SCREEN_2026-08-27.md`;
- hosted validation run **`33042624606`**.

Ten records were explicitly classified. Eight belong to the already represented `CNITIDISSIMA` molecular background:

- CnCHS cloning/expression (2011);
- CnCHI cloning/expression (2012);
- Zhou 2012 doctoral thesis on *C. nitidissima* flower-colour genes;
- CnFLS1 functional work (2013; already present in the historical screen);
- CnF3H cloning/expression (2015);
- CnCHS genetic transformation (2015);
- CnF3'H expression/function (2021);
- CnbHLH79 developmental/regulatory correlation (2023).

The pass also records:

- Huang et al. 2018 *C. oleifera* CoANR1/2 functional evidence — direct P-axis enzymatic feasibility but no matched petal-colour direction;
- Wu 1977 *C. oleifera* pollinating-bee work — historical pollinator context, not flower-colour selection.

Machine-validated outcome:

- records screened: **10**;
- `CNITIDISSIMA` same-background records: **8**;
- new independent directional A/F/C/P clusters: **0**;
- new candidate-free systems: **0**;
- historical ecology-context records: **1**.

This pass therefore deepens the documented Chinese candidate-gene/functional history without multiplying the recurrence denominator.

## Grey-literature policy

The indexed Chinese/thesis pass also freezes the following policy:

- theses/dissertations may support priority, source genealogy, completeness assessment, and an existing dependence cluster;
- the same thesis/programme is not counted again as a separate evolutionary replicate when later journal papers represent the same taxon/background;
- conference abstracts or unarchived summaries do not enter quantitative recurrence unless methods/data are sufficient to apply the frozen admission rules;
- functional or heterologous experiments without a canonically oriented flower/petal contrast remain feasibility evidence;
- candidate-free admission still requires auditable public raw RNA-seq and a pre-outcome contrast definition.

## Why relevant papers are not automatically recurrence replicates

The recurrence estimator is a **transcript-state comparison**, not a bibliography count. A study can be highly relevant while remaining outside the denominator if it lacks one or more of:

1. a matched flower/petal contrast with a canonical direction;
2. interpretable A/F/C/P transcript-state evidence;
3. independence from an already represented biological/evolutionary cluster;
4. auditable public raw data when used in the standardized candidate-free arm.

Accordingly:

- pigment-only chemistry informs state interpretation but not transcript-state signatures;
- upstream CHS/CHI/F3H/F3'H work can establish pathway feasibility without directly defining the frozen A/F/C/P modules;
- heterologous overexpression can establish function without adding an independent evolutionary origin;
- multiple studies within *C. nitidissima* strengthen `CNITIDISSIMA` but do not create multiple independent yellow origins;
- review articles are citation-chaining/novelty anchors rather than empirical replicates.

## Ecological literature coverage

The modern ecology registry covers field, exclusion, supplementation, sensory, seasonal, climate-mediated, and pollinator-efficiency studies from 1985–2026. The Chinese-language screen confirms that the historical pollination literature begins earlier.

Wu (1977), *The pollinating bees on Camellia oleifera with descriptions of four new species of the genus Andrena*, identifies specialist pollinating bees of cultivated *C. oleifera* and is repeatedly recognized in later reviews as an early landmark in Chinese pollination ecology.

This does not add evidence for a branch-specific flower-colour cause. It strengthens the boundary that *Camellia* pollination ecology is an established and heterogeneous field, so generic pollination context is not itself Paper 1 novelty.

## Current synthesis and direct competitors

The audit explicitly includes major recent synthesis/competitor work, including:

- Xiao et al. 2025, *Scientia Horticulturae* — broad *Camellia* flower-colour molecular review;
- Fan et al. 2026, *Plant Biotechnology Journal* — genus-scale colour phylogenomics, TE/SV regulatory diversification, and functional MYB evidence;
- Fan et al. 2026, *Industrial Crops and Products* — yellow-*Camellia* population genomics and WRKY23→FLS functional regulation.

These studies rule out broad priority claims about *Camellia* colour mechanisms, pathway convergence, regulatory diversification, or micro-to-macro colour genomics in general.

## Novelty confidence after the expanded audit

### High confidence: not novel

- the same flower colour can arise through different genes/mechanisms;
- alternative pigment pathways can converge on similar visible colour;
- pathway-level/modular flower-colour convergence;
- candidate/discovery design can alter apparent genetic repeatability;
- partial identification or measurement-process dependence as general concepts;
- ancestral-state/transition inference sensitivity;
- *Camellia* pigment biochemistry, DFR/FLS competition, MBW regulation, and yellow-flavonol biology;
- micro-to-macro *Camellia* flower-colour genomics in general;
- pollination/climate as possible flower-colour selective contexts.

### Still defensible as a specific empirical contribution

No directly matching study has been identified that combines all of the following in one flower-colour analysis:

1. literature mechanisms represented as partially observed multivariate states;
2. exact recurrence bounds over unresolved molecular cells;
3. remeasurement of the **same auditable public biological systems** under one frozen candidate-free protocol;
4. direct comparison of literature-conditioned and standardized identified recurrence;
5. topology- and trait-coding-robust testing of a macroevolutionary colour pattern;
6. a separate event-identity gate that prevents ecology/mechanism from being assigned to unstable branches.

This remains an application-specific contribution. The manuscript should avoid an unqualified `first` claim.

## Remaining completeness gaps

A formal PRISMA-style systematic-review claim would still require:

1. **formal CNKI/Wanfang exports** with frozen database-specific search strings, dates, and hit counts; the current Chinese screen is indexed/high-recall but not a full database export;
2. one complete cross-database deduplication and title/abstract/full-text flow covering all English and Chinese retrievals, not only priority records;
3. closed backward/forward citation chasing from Xiao 2025 and the major convergence/pollination anchors;
4. a final conference/grey-literature stopping rule applied to a defined search universe, beyond the thesis policy frozen here;
5. a PRISMA-style flow diagram and per-record full-text exclusion ledger.

Until those are done, use **database-counted high-recall evidence audit**, **targeted evidence synthesis**, or **literature-conditioned mechanism matrix**. Do not use `systematic review`, `exhaustive review`, or `comprehensive meta-analysis` as methodological labels.

## Current consequence for Paper 1

The formal database pass changed the literature-ascertainment layer once and was re-frozen as science v0.2.1. The subsequent Chinese/grey screen added no independent recurrence cluster and therefore does **not** reopen science v0.2.1 or AJB v0.8.

The current scientific interpretation remains:

> **Broader literature coverage strengthens evidence that the published molecular observation process is anthocyanin-heavy, while standardized remeasurement of the five auditable public common-set systems continues to reject one invariant whole A/F/C/P package and supports transition-class-dependent modular reuse. At the macro scale, local colour pattern remains identifiable while individual transition events remain non-robust.**
