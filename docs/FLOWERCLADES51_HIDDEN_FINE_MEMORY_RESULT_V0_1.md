# Hierarchical hidden flower-color memory — exploratory result v0.1

## New question

The v0.4–v0.5 extensions showed that flower-color profiles can be separated into:

- overall **memory amplitude**;
- coarse↔fine **scale tilt**;
- a structural **opportunity** for fine distinctions to exist inside coarse states.

But a global fine-minus-coarse AUC can still miss the biological quantity we actually care about.

A clade can have a strong coarse signal and still contain phylogenetically organized fine states **inside** each coarse phenotype.

This extension asks that question directly:

> among species pairs that already share the same coarse flower-color state, are close relatives more likely than expected to share the same fine flower-color state?

## Conditional estimand

For each of the 21 Flower-clades-51 common-frame clades with genuine fine→coarse compression opportunity:

1. retain only unordered species pairs that share the same frozen coarse state;
2. score each pair by negative patristic distance;
3. label whether the pair also shares the same frozen fine state;
4. calculate the conditional ROC AUC;
5. permute fine-state labels **within each coarse-state group**, preserving coarse membership and all fine-state counts;
6. repeat for 9,999 permutations.

The null is therefore not “no phylogenetic structure at all.” It is:

> no fine-state phylogenetic organization beyond that already implied by coarse-state membership.

Because coarse groups can differ in fine-state diversity and distance distributions, the conditional permutation AUC need not be centered on 0.5. The primary effect is therefore:

[
Delta AUC_{hidden}
=
AUC_{observed}
-
E(AUC_{within-coarse permutation}).
]

## Main result

Across the 21 opportunity clades:

- **18/21** have positive hidden-memory effects;
- median centered effect = **+0.0270 AUC**;
- bootstrap 95% interval for the median = **+0.0084 to +0.0453**;
- one-sided Wilcoxon P = **3.34 × 10^-5**;
- one-sided sign-test P = **7.45 × 10^-4**.

Six clades individually clear the 9,999-permutation P <= 0.05 threshold:

- *Diospyros*;
- *Lonicera*;
- *Passiflora*;
- *Rosa*;
- *Solanum*;
- *Symplocos*.

The cross-clade result is much broader than the list of individually significant clades: most clades show a small positive conditional effect, while a subset show large effects.

## Why this changes the interpretation

Previously the programme asked whether coarse, intermediate or fine resolution “wins” globally.

That framing can obscure nested structure.

A clade may show:

[
AUC_{coarse} > AUC_{fine}
]

and still satisfy:

[
Delta AUC_{hidden finemid coarse} > 0.
]

That happens here. Among the six clades with negative global fine-minus-coarse tilt, **5/6 still have positive hidden fine-memory effects**, with median +0.0177 AUC.

Among the 15 clades with positive global tilt, 13/15 have positive hidden effects, median +0.0290.

So global scale tilt is not equivalent to the presence or absence of fine-scale historical organization.

## Hidden memory is a distinct architectural layer

The permutation-centered hidden-memory effect is essentially unrelated to the two earlier global coordinates:

- hidden effect vs scale tilt: rho = **0.110**, P = **0.634**;
- hidden effect vs memory amplitude: rho = **0.131**, P = **0.571**.

This suggests three separable questions:

1. **memory amplitude** — how much flower-color history remains overall?
2. **scale tilt** — whether global history is more visible at coarse or fine representation;
3. **hierarchical hidden memory** — whether finer distinctions remain phylogenetically organized inside a coarse state.

The old winner taxonomy mixed all three.

## Revised conceptual model

The current exploratory architecture becomes:

[
oxed{
	ext{evolutionary memory architecture}
=
	ext{amplitude}
+
	ext{global scale tilt}
+
	ext{hidden within-state organization}
}
]

with representation opportunity acting as a structural gate: hidden fine organization can only be tested where fine distinctions actually exist inside coarse states.

This is a positive explanation for why “no universal resolution” does not imply absence of biological structure.

## Prospective consequence

The already outcome-unopened *Ruellia* HPLC system now has a frozen held-out prediction:

- first determine whether fine→coarse compression opportunity exists on its frozen common frame;
- if opportunity exists, predict a positive fine-minus-coarse effect under the pre-frozen profile estimator;
- no opportunity is a structural zero, not a biological success.

A stronger future version can preregister the **within-coarse hidden-memory estimand itself** in a new independent radiation before any phenotype outcomes are opened.

## Boundary

This Flower-clades-51 result is post-outcome and pilot-exposed. It reuses the same source trees and flower-color states and does not count as independent replication.

It does not identify the ecological cause of hidden fine organization.

Frozen Evolution Letters v0.3 and Camellia Paper 1 remain unchanged.
