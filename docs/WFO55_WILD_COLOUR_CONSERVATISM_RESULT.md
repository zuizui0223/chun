# WFO55 accepted-species wild-colour phylogenetic conservatism

## Question

Does the macro pattern of flower-colour phylogenetic conservatism survive current accepted taxonomy and a species-level wild/floristic trait audit?

## Frozen inputs

- WFO Plant List 2026-06 accepted-species nuclear sensitivity tree: 55 Camellia + Polyspora;
- strict wild seed: 24 Camellia species (A=1, W=19, Y=4);
- dominant-colour sensitivity seed: 30 Camellia species (A=4, W=22, Y=4).

All tests use unrooted nuclear topology edge distance and 100,000 count-preserving permutations. A singleton state contributes no same-state pair and is excluded from nearest-same-state averaging in both observed and permuted label sets.

## Result

### Strict wild-colour scenario

- global same-state MPD: observed 10.164 vs null 10.961 edges; **P=0.00803**;
- global nearest-same-state distance: observed 3.522 vs null 4.522; **P=0.00212**;
- Y (n=4) is strongly clustered: MPD P=0.00118; MNTD P=0.00582;
- W (n=19) is not individually significant at 0.05 (MPD P=0.0580; MNTD P=0.190);
- A has n=1 and is not individually testable.

### Dominant-colour sensitivity

- global same-state MPD: observed 10.444 vs null 11.213; **P=0.00770**;
- global nearest-same-state distance: observed 3.367 vs null 4.812; **P<1e-5**;
- A (n=4) is strongly clustered: MPD P=0.000210; MNTD P=0.00399;
- Y (n=4) is strongly clustered: MPD P=0.000730; MNTD P=0.00434;
- W (n=22) is not individually significant (MPD P=0.119; MNTD P=0.152).

## Interpretation

The accepted-species result retains the macro pattern that **visible flower-colour states are phylogenetically conserved as a whole**, despite removing taxonomic inflation, wild A/W polymorphism, dominant-only states in the strict scenario, and exact-colour-insufficient taxa.

The earlier claim of a uniquely A-specific lineage-permissivity effect is not retained. A-specific clustering is not estimable in the strict scenario and appears only in the dominant-colour sensitivity. The robust macro conclusion is broader: lineage/history constrains the distribution or persistence of flower-colour states.

## Relation to the public-data boundary

PR #53 found zero accepted-species branch transitions robust to both strict and dominant trait scenarios. Therefore the macro **pattern** is identifiable, whereas specific colour-transition branches and their climate/pollination/molecular causes are not currently identifiable from public hard-state data.

This pattern-versus-event distinction is a central candidate result for the macro paper and directly motivates empirical population-level colour/spectral and reproductive-function sampling.

## Claim ceiling

Root-independent phylogenetic pattern only. No transition direction, adaptation, climate causation, pollinator causation, or molecular mechanism is inferred here.
