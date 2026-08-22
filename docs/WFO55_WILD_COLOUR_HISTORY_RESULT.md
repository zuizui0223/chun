# WFO55 accepted-species wild-colour history result

## Purpose

Rebuild visible-colour history only after WFO Plant List 2026-06 taxonomy normalization and a species-level wild/floristic colour audit.

## Frozen inputs

- accepted-species nuclear sensitivity tree: 55 Camellia species + Polyspora outgroup;
- strict wild-colour seed: 24 species (A=1, W=19, Y=4);
- dominant-colour sensitivity seed: 30 species (A=4, W=22, Y=4).

## Root-state sensitivity

Both scenarios favour W as the top model-averaged crown state in all four branch-length/root-prior treatments, but W/Y uncertainty is substantial in the topology-only treatment.

Strict scenario:
- Fitch root set: W or Y; minimum changes: 3;
- model-averaged W posterior: 0.801–0.805 with ASTRAL branch lengths;
- model-averaged W posterior: 0.562–0.567 with unit edges.

Dominant scenario:
- Fitch root set: W or Y; minimum changes: 3;
- model-averaged W posterior: 0.864–0.871 with ASTRAL branch lengths;
- model-averaged W posterior: 0.626–0.647 with unit edges.

Thus W remains favoured, but an accepted-species wild-colour analysis does not justify a hard white-ancestor claim without retaining W/Y uncertainty.

## Branch-transition result

Using the same predeclared internal robustness gate as the legacy analysis (same top direction in all four Mk treatments and minimum directional posterior >=0.5):

- strict wild scenario: **0** strong robust branches;
- dominant scenario: **1** W→A branch, leading to the six-species clade `C. azalea`, `C. pitardii`, `C. polyodonta`, `C. reticulata`, `C. saluenensis`, `C. subintegra`;
- cross-scenario strict × dominant gate: **0** accepted robust transitions.

The dominant-only W→A branch is not promoted to a secure macro event because it disappears when dominant/rare-white and polymorphic taxa are treated as missing in the strict wild scenario.

## Public-data boundary

There is currently **no accepted-species branch transition robust to both strict wild-colour and dominant-colour assumptions**. Therefore branch-specific climate, pollination, or micro-to-macro causal enrichment is not identifiable from the current public hard-state colour evidence.

The next valid public-data analyses are branch-independent/pattern-level robustness checks on the accepted-species tree, especially phylogenetic colour conservatism and topology sensitivity. If those macro patterns remain, the paper can stop at a public-data boundary and use the missing wild population colour, spectral, pollination-efficiency and developmental/mechanistic observations to define the next empirical study.

## Superseded result

The three legacy-tip W→A branches from PR #44 remain historical conditional results only. PR #45 and the WFO55 rebuild show that they are not safe causal branches after wild-colour polymorphism and accepted taxonomy are enforced.
