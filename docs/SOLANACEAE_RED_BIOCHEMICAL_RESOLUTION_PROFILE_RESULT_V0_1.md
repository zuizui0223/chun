# Solanaceae red biochemical resolution profile result v0.1

## Terminal decision

`HOLD_INSUFFICIENT_COMMON_FRAME_OR_STATE_VARIATION`

This is the frozen outcome for the 27-species red-flowered Solanaceae candidate after the archived TreeBASE S16617 crosswalk gate passed. It is a **structural HOLD, not a biological winner/loser result**. No profile AUC, permutation p-value, or winning resolution was computed.

## Frozen inputs

- TreeBASE study: `S16617`
- archived source tree: `tree_85881.phy`
- exact source/tree crosswalk: 25 matched tips
- supplement: `supp_plw013_plw013supp_table1.docx`
- supplement SHA256: `be5b7c75d52fef4714080938d638e31645ef5909c6b7a40ca1e8f2cadacebc2a`
- preregistered rare-fine-state threshold: minimum 5 retained taxa per fine state
- permutation budget if the frame qualified: 9,999, seed `20260915`

The preregistration and frozen crosswalk were not modified after chemistry outcomes were opened.

## Source schema actually recovered

The supplement contains three same-universe species tables. The outcome runner joins the two chemistry tables by exact normalized source binomial:

1. anthocyanidin proportions, with six measured compounds aggregated into the preregistered branches:
   - pelargonidin = Pelargonidin;
   - cyanidin = Cyanidin + Peonidin;
   - delphinidin = Delphinidn + Petunidin + Malvidin;
2. carotenoid presence (`Y` / `N`, with `no data` treated as missing);
3. provenance/voucher information, not used to define phenotype states.

No synonym or fuzzy repair was introduced.

## Common-frame result

Of the 25 frozen crosswalk matches, **24** had complete chemistry required to construct the preregistered hierarchy. `Schizanthus grahamii` was ineligible because the carotenoid source field is `no data`.

Before the rare-state filter, the exact fine-state counts were:

| fine state | n |
|---|---:|
| `C0_P0_C0_D1` | 2 |
| `C0_P0_C1_D0` | 2 |
| `C0_P0_C1_D1` | 1 |
| `C0_P1_C0_D0` | 1 |
| `C0_P1_C1_D0` | 4 |
| `C1_P0_C0_D0` | 2 |
| `C1_P0_C0_D1` | 3 |
| `C1_P0_C1_D0` | 4 |
| `C1_P0_C1_D1` | 4 |
| `C1_P1_C0_D0` | 1 |

Every observed fine state therefore had fewer than the frozen minimum of 5 taxa. The common retained frame collapsed to **0 tips**.

The terminal hold reasons are:

- `COMMON_TIPS_LT_20`
- `COARSE_STATES_LT_2`
- `INTERMEDIATE_STATES_LT_2`
- `FINE_STATES_LT_2`

## Claim boundary

This candidate does **not** become a second completed biochemical exact-profile unit. It therefore does not identify a biochemical-versus-visible moderator and does not change the completed exact-profile count of 30.

The failure mode is nevertheless informative: in this source, the preregistered joint carotenoid × anthocyanidin-composition fine representation is too fragmented for the standardized exact-profile estimator at the frozen support threshold. Relaxing the minimum fine-state count, merging states after inspection, or replacing the frozen hierarchy would be post-hoc rescue and is prohibited for the primary result.

`resolution_profile_AUC_computed = false`

`winner_computed = false`

`post_hoc_rescue_allowed = false`

This unit remains retrospective standardized cross-representation training, not prospective replication. Camellia Paper 1 is unchanged.
