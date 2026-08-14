# chun

Comparative project on **reversible floral pigment deployment** in East Asian and Southeast Asian plants.

The starting question is whether repeated flower-colour transitions reflect irreversible pathway loss and de novo gain, or repeated **silencing, flux redirection, recruitment and reactivation of conserved pigment machinery**.

## Current comparative systems

- **East Asian *Cirsium*** — white versus pink/purple lineages in the Ryukyus, Taiwan, Japan and nearby continental relatives; test loss, retention, ancestral polymorphism and true anthocyanin reactivation as separate histories.
- ***Camellia*** — white, red/pink and yellow evolution, with special attention to early-diverging yellow-rich lineages in southwestern China and Vietnam and phylogenetically distinct yellow trajectories in Southeast Asia.

Visible yellow is **not** treated as one biochemical state. Anthocyanin, flavonol and carotenoid evidence are stored on separate axes; a visible colour is never used by itself to infer a pigment mechanism.

## Research rule

The term **reactivation/re-expression** is reserved for cases supported by both:

1. a phylogenetic history of active → suppressed/absent → active floral pigmentation; and
2. molecular evidence that the underlying pathway remained available during the suppressed interval.

Otherwise use `retention`, `recruitment`, or `gain`.

## Current evidence products

- [Flower-colour reactivation hypotheses](docs/FLOWER_COLOR_REACTIVATION_HYPOTHESES.md)
- [Pigment-state schema](docs/PIGMENT_STATE_SCHEMA.md) — **authoritative biochemical state definition; supersedes the earlier simplified A/W/Y shorthand**
- [Evidence audit — 2026-08-14](docs/EVIDENCE_AUDIT_2026-08-14.md)
- [Taxon × colour × pigment evidence matrix v0.1](data/evidence_matrix_v0_1.csv)
- [Source/provenance registry v0.1](data/source_registry_v0_1.csv)
- [Issue #1 — comparative problem, hypotheses and analysis gates](../../issues/1)

## Public raw-data anchors

- *Cirsium*: `PRJNA1311153` — leaf RNA-seq; usable for nuclear phylogeny and coding-integrity screens, **not** petal-expression evidence.
- *Camellia nitidissima*: `SRP112181` — developmental flower RNA-seq; usable for anthocyanin/flavonol/carotenoid pathway-expression reanalysis.

## Immediate execution goal

1. freeze accession/sample manifests for `PRJNA1311153` and `SRP112181`;
2. screen anthocyanin-pathway coding integrity across the focal *Cirsium* lineages;
3. reconstruct developmental pigment-pathway deployment in *C. nitidissima*;
4. expand the evidence matrix across the broad *Camellia* nuclear framework and the China–Vietnam yellow lineages;
5. run ancestral-state/transition models only after tree provenance and biochemical state definitions pass their evidence gates.

The first phylogenetic analyses will keep **visible colour** and **biochemically supported pigment profiles** separate. A white-bridge/accessibility model is a hypothesis to compare, not an assumed transition rule.