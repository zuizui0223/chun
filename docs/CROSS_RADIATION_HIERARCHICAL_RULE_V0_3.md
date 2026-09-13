# Cross-radiation hierarchical flower-colour rule v0.3 — separation from the Iris resolution-optimum falsification

## Why this revision is necessary

The prospective Iris result falsifies the frozen claim that the intermediate representation should maximize pairwise phylogenetic predictability relative to coarse and fine representations.

It does **not** directly test the older conditional-null result that finer organization can remain after fixing a coarse state.

These are different estimands and must remain separate.

## Claim A — conditional hierarchical organization

Question:

> After holding a coarse biological state fixed, does finer phenotype identity retain non-random phylogenetic organization?

Current external evidence remains:

- Linoideae — hue organization conditional on WHITE/nonwhite;
- Angraecinae — floral-organ configuration conditional on primary GREEN/WHITE;
- Antirrhineae — pigment class conditional on pigment presence.

Current status: **3/3 admitted external radiations support conditional fine-state organization.**

This claim survives the Iris result because Iris was not analysed with this conditional-null estimand.

## Claim B — universal resolution optimum

Question:

> On one common eligible-tip frame, is pairwise phylogenetic predictability maximized at the predeclared intermediate representation relative to both coarse and fine representations?

Prospective Iris result:

- AUC coarse = 0.4617285166
- AUC intermediate = 0.4543945669
- AUC fine = 0.4870504419
- intermediate − coarse = -0.0073339497
- intermediate − fine = -0.0326558750
- intermediate signal p = 0.9718
- fine > intermediate fail-side p = 0.0486

Terminal preregistered decision: **FAIL**.

Therefore a universal `coarse < intermediate > fine` resolution optimum is rejected by the held-out fourth radiation.

## Combined interpretation

The two results jointly support a narrower and more interesting model:

> **Biological state spaces are often hierarchical, but the resolution that carries the strongest evolutionary signal is not fixed across radiations.**

A fine state can contain structured information beyond a coarse state without implying that the fine state, or any intermediate state, must maximize an unconditional cross-taxon predictability statistic.

This distinction prevents three invalid inferences:

1. conditional fine-state organization -> universal fine-resolution optimum;
2. Iris failure of the intermediate optimum -> failure of hierarchical state structure;
3. repeated hierarchy -> one common causal mechanism.

## Revised status

- Universal WHITE transition direction: **not supported**.
- Coarse ancestry sufficient to determine direction: **not supported**.
- Conditional fine-state organization in the currently admitted external systems: **supported 3/3**.
- Universal intermediate-resolution optimum: **prospectively falsified in Iris**.
- Universal fine-resolution optimum: **not supported and not implied by Iris**.
- Best current synthesis: **radiation-specific resolution profiles within recurrently hierarchical phenotype spaces**.

## Next test

Do not simply add Iris to the 3/3 conditional-null denominator. That would change the estimand after seeing the outcome.

Instead, run two separate future programmes:

1. **Hierarchy replication:** preregister a conditional-null analysis in a new radiation with genuinely nested states.
2. **Resolution-profile prediction:** preregister an outcome-independent moderator model that predicts whether coarse, intermediate or fine resolution should carry the strongest signal in a held-out radiation.

Only the second programme can explain the Iris falsification rather than merely coexist with it.
