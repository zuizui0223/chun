# Resolution-profile training inventory — v0.2

## Current decision

**Do not fit a radiation-level quantitative moderator yet.**

Completed exact same-estimand radiation-level outcomes remain **1**. The frozen minimum before quantitative moderator fitting remains **5**.

The current bottleneck is now source execution, not model design.

## Exact estimand

A completed radiation must use one common retained-tip frame and three genuinely nested state resolutions on one phenotype axis, with negative patristic distance predicting same-state pairs, ROC AUC at all three resolutions, and 9,999 joint permutations of the complete state triplet.

A schema or source hold is not an outcome and cannot be encoded as zero signal.

## Completed outcome

### Iris — completed, prospective, training eligible

169 eligible tips. Frozen fourth-radiation prediction ended in **FAIL**:

- coarse AUC = 0.4617285166;
- intermediate AUC = 0.4543945669;
- fine AUC = 0.4870504419.

The universal intermediate-winner hypothesis is therefore prospectively rejected. Iris remains a valid training observation because the exact estimand was executed as frozen.

## Pre-outcome holds

### Gesnerioideae — schema HOLD

`HOLD_SCHEMA_SOURCE_AXES_NOT_NESTED`

Exact tree bytes were subsequently recovered and matched the frozen Dryad manifest, clearing the source-access issue, but this does not reopen the analysis. Pigment chemistry and visible/reflectance colour are cross-cutting dimensions rather than one nested hierarchy. No target AUC was computed.

### Flower-clades-51 standardized batch — source-access HOLD

`HOLD_SOURCE_ACCESS_OUTCOMES_UNOPENED`

This is the highest-leverage next execution path because the representation and statistic are already frozen before CHUN species-level colour outcome opening and the source reports 51 clades.

Dryad metadata is frozen at DOI `10.5061/dryad.r4xgxd2sc`, version id `402189`:

- `final_dataset.csv`: file id `4411881`, 118867 bytes, SHA-256 `a253308785e4cbd0e361b3ca04cdfdae29c523eefa843375cebf8030ee0874af`;
- `trees.zip`: file id `4411880`, 80326 bytes, SHA-256 `ae5c82945e5bf9c29bcabc52d6029acd8d4f5be1fe9141fad95918eacb4f674d`.

Automated public download returns an Anubis validation interstitial instead of source bytes. No species-level `flower_color`, colour frequency, state profile, AUC or winner has been opened/computed. Once exact bytes are supplied, the first allowed operation is identifier/tree-only crosswalk freeze, not outcome analysis.

### Ruellia 51-species HPLC profile — tree-source HOLD

`HOLD_TREE_SOURCE_OUTCOMES_UNOPENED`

A new same-axis biochemical hierarchy was preregistered before CHUN row-level HPLC ingestion:

- coarse: any anthocyanidin present vs none;
- intermediate: PEL/CYA/DEL three-branch presence pattern;
- fine: six-compound anthocyanidin presence pattern.

The primary HPLC source is frozen as Figshare v2 `raw_data.csv`, file id `58502635`, 130680 bytes, MD5 `0e3b9830abb1378f9546cd7d07ae1f97`. Header-only verification read zero data rows and confirmed identifiers plus the six required compound columns.

The author code requires `03-Ruellia_phylo.timed.tre`. It is absent from both Figshare v1 and v2 and absent from the checked author GitHub tree. A related New World Ruellia ddRAD phylogeny exists in the literature, but identity to the exact timed tree has not been established, so no substitution is allowed. No HPLC state pattern, AUC or winner has been computed.

## Other evidence not counted as exact-profile outcomes

Linoideae, Angraecinae and Antirrhineae retain their separate conditional-hierarchy result. They are scientifically relevant but are not exchangeable with the unconditional three-resolution AUC profile unless the exact profile estimand is separately executed under an auditable frozen rule.

Rhododendron remains a candidate only: the 30-species study supplies seven quantified anthocyanins and flower colour, but a same-30-species public branch-length tree plus auditable row-level source package has not yet been established. It is not admitted merely to increase n.

## Priority order

1. **Unlock Flower-clades-51 exact source bytes.** This can potentially convert many clades into standardized same-estimand training observations under one already-frozen batch rule.
2. **If exact Ruellia timed tree becomes available, freeze its identifier-only crosswalk and execute the preregistered biochemical profile.**
3. Continue bounded candidate admission only for sources that already have one nested phenotype axis, row-level public data and a public branch-length tree before outcomes are opened.
4. Fit no moderator until at least five completed radiation-level outcomes exist.

## Failure modes remain distinct

- Iris: valid terminal prospective **FAIL**.
- Gesnerioideae: pre-outcome **schema HOLD**.
- Flower-clades-51: pre-outcome **source-access HOLD**.
- Ruellia51: pre-outcome **tree-source HOLD**.

Collapsing these into one binary success/failure variable is forbidden.

Camellia Paper 1 remains unchanged and closed.
