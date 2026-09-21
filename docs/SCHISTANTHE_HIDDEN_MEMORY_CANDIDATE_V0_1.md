# Rhododendron sect. Schistanthe held-out candidate — source admission v0.1

## Decision

`ADMIT_SOURCE_COMPLETE_PENDING_ROWLEVEL_STATE_SUPPORT_GATE`

The candidate passes the outcome-blind source-completeness screen.

### Exact trait object

- `Vireya_RADsamples_tiplabels_ingroup_color_clade.csv`
- Dryad file id `3623568`
- size `6,182` bytes
- SHA-256 `266045976d6d0b78a74bcf43c90a30a9e52848d0f25cc4a3b96997b080581e4e`

### Exact chronogram

- `VireyaRADd10m5c91R1_0717_Rdref_min4_raxml_treePLCIs.mean.newick.named`
- Dryad file id `3623564`
- size `9,700` bytes
- SHA-256 `41bc04cdc63032086485c1ce6daf6dedc72fe582e142f7970b72d3143056390b`

The source study reports 114 sect. Schistanthe taxa.

## Trait hierarchy frozen before row-level colors

Fine state:

> exact source flower-color string after trivial normalization only.

Coarse state:

> `WHITE` iff the normalized exact source string is `white`; every other nonmissing exact string is `NONWHITE`.

No color synonyms, mixed-color interpretation or semantic merging is allowed after opening the rows. A composite/ambiguous source label that prevents the deterministic hierarchy from being applied enters `HOLD_SCHEMA`.

Existing support rules are retained:

- fine state minimum support = 5;
- minimum common frame = 20 tips.

## Firewall

At source admission:

- row-level color values: unopened;
- state frequencies: uncomputed;
- tree body / tip labels: unopened;
- hidden-memory AUC: uncomputed.

## Next gate

Recover both exact objects and verify their SHA-256 digests. Tree tips and branch lengths may then be inspected. From the color file, inspect header and identifier fields only and freeze the species/tree crosswalk **before** reading the target color-state values.

This candidate is an additional prospective validation route. It does not change the already-frozen EL v0.7 Ruellia promotion rule.

Frozen EL v0.3 and Camellia Paper 1 remain unchanged.
