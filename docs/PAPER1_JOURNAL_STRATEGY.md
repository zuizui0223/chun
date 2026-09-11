# Paper 1 journal strategy

Checked: 2026-09-11 after science v0.2.2, framing v0.3.4, the 2026-08-28 three-journal gate, merged Petunieae prospective test PR #212, and merged second-prospective bounded screen PR #226.

## Final decision

**Primary submission: American Journal of Botany (AJB), v1.0 route.**

The 2026-08-28 escalation gate retained AJB after comparing *Evolution Letters*, *Evolution*, and AJB. The later cross-radiation programme materially strengthened the general-evolution case, so that decision was reopened prospectively rather than assumed permanent. The reopen test still retains AJB.

The active title and manuscript remain:

> **Hierarchical molecular repeatability coexists with local flower-colour conservatism in *Camellia*.**

The sentence adopted for the cover letter and editorial positioning is:

> **When similar visible flower colours are compared, what remains equivalent as molecular observation and historical identification become stricter?**

This is an organizing question, not an additional result or a claim that state identity, many-to-one mapping, or measurement dependence is novel. The original gate and scorecard are in `docs/PAPER1_JOURNAL_ESCALATION_GATE_V0_1.md`; the prior-art audit is in `docs/PAPER1_JOURNAL_ESCALATION_WEB_AND_PRIOR_ART_AUDIT_2026-08-28.md`.

## 2026-09-11 escalation refresh

The old statement that the programme contained only two non-matched molecular and macro audits is now stale. After the frozen AJB Paper 1 package, the repository established a genuine cross-radiation bridge programme under the definition `VISIBLE_PHENOTYPE_AXIS_TO_MOLECULAR_SUBSPACE_WITHIN_ONE_RADIATION`:

- Iochrominae — retrospective phenotype-dimension to molecular-subspace alignment;
- Cape Erica — independent retrospective alignment;
- Petunieae — first genuinely pre-specified prospective test.

The Petunieae gate was frozen before source acquisition and analysis. It returned **MIXED**, not PASS:

- 59 Petunieae taxa in the amount frame and 53 anthocyanin-positive taxa in the hue frame;
- hue/hydroxylation strongly selected `BRANCHING_HUE`, best-vs-next AICc margin **11.60282936**;
- the frozen raw amount response instead selected `BRANCHING_HUE` by only **0.44436806** AICc and did not beat the null;
- the source-method log-amount sensitivity selected `LATE_OUTPUT` with margin **2.80766099**, but this post-gate sensitivity is not allowed to upgrade the prospective classification.

Therefore the strongest programme-level result has become more general than the Camellia paper:

> **The molecular subspace associated with floral colour variation depends on the phenotype dimension being resolved. Hue/hydroxylation repeatedly concentrates on pathway-branching machinery across independent radiations, including a strong prospective Petunieae component, whereas pigment amount/depletion is less stable and can be response-definition sensitive.**

That is a real advance, but it is narrower than the attempted full two-axis rule. `docs/EVOLUTION_ESCALATION_POST_PETUNIEAE_V0_1.md` therefore classified journal escalation as `EVOLUTION_ESCALATION_HOLD_AFTER_FIRST_PROSPECTIVE_MIXED_TEST`.

A second prospective full-bridge candidate was then sought under a bounded, unchanged admission rule. Ruellia, Rhododendron, Gesnerioideae, Antirrhineae, Mimulus, and Aquilegia all failed/HOLD because the same >=30-taxon frame did not simultaneously contain the two phenotype axes, >=3 matched molecular subspaces, and a usable phylogeny. No threshold was weakened after observing Petunieae. The merged result is:

`NO_SECOND_PROSPECTIVE_FULL_BRIDGE_CANDIDATE_ADMITTED_UNDER_FROZEN_SCREEN`

See `docs/EVOLUTION_SECOND_PROSPECTIVE_CANDIDATE_SCREEN_V0_1.md` and `data/evolution_second_prospective_candidate_screen_v0_1.csv`.

**Consequence:** the search for an immediate *Evolution* upgrade is closed. Reopen only if a newly released dataset already plausibly satisfies the frozen admission fields before decisive values are inspected. Do not delay the Camellia submission while fishing for a favourable second radiation.

## Manuscript identity

Paper 1 is an integrative plant-evolution study with two separate but complementary inferential audits:

1. the same admitted public molecular systems are represented under incomplete literature observation and annotation-driven, outcome-independent A/F/C/P remeasurement; and
2. accepted-species wild-colour data are tested first for topology/coding-robust local structure and then for the stricter identity of individual historical branches.

The strongest defensible synthesis is:

> molecular repeatability is modular and transition-class dependent; realised visible colours remain locally phylogenetically structured; individual transition-event identity is not robustly identifiable.

The RNA-seq comparisons quantify developmental or petal-sector colour-state-generating transcript changes. They are not treated as direct observations of independent macroevolutionary origins, and they are not aligned event-for-event with reconstructed branches.

## Why AJB is the best current fit

AJB's scope spans ecology, evolution, biodiversity, systematics, genetics, and development from ecosystem to molecular scales. Paper 1 genuinely connects those levels in a botanical system while retaining their evidential boundaries. The paper's narrow empirical novelty—the same-system multivariate recurrence audit plus a separate pattern/event robustness gate—is legible to its plant-evolution readership without claiming a universal evolutionary law.

Submission must lead with the general flower-colour question and then state the exact hierarchy:

1. standardized observation narrows anthocyanin-gain recurrence but does not erase all molecular reuse;
2. yellow development retains stronger A/C/P modular recurrence while F differs;
3. local same-colour structure is robust across topology and trait coding;
4. no accepted-species branch is shared as robust between strict and dominant coding;
5. generation, realised pattern, and event identity are distinct quantities.

The main editorial risk is that the study is data-integrative and partly re-analytical. The response is the frozen falsification sequence and exact bounds, not generic novelty language or a catalogue of public datasets.

## Why *Evolution Letters* and *Evolution* are not first targets

The 2026-09-11 refresh uses stronger evidence than the original 8/28 comparison, but the general-journal threshold is still not met for **Paper 1 as currently constituted**.

The current official *Evolution* guidance welcomes significant original empirical studies that broaden understanding of evolutionary processes, but explicitly warns that demonstrating a well-established phenomenon in another taxon or context may fall short for an Original Article. *Evolution Letters* sets a still higher bar: papers should be cutting-edge, broadly important, and substantially advance the field.

The new cross-radiation evidence improves the case because hue-to-branching localization is no longer Camellia-specific and includes a genuine prospective Petunieae component. It does **not** yet provide a clean replicated general rule because:

- prospective full two-axis bridge PASS count remains **0**;
- Petunieae's strongest prospective result is the hue component, while the amount component fails the frozen primary gate;
- the amount/depletion result is response-definition sensitive;
- Iochrominae and Cape Erica remain retrospective rather than prospective replications;
- no second independent prospective full-bridge radiation can currently be admitted without lowering the frozen coverage/matching rule;
- the current Camellia manuscript itself remains a separate bounded empirical synthesis rather than a manuscript architected around the later cross-radiation programme.

Thus retargeting the AJB manuscript merely by strengthening the title or cover letter would overstate the evidence. A future *Evolution* manuscript would need a deliberate new architecture built around replicated phenotype-dimension-to-molecular-subspace predictability, not a renamed AJB bundle.

The present AJB manuscript should therefore proceed. The cross-radiation programme remains scientifically valuable and can mature as a separate paper if new prospective evidence appears.

## Fallback order

If AJB declines the manuscript without a correctable package issue:

1. **Annals of Botany** — broad plant-science fit for the molecular, phylogenetic, and inferential architecture.
2. **Evolutionary Journal of the Linnean Society** — use only with a deliberate rewrite toward accessibility, trait-state aliasing, and macroevolutionary identifiability.

The fallbacks do not authorize expanded claims or new post-hoc analyses.

## Submission consequences

- Retain the v0.3.4 title, 242-word structured abstract, Figure 1 contract, Methods, Results, and Discussion.
- Do **not** import the later external-radiation programme into the frozen Paper 1 Results as if it were part of the original study.
- Use the state-identity question only in the cover letter or opening editorial pitch.
- Keep candidate-free defined as annotation-driven, outcome-independent quantification within four prespecified modules; it is not genome-wide hypothesis-free discovery.
- Keep exact incomplete-state bounds and dependence-cluster results visible.
- Do not infer taxon-level A/F/C/P states from visible hue.
- Do not claim a definitive white ancestor or branch-specific ecological causes.
- Do not delay Paper 1 while searching for another prospective radiation.
- Resume Issue #85 for author metadata, declarations, approvals, and the archive DOI.

## Official scope sources checked

Rechecked 2026-09-11:

- [American Journal of Botany — journal information and author resources](https://bsapubs.onlinelibrary.wiley.com/hub/journal/15372197/homepage/productinformation)
- [Evolution Letters — author guidelines](https://academic.oup.com/evlett/pages/author-guidelines)
- [Evolution — author guidelines](https://academic.oup.com/evolut/pages/author-guidelines)
