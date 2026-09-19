# Resolution opportunity versus realized flower-color memory — exploratory result v0.1

## Why this test

The memory-architecture extension separated cross-radiation profiles into two main coordinates:

1. **memory amplitude** — how much historical signal remains overall;
2. **scale tilt** — whether that signal is stronger at fine or coarse phenotype resolution.

A remaining concern is that scale tilt might be a trivial artifact of state coding. If fine coding simply contains more categories than coarse coding, perhaps fine AUC increases mechanically.

This extension separates **structural opportunity** from **realized phylogenetic structure**.

## Structural opportunity

For each of the frozen 28 common-frame clades we reconstructed, from the exact source object, how many retained fine flower-color states collapse when mapped to the frozen coarse partition.

We define compression opportunity as:

`fine-state count > coarse-state count`.

Seven clades have **zero compression opportunity**:

- Asparagus
- Capparis
- Cordia
- Cornus
- Ocotea
- Prunus
- Rubus

In all seven, fine and coarse partitions are identical on the retained frame and **scale tilt is exactly zero**.

This is a structural identity, not a biological result: if the two partitions are the same, their AUCs must be the same.

## Realization once opportunity exists

Twenty-one clades contain at least one fine distinction hidden by coarse coding.

Among these:

- **15/21** have positive scale tilt;
- **6/21** have negative scale tilt;
- median scale tilt = **+0.01998 AUC**;
- one-sided Wilcoxon P = **0.0192**;
- one-sided sign-test P = **0.0392**.

Thus, where the hierarchy actually provides an opportunity for fine-scale memory to exist, fine structure is more often stronger than coarse structure.

Because this result was pilot-exposed before the machine-readable design was frozen, it is exploratory rather than confirmatory.

## Compression amount does not determine realized tilt

Within the 21 opportunity clades, three different measures of how much information is lost under coarse coding fail to determine the signed tilt:

| compression measure | rho with signed tilt | P |
|---|---:|---:|
| number of fine states collapsed | 0.293 | 0.198 |
| Shannon entropy loss | 0.226 | 0.325 |
| increase in random-pair same-state probability | 0.206 | 0.369 |

The same measures also do not robustly predict absolute tilt magnitude. The strongest diagnostic, pair-collision gain versus |tilt|, remains below the conventional threshold (rho = 0.408, P = 0.0665).

Therefore the result is not simply:

`more compression -> larger fine advantage`.

Compression creates the **opportunity** for scale differences, but phylogenetic placement determines whether that opportunity is realized as a fine or coarse advantage.

## Specificity to scale, not memory strength

Across all 28 clades, fine-state richness is associated with scale tilt:

- rho = **0.422**, P = **0.0253**.

But this association includes the deterministic fact that all seven zero-opportunity clades have both low fine-state richness and zero tilt, so it is not treated as an independent biological effect.

Crucially, fine-state richness is completely unrelated to overall memory amplitude:

- rho = **0.0057**, P = **0.977**.

Thus adding more visible color states does not simply manufacture stronger phylogenetic memory.

## Opportunity × realization framework

The combined v0.4–v0.5 picture is now:

[
	ext{memory architecture}
=
egin{cases}
	ext{amplitude: how much history persists}\
	ext{opportunity: whether the hierarchy can hide finer distinctions}\
	ext{realized tilt: whether those hidden distinctions are phylogenetically organized}
end{cases}
]

This resolves an important ambiguity in the earlier “no universal resolution” result.

A phenotypic hierarchy does not itself determine the winning scale. It defines which scale differences are **possible**. The evolutionary history of the hidden states determines which differences are **realized**.

That gives a sharper biological target for future prospective tests:

> predict the phylogenetic organization of fine distinctions conditional on a known representation opportunity, rather than predicting a universal winner across all clades.

## Boundary

This is a post-outcome, pilot-exposed exploratory extension. It does not modify frozen EL v0.3, does not count as independent replication, and does not identify an ecological cause of realized tilt.

Camellia Paper 1 remains unchanged.
