# Wu 2022 public nuclear-backbone asset gate

## Result

The fully public `PRJNA665925` route resolves **98/98 species-level Camellia taxa** to a preferred public assembly/transcriptome source.

- ID-bound `All_assemblies` routes: **95** taxa.
- Bulk fallback routes: **3** taxa.
- Bulk fallback taxa: `Camellia campanisepala`, `Camellia lipoensis`, `Camellia salicifolia`.
- Taxon-level source coverage: **100%**.

## Decision

The macro-side bottleneck is no longer taxon-level source availability. The next gate is payload identity/checksum validation, especially for the three bulk-fallback taxa, followed by reconstruction of the Wu et al. low-copy nuclear backbone.

## Claim boundary

This is a **resource/provenance gate only**. It does not reconstruct the 405-gene topology, estimate branch lengths, infer flower-colour ancestral states, count transitions, or test pigment-module enrichment. The Fan 2026 figure-only topology is not substituted for a machine-readable public tree.
