# Paper 1 literature coverage audit — 2026-08-27

## Current verdict

The project now has a substantially broader, high-recall literature audit than the original Paper 1 reference list, but it should still **not** call the review PRISMA-complete or exhaustive in a formal systematic-review sense.

What is now defensible is:

> **A targeted, high-recall evidence audit with explicit inclusion/exclusion decisions, current-review citation chaining, and a standardized reanalysis of the public systems that meet the frozen molecular criteria.**

## Why the manuscript reference list was not the literature corpus

`data/paper1_reference_registry_v0_2.csv` is a submission reference registry, not a search database. It intentionally contains only references used directly by the v0.2 manuscript. It therefore cannot be used to argue that the literature search was comprehensive.

The broader evidence architecture is distributed across:

- `data/camellia_flower_color_mechanism_meta_v0_3.csv` — mechanism-focused study systems and independence clusters;
- `data/camellia_mechanistic_literature_expansion_decisions_v0_1.csv` — explicit admit/exclude decisions from the previous expansion;
- `data/camellia_mechanistic_literature_additional_screen_v0_1.csv` — high-recall historical/current screening added after the novelty audit;
- `data/ecological_driver_study_registry_v0_2.csv` and `data/paper1_ecological_primary_references_v0_1.csv` — ecology evidence;
- `data/paper1_novelty_prior_art_registry_v0_1.csv` and `data/paper1_novelty_search_log_v0_1.csv` — prior-art and novelty search decisions.

## Molecular literature coverage

### Modern omics layer

The current mechanism registry already contains the major public transcriptomic/metabolomic flower-colour systems used in the Paper 1 recurrence architecture, including:

- white/pink *C. sinensis*;
- multiple *C. japonica* colour systems;
- red/pink/white and spatial/developmental *C. reticulata* systems;
- *C. sasanqua* colour diversity;
- yellow developmental *C. nitidissima* and *C. perpetua*;
- multispecies red/yellow/white comparisons;
- genus-scale 2026 colour phylogenomics.

A 2026-08-27 high-recall species-by-species search recovered the major already-admitted modern studies and also identified auxiliary evidence that had not been part of the frozen recurrence matrix. Those additional studies are now decision-logged rather than silently omitted.

### Historical pigment layer

The search was extended backward well before the RNA-seq era. Examples now explicitly screened include:

- Endo 1958 — anthocyanin/leucoanthocyanin chemistry in *C. japonica*;
- Miyajima et al. 1985 and Scogin 1986 — yellow-pigment chemistry in *C. chrysantha*;
- Saito et al. 1987 — cyanidin derivatives across red *Camellia* species/cultivars;
- Sakata et al. 1987 — anthocyanins of wild Section *Camellia* forms;
- Hwang et al. 1992 — yellow-pigment inheritance in *C. chrysantha* hybrids;
- Nakayama et al. 2008 — aluminium–flavonoid interaction in deep-yellow *C. chrysantha*;
- Zhou et al. 2013 — functional CnFLS1 evidence.

These papers matter for biological interpretation and priority, but most do **not** contribute an independent A/F/C/P transcript-state direction signature. Their exclusion from the recurrence estimator is therefore methodological, not a literature-search omission.

### Current synthesis / direct competitors

The audit explicitly includes:

- Xiao et al. 2025, *Scientia Horticulturae* — a comprehensive Camellia flower-colour molecular review with roughly 180 references;
- Fan et al. 2026, *Plant Biotechnology Journal* — 237 accessions, 11 genomes, genus-scale colour reconstruction, TE/SV regulatory diversification and functional MYB evidence;
- Fan et al. 2026, *Industrial Crops and Products* — yellow-Camellia population genomics and functional WRKY23→FLS flavonol regulation.

These studies materially narrow what Paper 1 can claim as novel.

## Why some identified papers are not recurrence replicates

The frozen recurrence analysis is a **transcript-state comparison**, not a generic bibliography count. A study can be highly relevant yet remain outside the recurrence estimator if it lacks one of the required features:

1. a matched flower/petal contrast with a canonical direction;
2. interpretable A/F/C/P transcript-state evidence;
3. independence from an already represented biological/evolutionary cluster;
4. sufficient public raw data for candidate-free remeasurement when it is used in the standardized arm.

Accordingly:

- pigment-only chemistry studies inform state interpretation but not transcript-state signatures;
- functional heterologous overexpression can establish feasibility without adding an independent evolutionary origin;
- multiple papers on one taxon/developmental system strengthen a cluster but do not multiply the independent-cluster denominator;
- vegetative tea FLS studies are relevant to enzyme function but not to the flower-colour recurrence matrix;
- review articles are citation-chaining/novelty anchors, not empirical replicates.

This distinction should be made explicit in Methods if the manuscript uses the word `literature` for the molecular observation matrix.

## Ecological literature coverage

The existing ecology registry covers modern field, exclusion, supplementation, sensory, seasonal and climate-mediated studies from 1985–2026. The high-recall audit found that the historical Camellia pollination literature goes earlier.

A review of Chinese pollination ecology identifies Wu (1977), *The pollinating bees on Camellia oleifera with descriptions of 4 new species of the genus Andrena*, as the first Chinese pollination-ecology publication and describes specialist non-*Apis* pollinators of cultivated *C. oleifera*. This paper and its citation chain were absent from the current Paper 1 ecology registry.

This historical extension does not overturn the current ecological conclusion. It strengthens the statement that Camellia pollination ecology is an established, context-rich literature and therefore cannot serve as a generic novelty claim for Paper 1.

## Novelty confidence after high-recall screening

### High confidence: not novel

- same flower colour can have different genes/mechanisms;
- alternative pigment pathways can converge on similar visible colour;
- pathway-level/modular flower-colour convergence;
- candidate-focused study design can affect estimates of genetic reuse;
- ancestral-state/transition inference is coding/model sensitive;
- Camellia pigment biochemistry, DFR/FLS competition and MBW regulation;
- micro-to-macro Camellia flower-colour genomics in general;
- pollination/climate as potential flower-colour selective contexts.

### Still defensible as a specific contribution

No directly matching study was identified that combines all of the following in one flower-colour analysis:

1. literature mechanisms represented as partially observed multivariate states;
2. exact recurrence bounds over unresolved molecular cells;
3. remeasurement of the **same public biological systems** under one frozen candidate-free protocol;
4. direct comparison of literature-conditioned and standardized identified recurrence;
5. topology- and trait-coding-robust testing of a macroevolutionary colour pattern;
6. a separate event-identity gate that prevents ecology/mechanism from being assigned to unstable branches.

The manuscript may therefore claim this **empirical combination** as its contribution, but should avoid an unqualified `first` unless a closed systematic search later establishes priority.

## Remaining completeness gaps

A formal systematic-review claim would still require:

1. database-specific searches with frozen database names, dates, exact query strings and hit counts;
2. deduplication and title/abstract/full-text screening ledger;
3. complete backward/forward citation chasing from Xiao 2025 and the major flower-colour convergence reviews;
4. dedicated Chinese-language database coverage (CNKI/Wanfang or equivalent), especially older Camellia horticulture and pollination work;
5. explicit grey-literature/conference/thesis policy;
6. a documented stopping rule showing that additional search families no longer add eligible independent study systems.

Until those are done, use `high-recall evidence audit`, `targeted evidence synthesis`, or `literature-conditioned mechanism matrix`; do not use `systematic review`, `exhaustive review`, or `comprehensive meta-analysis` as methodological labels.
