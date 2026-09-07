# Hydrangea Cornidia: independent source-to-history reanalysis v0.2

## Result and status

**Executed, not a registry-only gate.** The 97 Figure-5 terminal observations were recovered, joined to the original specimen table and both archived nuclear alignments, and reanalysed on independently inferred maximum-likelihood trees. Cornidia contributes 88 accession observations (57 white, 31 red), not 88 independent species. The remaining 9 tips are outgroups (5 white, 4 purple). The ingroup contains 35 source taxon-name units, including unnamed/affinity identifications.

Across the two alignment treatments, the fitted red-to-white / white-to-red rate ratio is about 2.1–2.2. Its direction persists in taxon-balanced and sequence-bootstrap sensitivity checks, but 95% conditional profile intervals include 1 and the white ancestral state is not robust to root/model assumptions. This is evidence of recurrent colour turnover and a repeatable estimated return-to-white tendency, **not a demonstrated universal rate asymmetry or an independently confirmed white ancestor**.

The pooled cross-clade model is still NOT RUN. Two alternative alignments of one clade are not two independent radiations.

## Source recovery and corrections

Source: Granados Mendoza et al. (2021), *Molecular Phylogeny, Character Evolution, and Biogeography of Hydrangea Section Cornidia, Hydrangeaceae*, DOI `10.3389/fpls.2021.661522`, PMCID `PMC8276264`, CC BY.

The original supplementary archive supplies S1 specimen records, two S2 FASTA alignments and S3 gene-tree PDFs. It does not supply a machine-readable combined branch-length tree, so a new nuclear ML inference was run instead of inventing branch lengths from a figure.

Figure 5 terminal labels were visually transcribed without OCR. Terminal-circle colour was measured from the checksum-pinned embedded JPEG, not ancestral-node pies. A 5x5 interior median and nine perturbed 3x3 windows gave identical classifications for all 97 tips. The first test correctly stopped when a window crossed the black circle rim; moving it to the true interior fixed the geometry without changing any terminal state or relaxing the colour rules. Every accession joins one-to-one to S1 and both FASTAs.

Two source discrepancies remain explicit:

* Methods says 89 ingroup + 8 outgroup; S1, FASTA and Figure 5 instead reconcile to 88 + 9.
* The file labelled `original` contains 3,161 columns, while `phylogenetic inference` contains 3,167. Removing columns 2,924–2,929 (one-based, inclusive) from the longer file reproduces the shorter alignment exactly for every accession. Both treatments were retained rather than choosing a label by assumption.

`Hydrangea sp. 1` and `H. sprucei` have red and white sampled accessions. No majority coding or assumption of population monomorphism was imposed. Source names are not represented as a completed modern accepted-taxonomy audit.

## Actual analysis

IQ-TREE 2.0.7 was run separately for both alignments with GTR+G4, seed 20260907, outgroup HY098 and 1,000 ultrafast bootstrap replicates with BNNI. This is an independent unpartitioned two-locus reconstruction, not an exact reproduction of the paper's partitioned RAxML analysis. Branch lengths are nuclear substitutions per site, not elapsed years.

The ingroup was monophyletic in both ML trees and all 2,000 bootstrap realizations. After pruning all external tips, binary white/red Mk likelihoods were fitted by multi-start maximum likelihood. For a binary trait, SYM and ER are the same model, so ER and ARD were fitted under equal and stationary root priors. White ancestry was not imposed. Counts and state occupancies were integrated analytically over histories conditional on fitted Q and the tree; Q uncertainty is not integrated in those expected counts.

| Alignment | ARD/ER AIC, equal root prior | Return/gain rate ratio | Conditional profile 95% interval | Root P(white), ARD equal prior |
|---|---|---|---|---|
| 3,161 columns | 90.168 / 91.782 | 2.210 | 0.976–7.283 | 0.466 |
| 3,167 columns | 91.860 / 93.153 | 2.103 | 0.941–6.484 | 0.479 |

The corresponding asymptotic likelihood-ratio p-values are 0.0573 and 0.0696. These are conditional frequentist diagnostics, not posterior probabilities or independent cross-clade tests. Stationary root priors give rate ratios 2.148 and 2.059, while P(white) rises to about 0.657. Root inference is therefore uncertain rather than fixed as white.

Conditional expected counts under ARD/equal root are white-to-red 12.563 vs red-to-white 16.795 (short alignment), and 13.490 vs 16.686 (long alignment). Their ratios differ from rate ratios because state occupancies differ. Counts must not be substituted for rates.

## Sensitivity results

One accession per source taxon was selected in 20 seed-frozen draws for each alignment, preserving observed mixed-state sampling. All 39 interior ARD fits retained a return/gain ratio above 1: 1.998–3.487 in the short alignment and 1.958–3.426 in the long alignment. Long-alignment draw 0 hit the rate ceiling and is held out of the interior summary, not hidden. Model-selection strength remains variable.

All 1,000 bootstrap topologies per alignment were checked. Minimum changes needed to explain the sampled terminal observations were 9–14 (median 11) and 10–14 (median 11). These are parsimony lower bounds on these accession trees, not exact numbers of independent species-level colour origins.

Twenty seed-frozen bootstrap realizations per alignment were also fitted with ER/ARD. All 40 interior ARD fits estimated a return/gain ratio above 1 (ranges 1.679–11.626 and 1.642–10.529). Some realizations prefer ER by AIC, and these ranges are sensitivity ranges, not confidence intervals. Resampling the same clade is not independent biological replication.

## Supersession of the earlier published-count interpretation

The old `22.691 / 6.712 = 3.38` arithmetic is a faithful calculation from the published all-tree map summary, but **must not be promoted to an ingroup-only rate ratio**. All four observed purple terminals are external to Cornidia. Without branch-resolved source maps, the old purple-to-white counts cannot be allocated to within-Cornidia evolution. This does not imply that all unobserved ancestral purple histories must lie outside the ingroup; it means the aggregate is not an ingroup-specific estimator.

The earlier marginal-HPD rectangle audit also remains arithmetic sensitivity, not a joint 95% interval. v0.2 supersedes a strong internal-rate or fixed-white-root claim based on that audit. Legacy source numbers remain preserved for provenance; they are not likelihood inputs here.

## Reproduction and evidence locations

Original full execution: run `34111490311`, head `bf789abfd892dae248ad7e8df84b9ca5abf6d7f2`, artifact `10014665888`, ZIP SHA256 `2c24dc1e412e182031f6e452e2b71e20e131622e6b61a6cb854afafe70e21575`. It includes original sources, 97-row provenance CSV, both alignments, ML and bootstrap trees, all 88 primary/taxon-balanced model fits, exact scripts and package versions. Additional profile/bootstrap audits were executed locally on this downloaded and checksum-verified artifact.

The committed `data/hydrangea_source_reanalysis_v0_2/frozen_inputs.json` retains all 97 observations, unmodified source name strings, source hashes and both full-precision ML trees. `frozen_results.json` records computed primary and sensitivity summaries. Its indexed taxon names are a lossless table representation, not recoding. The canonical input checksum is validated before every offline replay.

```
python -m unittest discover -s tests -p 'test_hydrangea_mk_v0_2.py' -v
python scripts/verify_hydrangea_snapshot_v0_2.py \
  --inputs data/hydrangea_source_reanalysis_v0_2/frozen_inputs.json \
  --expected data/hydrangea_source_reanalysis_v0_2/frozen_results.json \
  --out build/hydrangea_replay_v0_2
```

The replay refits 88 models and four likelihood profiles without source-network access after dependency installation. Full sequence-bootstrap replay uses the original artifact's `trees/*.ufboot` with `audit_hydrangea_inference_v0_2.py`; it is explicitly separate from the offline primary replay. A manual source job can reacquire the sources and rerun IQ-TREE plus the full audit. Missing required input fails rather than passing via skipped science.

Tests check transition matrices against matrix exponentiation, pruning against exhaustive enumeration, jump/occupancy integrals against likelihood score identities, label symmetry and adversarial missing-state/tip/branch inputs.

## Next scientific gate

Carry estimated ancestral-state uncertainty into the comparative atlas instead of selecting on a deterministic published white root. Repeat this same source-to-history protocol in another independent radiation; do not count either alignment or the bootstrap realizations as additional clades. Ecological causes and molecular regain mechanisms are not established by this two-locus macro analysis.

Camellia Paper 1 science v0.2.2, framing v0.3.4 and AJB v1.0 are unchanged.
