# WFO53 UFBoot wild-colour phylogenetic conservatism sensitivity

## Question

Which accepted-species flower-colour clustering signals survive the stronger IQ-TREE LG+G4 + 1000 UFBoot gene-tree topology?

## Frozen inputs

- WFO53 ASTRAL-IV topology from 339 UFBoot gene trees (PR #56 / run 32552618223);
- PR #51 strict wild-colour seed, filtered to 23 species because accepted `C. petelotii` is absent from runtime91 UFBoot data: A=1, W=19, Y=3;
- PR #51 dominant sensitivity seed, filtered to 29 species: A=4, W=22, Y=3.

All tests use 100,000 count-preserving permutations and unrooted topology edge distance.

## Result

### Strict wild-colour scenario

- global same-state MPD: observed 9.644 vs null 9.937; P=0.1724 — not significant;
- global nearest-same-state distance: observed 3.500 vs null 4.357; **P=0.00116**;
- Y (n=3): MPD **P=0.00771**, MNTD **P=0.00721**;
- W (n=19): not significant;
- A is a singleton and is not individually testable.

### Dominant-colour sensitivity

- global same-state MPD: observed 10.000 vs null 10.330; P=0.1327 — not significant;
- global nearest-same-state distance: observed 3.448 vs null 4.651; **P=0.0000800**;
- A (n=4): MPD **P=0.00110**, MNTD **P=0.0119**;
- Y (n=3): MPD **P=0.00501**, MNTD **P=0.00530**;
- W (n=22): not significant.

## Cross-topology interpretation

The FastTree/WFO55 analysis in PR #55 found significant global same-state MPD and nearest-same-state clustering under both strict and dominant trait scenarios. The stronger UFBoot/WFO53 topology retains the **nearest-same-state** signal in both scenarios but not the global same-state MPD signal.

Therefore the topology-robust macro conclusion is narrower than the PR #55 headline:

> accepted wild flower-colour states show **local phylogenetic conservatism** — a labelled species is closer to another species with the same colour than expected from count-preserving random label placements — but evidence for broad/global compression of all same-colour pairs is topology-sensitive.

Y clustering is individually robust in both strict and dominant scenarios on the UFBoot topology. A clustering is only testable in the dominant scenario and therefore remains a sensitivity, not a strict result. W is not individually clustered.

## Public-data implication

Together with PR #53 (zero strict × dominant robust transition branches), the public-data macro result is now a **pattern-without-identifiable-events**:

- local same-colour phylogenetic conservatism is robust to accepted taxonomy, wild-colour assumptions, and nuclear gene-tree method;
- global same-colour MPD is topology-sensitive;
- specific accepted-species colour-transition branches are not robust to wild-colour assumptions.

This prevents branch-specific climate/pollination/molecular causal claims from current public hard-state data and defines the empirical need for population-level wild colour/spectral states and reproductive-function measurements.

## Claim ceiling

Root-independent local phylogenetic pattern only. No ancestral-state, transition-direction, climate, pollinator, or molecular-causation claim.
