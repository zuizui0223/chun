# Solanaceae red biochemical profile — archived TreeBASE crosswalk v0.2

## Decision

`PASS_ARCHIVED_TREEBASE_S16617_OBJECT_CROSSWALK_FROZEN`

The preregistered 27-species red-flowered Solanaceae biochemical exact-profile candidate has now cleared its source/tree gate **without opening the profile outcome**.

The earlier `HOLD_TREEBASE_WEB_UI_STUDY_UNAVAILABLE` was a live TreeBASE transport/interface limitation. Two pinned historical TreeBASE-derived archives now corroborate the source identity and recover the archived tree object itself. This is treated as recovery of a historical TreeBASE serialization, not as substitution of a different phylogeny.

## Archived source identity

Parent phylogeny source:
- DOI `10.1111/nph.13576`;
- TreeBASE study `S16617`.

Independent archived study serialization:
- repository: `rdmpage/treebase-studies`;
- pinned commit: `e08d03e4d6a945bd2fa3d927d93bd45a89a6bc77`;
- path: `studies/S16617.xml`;
- the archived XML identifies `TB2:S16617`, the Ng & Smith paper, DOI `10.1111/nph.13576`, and TreeBASE study serializations.

Archived static TreeBASE rendering:
- repository: `bomeara/treebasestatic`;
- pinned commit: `7adf8ff09557dc1d368d4b8f8e7848c98da7ad93`;
- path: `studies/study_16617.html`;
- the study page links exactly one tree object, `tree_85881.phy`, labelled `MLT`, with 1,344 taxa and `Species Tree` metadata.

Recovered tree object:
- `trees/2016/tree_85881.phy`;
- Git blob `7d145c11d61b795d6939934368092fe12723529e`;
- SHA-256 `5fcc6d72d7d8c78aee59c3c32b5b73567424d701281c5056fb0c5ac93fa0a249`;
- 1,344 terminal tips;
- 2,686 non-root branches;
- non-root branches missing a branch length: `0`;
- duplicate fully normalized tip labels: `0`.

No OpenTree, newly reconstructed tree, figure digitization, or outcome-selected tree was used.

## Trait identifier source

The exact preregistered supplement was reacquired independently:
- PMCID `PMC4804202`;
- file `supp_plw013_plw013supp_table1.docx`;
- 118,778 bytes;
- SHA-256 `be5b7c75d52fef4714080938d638e31645ef5909c6b7a40ca1e8f2cadacebc2a`;
- 27 normalized source species identifiers.

Only identifier structure was used for this gate. The durable receipt intentionally freezes the exact DOCX member identity rather than the volatile outer Europe PMC supplementary ZIP digest.

## Frozen exact crosswalk

The preregistered rule required at least 20 exact normalized species/tree matches with no automatic synonym or fuzzy repair.

Result:
- exact matches: **25/27**;
- threshold: `>=20`;
- automatic synonym/fuzzy repair: **not used**.

Two source identifiers remain unmatched and are deliberately not repaired:
- `Cestrum newelli` versus archived tree `Cestrum_newellii`;
- the source `Cestrum sp ...` identifier versus archived tree `Cestrum_SpNov`.

The 25 exact matches are therefore the only currently admitted source/tree identifiers for the outcome analysis.

## Outcome firewall

At this freeze:
- pigment values emitted: `false`;
- pigment states computed: `false`;
- state frequencies computed: `false`;
- trait-frame patristic distances computed: `false`;
- profile AUC computed: `false`;
- permutations computed: `false`;
- winner class computed: `false`.

The biochemical hierarchy, common-frame thresholds, AUC estimator, 9,999 joint permutations, seed `20260915`, and terminal-class rules remain exactly those frozen before this source/tree gate.

### Exposure note

During an earlier post-preregistration source diagnostic, a small number of row-level chemistry cells were inadvertently exposed internally while diagnosing the DOCX structure. They were not used to define the hierarchy, select the tree, alter the common-frame rule, choose thresholds, or compute any profile statistic. The present tree-object selection and 25-species crosswalk were completed without using pigment outcomes. Accordingly this candidate remains **retrospective standardized training**, as preregistered; it is not relabelled as a prospective replication.

## Next gate

Only after this crosswalk receipt is frozen on `main` may a separate outcome execution:
1. open the Table S1 pigment variables;
2. retain only the frozen exact tree crosswalk;
3. construct the preregistered coarse/intermediate/fine biochemical states;
4. apply the `<5` fine-state common-frame filter and the `>=20` retained-tip / `>=2` states-per-resolution gates;
5. if those gates pass, compute the rank ROC AUC profile and 9,999 joint permutations with seed `20260915`.

Sensitivity analyses cannot rescue a failed or held primary result. Camellia Paper 1 remains unchanged.
