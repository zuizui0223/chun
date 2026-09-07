# Angraecinae pre-result comparison gate v0.1

## Purpose

Freeze the interpretation rules **before** inspecting the new Angraecinae Mk estimates. This prevents the third radiation from being used post hoc to rescue a preferred white-ancestor narrative.

This gate is post-Paper-1 and does not modify Camellia Paper 1.

## Frozen observation unit

Primary terminal characters are source-organ states from Andriananjamanantsoa et al. 2016 S2/S3:

- character 20: sepal colour;
- character 23: petal colour.

`GREEN` means source code 1 (`green to yellowish`); `WHITE` means source code 2 (`white to white green`). Ocher/other states are `OUTSIDE_BINARY` and are pruned for the GREEN/WHITE Mk comparison, never recoded.

Labellum, spur, concordant sepal+petal and all-four-organ states are sensitivity layers, not replacements for the two primary organs.

## Frozen topology set

Three independently inferred public-sequence trees are evaluated as one biological radiation:

1. `plastid_full` — matK+rps16+trnL, all informative source columns;
2. `plastid50` — same loci, columns with >=50% A/C/G/T occupancy;
3. `all4_full` — plastid plus ITS.

Tree variants are topology/alignment sensitivities, **not independent clades**.

## Common binary estimator

Use the same two-state Mk likelihood implementation used for Hydrangea:

- ER (= SYM for two states);
- ARD;
- equal and stationary root priors;
- branch lengths in sequence substitutions/site, not years;
- no fixed ancestral WHITE state.

Primary cross-clade ratio:

`q(GREEN -> WHITE) / q(WHITE -> GREEN)`.

Ratio >1 points toward return/acquisition of WHITE; ratio <1 points toward GREEN. A point estimate alone is not a directional result.

## Pre-frozen result gates

### A. Data admission

A primary organ is analysis-ready only if:

- source S1 -> S3 joining is exact and unique for the included tip;
- at least 140 ingroup tips retain GREEN or WHITE for that organ;
- both states are represented;
- the full source-defined Angraecinae sample set forms a monophyletic clade on the tree before organ-policy pruning.

Failure is reported as an identifiability/data result, not repaired by relaxed name matching.

### B. Supported directional asymmetry within Angraecinae

Call a GREEN/WHITE rate asymmetry supported only if **both primary organs** satisfy all of the following:

1. all three tree variants have the same point-estimate direction;
2. at least two of three equal-root ARD conditional 95% profile intervals exclude ratio=1 in that same direction;
3. those same fits improve AIC over ER by >=2;
4. no fit used for the claim is on an optimizer boundary or high-rate likelihood plateau.

Otherwise report direction as unresolved/suggestive.

### C. Organ dependence

Call organ dependence supported if sepal and petal primary analyses give materially incompatible conclusions under the same tree set, for example:

- opposite supported directions; or
- one organ repeatedly supports asymmetry while the other repeatedly supports ER/interval overlap with 1.

A difference in point estimates alone is not sufficient.

### D. Robust ancestral WHITE

Do **not** call a WHITE root robust unless root `P(WHITE) >= 0.8` under both ER and ARD and under both equal/stationary-root treatments wherever those quantities are estimable, across all three tree variants for a primary organ. Published white symplesiomorphy remains a source comparison, not a prior.

### E. Cross-clade universal direction

A universal WHITE-direction law would require at least three independent radiations with source-to-tree reanalyses that each pass criterion B in the same direction. Hydrangea and Linoideae already do not satisfy this condition, so Angraecinae cannot by itself establish a universal direction.

### F. Retained general-rule candidate

The currently retained rule is instead:

> ancestral/display state constrains the evolutionary state space without fixing one universal transition direction; biologically informative repeatability or organization may occur at finer hue, organ or molecular-module levels than a coarse WHITE/NONWHITE collapse.

Angraecinae tests a strong prediction of this formulation because it is a low-dimensional GREEN/WHITE system. The rule gains support if the third radiation is analyzable without recovering a universal direction and/or if organ-specific state representation materially changes inference. It is weakened if the common binary estimator produces the same robust direction and robust WHITE root across independent white-like radiations under the frozen criteria.

## Claim boundary

No Angraecinae result is encoded in this file. It freezes only methods and interpretation thresholds before the current source/tree/model workflow finishes.
