# Nuclear phylogenetic realization pattern v0.1

## Why this supersedes the traditional-section proxy as the primary macro layer

The earlier accessibility–realization gap used Fan 2026 traditional sections as historical-background bins. That analysis is useful as a count-controlled taxonomic sensitivity, but sections are not a substitute for a nuclear phylogeny.

The repository already contains a stronger accepted-species result built from public nuclear data and two independent gene-tree pipelines:

1. WFO55 FastTree gene trees -> ASTRAL accepted-species topology;
2. WFO53 IQ-TREE LG+G4 + 1000 UFBoot gene trees -> ASTRAL-IV accepted-species topology.

Both were joined to WFO Plant List 2026-06 taxonomy-normalized wild-colour audits and tested with 100,000 count-preserving label permutations using unrooted topology edge distance.

The nuclear result is therefore promoted to the primary macro realization/persistence pattern. Traditional-section concentration becomes supplementary sensitivity only.

## Global topology-robust pattern

Nearest-same-state phylogenetic distance is shorter than the count-preserving null under both wild-colour coding scenarios and both nuclear topologies.

### FastTree / ASTRAL WFO55

- strict wild: observed nearest-same distance 3.522 vs null 4.522; **P = 0.00212**;
- dominant sensitivity: 3.367 vs 4.812; **P < 1e-5**.

### UFBoot / ASTRAL WFO53

- strict wild: 3.500 vs 4.357; **P = 0.00116**;
- dominant sensitivity: 3.448 vs 4.651; **P = 0.0000800**.

Thus accepted wild colour states show reproducible **local phylogenetic conservatism**. The broader/global same-state MPD signal is topology-sensitive and is not promoted as the robust headline.

## State-specific robustness

### Yellow / Y

Y is the strongest state-specific result.

FastTree / ASTRAL:

- strict: MPD **P = 0.00118**, MNTD **P = 0.00582**;
- dominant: MPD **P = 0.000730**, MNTD **P = 0.00434**.

UFBoot / ASTRAL:

- strict: MPD **P = 0.00771**, MNTD **P = 0.00721**;
- dominant: MPD **P = 0.00501**, MNTD **P = 0.00530**.

Therefore Y clustering survives both stronger/weaker gene-tree methods and both strict/dominant colour codings.

### Anthocyanic / A

A is not testable under strict wild coding because only one strict A species is retained. Under dominant-colour sensitivity, A clusters on both topologies:

- FastTree / ASTRAL: MPD **P = 0.000210**, MNTD **P = 0.00399**;
- UFBoot / ASTRAL: MPD **P = 0.00110**, MNTD **P = 0.0119**.

This remains a sensitivity result, not a strict wild-colour conclusion.

### White / W

W is not individually clustered under either strict or dominant coding on either nuclear topology. The FastTree result gives:

- strict: MPD P = 0.0580, MNTD P = 0.190;
- dominant: MPD P = 0.119, MNTD P = 0.152.

The UFBoot result also reports W as non-significant in both scenarios.

## Cross-scale interpretation

Short-timescale feasibility is documented for A, W and Y outcome classes, but the nuclear tree does not show the same historical distribution pattern for all three states:

- **Y:** demonstrably feasible and strongly/local phylogenetically clustered across both topology and trait-coding sensitivities;
- **A:** demonstrably feasible, but state-specific clustering is only estimable/positive under dominant-colour sensitivity;
- **W:** demonstrably feasible but not individually phylogenetically clustered.

Therefore the simple equivalence

`demonstrably feasible state <=> same macro historical realization pattern`

is rejected more directly by nuclear phylogenetic evidence than by traditional sections.

This still does not identify a generation rate or transition hazard. Local clustering can arise through low transition rates, lineage-specific generation, differential persistence/loss, radiation after an origin, introgression structure, ecological filtering, or combinations of these processes.

## Pattern-versus-event boundary

The accepted-species branch-transition analysis remains more restrictive than the pattern analysis:

- strict wild scenario: zero strong robust branches;
- dominant scenario: one W->A candidate branch;
- cross-scenario strict × dominant gate: **zero accepted robust transitions**.

Thus the current public-data result is deliberately a **pattern without identifiable events**.

This distinction is central to the paper:

> macroevolutionary structure can be reproducibly detected even when individual evolutionary events and their causes cannot be safely assigned.

## Role in the new paper

Primary macro evidence:

1. topology-robust nearest-same-state conservatism;
2. robust Y-specific clustering;
3. W non-clustering and A trait-coding sensitivity;
4. zero branch events robust across strict/dominant wild-state coding.

Supplementary macro sensitivity:

- Fan 2026 traditional-section concentration / realization gap.

The next bridge is not another visible-hue phylogenetic test. It is to replace coarse hue with candidate-free mechanistic A/F/C/P states where public RNA-seq permits, then ask whether mechanistic-state identification alters this pattern-level contrast.
