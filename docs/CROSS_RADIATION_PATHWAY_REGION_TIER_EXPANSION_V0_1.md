# Cross-radiation pathway-region tier expansion — v0.1

## Why this analysis was needed

The first cross-radiation synthesis used a strict four-subspace comparison for the directly matched Iochrominae, Cape Erica and Petunieae systems. Under that strict coding, hue/hydroxylation mapped cleanly to branching machinery in 3/3 systems, whereas only Iochrominae gave a single fixed late/output label for pigment amount/depletion.

That strict result risked confusing **exact subspace identity** with the broader biological question the user wants to test: whether different kinds of flower-colour change repeatedly use the same **region of the pigment network** across many radiations.

The present analysis therefore expands the evidence in tiers rather than weakening the M1 matched-axis definition.

## Tier definitions

### M1 — matched-axis radiation evidence

One radiation contains direct information for both a hue/branching dimension and an amount/depletion dimension under a common comparative frame.

Systems: Iochrominae, Cape Erica, Petunieae.

### M2 — hue/branching functional stress tests

Independent event-specific functional data can test whether branching/hydroxylation nodes recur, but these data are not silently treated as the same observation regime as M1.

Current system: Ipomoea.

### M3 — pigment-loss/depletion functional stress tests

Independent event, lineage or endpoint-panel data can test whether pigment loss/depletion repeatedly localizes downstream or to pigment-output regulation. Event identity must remain explicit.

Current systems: Aquilegia, Epimedium.

Numerical pooling across M1/M2/M3 is forbidden because the biological units differ.

## Result 1 — hue/branching is stable across matched and functional tiers

### M1

- Iochrominae — hue shifts involve F3'H/F3'5'H branching expression.
- Cape Erica — both yellow/hue-branch taxa localize to F3'H.
- Petunieae — preregistered hue response selects `BRANCHING_HUE` across 53 anthocyanin-positive taxa, AICc margin 11.60282936.

M1 support = **3/3 systems**.

### M2

Ipomoea provides a qualitatively different but strong functional stress test: three robust independent blue/purple-to-red origins repeatedly implicate reduced floral F3'H regulation.

Expanded support = **4/4 systems across M1 + M2**.

This does not imply the same mutation or expression coefficient recurs. The recurrent level is the branching/hydroxylation region.

## Result 2 — the initial amount/depletion conclusion changes at hierarchical pathway resolution

The earlier strict summary said only 1/3 matched systems selected one fixed output subspace. That statement remains correct for the exact M1 subspace coding, but it is incomplete biologically.

### Iochrominae

The four independent pigment losses converge on a downstream/late expression module including F3'5'H, DFR and ANS.

### Cape Erica

The six white/depletion taxa are heterogeneous at the exact causal node:

- UDP-GST: 2;
- DFR: 2;
- ANS: 1;
- bHLH: 1.

However, at the next hierarchical level the pattern is not arbitrary:

- **5/6** focal nodes are `STRUCTURAL_LATE`;
- **1/6** is a trans-regulatory bHLH loss;
- **0/6** uses the F3'H hue-branch node.

Thus Cape Erica is heterogeneous at exact node resolution but concentrated on the downstream/output side at pathway-region resolution.

### Petunieae

The preregistered raw pigment-amount response remains a genuine unresolved case:

- nominal best = `BRANCHING_HUE`;
- best-vs-next AICc margin = 0.44436806;
- the nominal best does not improve on the null;
- a source-method log-amount sensitivity selects `LATE_OUTPUT`, but this cannot change the frozen primary classification.

Therefore M1 amount/depletion region support is **2/3**, with **1/3 unresolved**, not a supported contrary region.

## Result 3 — M3 external stress tests strengthen downstream/output localization

### Aquilegia

Seven A-minus molecular lineages associated with repeated anthocyanin loss show convergent stronger downregulation toward the late pathway. Exact causal regulators are not resolved for every event.

### Epimedium

Four A-minus endpoint species share ANS downregulation (4/4), DFR is low in 3/4, and CHS/FLS implementation remains heterogeneous. Historical event identity is unresolved, so this is endpoint/common-panel evidence rather than an event-recurrence estimate.

Across M1 + M3:

- downstream/output/regulatory support = **4/5 systems**;
- unresolved = **1/5** (Petunieae raw amount);
- supported early-core or hue-branching counterexample = **0/5**.

The units are heterogeneous, so 4/5 is a system tally, not a pooled effect size or binomial meta-analysis.

## Revised cross-radiation candidate

The more comprehensive evidence no longer supports the simple story that `hue is predictable whereas amount/depletion is not`.

A stronger and more accurate candidate is:

> **Flower-colour predictability concentrates at intermediate biological resolution. Hue/hydroxylation changes repeatedly localize to pathway branching machinery, whereas pigment loss/depletion repeatedly concentrates toward downstream output or pigment regulation, even though exact genes and complete molecular implementations remain heterogeneous. At the macro scale, fine-state organization recurs while one shared coarse boundary or transition direction does not.**

This produces one aligned hierarchy:

`coarse visible state/direction` -> weakly shared

`fine biochemical phenotype dimension` -> repeatedly structured

`pathway region / functional module` -> repeatedly shared

`exact causal implementation / complete programme` -> heterogeneous

The current data do **not** justify a pooled numerical statement that predictability literally peaks at one ordinal scale, because the levels use different units. The defensible wording is that repeatable structure **concentrates at intermediate resolutions** across the admitted systems.

## Critical post-hoc boundary

The M2/M3 hierarchical pathway-region synthesis was constructed after the relevant source results were already known. It is therefore **retrospective and hypothesis generating**.

Only the Petunieae hue component was prospectively specified under the current cross-level architecture. Petunieae raw amount remains an adverse/unresolved prospective component and is retained as such.

The intermediate-resolution rule must therefore be frozen before testing newly admitted external systems.

## Next prospective gate

For every new external system, declare before decisive mechanism inspection:

1. phenotype dimension: hue/hydroxylation versus amount/loss/depletion;
2. evidence tier and biological unit;
3. pathway-region ontology;
4. event/lineage independence requirement;
5. what counts as region support versus unresolved versus counterexample;
6. whether the test is prospective or retrospective.

The next data search should target **new systems that test one dimension well**, rather than demanding one radiation reproduce every Camellia data layer.

Camellia Paper 1 remains separate and scientifically unchanged.
