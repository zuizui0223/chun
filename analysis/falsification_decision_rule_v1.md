# Falsification decision rule v1

This audit separates two claims that must not be conflated.

## A. Already rejected stronger claim

The universal/coarse-state version is already rejected at the tested cross-radiation level: no shared transition direction passes across the comparable Mk systems, and no preselected biological coarse partition is ENRICHED across the three fine-state radiations.

## B. Surviving claim under prospective falsification

The current positive claim is narrower: **fine-state phylogenetic organization recurs after conditioning on a biologically predeclared coarse state**.

A new candidate counts as a genuine counterexample to that surviving claim only when all of the following hold:

1. **Independent radiation** — the test unit is phylogenetically independent from Linoideae, Angraecinae, and Antirrhineae.
2. **Matched phenotype level** — both fine visible/organ flower-colour states and an a priori biological coarse grouping are available; a molecular endpoint alone is not a matched test.
3. **Matched observation regime** — tip-state coverage is adequate and state missingness/ambiguity is handled by a rule frozen before computation.
4. **Matched statistic** — use a phylogenetic fine-state organization statistic and a conditional null that permutes fine states within coarse groups. The primary implementation is the Sankoff minimum-change score with 9,999 conditional permutations.
5. **Identifiable randomization support** — the frozen topology/statistic/null combination must permit the statistic to vary over admissible rearrangements. A complete star tree, a degenerate conditional null (`null_min == null_max`) produced by topology/statistic invariance, or another zero-power randomization regime cannot support either SUPPORT or REFUTATION. Such a case is `HOLD_IDENTIFIABILITY`, while any prospectively frozen mechanical classifier output is retained separately as an audit artifact.
6. **Failure of the surviving prediction** — the observed fine-state score is not lower than expected under the identifiable conditional null (`p_lower > 0.01` or `observed / mean(null) >= 1`) under the frozen primary analysis.
7. **Robust failure** — predeclared sensitivity analyses do not recover a stable supportive signal. If primary and sensitivity results disagree materially, classify MIXED rather than REFUTATION.

Classification:
- `REFUTATION`: criteria 1–7 satisfied; this is a matched prospective failure of the surviving fine-state recurrence claim.
- `ADVERSE_BUT_NOT_REFUTATION`: primary evidence is adverse but matched coverage/sensitivity/admission criteria are incomplete.
- `HOLD`: data or observation regime cannot adjudicate the matched claim.
- `HOLD_IDENTIFIABILITY`: source/taxon admission may pass and a frozen classifier may even return an adverse label, but the topology/statistic/null combination has zero discriminating power over admissible rearrangements.
- `SUPPORTIVE_ALIGNMENT`: the matched test supports residual fine-state organization.
- `MIXED`: primary and frozen sensitivity analyses disagree materially.

The identifiability gate was added after the Epimedium prospective endpoint exposed a complete 36-tip OpenTree star: all 9,999 conditional permutations and multiple deterministic within-coarse rearrangements returned exactly the same Sankoff score. The original Epimedium prefreeze and its formal `REFUTATION` classifier output remain immutable; only its promotion to biological counterexample is blocked by the independent validity audit.

A directionally opposite transition rate is not required to refute the surviving claim, because that claim no longer asserts a universal transition direction. Mechanistic non-replication likewise does **not** by itself refute a macro phenotype-level representation pattern.
