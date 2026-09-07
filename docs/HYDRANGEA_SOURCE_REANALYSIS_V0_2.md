# Hydrangea Cornidia: independent source-to-history reanalysis v0.2

## Result and current status

**Executed, not a registry-only gate.** All 97 Figure-5 terminal observations were recovered and joined to original specimen records and both nuclear alignments. Cornidia contributes 88 accession observations (57 WHITE,31 RED), not 88 independent species. The 9 external tips are 5 WHITE and4 PURPLE. The ingroup contains35 source taxon-name units, including unnamed/affinity identifications; accepted taxonomy remains unresolved.

Across two alignment treatments, the fitted red-to-white / white-to-red rate ratio is approximately2.1–2.2. Its direction persists in taxon-balanced and sequence-bootstrap sensitivity checks, but95% conditional profile intervals include1 and root colour depends on model/root priors. The defensible result is recurrent colour turnover with a repeatable estimated return-to-white tendency, **not a demonstrated universal rate asymmetry or an independently confirmed white ancestor**.

Current status: `EXECUTED_CONDITIONAL_TWO_LOCUS_INGROUP_MK`. Pooled cross-clade model: `NOT_RUN`. The two alignments are one biological radiation, not two.

## Original observations and source audit

Source: Granados Mendoza et al.(2021), *Molecular Phylogeny, Character Evolution, and Biogeography of Hydrangea Section Cornidia, Hydrangeaceae*, DOI `10.3389/fpls.2021.661522`, PMCID`PMC8276264`, CC BY. S1 supplies specimens; S2 supplies two nuclear FASTAs; S3 supplies gene-tree PDFs. No machine-readable combined branch-length tree was supplied, so new ML trees were inferred rather than extracting branch lengths from a cladogram.

Figure5 accession labels were visually transcribed without OCR. Colour was measured from the checksum-pinned terminal circles, not internal ancestral pies. All97 classifications survived nine perturbed sampling windows. The initial rim-crossing failure was resolved by centering the measurement inside the circle, without changing any terminal state or relaxing colour thresholds. All97 accessions match S1 and both FASTAs exactly.

Methods says89 ingroup+8 outgroup, whereas the archived sources resolve to88+9. The file labelled `original` has3161 columns; `phylogenetic inference` has3167. Deleting columns2924–2929 (one-based inclusive) from the longer alignment exactly reproduces the shorter for all97 specimens. Both were analysed. `Hydrangea sp.1` and `H.sprucei` have both WHITE and RED sampled accessions; no majority coding or natural-monomorphism inference was imposed.

## Independent analysis and principal estimates

IQ-TREE2.0.7: GTR+G4, seed20260907, HY098 outgroup,1000 ultrafast bootstrap replicates with BNNI per alignment. This is an independent unpartitioned two-locus reconstruction, not an exact reproduction of the paper's partitioned RAxML analysis. Branches are nuclear substitutions/site, not years.

Cornidia was monophyletic in both ML trees and all2000 bootstrap realizations. External tips were pruned. Binary white/red Mk models were fitted by multi-start ML with ER/ARD rates and equal/stationary root priors. For two states SYM equals ER. White ancestry was never imposed. Expected transitions and state occupancies integrate histories conditional on fitted Q and tree, not parameter uncertainty.

| Alignment | ARD/ER AIC, equal root prior | Return/gain rate ratio | Conditional profile95% interval | RootP(WHITE), ARD/equal |
|---|---|---|---|---|
|3161 columns|90.168/91.782|2.210|0.976–7.283|0.466|
|3167 columns|91.860/93.153|2.103|0.941–6.484|0.479|

Conditional asymptotic LR p-values are0.0573 and0.0696. Stationary priors give ratios2.148 and2.059 and rootP(WHITE)~0.657. Thus directionality is suggestive, not decisive, and the white root is uncertain. These intervals are conditional frequentist diagnostics, not posterior or across-tree credible intervals.

ARD/equal-root expected counts are W→R12.563 versus R→W16.795(short), and13.490 versus16.686(long). Count ratios differ from rate ratios because state occupancy differs. Neither is an exact observed historical event count.

## Sensitivity and rate identifiability

Twenty seed-frozen draws per alignment select one accession per source taxon. The current usable count is **38 ARD fits**, all with return/gain ratio>1:20 short-alignment fits (range1.998–3.487,median2.506) and18 long-alignment fits (1.958–3.426,median2.423).

Long-alignment draws0 and11 reach a high-rate likelihood plateau. Multiplying both fitted rates by1000 changes logL by<1e-6; their absolute rate scales are not identified. Draw11 sometimes lands at the numerical optimization bound and sometimes just below it across numerical environments, despite identical chosen specimens and logL agreement to1.5e-8. Therefore a reproducibility test based solely on box-contact count was scientifically inadequate. The likelihood-plateau diagnostic replaces it; both datasets diagnose exactly the same two draws. No likelihoods, principal estimates or confidence bounds were changed to make a test pass.

`rate_scale_diagnostic.json` supersedes the original39-interior-fit robustness count in archival `frozen_results.json`. All8 full-ingroup primary models are outside the high-rate plateau. Boundary-only flags remain saved for transparency.

All1000 bootstrap topologies per alignment were also checked: minimum changes needed for the sampled observations range9–14(median11) and10–14(median11). These are parsimony lower bounds on accession trees, not exact numbers of independent species-level origins. Twenty seed-frozen bootstrap trees per alignment additionally received ER/ARD fitting; all40 numerical-interior ARD fits had ratios>1, with broad ranges1.679–11.626 and1.642–10.529. Some trees prefer ER by AIC. These are sensitivity ranges, not confidence intervals or independent biological replicates.

## Correction to the earlier published-count interpretation

The earlier22.691/6.712=3.38 remains faithful arithmetic from the published all-tree map summary, but **is not a Cornidia-only rate ratio**. All four observed purple tips are external. Without branch-resolved source maps, purple→white counts cannot be allocated to internal Cornidia histories. This does not exclude unobserved ancestral purple states; it prohibits assigning an aggregate to a narrower group without evidence.

Likewise, the earlier marginal-HPD rectangle is not a joint95% interval. v0.2 supersedes a strong internal-rate or fixed-white-root claim based on that audit. Legacy published numbers remain source QC, not inputs to the new likelihood.

## Reproduction and evidence locations

Full source/reconstruction/model run`34111490311` succeeded; head`bf789abfd892dae248ad7e8df84b9ca5abf6d7f2`; artifact`10014665888`; ZIP SHA256`2c24dc1e412e182031f6e452e2b71e20e131622e6b61a6cb854afafe70e21575`. It includes original sources,97-row provenance CSV, alignments, ML/bootstrap trees,88 primary/taxon-balanced fits, scripts and versions. Profile/bootstrap audits were executed locally on that checksum-verified artifact. The subsequent hosted replay reproduced principal estimates and profiles before correctly exposing the plateau/box-contact issue; the diagnosis was independently checked on both local and hosted outputs.

Committed `frozen_inputs.json` preserves all97 observations, source-name strings, source hashes and both full-precision ML trees. Indexed source names are a lossless representation. `frozen_results.json` records original computed results; `rate_scale_diagnostic.json` contains the current usable-fit classification.

```
python -m unittest discover -s tests -p 'test_hydrangea_mk_v0_2.py' -v
python scripts/verify_hydrangea_snapshot_v0_2.py \
  --inputs data/hydrangea_source_reanalysis_v0_2/frozen_inputs.json \
  --expected data/hydrangea_source_reanalysis_v0_2/frozen_results.json \
  --out build/hydrangea_replay_v0_2
```

Automatic CI refits88 models,4 likelihood profiles and the rate-scale diagnosis offline after dependency installation. Missing required data fails. Full sequence-bootstrap replay separately requires original `trees/*.ufboot` and `audit_hydrangea_inference_v0_2.py`; it is not counted as rerun by the offline primary job. The explicit manual source job can reacquire inputs and rebuild trees. Tests compare pruning with exhaustive enumeration, transition matrices with matrix exponentiation, and jump/occupancy integrals with likelihood-score derivatives, plus adversarial missing-tip/state/branch tests.

## Cross-clade implication and remaining gate

Carry organ-specific ancestral-state uncertainty into the comparative atlas instead of treating a published white-root classification as fixed. Another independent radiation must pass the same source-to-history protocol before claiming a common law. These two-locus results do not establish ecological causes or molecular regain mechanisms.

Camellia Paper1sciencev0.2.2,framingv0.3.4 andAJBv1.0 remain untouched.
