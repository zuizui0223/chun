# Paper 1 source provenance audit

## Scope

This audit covers the two source layers that carry the most manuscript risk:

1. the accepted-species wild/floristic flower-colour registry used to define strict and dominant trait seeds;
2. the sequence-aware micro anchors used for the FLS/DFR headline and ANS/ANR supporting mechanism.

It does not re-run any biological analysis.

## Wild-colour provenance policy

The authoritative trait table is `data/wfo55_accepted_species_wild_colour_registry_v0_1.csv`.

Every row must retain:

- the accepted WFO species name;
- species-level evidence granularity;
- exact source authority and HTTPS locator;
- a concise evidence statement;
- strict/dominant state treatment and audit decision.

Sources are classified as:

- **A — authoritative species source:** Flora of China / World Flora Online / official flora, peer-reviewed taxonomic description/revision, or an official biodiversity/institutional species record;
- **B — curated species register:** the International Camellia Register species page, which supplies a species description and bibliographic links to original descriptions/floras; these must be cited as curated sources and the underlying primary reference should be cited when available;
- **C — insufficient/other secondary:** not allowed to support a strict or dominant hard state.

The CI audit forbids C-grade sources from entering either downstream state seed and forbids a strict state whose wild-status label is polymorphic, dominant-only, or exact-colour-insufficient.

Important caveat: `C. drupifera` and `C. sinensis` may retain strict white petal descriptions while carrying explicit provenance caveats about wild versus cultivated material. That caveat must remain visible in Methods/Supplement rather than being silently removed.

## Primary-source checks completed for key wild-colour cases

The audit specifically rechecked high-risk examples that drove the trait reset:

- `C. brevistyla`, `C. japonica`, `C. saluenensis`, and `C. cuspidata` are treated as polymorphic rather than forced A/W hard states;
- `C. reticulata`, `C. polyodonta`, and `C. subintegra` are dominant-A/rare-W sensitivities, not strict A;
- yellow/golden species retained in the strict seed have species-level descriptions rather than a section-level yellow assumption;
- curated-register strict cases retain exact species pages and underlying bibliographic references where available.

The strict seed therefore remains intentionally smaller than the Fan species-level hard-state table.

## Micro sequence-anchor provenance

The machine-readable micro citation table is `data/paper1_micro_source_provenance_v0_1.csv`.

### FLS headline

- **Feng et al. 2024**, BMC Plant Biology 24:847, DOI `10.1186/s12870-024-05332-w`, source project `PRJNA909942`, F01 PacBio run `SRR22729450`: primary CnFLS2 petal-expression/function and primer provenance.
- **Wang et al. 2025**, Scientific Data, DOI `10.1038/s41597-025-05157-8`, `GWHFILD00000000.1 / GCA_049201075.1`: public T2T genome and annotation used to identify the unique primer-compatible genome candidate and local context.
- **Zhou et al. 2013**, Journal of Biosciences, DOI `10.1007/s12038-013-9339-2`, `JF343560.1`: independent CnFLS1 comparator/reference.

The manuscript must distinguish source-paper facts from project inference: Feng et al. identify/functionally test CnFLS2, while `GWHTFILD005297.1` as the operational public genome counterpart is inferred here from exact primers, source-run reads, full-length sequence and local context.

### DFR headline

- **Tateishi, Ozaki & Okubo 2010**, J. Fac. Agr. Kyushu Univ. 55(1):21–28, institutional repository, `AB524885.1`: 605-bp partial CjDFR clone and source RT-PCR assay.
- **Berruti et al. 2015**, Frontiers in Plant Science 6:983, DOI `10.3389/fpls.2015.00983`: independent 167-bp CjDFR qPCR assay, linked by the project to `AB524885.1`. The historical internal assay ID `LARCHER2015_CJDFR_QPCR` is retained only for computational provenance.
- **Mei et al. 2019**, PLOS ONE 14:e0227225, DOI `10.1371/journal.pone.0227225`: tea DFR-family reference set separating canonical CsDFRa (`AB018685.1 / TEA032730`) from CsDFRb subclasses including CsDFRb2 (`XM_028243762.1 / TEA024758`).
- **Zhou et al. 2020**, Molecules 25:190, DOI `10.3390/molecules25010190`, `PRJNA597123 / PRJNA597289`: independent white/pink tea expression cluster containing source DFR/ANS-family loci.

The headline remains a paralog-subclass contrast, not an assumption that all putative DFRbs are biochemically equivalent to canonical DFR.

### ANS / ANR supporting evidence

- **Geng et al. 2022**, Frontiers in Genetics 13:1059717, DOI `10.3389/fgene.2022.1059717`, `PRJCA012977`.
- **Qu et al. 2024**, BMC Plant Biology 24:18, DOI `10.1186/s12870-023-04655-4`, `GSE236364`.

Two bibliographic corrections are preserved explicitly. The historical internal study label `Xu2023_reticulata_mixed_regions` points to **Qu et al. 2024**. The historical internal assay label `LARCHER2015_CJDFR_QPCR` points to the **Berruti et al. 2015** paper above. These legacy computational IDs may remain for reproducibility, but manuscript and source-display citations use the corrected bibliographic metadata.

## Manuscript citation rule

For every Main/Supplement mechanism claim:

1. cite the primary article rather than the project summary document;
2. include versioned public accession/run/database identifiers in Methods or Supplement where the project reanalyses public sequence data;
3. separate what the source paper states from what `chun` infers by crosswalk, primer matching, sequence comparison, or synteny;
4. preserve explicit caveats when a source is a curated register or when wild/cultivated provenance is uncertain.

## CI outputs

`audit_paper1_source_provenance.py` produces:

- `wild_colour_source_audit.csv` with source grades and manuscript citation policy;
- `micro_source_audit.csv` with exact primary citations and public accessions;
- `summary.json` listing curated-register dependence and strict-seed provenance caveats.

The audit fails if an insufficient source enters strict/dominant seeds or if a current micro result lacks an exact source-provenance row.
