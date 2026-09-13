# CHUN intermediate-resolution rule — prospective fourth-radiation preregistration v0.1

## Status

**FROZEN BEFORE CHUN IRIS ROW-LEVEL OUTCOME INGESTION.**

This is a post-Paper-1 analysis. It does not alter Camellia Paper 1 science, figures, framing, or submission routing.

## Rule

CHUN's current cross-radiation results suggest a more specific hypothesis than either “fine states always win” or “coarse biological states constrain evolution”:

> **Flower-colour predictability should peak at an intermediate biologically grounded resolution: finer than binary pigment presence/absence, but coarser than exact human-visible hue.**

The proposed mechanism-free interpretation is that very coarse coding aliases distinct biological routes, whereas exact visible hue contains additional variation that need not track the same evolutionary state. A pigment-class representation may therefore retain more reproducible evolutionary structure without pretending that one complete molecular programme is shared.

## Held-out fourth radiation

**Iris** is fixed as the fourth radiation for this test.

It was not used to derive either:
- the 3-radiation macro state-granularity result (Linoideae, Angraecinae, Antirrhineae), or
- the matched phenotype-axis molecular result (Iochrominae, Cape Erica, Petunieae).

The source study (`10.3389/fpls.2020.569811`) supplies a large genus-scale phylogenetic frame, seven visible hue categories, biologically grounded pigment categories, and a public accession list. The source paper's aggregate results are known; therefore this is **analysis-prospective, not literature-blinded**. The CHUN row-level trait ingestion, reconstructed tree, and frozen AUC contrasts have not been computed before this freeze.

## Frozen resolutions

The same eligible tip set is used at all three resolutions.

1. **Coarse — pigment presence**
   - chromatic pigment present
   - no chromatic pigment
2. **Intermediate — major pigment class**
   - anthocyanin
   - carotenoid
   - no chromatic pigment
3. **Fine — visible hue**
   - maroon, orange, pink, purple, red, yellow, white

Primary analysis admits only taxa with one unambiguous hue and one unambiguous major-pigment state. Fine hue states represented by fewer than five eligible tips are removed, then the identical remaining tip frame is used for all three resolutions. No missing-state imputation is allowed.

## Outcome-independent tree

The tree is rebuilt from the source accession list without using any flower-colour trait values:

- six source loci: matK, trnL, trnK, NADPH, rbcL, ITS;
- MAFFT `--localpair --maxiterate 1000` by locus;
- trimAl `-automated1` by locus;
- partitioned concatenation in IQ-TREE2 with ModelFinder and 1000 ultrafast bootstraps;
- source outgroups retained for rooting and then removed;
- source-specified *Iris darwasica* exclusion retained.

## Primary statistic

For each resolution, all unordered tip pairs are labelled `same state` versus `different state`. Negative patristic distance is used to predict same-state membership. The area under the ROC curve is the frozen phylogenetic-predictability score.

To compare resolutions fairly, the complete `(coarse, intermediate, fine)` state triplet is permuted jointly across tips 9,999 times (`seed=20260913`). This preserves each resolution's state frequencies and the cross-resolution relationships while destroying phylogenetic association.

Primary outputs:
- `AUC_coarse`
- `AUC_intermediate`
- `AUC_fine`
- `Δ(intermediate-coarse)`
- `Δ(intermediate-fine)`
- one-sided empirical permutation P values for intermediate signal and both superiority contrasts.

## Frozen decision

**PASS** only if all three are satisfied:
1. intermediate AUC > 0.5, empirical `P <= 0.05`;
2. intermediate > coarse, empirical `P <= 0.05`;
3. intermediate > fine, empirical `P <= 0.05`.

**MIXED** if intermediate has significant signal and both observed differences are positive but one/both superiority tests miss 0.05, or if one contrast supports superiority while the other does not significantly contradict it.

**FAIL** if intermediate lacks phylogenetic signal or coarse/fine is significantly more predictive under the frozen test.

Planned sensitivities cannot upgrade MIXED/FAIL to PASS.

## If PASS

A PASS would move CHUN beyond retrospective synthesis by adding an independently held-out fourth radiation supporting the pre-frozen ordering:

`coarse < intermediate > fine`

It would justify a stronger cross-radiation statement about **resolution-dependent evolutionary predictability**, while still not authorizing a universal causal law or a claim that all radiations share the same intermediate partition.
