# Flower-color evolutionary memory architecture — exploratory result v0.1

## New question

The previous programme asked which phenotype resolution “wins”: coarse, intermediate, or fine.

That framing treats the three levels as competing alternatives. The current exploratory extension asks a different question:

> Can the three-resolution profile be decomposed into biologically interpretable continuous coordinates?

We define three fixed, algebraic coordinates before any new fitting:

1. **memory amplitude**  
   `(AUC_coarse + AUC_intermediate + AUC_fine)/3 - 0.5`

   This measures how much same-state phylogenetic memory is retained overall.

2. **scale tilt**  
   `AUC_fine - AUC_coarse`

   Positive values mean that the retained history is expressed more strongly at fine than coarse phenotype resolution; negative values mean the reverse.

3. **intermediate curvature**  
   `AUC_intermediate - (AUC_coarse + AUC_fine)/2`

   This measures whether the intermediate representation forms a distinct peak or trough beyond the coarse-to-fine line.

This is a **post-outcome exploratory reparameterization**. It does not alter frozen EL v0.3 and cannot be presented as prospective evidence.

## Result 1 — most between-clade variation is memory amplitude

Using the fixed orthogonal equivalents of those three coordinates, the 28 completed clades partition their between-clade profile variance as:

| axis | variance share |
|---|---:|
| memory amplitude | **90.65%** |
| coarse↔fine scale tilt | **6.49%** |
| intermediate-specific curvature | **2.86%** |

Clade bootstrap 95% intervals:

- amplitude: **79.1–96.2%**
- scale tilt: **2.5–14.6%**
- intermediate curvature: **0.9–7.1%**

Thus most apparent differences among “winner classes” are actually differences in **how much evolutionary memory remains at all**, not categorical differences among three independent resolution regimes.

## Result 2 — the meaningful shape axis is coarse↔fine tilt, not an intermediate optimum

Median absolute scale tilt was **0.0178 AUC**, about twice the median absolute intermediate curvature (**0.0090 AUC**).

Paired Wilcoxon test:

- |scale tilt| > |intermediate curvature|: **P = 0.00105**

The median intermediate curvature itself was exactly 0 and showed no displacement from zero (P = 0.375).

This provides a simple explanation for why the prospectively predicted intermediate optimum failed: the dominant profile-shape variation is not “where is the middle peak?” but **which side of a coarse↔fine continuum carries more of the retained memory**.

## Result 3 — amplitude has temporal meaning

Memory amplitude strongly tracks the already-derived relative-time persistence summaries:

- amplitude vs persistence slope: **Spearman rho = -0.773, P = 1.44 × 10^-6**
- amplitude vs persistence area: **rho = +0.661, P = 1.28 × 10^-4**
- amplitude vs near–far retention contrast: **rho = +0.641, P = 2.34 × 10^-4**

Higher amplitude therefore corresponds to slower loss / greater retention of flower-color identity across relative divergence.

This does not provide independent replication because both quantities reuse the same states and phylogenetic distances. It does validate the biological interpretation of the amplitude coordinate.

## Result 4 — scale placement is largely independent of memory strength

Amplitude and scale tilt are essentially uncorrelated:

- **rho = -0.017, P = 0.931**

Scale tilt also does not track integrated fine-color temporal persistence:

- tilt vs persistence area: **rho = 0.006, P = 0.978**

So two questions that were previously mixed together are empirically separable:

[
oxed{
	ext{How much evolutionary memory remains?}
}
]

and

[
oxed{
	ext{At what phenotypic scale is that memory expressed?}
}
]

This is the main conceptual gain.

## Revised biological picture

The earlier winner-based view was:

`coarse vs intermediate vs fine`

The memory-architecture view is:

[
	ext{radiation}
ightarrow
(	ext{memory amplitude}, 	ext{scale tilt})
]

with only a small residual intermediate-curvature component.

This converts the apparently negative “no universal winner” result into a positive structural result:

> Flower-color radiations differ primarily in the amount of historical memory they retain, while the phenotype hierarchy independently determines where that memory is visible.

A universal optimal resolution fails because **memory strength and memory scale are separate biological dimensions**.

## Next test

The causal problem can now be made much sharper.

Instead of asking one ecological variable to predict the whole three-resolution profile, future prospective tests can separately predict:

1. **memory amplitude** — expected to respond to forces controlling overall turnover / persistence;
2. **scale tilt** — expected to respond to whether selection, developmental constraint, or sensory function acts on coarse pigment state versus fine biochemical / perceptual identity.

This is a more targeted biological programme than searching for a single “best resolution.”

## Boundary

This result is exploratory and post-outcome. The fixed coordinate transformation is algebraic, not a discovered latent causal model. Temporal associations are not independent evidence. The result belongs to a v0.4 extension and **does not modify frozen Evolution Letters v0.3**.
