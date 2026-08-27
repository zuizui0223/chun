# Paper 1 Luo et al. 2016 literature recheck

## Trigger

Backward/forward citation chasing on 2026-08-27 recovered Luo et al. (2016), DOI `10.3389/fpls.2015.01257`, a comparative red-versus-white flower study that includes *Camellia japonica*. The study had not been represented in the frozen Paper 1 literature matrix because its title is cross-plant rather than Camellia-specific.

For *C. japonica*, Luo et al. report CjDFR expression 9.3-fold higher in red flowers and CjFLS 2.8-fold higher in white flowers. Under the existing outcome-independent white-to-red orientation this maps to:

- A = up;
- F = down;
- C = unknown;
- P = unknown.

This is not a new dependence cluster. It is an additional literature system within `CJAPONICA`.

## Recalculation rule

No estimator or coding rule was changed. The recheck reuses:

- `scripts/analyze_micro_accessibility_v0_1.py` for the full literature observation layer;
- `scripts/analyze_observation_corrected_recurrence_v0_1.py` for class-stratified exact completion bounds and direct overlap;
- the committed 20-cell candidate-free Fig. 2 table for the unchanged standardized common set.

Visible colour does not fill C/P, and Luo is not used to change any candidate-free direction.

## Full literature observation layer

Adding Luo changes the literature matrix from 11 to **12 biological systems**, while the number of dependence clusters remains **6**.

System-level A/F/C/P coverage becomes:

`10 / 5 / 1 / 3`

The exact axis-symmetric ascertainment tests are:

- A enrichment P = **0.0015277862548828125**;
- any-axis maximum-minus-minimum imbalance P = **0.003514796127507716**.

Thus system-level molecular reporting remains strongly nonuniform.

After dependence collapse, A/F/C/P coverage becomes:

`5 / 4 / 1 / 2`

The exact tests are:

- A-specific enrichment P = **0.078125**;
- any-axis imbalance P = **0.1736111111111111**.

Therefore the previous v0.2.1 statement that anthocyanin-axis enrichment remained detectable below 0.05 after dependence collapse is **superseded**. The defensible result is narrower: reporting is clearly nonuniform across biological systems, whereas A-specific enrichment is not retained at the same threshold once repeated evolutionary backgrounds are collapsed.

The descriptive/non-primary recurrence sensitivity is:

- system-level observed signature concentration = **0.23611111111111113**;
- system-level permutation P = **0.031096890310968902** in the hosted frozen-seed run;
- dependence-collapsed observed concentration = **0.2222222222222222**;
- dependence-collapsed permutation P = **0.16048395160483953**.

These permutation values describe the literature-coded matrix and are not the Paper 1 matched transition-class recurrence estimator.

## Anthocyanin-gain matched common set

Luo resolves the literature-side `CJAPONICA:F` cell as down. The three literature signatures on the matched common set are therefore:

- `CJAPONICA`: A up / F down / C unknown / P unknown;
- `CRETICULATA`: A up / F unknown / C unknown / P down;
- `CSIN_WHITE_PINK`: A up / F down / C unknown / P unknown.

There are now **6 unresolved** cluster×axis cells rather than 7, giving `3^6 = 729` exact completions.

Updated literature identified sets:

- exact whole-signature recurrence = **0.333–1.0** — unchanged;
- pairwise A/F/C/P concordance = **0.333–1.0** — lower bound increases from 0.25;
- pairwise identified-set width = **0.6667** rather than 0.75.

The candidate-free common set is unchanged:

- exact whole-signature recurrence = **0.333 exactly**;
- pairwise concordance = **0.333–0.5**;
- pairwise width = **0.1667**.

Thus the pairwise width reduction becomes **0.5** rather than 0.5833. Complete three-cluster recurrence remains permitted by the literature and excluded by the standardized remeasurement.

## Direct literature-versus-candidate-free overlap

The number of independently resolved comparable anthocyanin cells rises from 5 to **6**.

- agreements = **2**;
- conflicts = **4**;
- agreement fraction = **1/3**.

Agreements:

- `CRETICULATA:A`;
- `CSIN_WHITE_PINK:F`.

Conflicts:

- `CJAPONICA:A`: literature up vs candidate-free down/near-flat signed estimate;
- `CJAPONICA:F`: **literature down vs candidate-free up** — newly exposed by Luo;
- `CRETICULATA:P`: literature down vs candidate-free up;
- `CSIN_WHITE_PINK:A`: literature up vs candidate-free down.

The new F conflict is especially relevant to the biological interpretation because Luo explicitly frames DFR–FLS competition as a recurring red/white mechanism, whereas pathway-wide remeasurement of the public Joy Kendrick system does not replay that literature-side F direction.

## Yellow and macro results

No yellow-development input changes. The candidate-free result remains:

- exact recurrence = **0.5**;
- pairwise concordance = **0.75**;
- A/C/P directions shared; F differs.

No taxonomy, topology, wild-colour, local-conservatism or event-identifiability input changes. The strict × dominant shared robust branch count remains **0**.

## Revised interpretation

Luo weakens one earlier observation-process headline but strengthens the central temporal-repeatability result.

The paper should no longer lead with the claim that anthocyanin-specific ascertainment remains significant after dependence collapse. Instead:

> **Published molecular observation is nonuniform, but the stronger biological result is that increasing literature coverage exposes additional disagreement with standardized measurement while leaving literature-compatible complete whole-package replay much broader than the candidate-free identified set.**

At the programme level this supports the revised Paper 1 question:

> **When similar flower-colour states are repeatedly generated through evolutionary time, how much of the underlying pigment-network transition is actually replayed?**

The answer remains: repeated visible generation does not imply replay of one invariant complete A/F/C/P programme; repeatability is modular and transition-class dependent.

## Freeze status

The calculation steps completed successfully in hosted run `33045036222`; its first validator failed only because the QC file contained an incorrect hand-predicted Monte Carlo P expectation. The official hosted value above is the value produced by the frozen code and seed. A corrected validator rerun is required before promotion to the next numbered science freeze.
