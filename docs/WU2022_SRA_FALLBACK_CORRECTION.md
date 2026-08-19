# Wu 2022 public-backbone fallback correction

## Result

The three TPIA bulk-download fallbacks were retired after the frozen URL for `Camellia campanisepala` returned HTTP 404 during the live payload audit. The authoritative v0.2 resource manifest therefore uses **95 ID-bound TPIA assemblies + 3 frozen NCBI SRA raw-read fallbacks**.

- `Camellia lipoensis` -> `SRR19266662`
- `Camellia campanisepala` -> `SRR19266763`
- `Camellia salicifolia` -> `SRR19266758`

No TPIA bulk fallback remains in v0.2.

## Next gate

Assemble or otherwise recover transcript sequences for the three raw-read fallbacks, then pass all 98 taxa through the same low-copy nuclear-locus recovery pipeline.

## Claim boundary

This fixes resource provenance only. The three raw SRA runs are not yet equivalent to assembled transcriptomes and are not admitted to topology reconstruction until transcript/locus recovery succeeds.
