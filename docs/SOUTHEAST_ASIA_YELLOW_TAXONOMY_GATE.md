# Southeast Asian yellow-*Camellia* taxonomy gate

## Why this gate is necessary

The 2026 population-genomic study of yellow *Camellia* reports a distinct clade containing the names *C. cucphuongensis*, *C. flava*, *C. krempfii* and *C. vidalii*, separated from the main yellow-*Camellia* lineage. That topology is potentially important for testing repeated yellow recruitment, relict retention and transitions between pigment states.

However, those four labels are **not four independent species-level evolutionary units under the current taxonomic backbone**.

## Reconciliation of the four published labels

### *Camellia cucphuongensis* -> *Camellia flava*

Current Plants of the World Online treatment follows taxonomic work that reduces *C. cucphuongensis* to a heterotypic synonym of *C. flava*. Therefore the two names must not be counted as two independent yellow origins.

A 2026 transcriptome study nevertheless uses the name *C. cucphuongensis* and generated a pooled vegetative transcriptome from fresh leaf, stem and root tissues collected in Cuc Phuong National Park, Vietnam. It reports 13,600,954 retained clean reads and 118,552 unigenes. In the present audit, the article/Zenodo records expose the paper and supplementary materials, but no open SRA accession or assembled-unigene FASTA was recovered. This remains a potentially valuable coding-pathway resource if the actual sequences are obtained, but it is not currently an independently executable raw-data input.

### *Camellia vidalii* -> *Camellia langbianensis*

Current taxonomy treats *C. vidalii* as a heterotypic synonym of *C. langbianensis*. A 2023 revision also synonymised several other southern Vietnamese names with *C. langbianensis*. Thus *vidalii* must not be counted as a separate yellow origin; the working evolutionary unit is the accepted *C. langbianensis* lineage unless accession-level data later demonstrate otherwise.

### *Camellia krempfii*

*C. krempfii* remains an accepted Vietnamese species. Critically, its colour state must not be inferred from membership in a study of “yellow camellias”. Historical treatments are inconsistent, and at least one standard taxonomic description gives red petals. Therefore the 2026 sequenced accession needs voucher-level flower-colour evidence before it can enter a yellow-state ancestral reconstruction.

### *Camellia flava*

*C. flava* remains an accepted Vietnamese yellow species. A complete chloroplast genome is publicly available as `OR605723` from `PRJNA1089488` / `SRR28385168` / `SAMN40540878`.

That plastome is useful as a maternal-history anchor, but **not** as the main species-history topology for a group already suspected of reticulation and nuclear/plastid discordance.

## Consequence for the 2026 “distinct clade” result

The biologically interesting observation is not “four unusual yellow species form another yellow clade”. After taxonomic reconciliation, the safer interpretation is:

> a Southeast Asian lineage complex containing at least the *C. flava* and *C. langbianensis* evolutionary units, plus accepted *C. krempfii*, is genetically separated from the main yellow-*Camellia* lineage in the published nuclear population analysis; the individual visible-colour and pigment states of each sequenced accession must be verified independently.

That framing creates stronger hypotheses:

1. **Repeated yellow recruitment** — yellow pigmentation evolved independently in the Southeast Asian lineage and the main China–Vietnam yellow lineage.
2. **Retention** — both lineages retained an older yellow-capable regulatory state while later lineages lost it.
3. **Hybrid transfer / reticulation** — parts of the yellow phenotype or its regulatory architecture moved between lineages.
4. **Phenotypic convergence with different chemistry** — the lineages look yellow but differ in flavonol/carotenoid deployment.
5. **Mixed-colour lineage** — the distinct clade itself may contain yellow and non-yellow taxa, making it particularly informative for locating the transition without relying on distant outgroups.

## Admission rules for ancestral-state analyses

For every accession in this Southeast Asian group, require separate fields for:

- published sequence name;
- accepted working taxon;
- synonym / hybrid / unresolved status;
- voucher or sample identifier;
- visible flower colour of that exact sampled accession where possible;
- pigment chemistry evidence;
- nuclear sequence evidence;
- plastid sequence evidence;
- whether it is an independent transition-counting unit.

A species name appearing in a yellow-*Camellia* paper is **not** sufficient evidence that the sequenced accession has a yellow flower.

## Immediate open-data priorities

1. Use `OR605723` as a verified *C. flava* plastid anchor but not as the nuclear history.
2. Recover nuclear ITS/transcriptome/genome data for accepted *C. flava*, *C. langbianensis* and *C. krempfii*.
3. Recover the raw/unigene sequence product behind the 2026 *C. cucphuongensis* pooled transcriptome if legally/publicly available.
4. Tie every 2026 population-genomic accession to voucher-level colour metadata if the request-only dataset becomes available.
5. Compare pigment-pathway coding architecture only after synonym reconciliation so duplicate names do not masquerade as evolutionary replication.

The key unit of replication is therefore **a taxonomically independent, molecularly resolved lineage with verified pigment state**, not a published species name.