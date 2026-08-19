# Wu 2022 known checksum-collision correction

## Decision

The authoritative public-backbone resource state is **93 ID-bound TPIA transcriptome assemblies + 5 frozen PRJNA665925 raw RNA-seq fallbacks**.

In addition to the three stale bulk-route fallbacks already moved to SRA, two nominally ID-bound TPIA archives are excluded because an earlier live audit found their outer ZIP SHA256 checksums to be exactly identical despite different taxon metadata and different NCBI runs:

- `Camellia euphlebia` -> `SRR19266673`
- `Camellia pilosperma` -> `SRR19266674`

The other raw fallbacks remain `C. lipoensis` (`SRR19266662`), `C. campanisepala` (`SRR19266763`) and `C. salicifolia` (`SRR19266758`).

## Claim boundary

This is a provenance correction, not a phylogenetic result. The five SRA fallbacks require transcriptome/locus recovery before admission to a nuclear topology. No colour-transition or pigment-module inference is changed.
