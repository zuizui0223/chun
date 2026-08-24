# Micro-accessibility registry provenance v0.1

This file records why each seed edge is admitted. It is not a substitute for the primary references or unified raw-data reanalysis.

| system | dependence cluster | admission role | current mechanistic evidence |
|---|---|---|---|
| *C. japonica* bud-sport series | `CJAPONICA` | somatic accessibility | redder states track stronger anthocyanin deployment |
| *C. japonica* Joy Kendrick sectors | `CJAPONICA` | within-genotype accessibility | red versus pink sectors differ in anthocyanin-related transcription |
| *C. japonica* white-to-crimson cultivar series | `CJAPONICA` | within-species accessibility | anthocyanin abundance tracks colour intensity |
| *C. reticulata* red/white sectors | `CRETICULATA` | within-genotype accessibility | red has higher cyanidin; white has lower CHS and higher ANR |
| *C. reticulata* Tongzimian fading | `CRETICULATA` | developmental accessibility | pink-to-white fading accompanies lower ANS/cyanidin and greater procyanidin diversion |
| *C. reticulata* cultivar series | `CRETICULATA` | within-species cultivar accessibility | red > pink > white anthocyanin programme |
| *C. sinensis* white/pink developmental series | `CSIN_WHITE_PINK` | matched developmental accessibility | pink has stronger anthocyanin deployment while FLS is higher in white |
| *C. nitidissima* 2017 yellow development | `CNITIDISSIMA` | developmental accessibility | yellow accumulation involves flavonol and carotenoid deployment |
| *C. nitidissima* 2024 yellow development | `CNITIDISSIMA` | independent study within same cluster | golden-stage flavonol deployment rises while anthocyanin/proanthocyanidin branches decline |
| *C. perpetua* yellow development | `CPERPETUA` | independent yellow developmental system | FLS-centred flavonoid deployment changes during yellowing |

## Dependence rule

A biological experiment is one system row, but repeated systems from the same focal taxon/evolutionary context share a broader `dependence_cluster`. The primary recurrence test is performed after cluster collapse. System-level results are sensitivity analyses only.

## Conservative coding rule

An axis is `unknown` unless the existing evidence product gives a directional mechanistic interpretation. Missing axes are never filled from visible colour. Conflicting known directions inside one dependence cluster become `mixed` rather than being majority-voted away.

## Candidate-ascertainment rule

These literature-coded edges are discovery inputs. The analysis separately tests whether A/F/C/P axes are resolved equally often. The observed system-level matrix is anthocyanin-heavy, so the validation layer must re-estimate all predefined pathway modules from public petal RNA-seq without selecting genes because the source paper highlighted them.

## External holdout rule

The three-species red/yellow/white dataset `PRJNA1136134` is not admitted as a short-timescale accessibility edge. It is reserved as an external candidate-free state-representation check after the micro model is frozen.
