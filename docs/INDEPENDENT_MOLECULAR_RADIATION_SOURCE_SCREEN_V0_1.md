# Independent floral pigment + transcript + tree source screen — 2026-10-28

**Status: publication-level screen only, zero independent matched source datasets admitted.** This screen follows the representation audit in PR #432 and does not reopen or reinterpret the original 47 Petunieae outcomes.

## First source to inspect: Iochrominae

The 2018 *Molecular Biology and Evolution* study, [Convergent Evolution at the Pathway Level: Predictable Regulatory Changes during Flower Color Transitions](https://academic.oup.com/mbe/article/35/9/2159/5034462), reports **pigment production across 28 species**, expression of **seven anthocyanin pathway genes**, and comparative phylogenetic analyses. This is the strongest identified candidate for a genuinely independent source. **It is not yet admitted:** the report does not by itself verify that all 28 species have complete quantitative concentrations, expression values, and exact tip identifiers in the author-used dated tree. The first empirical task is to recover source matrices, identify the actual overlap, and validate the original tree.

A second potentially useful source is the 2025 Iochroma study [MYB regulator of “colorless” flavonols underlies the evolution of red flowers](https://academic.oup.com/g3journal/article/15/12/jkaf230/8269314), with [OSF data/code](https://osf.io/j5m8f/) and floral RNA-seq for six species under SRA PRJNA1102413. It is mechanistically relevant to flavonol-related MYBs, but six species with expression data are **not proof** of a six-tip matched metabolite-concentration dataset. It remains HOLD until the original chemical matrix and tree are verified.

Other candidates: the two-species *Lysimachia* blue/orange polymorphism study has floral transcriptomics and biochemistry but does not provide a suitable independent macroevolutionary radiation by itself; four-species *Achimenes* comparative floral transcriptomics requires quantitative pigment overlap verification; *Ruellia* offers 51-species pigment chemistry and phylogeny but its authoritative author-used tree remains unresolved in the CHUN source gate, and gene expression is not established. These are not interchangeable controls.

## Admission criteria

1. Authoritative original data archive and license/provenance established, with accessible raw species × quantitative pigment concentration and species × measured expression matrices.
2. A species-ID intersection is materialized and audited, including missingness and stage/tissue comparability, **before any source prediction outcome**.
3. The author-used original phylogeny is retrieved and taxon names are reconciled without topology substitution.
4. A pre-outcome contrast is frozen on that intersection. The original Petunieae four-gene and flavonol target sets must **not** be blindly copied to a different radiation with a different gene/compound assay; compare biologically homologous pathway modules and document mismatches.
5. Only then run source-internal leave-one-tip-out pigment+phylogeny vs pigment+phylogeny+expression, with suitable negative controls and model-dependent null. One small radiation cannot establish universal ancestry-independent expression→product effects.

**Current decision:** prioritize **Iochrominae 2018** raw source retrieval and matrix/tree intersection. No second empirical radiation has been validated, no new P has been computed, and the source-level Petunieae phylogeny-adjusted negative remains intact.

**Governance:** Original Camellia AJB Paper 1, frozen Evolution Letters v0.3 and integrated CHUN Draft #414 remain unchanged.
