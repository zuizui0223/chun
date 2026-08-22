# Paper 1 analysis disposition

## Purpose

Paper 1 now has a frozen authoritative result registry. This document controls a separate question: **where do the analyses that produced, challenged, or were superseded by those results belong in the manuscript pipeline?**

The machine-readable map is `data/paper1_analysis_disposition_v0_1.csv`.

## Four placements

### Main

Use when the analysis directly supports a current Paper 1 claim or method that appears in the main text/figures.

Current Main analyses include:

- FLS and DFR sequence-aware implementation evidence;
- the current climate and pollination screening results, with their narrow claim boundaries;
- WFO 2026-06 taxonomy normalization;
- wild/floristic colour auditing;
- accepted-species topology concordance;
- the UFBoot accepted-species local colour-conservatism result;
- the accepted-species zero-shared-event identifiability boundary;
- the cross-scale accessibility/persistence synthesis and explicit public-data stop rule.

### Supplement

Use when the analysis is scientifically useful sensitivity/context but should not carry the headline claim alone.

Examples:

- ANS/LDOX and ANR copy-specific heterogeneity;
- FastTree accepted-species topology and colour-conservatism sensitivities;
- accepted-species root-state sensitivity (W favoured but W/Y uncertainty retained);
- the PR #45 wild-colour/taxonomy stress test explaining why legacy W→A branches were reset;
- intermediate Fan aggregation after taxonomy collapse;
- current machine-readable orthology ledger.

### Provenance only

Retain for reproducibility, but do not cite as an independent manuscript result.

Examples:

- consumed runtime91 UFBoot computation intermediates (PR #31/#47) after their gene trees were used in PR #56;
- exploratory ANS/LDOX sequence-recovery output superseded by the conservative resolver;
- historical orthology ledger versions;
- manuscript-governance registry itself.

### Exclude

Do not use in the Main text, Main figures, or as a positive Supplementary conclusion.

Explicit exclusions are:

- legacy three W→A branches from the 93-tip tree (PR #44);
- legacy definitive/novel white-ancestor framing (PR #43);
- legacy A-specific lineage-permissivity headline (PR #35/#40);
- legacy global same-colour MPD headline as if topology-independent (PR #40).

These remain in Git history solely to document falsification and analytical development.

## Why this matters

The strongest early narrative was progressively weakened by better taxonomy, wild-colour evidence and nuclear-topology sensitivity. Paper 1 is stronger if that history is treated as a falsification path rather than quietly selecting the most dramatic legacy result.

The final manuscript should distinguish:

1. **current positive result** — local nearest-same-colour conservatism;
2. **current negative robustness result** — global same-colour MPD does not survive UFBoot topology;
3. **current identifiability result** — no accepted-species branch event is robust to strict × dominant wild-colour assumptions;
4. **superseded historical results** — useful only to explain why the analysis was reset.

## CI contract

`validate_paper1_analysis_disposition.py` enforces that:

- superseded analyses cannot be placed in Main or Supplement;
- consumed intermediates are provenance-only;
- every superseded result ID in `paper1_authoritative_results_v0_1.csv` has at least one explicit `exclude` disposition;
- no Main disposition references a superseded/excluded result ID.

## Manuscript consequence

Once this map is frozen, manuscript drafting should pull sources from Main/Supplement placements only. `provenance_only` and `exclude` analyses remain outside the prose pipeline unless specifically cited to explain a sensitivity reset or computational provenance.
